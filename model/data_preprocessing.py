import cv2
import numpy as np

# FUNCTION TO GET IMAGE FROM TIF PATH
def tif_to_img(tif_file):
  disaster_img = np.dstack((tif_file.GetRasterBand(1).ReadAsArray(),
                  tif_file.GetRasterBand(2).ReadAsArray(),
                  tif_file.GetRasterBand(3).ReadAsArray()))
  return disaster_img

def create_channel_masks(mask_path):
    # Read the image
    output = cv2.imread(mask_path)

    # Convert image to HSV
    hsv = cv2.cvtColor(output, cv2.COLOR_BGR2HSV)

    # Define color thresholds in HSV (Hue, Saturation, Value) space
    lower_red = np.array([0, 50, 50])
    upper_red = np.array([10, 255, 255])

    lower_yellow = np.array([20, 50, 50])
    upper_yellow = np.array([30, 255, 255])  # Adjusted upper limit for yellow

    lower_orange = np.array([10, 50, 50])
    upper_orange = np.array([20, 255, 255])

    lower_green = np.array([31, 50, 50])     # Adjusted lower limit for green
    upper_green = np.array([80, 255, 255])

    # Create masks
    mask_red = cv2.inRange(hsv, lower_red, upper_red)
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
    mask_orange = cv2.inRange(hsv, lower_orange, upper_orange)
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    # Make a mask array that contains all the masks in one array
    msk = np.zeros((5, output.shape[0], output.shape[1]), dtype=np.uint8)
    # msk[0, :, :] = 255 - np.max(output, axis=2)  # Invert the binary image
    msk[1, :, :] = mask_green
    msk[2, :, :] = mask_yellow
    msk[3, :, :] = mask_orange
    msk[4, :, :] = mask_red

    # Threshold to make binary
    msk = msk > 5

    return msk
