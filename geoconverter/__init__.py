"""
Geoconverter: Application for converting between geospatial raster formats.

This package provides tools for converting geospatial raster data between different
formats, with support for GDAL-compatible formats and Cesium terrain tiles.

Key modules:
- gdal_convert: Core conversion functionality
- utils: Utility functions for file handling and format detection
- app: GUI application for interactive conversion

Example:
    >>> from geoconverter import gdal_convert
    >>> # Convert a raster file
    >>> gdal_convert.main(args)
"""

__version__ = "0.2.0"
__author__ = "Ashwin Nair"
__email__ = "ashnair0007@gmail.com"

# Public API exports
from geoconverter import gdal_convert, utils

# Version info tuple for programmatic access
version_info = tuple(int(x) for x in __version__.split("."))

# Metadata for package introspection
__all__ = [
    "gdal_convert",
    "utils",
    "__version__",
    "version_info",
]
