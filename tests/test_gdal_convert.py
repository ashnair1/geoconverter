"""Tests for geoconverter.gdal_convert module."""

import pytest
from pathlib import Path
from argparse import Namespace
from unittest.mock import patch, MagicMock

# Only import if GDAL is available
gdal = pytest.importorskip("osgeo.gdal")

from geoconverter import gdal_convert


class TestBitRangeConstants:
    """Test BITRANGE constants."""
    
    def test_bitrange_types(self):
        """Test that BITRANGE contains expected data types."""
        expected_types = ["Byte", "UInt8", "UInt16", "UInt32", "Int16", "Int32", "Float32", "Float64"]
        
        for dtype in expected_types:
            assert dtype in gdal_convert.BITRANGE
            assert isinstance(gdal_convert.BITRANGE[dtype], list)
            assert len(gdal_convert.BITRANGE[dtype]) == 2
    
    def test_bitrange_values(self):
        """Test specific BITRANGE values."""
        assert gdal_convert.BITRANGE["Byte"] == [0.0, 255.0]
        assert gdal_convert.BITRANGE["UInt16"] == [0.0, 65535.0]
        assert gdal_convert.BITRANGE["Float32"] == [0.0, 1.0]


class TestTypeDict:
    """Test TYPE_DICT constants."""
    
    def test_type_dict_completeness(self):
        """Test that TYPE_DICT contains all BITRANGE keys."""
        for dtype in gdal_convert.BITRANGE.keys():
            assert dtype in gdal_convert.TYPE_DICT
    
    def test_type_dict_values(self):
        """Test that TYPE_DICT values are valid GDAL types."""
        assert gdal_convert.TYPE_DICT["Byte"] == gdal.GDT_Byte
        assert gdal_convert.TYPE_DICT["Float32"] == gdal.GDT_Float32


class TestGetScaleParams:
    """Tests for getScaleParams function."""
    
    @pytest.fixture
    def mock_dataset(self):
        """Create a mock GDAL dataset for testing."""
        mock_ds = MagicMock()
        mock_ds.RasterCount = 1
        
        # Mock band statistics
        mock_band = MagicMock()
        mock_band.GetStatistics.return_value = (0.0, 100.0, 50.0, 25.0)  # min, max, mean, std
        mock_ds.GetRasterBand.return_value = mock_band
        
        # Mock ReadAsArray for percentile calculations
        import numpy as np
        mock_ds.ReadAsArray.return_value = np.random.rand(1, 100, 100) * 100
        
        return mock_ds
    
    def test_get_scale_params_no_stretch(self, mock_dataset):
        """Test getScaleParams without percentile stretching."""
        output_range = [0.0, 255.0]
        
        result = gdal_convert.getScaleParams(
            mock_dataset, output_range, stretch=False, lower=2.0, upper=98.0
        )
        
        assert len(result) == 1  # One band
        assert len(result[0]) == 4  # [input_min, input_max, output_min, output_max]
        assert result[0][2:] == output_range  # Output range preserved
    
    def test_get_scale_params_with_stretch(self, mock_dataset):
        """Test getScaleParams with percentile stretching."""
        import numpy as np
        
        # Mock specific array data
        test_data = np.array([[[10, 20, 30, 90, 95]]])  # Shape: (bands, height, width)
        mock_dataset.ReadAsArray.return_value = test_data
        
        output_range = [0.0, 255.0]
        
        result = gdal_convert.getScaleParams(
            mock_dataset, output_range, stretch=True, lower=20.0, upper=80.0
        )
        
        assert len(result) == 1
        assert len(result[0]) == 4
        assert result[0][2:] == output_range


class TestSetupOptions:
    """Tests for setupOptions function."""
    
    @pytest.fixture
    def mock_dataset(self):
        """Create a mock dataset with multiple bands."""
        mock_ds = MagicMock()
        mock_ds.RasterCount = 3
        
        # Mock band statistics for 3 bands
        mock_band = MagicMock()
        mock_band.GetStatistics.return_value = (0.0, 100.0, 50.0, 25.0)
        mock_ds.GetRasterBand.return_value = mock_band
        
        return mock_ds
    
    def test_setup_options_basic(self, mock_dataset):
        """Test setupOptions with basic parameters."""
        with patch('geoconverter.gdal_convert.getScaleParams') as mock_scale:
            mock_scale.return_value = [[0, 100, 0, 255], [0, 100, 0, 255], [0, 100, 0, 255]]
            
            with patch('geoconverter.gdal_convert.gdal.TranslateOptions') as mock_options:
                result = gdal_convert.setupOptions(
                    mock_dataset, "GTiff", "Byte", [0.0, 255.0], None
                )
                
                mock_options.assert_called_once()
                call_kwargs = mock_options.call_args[1]
                assert call_kwargs["format"] == "GTiff"
                assert call_kwargs["outputType"] == gdal_convert.TYPE_DICT["Byte"]
    
    def test_setup_options_with_bands(self, mock_dataset):
        """Test setupOptions with specific band selection."""
        with patch('geoconverter.gdal_convert.getScaleParams') as mock_scale:
            mock_scale.return_value = [[0, 100, 0, 255], [0, 100, 0, 255], [0, 100, 0, 255]]
            
            with patch('geoconverter.gdal_convert.gdal.TranslateOptions') as mock_options:
                result = gdal_convert.setupOptions(
                    mock_dataset, "GTiff", "Byte", [0.0, 255.0], [1, 3]  # Bands 1 and 3
                )
                
                call_kwargs = mock_options.call_args[1]
                assert call_kwargs["bandList"] == [1, 3]


