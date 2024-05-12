import numpy as np
import rasterio
# from osgeo import gdal


# def tif_to_img(pre_tif_path, post_tif_path):
#   pre_tif, post_tif = gdal.Open(pre_tif_path), gdal.Open(post_tif_path)
#   pre_post = []
#   for tif_file in [pre_tif, post_tif]:
#     disaster_img = np.dstack((tif_file.GetRasterBand(1).ReadAsArray(),
#                     tif_file.GetRasterBand(2).ReadAsArray(),
#                     tif_file.GetRasterBand(3).ReadAsArray()))
#     pre_post.append(disaster_img)
#   return pre_post

def tif_to_img(pre_tif_path, post_tif_path):
    with rasterio.open(pre_tif_path) as pre_tif, rasterio.open(post_tif_path) as post_tif:
        pre_img = np.transpose(pre_tif.read(), (1, 2, 0))
        post_img = np.transpose(post_tif.read(), (1, 2, 0))
        
    return [pre_img, post_img]

