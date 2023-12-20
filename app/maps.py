import folium

# Center of Karachi
karachi_center = [24.8607, 67.0011]

# Create a map object
map = folium.Map(location=karachi_center, 
                 zoom_start=14)
esri_satellite = folium.TileLayer(tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                                  attr='Esri',
                                  name='Esri Satellite',
                                  overlay=True,
                                  control=True).add_to(map)

# Define the rectangles with their respective colors
rectangles = [
    {"color": "red", "coordinates": [(24.861, 67.0005), (24.8615, 67.001), (24.8605, 67.001), (24.86, 67.0005)]},
    {"color": "yellow", "coordinates": [(24.8605, 67.001), (24.861, 67.0015), (24.860, 67.0015), (24.8595, 67.001)]},
    {"color": "green", "coordinates": [(24.861, 67.0015), (24.8615, 67.002), (24.8605, 67.002), (24.86, 67.0015)]},
]



# Add the rectangles to the map
for rectangle in rectangles:
    folium.Polygon(locations=rectangle["coordinates"], 
                   color=rectangle["color"], 
                   fill=True, 
                   fill_opacity=0.7).add_to(map)

# Save the map as an HTML file
map.save("map.html")