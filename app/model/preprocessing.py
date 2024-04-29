import numpy as np

# FUNCTION TO GET IMAGE FROM TIF PATH
def tif_to_img(tif_file):
  disaster_img = np.dstack((tif_file.GetRasterBand(1).ReadAsArray(),
                  tif_file.GetRasterBand(2).ReadAsArray(),
                  tif_file.GetRasterBand(3).ReadAsArray()))
  return disaster_img