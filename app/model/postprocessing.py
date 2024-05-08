import numpy as np
import torch
import cv2
import time

def preprocess_inputs(x):
  """
  Takes in an image x and normalizes it.
  """
  x = np.asarray(x, dtype='float32')
  x /= 127
  x -= 1
  return x  

def float_to_uint(img):
  """
  This function converts the datatype of pixel values of an image from float32 to uint8 for downstream processing.
  """
  scaled_img = (img - img.min()) / (img.max() - img.min())
  uint8_img = (scaled_img * 255).astype(np.uint8)
  return uint8_img


# help from link: https://github.com/nka77/DAHiTra/blob/main/xBD_code/visualize_results.py
def get_dmg_msk(img1, img2, model):
  """
  Function that will return the predicted masks from the input images.

      Parameters
      img1 (): pre-disaster image
      img2 (): post-disaster image
      model: the model that will process the images and produce the output

      Returns
      msk (): output damage segmentation mask
  """
  # make image ready for model
  img = np.concatenate([img1, img2], axis=2)
  img = preprocess_inputs(img)
  img = torch.from_numpy(img.transpose((2, 0, 1))).float()
  img = img.unsqueeze(0)

  model.eval()
  with torch.no_grad():
    # check whether to use device agnostic code or not
    msk = model(img)
    msk = torch.sigmoid(msk)
    msknp = msk.cpu().numpy().transpose((0, 2, 3, 1))

    return msknp
  

def postprocess_per_img(img):
    """
    This function will smoothen and sharpen the edges of the buldings to provide a better result.

        Parameters:
        img: the set of masks to be smoothened, expected shape: (1, 5, img width, img height)

        Returns:
        dmg_msk: the processed and colored mask
    """
    # seperating the masks
    seg_msk = img[0, :, :, 0]
    green_msk = img[0, :, :, 1]
    yellow_msk = img[0, :, :, 2]
    orange_msk = img[0, :, :, 3]
    red_msk = img[0, :, :, 4]

    msk_list = [seg_msk, green_msk, yellow_msk, orange_msk, red_msk]
    output_msks = []

    for msk in msk_list:
        # convert datatype
        msk = float_to_uint(msk)
        # apply gaussian blur on each mask
        smooth_msk = cv2.GaussianBlur(msk, (3, 3), 0)
        # threshold to create a binary mask
        _, binary_msk = cv2.threshold(smooth_msk, 127, 255, cv2.THRESH_BINARY)
        # find contours
        contours, _ = cv2.findContours(binary_msk.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # draw polygons around the contours
        smooth_edge_msk = np.zeros_like(msk)
        for contour in contours:
            epsilon = 0.0001 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            cv2.drawContours(smooth_edge_msk, [approx], -1, (255), -1)  # fill contours
        # save the output mask
        output_msks.append(smooth_edge_msk)
    return output_msks

def assign_colors(msks):
  """
  This function assigns colors to each segmentation mask of each class and returns a combined colored mask.
  """
  height = msks[0].shape[0]
  width = msks[0].shape[1]
  colored_msk = np.zeros((height, width, 3), dtype=np.uint8)

  # assign colors
  colored_msk[msks[1] > 0.5] = [0, 200, 0] # green
  colored_msk[msks[2] > 0.5] = [255, 255, 0] # yellow
  colored_msk[msks[3] > 0.5] = [240, 128, 0] # orange
  colored_msk[msks[4] > 0.5] = [255, 0, 0] # red

  colored_msk_nrm = colored_msk / np.max(colored_msk)
  return colored_msk_nrm

def postprocessing(pre_image, post_image, model):
  """
  Wrapper function which performs all the operations required for post-processing the image sequentially.
  """
  start_time = time.time()
  model_output = get_dmg_msk(pre_image, post_image, model)
  end_time = time.time()
  inference_time = end_time - start_time
  print(f"Model Inference Time: {inference_time} seconds")

  start_time = time.time()
  output_msks = postprocess_per_img(model_output)
  end_time = time.time()
  preprocessing_time = end_time - start_time
  print(f"Preprocessing Time: {preprocessing_time} seconds")
  
  return output_msks
