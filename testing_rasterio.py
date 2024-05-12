import rasterio
import numpy as np

def tif_to_img(pre_tif_path, post_tif_path):
    with rasterio.open(pre_tif_path) as pre_tif, rasterio.open(post_tif_path) as post_tif:
        pre_img = pre_tif.read()
        post_img = post_tif.read()
        
    return [pre_img, post_img]


def tiff_has_geospatial_info(tiff_path):
    try:
        with rasterio.open(tiff_path) as dataset:
            # Check if the TIFF file has geospatial information
            return dataset.crs is not None
    except Exception as e:
        print(f"Error checking geospatial info: {e}")
    return False


pre_tif_path = "app\\test_batches\hurricane-florence_00000480_pre_disaster.tif"
post_tif_path = "app\\test_batches\hurricane-florence_00000480_post_disaster.tif"

pre, post = tif_to_img(pre_tif_path, post_tif_path)
print(type(pre), type(post))
print(tiff_has_geospatial_info(pre_tif_path))
print(tiff_has_geospatial_info(post_tif_path))
print(tiff_has_geospatial_info("app\\test_batches\empty_post_image.tif"))


import matplotlib.pyplot as plt

plt.imshow(np.transpose(pre, (1,2,0)))
plt.show()