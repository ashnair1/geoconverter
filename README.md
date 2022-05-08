# geoconverter

[![docs](https://github.com/ashnair1/geoconverter/actions/workflows/docs.yml/badge.svg)](https://github.com/ashnair1/geoconverter/actions/workflows/docs.yml)

Application for converting between geospatial raster formats. 

## Requirements

- gdal >= 3.1
- Python >= 3.6

## Overview
`geoconverter` is an application built for simple conversion between geospatial raster formats. It leverages [gdal](https://gdal.org/) for handling the geospatial rasters and a [fork](https://github.com/ahuarte47/cesium-terrain-builder) of [cesium-terrain-builder](https://github.com/geo-data/cesium-terrain-builder) for cesium terrain formats. 

## Features

- Correctly handles dtype conversion via correctly checking the min and max of raster bands and rescaling appropriately. This is possible via [`gdal_translate`](https://gdal.org/programs/gdal_translate.html) but you will need to manually find the min and max of the raster bands and specify it via the [-scale](https://gdal.org/programs/gdal_translate.html#cmdoption-gdal_translate-scale) parameter. Geoconverter does this automatically.
- Supports cesium terrain formats. Using the cesium-terrain-builder (fork), geoconverter is also able to convert DEM rasters to cesium compatible terrain and quantized mesh formats.
- Supports percentile contrast enhancement.
- Provides a simple GUI.


## Documentation
Project documentation can be found [here](https://ashnair1.github.io/geoconverter/index)

## Acknowledgements
The author would like to thank all the contributors to the gdal library and to [@homme](https://github.com/homme) and [@ahuarte47](https://github.com/ahuarte47) for their work on Cesium Terrain Builder and quantized-mesh support respectively.