"""Utilities for geoconverter"""

from pathlib import Path
from typing import List, Tuple, Union

from osgeo import gdal


def get_dtype(input: Union[Path, str]) -> str:
    """Get dtype of raster.

    Args:
        input (Union[Path, str]): Path to raster

    Returns:
        str: Raster dtype
    """
    ds = gdal.Open(str(input))
    DataType = ds.GetRasterBand(1).DataType
    dtype: str = gdal.GetDataTypeName(DataType)
    ds = None
    return dtype


def get_extension(input: Union[Path, str], format: str) -> str:
    """Get extension for specified format.

    Args:
        input (Union[Path, str]): Path to raster
        format (str): Raster format

    Raises:
        AssertionError: if specified format is not a valid GDAL driver
        AssertionError: if specified format does not have a valid extension

    Returns:
        str: File extension
    """

    if format.lower() != "native":
        drv = gdal.GetDriverByName(format)
    else:
        ds = gdal.Open(str(input))
        drv = ds.GetDriver()
        del ds
    if not drv:
        raise AssertionError(
            "Invalid Driver. Refer GDAL documentation "
            "for accepted list of raster drivers"
        )

    if drv.GetMetadataItem(gdal.DCAP_RASTER):
        ext: str = (
            "tif" if format == "COG" else drv.GetMetadata_Dict().get("DMD_EXTENSION")
        )
    if not ext:
        raise AssertionError(f"Specified output format {format} is not a raster format")
    return ext


def parse_files(
    input: str, output: str, format: str, output_stub: str = "converted"
) -> Tuple[List[Path], List[Path]]:
    """Parse specified input (file/dir) and output (file/dir)

    Args:
        input (str): Path to raster or directory of rasters
        output (str): Path to output raster or directory
        format (str): Raster format
        output_stub (str, optional): String added to output filename. Defaults to "converted".

    Returns:
        Tuple[List[Path], List[Path]]: List of input and output paths
    """
    assert Path(input).exists() and input != ""

    inpath = Path(input)
    outpath = Path(output) if output else None

    if inpath.is_dir():
        # If input is a dir, then output dir must be specified
        outpath = Path(output)
        assert outpath.is_dir()
        files = []
        outpaths = []
        for f in inpath.rglob("*"):
            # Skip auxiliary files and subdirectories
            if f.suffix.lower() == ".xml" or f.is_dir():
                continue
            files.append(f)
            ext = get_extension(f, format)
            outpaths.append(outpath / f"{f.stem}_{output_stub}.{ext}")
    elif inpath.is_file():
        ext = get_extension(inpath, format)
        outpaths = (
            [outpath] if outpath else [inpath.parent / Path(f"{output_stub}.{ext}")]
        )
        assert inpath.suffix.lower() != ".xml"
        files = [inpath]

    return files, outpaths
