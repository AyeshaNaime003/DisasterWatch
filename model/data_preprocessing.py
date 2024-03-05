from osgeo import gdal
import numpy as np

# FUNCTION TO GET IMAGE FROM TIF PATH
def tif_to_img(tif_file):
  disaster_img = np.dstack((tif_file.GetRasterBand(1).ReadAsArray(),
                  tif_file.GetRasterBand(2).ReadAsArray(),
                  tif_file.GetRasterBand(3).ReadAsArray()))
  return disaster_img

# def tif_to_img(tif_path):
#   disaster = gdal.Open(r''+tif_path+'')
#   disaster_img = np.dstack((disaster.GetRasterBand(1).ReadAsArray(),
#                   disaster.GetRasterBand(2).ReadAsArray(),
#                   disaster.GetRasterBand(3).ReadAsArray()))
#   return disaster_img