"""Tests for geoconverter.utils module."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Only import if GDAL is available
gdal = pytest.importorskip("osgeo.gdal")

from geoconverter import utils


class TestGetDtype:
    """Tests for get_dtype function."""
    
    def test_get_dtype_with_valid_file(self, sample_tif):
        """Test get_dtype returns correct data type for valid raster."""
        dtype = utils.get_dtype(sample_tif)
        assert isinstance(dtype, str)
        assert dtype in ["Byte", "UInt16", "Int16", "UInt32", "Int32", "Float32", "Float64"]
    
    def test_get_dtype_with_path_object(self, sample_tif):
        """Test get_dtype works with Path objects."""
        dtype = utils.get_dtype(Path(sample_tif))
        assert isinstance(dtype, str)
    
    def test_get_dtype_with_invalid_file(self, temp_dir):
        """Test get_dtype raises appropriate error for invalid file."""
        invalid_file = temp_dir / "nonexistent.tif"
        with pytest.raises(Exception):  # GDAL will raise some exception
            utils.get_dtype(invalid_file)


class TestGetExtension:
    """Tests for get_extension function."""
    
    def test_get_extension_gtiff(self, sample_tif):
        """Test get_extension returns correct extension for GTiff."""
        ext = utils.get_extension(sample_tif, "GTiff")
        assert ext == "tif"
    
    def test_get_extension_cog(self, sample_tif):
        """Test get_extension returns correct extension for COG."""
        ext = utils.get_extension(sample_tif, "COG")
        assert ext == "tif"
    
    def test_get_extension_native(self, sample_tif):
        """Test get_extension returns correct extension for native format."""
        ext = utils.get_extension(sample_tif, "native")
        assert ext == "tif"  # Should detect from input file
    
    def test_get_extension_invalid_format(self, sample_tif):
        """Test get_extension raises error for invalid format."""
        with pytest.raises(AssertionError):
            utils.get_extension(sample_tif, "INVALID_FORMAT")
    
    def test_get_extension_non_raster_format(self, sample_tif):
        """Test get_extension raises error for non-raster formats."""
        with pytest.raises(AssertionError, match="not a raster format"):
            utils.get_extension(sample_tif, "ESRI Shapefile")


class TestParseFiles:
    """Tests for parse_files function."""
    
    def test_parse_files_single_file(self, sample_tif, temp_dir):
        """Test parse_files with single input file."""
        output_file = temp_dir / "output.tif"
        
        files, outfiles = utils.parse_files(
            str(sample_tif), str(output_file), "GTiff"
        )
        
        assert len(files) == 1
        assert len(outfiles) == 1
        assert files[0] == sample_tif
        assert outfiles[0] == output_file
    
    def test_parse_files_single_file_auto_output(self, sample_tif):
        """Test parse_files with single file and automatic output naming."""
        files, outfiles = utils.parse_files(
            str(sample_tif), "", "GTiff", output_stub="processed"
        )
        
        assert len(files) == 1
        assert len(outfiles) == 1
        assert files[0] == sample_tif
        assert outfiles[0].name == "processed.tif"
        assert outfiles[0].parent == sample_tif.parent
    
    def test_parse_files_directory(self, temp_dir):
        """Test parse_files with input directory."""
        # Create test input directory with multiple files
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        input_dir.mkdir()
        output_dir.mkdir()
        
        # Create test files
        from tests.data import create_test_tif
        file1 = create_test_tif(str(input_dir / "test1.tif"))
        file2 = create_test_tif(str(input_dir / "test2.tif"))
        
        files, outfiles = utils.parse_files(
            str(input_dir), str(output_dir), "GTiff"
        )
        
        assert len(files) == 2
        assert len(outfiles) == 2
        
        # Check that all files are found and outputs are in output dir
        input_names = {f.stem for f in files}
        assert "test1" in input_names
        assert "test2" in input_names
        
        for outfile in outfiles:
            assert outfile.parent == output_dir
            assert outfile.suffix == ".tif"
    
    def test_parse_files_nonexistent_input(self):
        """Test parse_files raises error for nonexistent input."""
        with pytest.raises(AssertionError):
            utils.parse_files("/nonexistent/path", "/output", "GTiff")
    
    def test_parse_files_xml_files_ignored(self, temp_dir):
        """Test that XML auxiliary files are ignored."""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        input_dir.mkdir()
        output_dir.mkdir()
        
        # Create test files including XML
        from tests.data import create_test_tif
        create_test_tif(str(input_dir / "test.tif"))
        (input_dir / "test.tif.xml").write_text("<?xml version='1.0'?>")
        
        files, outfiles = utils.parse_files(
            str(input_dir), str(output_dir), "GTiff"
        )
        
        # Should only find the .tif file, not the .xml
        assert len(files) == 1
        assert files[0].suffix == ".tif"


class TestUtilsIntegration:
    """Integration tests for utils module."""
    
    @pytest.mark.integration
    def test_full_workflow(self, sample_tif, temp_dir):
        """Test a complete workflow using utils functions."""
        # Get dtype of input
        input_dtype = utils.get_dtype(sample_tif)
        
        # Get extension for COG format
        ext = utils.get_extension(sample_tif, "COG")
        
        # Parse files for conversion
        output_file = temp_dir / f"converted.{ext}"
        files, outfiles = utils.parse_files(
            str(sample_tif), str(output_file), "COG"
        )
        
        # Verify workflow
        assert input_dtype in ["Byte", "UInt16", "Int16", "UInt32", "Int32", "Float32", "Float64"]
        assert ext == "tif"
        assert len(files) == 1
        assert len(outfiles) == 1
        assert outfiles[0].suffix == ".tif"