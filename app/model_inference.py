import os
import sys
from PIL import Image
import torch
from osgeo import gdal
import cv2
import matplotlib.pyplot as plt
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
server_dir = os.path.join(parent_dir, 'server')
model_dir = os.path.join(parent_dir, 'model')

sys.path.append(parent_dir)
sys.path.append(server_dir)
sys.path.append(model_dir)
os.environ['TORCH_HOME'] = model_dir
# print(f"paths to check for module: {sys.path}")
from server.settings import *
from model.models import SeResNext50_Unet_MultiScale
from model.data_preprocessing import *

# Function to convert mask to polygons
def mask_to_polygons(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    polygons = []
    for contour in contours:
        # Approximate the contour to reduce the number of points
        epsilon = 0.01 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Filter out contours with fewer than 4 points
        if len(approx) >= 4:
            polygons.append(approx)
        else:
            # If the contour has fewer than 4 points, add points to make it at least 4
            while len(approx) < 4:
                # Duplicate the last point to make the contour at least 4 points
                approx = np.vstack((approx, approx[-1]))

            polygons.append(approx)

    return polygons


if True:
    # if request.method == 'POST' and request.FILES['pre_image'] and request.FILES['post_image']:

        # pre_image = request.FILES['pre_image']
        # post_image = request.FILES['post_image']
        # city = request.POST['city']  
        # date = request.POST['date']
        # disaster_type = request.POST['disaster_type']

        pre_path = os.path.join('woolsey-fire_00000715_pre_disaster.tif')
        post_path = os.path.join('woolsey-fire_00000715_post_disaster.tif')
        print(f"Using {pre_path} and {post_path}")
        # with open(pre_path, 'wb') as f:
        #     for chunk in pre_image.chunks():
        #         f.write(chunk)
        # with open(post_path, 'wb') as f:
        #     for chunk in post_image.chunks():
        #         f.write(chunk)

        pre_tif, post_tif = gdal.Open(pre_path), gdal.Open(post_path)
        pre, post = torch.from_numpy(tif_to_img(pre_tif)), torch.from_numpy(tif_to_img(post_tif))
        print(f"pre image shape: {pre.shape}, post image shape: {post.shape}")        
        pre_post = torch.cat((pre, post), dim=2).permute(2,0,1).unsqueeze(0).to(torch.float)
        print(pre_post.dtype, pre_post.shape, "\n\n\n")        


        # model = SeResNext50_Unet_MultiScale()
        # output = model(pre_post).squeeze()
        output = plt.imread("woolsey-fire_00000715_post_disaster.png")
        print(output.shape)

        masks = create_channel_masks("woolsey-fire_00000715_post_disaster.png")
        fig, axes = plt.subplots(1, len(masks), figsize=(20, 8))
        for i, mask in enumerate(masks):
            axes[i].imshow(mask, cmap='gray')
            axes[i].set_title(f"Mask {i + 1}")
            axes[i].axis('off')
        plt.show()

        # for mask in output:
        #     mask = mask.detach().numpy()
        #     print(f"mask shape: {mask.shape}")
        #     print(f"mask min: {mask.min()}  mask max: {mask.max()} avg: {mask.mean()}")

        #     mask = mask.astype('uint8')

        #     # Threshold the mask to convert it to a binary image
        #     _, mask = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY)
        #     print(f"mask min: {mask.min()}  mask max: {mask.max()} median: {np.median(mask)}")

        #     polygons_in_mask = mask_to_polygons(mask)
           
        #     print(type(polygons_in_mask))
        #     print(polygons_in_mask[:10])




        