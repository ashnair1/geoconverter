"""Test data generation utilities for geoconverter tests."""

import numpy as np
from osgeo import gdal, osr


def create_test_tif(output_path: str, width: int = 32, height: int = 32) -> str:
    """
    Create a test GeoTIFF file for testing purposes.

    Args:
        output_path: Path where the test TIFF should be created
        width: Width of the raster in pixels
        height: Height of the raster in pixels

    Returns:
        Path to the created file

    Reference: https://mygeoblog.com/2021/01/28/create-your-dummy-geotiff/
    """
    # Set up spatial reference system (Web Mercator)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(3857)  # Web Mercator

    # Create the GeoTIFF
    driver = gdal.GetDriverByName("GTiff")
    dst_ds = driver.Create(output_path, width, height, 1, gdal.GDT_Float32)

    if dst_ds is None:
        raise RuntimeError(f"Failed to create test file at {output_path}")

    # Create test data - simple gradient with some randomness
    arr = np.random.rand(height, width) * 100  # Random values 0-100

    # Write the array to the raster band
    band = dst_ds.GetRasterBand(1)
    band.WriteArray(arr)
    band.SetNoDataValue(-9999)

    # Set geospatial information
    dst_ds.SetProjection(srs.ExportToWkt())
    # GeoTransform: [top_left_x, pixel_width, rotation, top_left_y, rotation, pixel_height]
    dst_ds.SetGeoTransform([32.0, 1.0, 0.0, 32.0, 0.0, -1.0])

    # Force write to disk
    dst_ds.FlushCache()
    dst_ds = None  # Close file

    return output_path


def create_test_dem(output_path: str, width: int = 65, height: int = 65) -> str:
    """
    Create a test DEM (Digital Elevation Model) for terrain testing.

    Args:
        output_path: Path where the test DEM should be created
        width: Width of the DEM in pixels (default 65 for terrain tiles)
        height: Height of the DEM in pixels (default 65 for terrain tiles)

    Returns:
        Path to the created file
    """
    # Set up spatial reference system (WGS84 Geographic)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)  # WGS84

    # Create the GeoTIFF
    driver = gdal.GetDriverByName("GTiff")
    dst_ds = driver.Create(output_path, width, height, 1, gdal.GDT_Float32)

    if dst_ds is None:
        raise RuntimeError(f"Failed to create test DEM at {output_path}")

    # Create realistic elevation data (mountain-like terrain)
    x = np.linspace(0, 2 * np.pi, width)
    y = np.linspace(0, 2 * np.pi, height)
    X, Y = np.meshgrid(x, y)

    # Create mountain-like terrain
    elevation = (
        1000 * np.sin(X) * np.cos(Y)  # Main terrain
        + 500 * np.sin(2 * X) * np.sin(2 * Y)  # Secondary features
        + np.random.normal(0, 50, (height, width))  # Noise
    )

    # Ensure positive elevations
    elevation = np.maximum(elevation, 0)

    # Write the elevation data
    band = dst_ds.GetRasterBand(1)
    band.WriteArray(elevation.astype(np.float32))
    band.SetNoDataValue(-9999)

    # Set geospatial information (small area in geographic coordinates)
    dst_ds.SetProjection(srs.ExportToWkt())
    dst_ds.SetGeoTransform([-180.0, 0.1, 0.0, 90.0, 0.0, -0.1])

    # Force write to disk
    dst_ds.FlushCache()
    dst_ds = None  # Close file

    return output_path


if __name__ == "__main__":
    # Create default test files when run directly
    create_test_tif("tests/dummy.tif")
    create_test_dem("tests/dummy_dem.tif")
    print("Test files created: tests/dummy.tif, tests/dummy_dem.tif")
