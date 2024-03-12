from leaflet import LatLng

# Get the pixel coordinates from your model
x = 100
y = 200

# Convert pixels to latitude and longitude
latlng = LatLng(y, x)

# Get the latitude and longitude values
latitude = latlng.lat
longitude = latlng.lng
