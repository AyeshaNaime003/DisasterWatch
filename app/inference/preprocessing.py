import numpy as np
import rasterio

def tif_to_img(pre_tif_path, post_tif_path):
    with rasterio.open(pre_tif_path) as pre_tif, rasterio.open(post_tif_path) as post_tif:
        pre_img = np.transpose(pre_tif.read(), (1, 2, 0))
        post_img = np.transpose(post_tif.read(), (1, 2, 0))
        
    return [pre_img, post_img]

