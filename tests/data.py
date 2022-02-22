import numpy as np
from osgeo import gdal, osr

# Ref: https://mygeoblog.com/2021/01/28/create-your-dummy-geotiff/

# get the osr spatial reference
srs = osr.SpatialReference()
# we want meters
srs.ImportFromEPSG(3857)

# set pixel dimensions
nx = 32
ny = 32

# we create a geotiff with 1 band
dst_ds = gdal.GetDriverByName("GTiff").Create(
    "tests/dummy.tif", nx, ny, 1, gdal.GDT_Float32
)

# create a random grid of 32 by 32 pixels
arr = np.random.rand(32, 32)

# write the array to the geotiff
dst_ds.GetRasterBand(1).WriteArray(arr)
# optionally set some nodata
dst_ds.GetRasterBand(1).SetNoDataValue(-9999)
# set the projection
dst_ds.SetProjection(srs.ExportToWkt())
# /* top left x */
# /* w-e pixel resolution */
# /* 0 */
# /* top left y */
# /* 0 */
# /* n-s pixel resolution (negative value) */
dst_ds.SetGeoTransform([32, 1, 0, 32, 0, -1])
# FlushChache to write
dst_ds.FlushCache()
