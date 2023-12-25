import plotly.graph_objects as go
from numpy import average
from PIL import Image
import matplotlib.pyplot as plt

import rasterio
from rasterio.transform import from_origin

from geopy_address import get_street_name



# Sample data for demonstration
top_left_lon = -95.54183692483139
top_left_lat = 29.740561879769132
bottom_right_lon = -95.53718503013677
bottom_right_lat = 29.73590998507452

center_lat, center_lon = average([top_left_lat, bottom_right_lat]), average([top_left_lon, bottom_right_lon])
print(center_lat, center_lon)

mapbox_token = "pk.eyJ1IjoiYW5haW1lIiwiYSI6ImNscWdpeGhwZTEyMG4ydW1rY3l1aXRmdWYifQ.1NbqsFXFOcooQaqxAZ-DSA"

# Figure
fig = go.Figure()
karachi_center = [24.8607, 67.0011]
fig.update_layout(width=1000, height=500, 
                  margin=dict(l=10, r=10, t=30, b=10),
                  mapbox=dict(
                        style="satellite",
                        accesstoken=mapbox_token,
                        zoom=15,
                        center={"lat": center_lat, "lon":center_lon}))



# polygons
data = [
    {
        "id": 1, 
        "color": "green",
        "polygons": [
            (232.5173770256123, 845.8363458843754), 
            (239.3562863812729, 843.1007821418067), 
            (238.7700941502514, 841.1468080412766), 
            (264.5625522872949, 833.5263090463677), 
            (275.1140124319841, 847.7903199859203), 
            (276.4817943022538, 867.3300609942661), 
            (246.781387966433, 876.1229444537547), 
            (243.2642345838553, 875.7321496301988), 
            (232.5173770256123, 845.8363458843754)
        ]
    },
    {
        "id": 2, 
        "color": "green",
        "polygons": [
            (272.3606943939114, 828.7269851763605), 
            (301.7877835981718, 819.2504649224168), 
            (315.0050355282862, 836.7072127523271), 
            (318.7457672064864, 858.9022207142826), 
            (302.0371657092231, 863.8898629495154), 
            (300.5408730378415, 862.1441881663214), 
            (285.5779463235185, 866.1343019553195), 
            (272.3606943939114, 828.7269851763605)
        ]
    }
]
# Replace these values with your actual metadata
pixel_width, pixel_height = (top_left_lon-bottom_right_lon)/1024, (top_left_lat-bottom_right_lat)/1024
transform = from_origin(top_left_lon, top_left_lat, pixel_width, pixel_height)


# transform_str = f"|{transform.a:.10f}, {transform.b:.10f}, {transform.c:.10f}\n" \
#                 f"|{transform.d:.10f}, {transform.e:.10f}, {transform.f:.10f}|\n" \
#                 f"|{transform.xoff:.10f}, {transform.yoff:.10f}, {transform.g:.10f}|"


# Example x-y coordinates
latitudes = []
longitudes = []

for entry in data:
    polygons = entry["polygons"]
    x_coords, y_coords = zip(*polygons)
    lon, lat = rasterio.transform.xy(transform, x_coords, y_coords)
    latitudes.append(list(lat))
    longitudes.append(list(lon))


colors = {"red":"rgba(255,0,0, 0.5)",
          "green":"rgba(0,255,0, 0.5)",
          "yellow":"rgba(255,255,0, 0.5)"
          }

num_polygons = len(data)
for i in range(num_polygons):
    polygon_lat = latitudes[i]
    polygon_lon = longitudes[i]
    midpoint = (average(polygon_lat),average(polygon_lon))
    fillcolor = colors[data[i]['color']]
    ( landmark, street_name, locality, sublocality, district, city, region, postal_code, country ) = get_street_name(midpoint[0], midpoint[1])
    text = f"{landmark} {street_name}, {locality}, {sublocality}"
    
    # polygon trace
    polygon_trace = go.Scattermapbox(
        lat=polygon_lat,
        lon=polygon_lon,
        mode='lines',
        fill='toself',  
        fillcolor=fillcolor,  
        line=dict(color=fillcolor, width=2),  
        hoverinfo='none',
    )
    # hover trace
    hover_trace = go.Scattermapbox(
        lat=[midpoint[0]],
        lon=[midpoint[1]],
        mode='markers',
        hoverinfo='text',
        text=text,
        marker=dict(color=data[i]['color'])
    )


    fig.add_trace(polygon_trace)
    fig.add_trace(hover_trace)

fig.write_html("./file.html", auto_open=True)


