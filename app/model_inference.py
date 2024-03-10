import os
import sys
from PIL import Image
import torch
from osgeo import gdal
import cv2
import matplotlib.pyplot as plt
import numpy as np
import time
import json

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
def mask_to_polygons(mask, rdp=True):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(len(contours))
    polygons = []
    for contour in contours:
        contour_points = np.squeeze(contour)
        epsilon = 0.01 * cv2.arcLength(contour_points, True)
        approx = np.squeeze(cv2.approxPolyDP(contour_points, epsilon, True)).tolist()
        polygons.append(approx)
    return polygons

def polygons_to_masks(polygons, image_shape=(1024,1024)):
    mask = np.zeros(image_shape, dtype=np.uint8)
    for polygon in polygons:
        cv2.fillPoly(mask, [polygon], 255)  # Fill each polygon with white color (255)
    return mask

def one_hot_encoding_mask(mask):
    # convert mask to hsv
    hsv = cv2.cvtColor(mask, cv2.COLOR_BGR2HSV)
    plt.imshow(mask)
    plt.show()
    # define color ranges
    lower_red = np.array([0, 50, 50])
    upper_red = np.array([10, 255, 255])
    lower_yellow = np.array([20, 50, 50])
    upper_yellow = np.array([30, 255, 255])
    lower_orange = np.array([10, 50, 50])
    upper_orange = np.array([20, 255, 255])
    lower_green = np.array([31, 50, 50])
    upper_green = np.array([80, 255, 255])
    # Create masks for each class using inRange function
    mskr = cv2.inRange(hsv, lower_red, upper_red)
    msky = cv2.inRange(hsv, lower_yellow, upper_yellow)
    msko = cv2.inRange(hsv, lower_orange, upper_orange)
    mskg = cv2.inRange(hsv, lower_green, upper_green)
    plt.imshow(mskr)
    plt.show()
    plt.imshow(msky)
    plt.show()
    plt.imshow(msko)
    plt.show()
    plt.imshow(mskg)
    plt.show()
    # Stack the masks along the channel axis to create one-hot encoded representation
    one_hot_encoded = np.stack([mskr, msko, msky, mskg])
    return one_hot_encoded


print("INPUT")
pre_path = os.path.join('woolsey-fire_00000715_pre_disaster.tif')
post_path = os.path.join('woolsey-fire_00000715_post_disaster.tif')
print(f"Using {pre_path} and {post_path}")
pre_tif, post_tif = gdal.Open(pre_path), gdal.Open(post_path)
pre, post = torch.from_numpy(tif_to_img(pre_tif)), torch.from_numpy(tif_to_img(post_tif))
print(f"pre image shape: {pre.shape}, post image shape: {post.shape}")        
pre_post = torch.cat((pre, post), dim=2).permute(2,0,1).unsqueeze(0).to(torch.float)
print(pre_post.dtype, pre_post.shape, "\n\n\n")        


# model = SeResNext50_Unet_MultiScale()
# output = model(pre_post).squeeze()
print("DUMMY OUTPUT")
classes=["green", "yellow", "orange","red"]
mask = cv2.imread("woolsey-fire_00000715_post_disaster.png")
masks = one_hot_encoding_mask(mask)
print(masks.shape, "\n\n")


# # plt.figure(figsize=(15, 5))  # Adjust the figure size as needed
# # for i in range(4):
# #     plt.subplot(1, 4, i + 1)
# #     plt.imshow(masks[i], cmap='gray')
# #     plt.title(classes[i])
# #     plt.axis('off')
# # plt.show()

print("MASKS TO POLYGON")
os.makedirs("./masks", exist_ok=True)
allcolor_polygons={}
for i, mask in enumerate(masks):
    color=classes[i]
    print(f"Working on {color} mask of shape {mask.shape}")
    
    mask = mask.astype('uint8')
    _, mask = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY)
    polygons_in_mask = mask_to_polygons(mask, rdp=False)

    allcolor_polygons[color]=polygons_in_mask
    # print(f"mask from polygon done, shape is {mask_from_polygon.shape}")
    # cv2.imwrite(f"./masks/og_{color}_mask.png", mask)
    # cv2.imwrite(f"./masks/approx_{color}_mask.png", mask_from_polygon)
    # print("masks written")


with open('./masks/data.json', 'w') as json_file:
    json.dump(allcolor_polygons, json_file)