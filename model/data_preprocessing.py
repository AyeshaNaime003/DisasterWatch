import cv2
import numpy as np
import rasterio

def get_tif_transform(file_name):
    # Open the TIFF file using rasterio
    with rasterio.open(file_name) as tif:
        return tif.transform

def pixels_to_coordinates(transform, pixel):
    longitude, latitude = transform * pixel
    return latitude, longitude

# FUNCTION TO GET IMAGE FROM TIF PATH
def tif_to_img(tif_file):
  disaster_img = np.dstack((tif_file.GetRasterBand(1).ReadAsArray(),
                  tif_file.GetRasterBand(2).ReadAsArray(),
                  tif_file.GetRasterBand(3).ReadAsArray()))
  return disaster_img

def mask_to_polygons(mask, transform, rdp=True):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    polygons = []
    for contour in contours:
        contour_points = np.squeeze(contour)
        epsilon = 0.01 * cv2.arcLength(contour_points, True)
        approx = np.squeeze(cv2.approxPolyDP(contour_points, epsilon, True)).tolist()
        approx_latlong = [pixels_to_coordinates(transform, (x, y)) for x, y in approx]
        
        # Convert back to numpy array and append to polygons list
        polygons.append(approx_latlong)
    return polygons

def polygons_to_masks(polygons, image_shape=(1024,1024)):
    mask = np.zeros(image_shape, dtype=np.uint8)
    for polygon in polygons:
        cv2.fillPoly(mask, [polygon], 255)  # Fill each polygon with white color (255)
    return mask

def one_hot_encoding_mask(mask):
    # convert mask to hsv
    hsv = cv2.cvtColor(mask, cv2.COLOR_BGR2HSV)
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
    # Stack the masks along the channel axis to create one-hot encoded representation
    one_hot_encoded = np.stack([mskr, msko, msky, mskg])
    return one_hot_encoded
