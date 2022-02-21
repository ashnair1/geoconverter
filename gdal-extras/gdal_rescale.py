#!/usr/bin/env python3

""" 
Rescales imagery to specified bit resolution and converts to specified format

Requires GDAL>=3.1

Usage:

python gdal-extras/gdal_rescale.py -i ./data/in/a.tif
python gdal-extras/gdal_rescale.py -i ./data/in/a.tif -o out/a_cog.tif -of COG
python gdal-extras/gdal_rescale.py -i ./data/in/a.tif -of COG -or 0 255
python gdal-extras/gdal_rescale.py -i ./data/in/ -o ./data/out/ -of JPEG -b 5,3,2

Full disclosure: This can be done using gdal_translate but you will need to manually set the scale params
"""

from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from osgeo import gdal

BITRANGE = {
    "Byte": [0.0, 255.0],
    "UInt8": [0.0, 255.0],
    "UInt16": [0.0, 65535.0],
    "UInt32": [0.0, 4294967295.0],
    "Int16": [-32768.0, 32767.0],
    "Int32": [-2147483648.0, 2147483647.0],
    "Float32": [0.0, 1.0],
    "Float64": [0.0, 1.0],
}  # type: Dict[str, List[float]]

TYPE_DICT = {
    "Byte": gdal.GDT_Byte,
    "UInt8": gdal.GDT_Byte,
    "UInt16": gdal.GDT_UInt16,
    "UInt32": gdal.GDT_UInt32,
    "Int16": gdal.GDT_Int16,
    "Int32": gdal.GDT_Int32,
    "Float32": gdal.GDT_Float32,
    "Float64": gdal.GDT_Float64,
}  # type: Dict[str, int]


def getScaleParams(ds: gdal.Dataset, outputRange: List[float]) -> List[List[float]]:
    stats = [
        ds.GetRasterBand(i + 1).GetStatistics(True, True) for i in range(ds.RasterCount)
    ]
    vmin, vmax, vmean, vstd = zip(*stats)
    scaleParams = list(zip(*[vmin, vmax]))
    scaleParams = [list(s) for s in scaleParams]
    return [s + outputRange for s in scaleParams]


def setupOptions(
    ds: gdal.Dataset,
    outputFormat: str,
    outputType: str,
    outputRange: List[float],
    bands: Optional[List[int]],
) -> gdal.GDALTranslateOptions:

    scaleParams = getScaleParams(ds, outputRange)
    if not bands:
        bands = list(range(1, ds.RasterCount + 1))
    scaleParams = [scaleParams[i - 1] for i in bands]
    return gdal.TranslateOptions(
        format=outputFormat,
        outputType=TYPE_DICT[outputType],
        bandList=bands,
        scaleParams=scaleParams,
    )


def parse_args() -> Namespace:
    parser = ArgumentParser(description="Rescaler")
    parser.add_argument("-i", "--input", help="input image/directory")
    parser.add_argument("-b", "--bands", type=str, help="bands string delimited by ,")
    parser.add_argument("-o", "--output", help="output image/directory")
    parser.add_argument("-of", "--format", default="GTiff", help="output format")
    parser.add_argument("-ot", "--dtype", default="Byte", help="output dtype")
    parser.add_argument("-or", "--range", type=float, nargs=2, help="output range")

    return parser.parse_args()


def parse_files(input: str, output: str, format: str) -> Tuple[List[Path], List[Path]]:

    drv = gdal.GetDriverByName(format)
    if not drv:
        raise AssertionError(
            "Invalid Driver. Refer GDAL documentation for accepted list of raster drivers"
        )

    if drv.GetMetadataItem(gdal.DCAP_RASTER):
        ext = ".tif" if format == "COG" else drv.GetMetadata_Dict().get("DMD_EXTENSION")
    if not ext:
        raise AssertionError(f"Specified output format {format} is not a raster format")

    inpath = Path(input)
    outpath = None if not output else Path(output)

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
            outpaths.append(outpath / f"{f.stem}_rescaled.{ext}")
    elif inpath.is_file():
        outpaths = (
            [inpath.parent / Path(f"rescaled{inpath.suffix}")]
            if not outpath
            else [outpath]
        )
        assert inpath.suffix.lower() != ".xml"
        files = [inpath]

    return files, outpaths


def main() -> None:
    args = parse_args()
    files, outfiles = parse_files(args.input, args.output, args.format)

    bands_out = [int(b) for b in args.bands.split(",")] if args.bands else None

    if args.range:
        # Custom range
        outputRange = [float(i) for i in args.range]
    else:
        outputRange = BITRANGE[args.dtype]

    for entry, out in zip(files, outfiles):
        ds = gdal.Open(str(entry))
        options = setupOptions(ds, args.format, args.dtype, outputRange, bands_out)
        gdal.Translate(
            destName=str(out),
            srcDS=ds,
            options=options,
        )


if __name__ == "__main__":
    main()