class TestGetArgs:
    """Tests for get_args function."""
    
    def test_get_args_basic(self):
        """Test get_args with basic arguments."""
        with patch('sys.argv', ['gdal_convert.py', '-i', 'input.tif']):
            args = gdal_convert.get_args()
            assert args.input == 'input.tif'
            assert args.format == 'Native'  # Default
            assert args.dtype == 'Native'   # Default
    
    def test_get_args_all_options(self):
        """Test get_args with all options."""
        test_argv = [
            'gdal_convert.py',
            '-i', 'input.tif',
            '-o', 'output.tif', 
            '-of', 'COG',
            '-ot', 'Byte',
            '-b', '1,2,3',
            'stretch', '-s', '2', '98'
        ]
        
        with patch('sys.argv', test_argv):
            args = gdal_convert.get_args()
            assert args.input == 'input.tif'
            assert args.output == 'output.tif'
            assert args.format == 'COG'
            assert args.dtype == 'Byte'
            assert args.bands == '1,2,3'
            assert args.subcommands == 'stretch'
            assert args.stretch == [2.0, 98.0]


class TestCliEntrypoint:
    """Tests for cli_entrypoint function."""
    
    def test_cli_entrypoint_basic(self):
        """Test cli_entrypoint creates proper args."""
        with patch('geoconverter.gdal_convert.main') as mock_main:
            with patch('geoconverter.gdal_convert.get_args') as mock_get_args:
                mock_args = Namespace()
                mock_get_args.return_value = mock_args
                
                gdal_convert.cli_entrypoint(
                    'input.tif', 'output.tif', 'COG', 'Byte', True, 2.0, 98.0
                )
                
                # Verify args were set correctly
                assert mock_args.input == 'input.tif'
                assert mock_args.output == 'output.tif'
                assert mock_args.format == 'COG'
                assert mock_args.dtype == 'Byte'
                assert mock_args.subcommands == 'stretch'
                assert mock_args.stretch == (2.0, 98.0)
                
                mock_main.assert_called_once_with(mock_args)
    
    def test_cli_entrypoint_no_contrast(self):
        """Test cli_entrypoint without contrast enhancement."""
        with patch('geoconverter.gdal_convert.main') as mock_main:
            with patch('geoconverter.gdal_convert.get_args') as mock_get_args:
                mock_args = Namespace()
                mock_get_args.return_value = mock_args
                
                gdal_convert.cli_entrypoint(
                    'input.tif', 'output.tif', 'GTiff', 'Native', False, 0.0, 100.0
                )
                
                assert not hasattr(mock_args, 'subcommands') or mock_args.subcommands is None


class TestMainFunction:
    """Tests for main function."""
    
    @pytest.fixture
    def basic_args(self, sample_tif, temp_dir):
        """Create basic args for testing."""
        output_file = temp_dir / "output.tif"
        args = Namespace(
            input=str(sample_tif),
            output=str(output_file),
            format='GTiff',
            dtype='Native',
            bands=None,
            range=None,
            subcommands=None
        )
        return args
    
    @pytest.mark.integration 
    def test_main_basic_conversion(self, basic_args):
        """Test main function performs basic conversion."""
        with patch('geoconverter.gdal_convert.gdal.Open') as mock_open:
            with patch('geoconverter.gdal_convert.gdal.Translate') as mock_translate:
                with patch('geoconverter.utils.parse_files') as mock_parse:
                    # Setup mocks
                    mock_ds = MagicMock()
                    mock_ds.GetDriver.return_value.GetDescription.return_value = 'GTiff'
                    mock_open.return_value = mock_ds
                    
                    mock_parse.return_value = ([Path(basic_args.input)], [Path(basic_args.output)])
                    
                    # Run main
                    gdal_convert.main(basic_args)
                    
                    # Verify calls
                    mock_open.assert_called()
                    mock_translate.assert_called()
    
    def test_main_with_custom_range(self, basic_args):
        """Test main function with custom output range."""
        basic_args.range = [0, 100]
        
        with patch('geoconverter.gdal_convert.gdal.Open') as mock_open:
            with patch('geoconverter.gdal_convert.gdal.Translate') as mock_translate:
                with patch('geoconverter.utils.parse_files') as mock_parse:
                    mock_ds = MagicMock()
                    mock_ds.GetDriver.return_value.GetDescription.return_value = 'GTiff'
                    mock_open.return_value = mock_ds
                    
                    mock_parse.return_value = ([Path(basic_args.input)], [Path(basic_args.output)])
                    
                    gdal_convert.main(basic_args)
                    
                    # Should not raise errors
                    mock_translate.assert_called()


@pytest.mark.integration
class TestGdalConvertIntegration:
    """Integration tests for the complete gdal_convert workflow."""
    
    def test_full_conversion_workflow(self, sample_tif, temp_dir):
        """Test complete conversion from input to output file."""
        output_file = temp_dir / "converted.tif"
        
        # Create args similar to CLI usage
        args = Namespace(
            input=str(sample_tif),
            output=str(output_file),
            format='GTiff',
            dtype='Native',
            bands=None,
            range=None,
            subcommands=None
        )
        
        # Run conversion
        gdal_convert.main(args)
        
        # Verify output file was created
        assert output_file.exists()
        
        # Verify it's a valid raster
        ds = gdal.Open(str(output_file))
        assert ds is not None
        assert ds.RasterCount >= 1
        ds = None  # Close file