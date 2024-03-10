import rasterio
from rasterio.windows import Window
import numpy as np

# Replace 'your_tiff_file.tif' with the actual path to your TIFF file
# tiff_file_path = 'woolsey-fire_00000715_pre_disaster.tif'

# # Open the TIFF file using rasterio
# with rasterio.open(tiff_file_path) as tif:
#     # transform object contains information about how pixel coordinates relate to geographic coordinates.
#     transform = tif.transform

#     # Get the coordinates of the top-left pixel
#     top_left_x, top_left_y = transform * (0, 0)
#     middle_x, middle_y = transform * (tif.width//2, tif.height//2)

#     # Get the coordinates of the bottom-right pixel
#     bottom_right_x, bottom_right_y = transform * (tif.width, tif.height)

#     # Print the results
#     # print(f"Top-left pixel - Longitude: {top_left_x}, Latitude: {top_left_y}")
#     # print(f"Middle pixel - Longitude: {middle_x}, Latitude: {middle_y}")
#     # print(f"Bottom-right pixel - Longitude: {bottom_right_x}, Latitude: {bottom_right_y}")


# # Open a raster dataset for reading
# with rasterio.open(tiff_file_path) as src:
    # Metadata
    # print("Metadata:")
    # print(src.meta)

    # Affine Transformation
    # print("\nAffine Transformation:")
    # transform = src.transform
    # print(transform)

    # # Coordinate Reference System (CRS)
    # print("\nCoordinate Reference System (CRS):")
    # print(src.crs)

    # # Number of Bands
    # print("\nNumber of Bands:")
    # print(src.count)

    # # Read pixel values for a specific window
    # window = Window(0, 0, 100, 100)  # Define a window (col_off, row_off, width, height)
    # data = src.read(window=window)

    # # Displaying pixel values
    # print("\nPixel Values for a Window:")
    # print(data)

    # # Statistics for each band
    # print("\nStatistics for Each Band:")
    # for band in range(1, src.count + 1):
    #     band_data = src.read(band)
    #     print(f"Band {band} - Min: {np.min(band_data)}, Max: {np.max(band_data)}, Mean: {np.mean(band_data)}")



def get_tif_transform(file_name):
    # Open the TIFF file using rasterio
    with rasterio.open(file_name) as tif:
        return tif.transform

def pixels_to_coordinates(transform, pixel):
    longitude, latitude = transform * pixel
    return latitude, longitude