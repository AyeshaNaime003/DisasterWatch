import plotly.graph_objects as go
import numpy as np
from PIL import Image

# Sample data for demonstration
top_left_lat = -95.54183692483139
top_left_lon = 29.740561879769132
bottom_right_lat = -95.53718503013677
bottom_right_lon = 29.73590998507452

center_lat, center_lon = np.average([top_left_lat, bottom_right_lat]), np.average([top_left_lon, bottom_right_lon])

mapbox_token = "pk.eyJ1IjoiYW5haW1lIiwiYSI6ImNscWdpeGhwZTEyMG4ydW1rY3l1aXRmdWYifQ.1NbqsFXFOcooQaqxAZ-DSA"

# Load the segmentation mask image (replace 'your_mask.png' with the actual file path)
mask_image = Image.open('hurricane-harvey_00000428_post_disaster.png')

# Create a Mapbox figure
fig = go.Figure()

fig.add_trace(go.Scattermapbox(
    mode="markers",
    lat=[center_lat],
    lon=[center_lon],
    marker=dict(size=10, color="red"),
))

# Update the layout with Mapbox style and center
fig.update_layout(width=1000, height=500, 
                  margin=dict(l=10, r=10, t=30, b=10),
                  mapbox=dict(
                        style="satellite",
                        accesstoken=mapbox_token,
                        zoom=10,
                        center={"lat": center_lat, "lon": center_lon}))

# Save the figure to an HTML file
fig.write_html("./file.html", auto_open=True)
