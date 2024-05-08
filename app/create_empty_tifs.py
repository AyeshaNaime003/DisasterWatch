
from io import BytesIO
from PIL import Image

def create_dummy_tiff(width, height):
    # Create a blank TIFF image using PIL
    image = Image.new('RGB', (width, height))
    with BytesIO() as buffer:
        image.save(buffer, format='TIFF')
        return buffer.getvalue()

# Example usage:
width = 1024
height = 1024

# Create empty TIFF files and save them
pre_image_data = create_dummy_tiff(width, height)
with open('empty_pre_image.tif', 'wb') as f:
    f.write(pre_image_data)

post_image_data = create_dummy_tiff(width, height)
with open('empty_post_image.tif', 'wb') as f:
    f.write(post_image_data)

print("Empty TIFF files created and saved.")