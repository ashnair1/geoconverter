#!/usr/bin/env python3

"""
Apply contrast stretch on imagery

Requires GDAL>=3.1

Usage example

python gdal_stretch.py -i ./data/mosaic.tif -b 5,3,2 -o ./data/mosaic_stretched.tif
"""

import os
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List, Optional, Sequence, Tuple, Union

import numpy as np
from osgeo import gdal, osr


def percentile_normalization(
    arr: np.ndarray,
    lower: float,
    upper: float,
    axis: Optional[Union[int, Sequence[int]]] = None,
) -> np.ndarray:
    assert lower < upper
    lower_percentile = np.percentile(arr, lower, axis=axis)
    upper_percentile = np.percentile(arr, upper, axis=axis)
    return np.clip(
        (arr - lower_percentile) / (upper_percentile - lower_percentile), 0, 1
    )


def parse_files(input: str, output: str) -> Tuple[List[Path], List[Path]]:

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
            outpaths.append(outpath / f"{f.stem}_stretched{f.suffix}")
    elif inpath.is_file():
        outpaths = (
            [inpath.parent / Path(f"stretched{inpath.suffix}")]
            if not outpath
            else [outpath]
        )
        assert inpath.suffix.lower() != ".xml"
        files = [inpath]

    return files, outpaths


def parse_args() -> Namespace:
    parser = ArgumentParser(description="Rescaler")
    parser.add_argument("-i", "--input", help="input image/directory")
    parser.add_argument("-b", "--bands", type=str, help="bands string delimited by ,")
    parser.add_argument("-o", "--output", help="output image/directory")
    parser.add_argument(
        "-s",
        "--stretch",
        nargs=2,
        type=float,
        default=[2.0, 98.0],
        help="stretch lower & upper percentiles",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    files, outfiles = parse_files(args.input, args.output)

    for entry, out in zip(files, outfiles):

        print(
            f"Applying percentile normalization on {entry}. "
            f"Output will be written to {out}"
        )
        inDs = gdal.Open(str(entry))
        srs = osr.SpatialReference()

        bands = (
            [int(b) for b in args.bands.split(",")]
            if args.bands
            else list(range(1, inDs.RasterCount + 1))
        )

        bands_out = []
        for b in bands:
            band = inDs.GetRasterBand(b).ReadAsArray()
            bands_out.append(band)

        lower, upper = args.stretch
        bands_scaled: np.ndarray = percentile_normalization(
            np.dstack(bands_out), lower, upper, (0, 1)
        )

        rows, cols = bands_scaled.shape[:2]

        driver = inDs.GetDriver()

        if driver.GetMetadataItem(gdal.DCAP_CREATE):
            outDs = driver.Create(
                str(out), cols, rows, bands_scaled.shape[-1], gdal.GDT_Float64
            )
        elif driver.GetMetadataItem(gdal.DCAP_CREATECOPY):
            tmp_drv = gdal.GetDriverByName("GTiff")
            bands_scaled *= np.iinfo(np.uint16).max
            outDs = tmp_drv.Create(
                "/tmp/tmp.tif", cols, rows, bands_scaled.shape[-1], gdal.GDT_UInt16
            )

        else:
            drv_name = driver.GetDescription()
            print(f"{drv_name} does not support creation. Skipping..")
            continue

        # Write metadata
        srs.ImportFromWkt(inDs.GetProjection())
        outDs.SetGeoTransform(inDs.GetGeoTransform())
        outDs.SetProjection(srs.ExportToWkt())

        # Write raster data sets
        for i in range(bands_scaled.shape[-1]):
            outBand = outDs.GetRasterBand(i + 1)
            outBand.WriteArray(bands_scaled[:, :, i])

        if driver.GetMetadataItem(gdal.DCAP_CREATECOPY):
            outDs = driver.CreateCopy(str(out), outDs)
            if os.path.exists("/tmp/tmp.tif"):
                os.remove("/tmp/tmp.tif")
        # Close raster file
        outDs = None
        inDs = None


if __name__ == "__main__":
    main()
