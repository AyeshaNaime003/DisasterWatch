import numpy as np
from osgeo import gdal


def tif_to_img(pre_tif_path, post_tif_path):
  pre_tif, post_tif = gdal.Open(pre_tif_path), gdal.Open(post_tif_path)
  pre_post = []
  for tif_file in [pre_tif, post_tif]:
    disaster_img = np.dstack((tif_file.GetRasterBand(1).ReadAsArray(),
                    tif_file.GetRasterBand(2).ReadAsArray(),
                    tif_file.GetRasterBand(3).ReadAsArray()))
    pre_post.append(disaster_img)
  return pre_post
