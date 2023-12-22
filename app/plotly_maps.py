import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Create a DataFrame with the data
data = {
    'color': ['red', 'yellow', 'green'] * 6,
    'coordinate1': [[67.0005, 24.861],[67.001, 24.8605],[67.0015, 24.861],[67.002, 24.8605],[67.0025, 24.861],[67.003, 24.8605],[67.0035, 24.861],[67.004, 24.8605],[67.0045, 24.861],[67.005, 24.8605],[67.0055, 24.861],[67.006, 24.8605],[67.0065, 24.861],[67.007, 24.8605],[67.0075, 24.861],[67.008, 24.8605],[67.0085, 24.861],[67.009, 24.8605]], 
    'coordinate2': [[67.001, 24.8615],[67.0015, 24.861],[67.002, 24.8615],[67.0025, 24.861],[67.003, 24.8615],[67.0035, 24.861],[67.004, 24.8615],[67.0045, 24.861],[67.005, 24.8615],[67.0055, 24.861],[67.006, 24.8615],[67.0065, 24.861],[67.007, 24.8615],[67.0075, 24.861],[67.008, 24.8615],[67.0085, 24.861],[67.009, 24.8615],[67.0095, 24.861]],
    'coordinate3': [[67.001, 24.8605],[67.0015, 24.860],[67.002, 24.8605],[67.0025, 24.860],[67.003, 24.8605],[67.0035, 24.860],[67.004, 24.8605],[67.0045, 24.860],[67.005, 24.8605],[67.0055, 24.860],[67.006, 24.8605],[67.0065, 24.860],[67.007, 24.8605],[67.0075, 24.860],[67.008, 24.8605],[67.0085, 24.860],[67.009, 24.8605],[6.0095, 24.860]],
    'coordinate4':[[67.0005, 24.86],[67.001, 24.8595],[67.0015, 24.86],[67.002, 24.8595],[67.0025, 24.86],[67.003, 24.8595],[67.0035, 24.86],[67.004, 24.8595],[67.0045, 24.86],[67.005, 24.8595],[67.0055, 24.86],[67.006, 24.8595],[67.0065, 24.86],[67.007, 24.8595],[67.0075, 24.86],[67.008, 24.8595],[67.0085, 24.86],[67.009, 24.8595]]
}
df = pd.DataFrame(data)

# x = df['coordinate1'].apply(lambda coords: coords[0])
# y = df['coordinate1'].apply(lambda coords: coords[1])
# fig = px.scatter(x=x, y=y)

# karachi_center = [24.8607, 67.0011]
# # Create a Mapbox layout
# layout = go.Layout(
#     mapbox_style="satellite",
#     mapbox_access_token = my_token,
#     mapbox_zoom=15,
#     mapbox_center={"lat": 24.773972, "lon":  67.431297},  
# )
# fig = go.Figure(layout=layout)
# # Add a polygon layer
# polygon = go.Scattermapbox(
#     mode="markers+text",
#     lon=[67.431297, 67.427867, 67.439087, 67.430117, 67.431297],  # Specify polygon vertices
#     lat=[24.773972, 24.776166, 24.776801, 24.774799, 24.773972],  # Specify polygon vertices
#     # fill="toself",  # Fills the area defined by the polygon
#     # fillcolor="rgba(255,0,0,0.2)",  # Set the fill color with alpha for transparency
#     # line=dict(color="rgba(255,0,0,0.6)", width=2),  # Set the border color and width
# )

# # Add the polygon layer to the figure
# fig.add_trace(polygon)

fig = go.Figure(go.Scattermapbox(
    lat=[38.91427, 38.91538, 38.91458],
    lon=[-77.02827, -77.02013, -77.03155],
    mode='markers',
    marker=go.scattermapbox.Marker(
        size=9
    ),
    text=["The coffee bar", "Bistro Bohem", "Black Cat"]
))

fig.update_layout(
    mapbox=dict(
        style="satellite",
        accesstoken="pk.eyJ1IjoiYW5haW1lIiwiYSI6ImNscWdpeGhwZTEyMG4ydW1rY3l1aXRmdWYifQ.1NbqsFXFOcooQaqxAZ-DSA",
        zoom=15,
        center={"lat": 38.91, "lon": -77.03}
    )
)


fig.write_html('file.html', auto_open=True)

