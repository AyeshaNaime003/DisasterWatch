import folium
from folium.plugins import MarkerCluster

# Center of Karachi
karachi_center = [24.8607, 67.0011]

# Create a map object
mymap = folium.Map(location=karachi_center, zoom_start=14)

# Add Esri Satellite tile layer
esri_satellite = folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri',
    name='Esri Satellite',
    overlay=True,
    control=True
).add_to(mymap)

# Add FeatureGroup to hold polygons
# polygon_group = folium.FeatureGroup(name='Polygons').add_to(mymap)

# Define the rectangles with their respective colors
rectangles = [
    {"color": "red", "coordinates": [(24.861, 67.0005), (24.8615, 67.001), (24.8605, 67.001), (24.86, 67.0005)]},
    {"color": "yellow", "coordinates": [(24.8605, 67.001), (24.861, 67.0015), (24.860, 67.0015), (24.8595, 67.001)]},
    {"color": "green", "coordinates": [(24.861, 67.0015), (24.8615, 67.002), (24.8605, 67.002), (24.86, 67.0015)]},
]

geojson = {
  "features": [
    {
      "geometry": {
        "coordinates": [
          [
            [67.0005, 24.861],
            [67.001, 24.8615],
            [67.001, 24.8605],
            [67.0005, 24.86],
            [67.0005, 24.861]
          ]
        ],
        "type": "Polygon"
      },
      "properties": {
        "color": "red"
      },
      "type": "Feature"
    },
    {
      "geometry": {
        "coordinates": [
          [
            [67.001, 24.8605],
            [67.0015, 24.861],
            [67.0015, 24.860],
            [67.001, 24.8595],
            [67.001, 24.8605]
          ]
        ],
        "type": "Polygon"
      },
      "properties": {
        "color": "yellow"
      },
      "type": "Feature"
    },
    {
      "geometry": {
        "coordinates": [
          [
            [67.0015, 24.861],
            [67.002, 24.8615],
            [67.002, 24.8605],
            [67.0015, 24.86],
            [67.0015, 24.861]
          ]
        ],
        "type": "Polygon"
      },
      "properties": {
        "color": "green"
      },
      "type": "Feature"
    }
  ],
  "type": "FeatureCollection"
}


# # Add the rectangles to the map
# for rectangle in rectangles:
#     folium.Polygon(
#         locations=rectangle["coordinates"],
#         color=rectangle["color"],
#         fill=True,
#         fill_opacity=0.7
#     ).add_to(polygon_group)


# Define a polygon layer and add it to the map
# polygon_layer = folium.GeoJson(data=geojson)
# polygon_layer.add_to(mymap)

polygon_layer = folium.GeoJson(
    data = geojson,
    style_function = lambda feature: {
        'fillColor': 'green',  # Set the fill color
        'color': 'green',  # Set the border color
        'weight': 1,  # Set the border weight
        'fillOpacity': 0.5
    }
)
polygon_layer.add_to(mymap)


# Bind a popup to the polygon layer that displays the latitude and longitude
popup_text = "Latitude: {lat}, Longitude: {lon}".format(lat=24.8607, lon=67.0011)
polygon_layer.add_child(folium.Popup(popup_text))

# Display the map

# Add MarkerCluster for capturing click events
# marker_cluster = MarkerCluster().add_to(mymap)

# Add LayerControl for toggling layers
# folium.LayerControl().add_to(mymap)

# Render the map to obtain the HTML code as a string
html_code = mymap._repr_html_()
