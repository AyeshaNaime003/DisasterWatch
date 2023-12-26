import rasterio
from rasterio.windows import Window
import numpy as np

# Replace 'your_tiff_file.tif' with the actual path to your TIFF file
tiff_file_path = 'hurricane-florence_00000004_post_disaster.tif'

# Open the TIFF file using rasterio
with rasterio.open(tiff_file_path) as tif:
    # transform object contains information about how pixel coordinates relate to geographic coordinates.
    transform = tif.transform

    # Get the coordinates of the top-left pixel
    top_left_x, top_left_y = transform * (0, 0)

    # Get the coordinates of the bottom-right pixel
    bottom_right_x, bottom_right_y = transform * (tif.width, tif.height)

    # Print the results
    print(f"Top-left pixel - Longitude: {top_left_x}, Latitude: {top_left_y}")
    print(f"Bottom-right pixel - Longitude: {bottom_right_x}, Latitude: {bottom_right_y}")


# Open a raster dataset for reading
with rasterio.open(tiff_file_path) as src:
    # Metadata
    print("Metadata:")
    print(src.meta)

    # Affine Transformation
    print("\nAffine Transformation:")
    transform = src.transform
    print(transform)

    # Coordinate Reference System (CRS)
    print("\nCoordinate Reference System (CRS):")
    print(src.crs)

    # Number of Bands
    print("\nNumber of Bands:")
    print(src.count)

    # Read pixel values for a specific window
    window = Window(0, 0, 100, 100)  # Define a window (col_off, row_off, width, height)
    data = src.read(window=window)

    # Displaying pixel values
    print("\nPixel Values for a Window:")
    print(data)

    # Statistics for each band
    print("\nStatistics for Each Band:")
    for band in range(1, src.count + 1):
        band_data = src.read(band)
        print(f"Band {band} - Min: {np.min(band_data)}, Max: {np.max(band_data)}, Mean: {np.mean(band_data)}")
"""
OUTPUT:
trasnform: 
| 0.00, 0.00,-95.54|    |a, b, c|
| 0.00,-0.00, 29.74|    |d, e, f|
| 0.00, 0.00,  1.00|    |0, 0, 1|
a and e: Scaling factors for the x and y axes. They represent the change in size of a pixel in the x and y directions.
b and d: Rotation coefficients. They represent the rotation of the image. If both are zero, the image is not rotated.
c and f: Translation coefficients. They represent the shift or translation of the image in the x and y directions.
The last row, [0, 0, 1], is typically a constant row.

Top-left pixel 
Longitude: -95.54183692483139, Latitude: 29.740561879769132     
Bottom-right pixel - 
Longitude: -95.53718503013677, Latitude: 29.73590998507452


Top-left pixel - Longitude: -79.0370213189266, Latitude: 33.60739228649503
Bottom-right pixel - Longitude: -79.03236854506585, Latitude: 33.60273951263427
"""