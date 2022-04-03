#!/usr/bin/env python3

"""
Rescales imagery to specified bit resolution and converts to specified format.

Requires GDAL>=3.1

Usage:

```console
python geoconverter/gdal_convert.py -i ./data/in/a.tif
python geoconverter/gdal_convert.py -i ./data/in/a.tif -o out/a_cog.tif -of COG
python geoconverter/gdal_convert.py -i ./data/in/a.tif -of COG -or 0 255
python geoconverter/gdal_convert.py -i ./data/in/ -o ./data/out/ -of JPEG -b 5,3,2
python geoconverter/gdal_convert.py -i ./data/in/ -o ./data/out/ -of JPEG -b 5,3,2 stretch 2 98
```
Full disclosure: This can be done using gdal_translate but you will need to
manually set the scale params
"""

from argparse import ArgumentParser, Namespace
from typing import Dict, List, Optional

import numpy as np
from osgeo import gdal

from geoconverter.utils import get_dtype, parse_files

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


def getScaleParams(
    ds: gdal.Dataset,
    outputRange: List[float],
    stretch: Optional[bool],
    lower: float,
    upper: float,
) -> List[List[float]]:

    if stretch:
        band_arr = ds.ReadAsArray()  # (B, H, W)
        assert band_arr.ndim == 3
        lower_percentile = np.percentile(band_arr, lower, axis=(1, 2))
        upper_percentile = np.percentile(band_arr, upper, axis=(1, 2))
        scaleParams = [
            [lower, upper] for lower, upper in zip(lower_percentile, upper_percentile)
        ]
    else:
        stats = [
            ds.GetRasterBand(i + 1).GetStatistics(True, True)
            for i in range(ds.RasterCount)
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
    stretch: Optional[bool] = False,
    lower: float = 0.0,
    upper: float = 100.0,
) -> gdal.GDALTranslateOptions:

    scaleParams = getScaleParams(ds, outputRange, stretch, lower, upper)
    if not bands:
        bands = list(range(1, ds.RasterCount + 1))
    scaleParams = [scaleParams[i - 1] for i in bands]
    return gdal.TranslateOptions(
        format=outputFormat,
        outputType=TYPE_DICT[outputType],
        bandList=bands,
        scaleParams=scaleParams,
    )


def get_args() -> Namespace:
    parser = ArgumentParser(description="Converter")
    parser.add_argument("-i", "--input", help="input image/directory")
    parser.add_argument("-b", "--bands", type=str, help="bands string delimited by ,")
    parser.add_argument("-o", "--output", help="output image/directory")
    parser.add_argument("-of", "--format", default="Native", help="output format")
    parser.add_argument("-ot", "--dtype", default="Native", help="output dtype")
    parser.add_argument("-or", "--range", type=float, nargs=2, help="output range")

    subparsers = parser.add_subparsers(dest="subcommands", help="Subcommands")

    # Contrast stretching
    stretch_parser = subparsers.add_parser("stretch", help="Contrast stretch")
    stretch_parser.add_argument(
        "-s",
        "--stretch",
        nargs=2,
        type=float,
        default=[0.0, 100.0],
        metavar=("lower", "upper"),
        required=False,
        help="stretch lower & upper percentiles",
    )

    return parser.parse_args()


def cli_entrypoint(
    input: str,
    output: str,
    format: str,
    dtype: str,
    docontrast: bool,
    lower: float,
    upper: float,
) -> None:
    args = get_args()
    args.input = input
    args.output = output
    args.format = format
    args.dtype = dtype
    if docontrast:
        args.subcommands = "stretch"
        args.stretch = (lower, upper)
    main(args)


def main(args: Namespace) -> None:
    files, outfiles = parse_files(args.input, args.output, args.format)

    bands_out = [int(b) for b in args.bands.split(",")] if args.bands else None

    for entry, out in zip(files, outfiles):
        ds = gdal.Open(str(entry))
        if args.format.lower() == "native":
            args.format = ds.GetDriver().GetDescription()
        if args.dtype.lower() == "native":
            args.dtype = get_dtype(entry)
        if args.range:
            # Custom range
            outputRange = [float(i) for i in args.range]
        else:
            outputRange = BITRANGE[args.dtype]

        if args.subcommands == "stretch":
            kwargs = {
                "stretch": True,
                "lower": args.stretch[0],
                "upper": args.stretch[1],
            }
        else:
            kwargs = {}

        options = setupOptions(
            ds, args.format, args.dtype, outputRange, bands_out, **kwargs
        )
        gdal.Translate(destName=str(out), srcDS=ds, options=options)
        ds = None


if __name__ == "__main__":
    args = get_args()
    main(args)
