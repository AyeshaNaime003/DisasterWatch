import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import plotly.io as pio

from numpy import average
from .geopy_address import get_street_name

mapbox_token = "pk.eyJ1IjoiYW5haW1lIiwiYSI6ImNscWdpeGhwZTEyMG4ydW1rY3l1aXRmdWYifQ.1NbqsFXFOcooQaqxAZ-DSA"
data = {
    'color': ['red', 'yellow', 'green'] * 6,
    'coordinate1': [[67.0005, 24.861],[67.001, 24.8605],[67.0015, 24.861],[67.002, 24.8605],[67.0025, 24.861],[67.003, 24.8605],[67.0035, 24.861],[67.004, 24.8605],[67.0045, 24.861],[67.005, 24.8605],[67.0055, 24.861],[67.006, 24.8605],[67.0065, 24.861],[67.007, 24.8605],[67.0075, 24.861],[67.008, 24.8605],[67.0085, 24.861],[67.009, 24.8605]], 
    'coordinate2': [[67.001, 24.8615],[67.0015, 24.861],[67.002, 24.8615],[67.0025, 24.861],[67.003, 24.8615],[67.0035, 24.861],[67.004, 24.8615],[67.0045, 24.861],[67.005, 24.8615],[67.0055, 24.861],[67.006, 24.8615],[67.0065, 24.861],[67.007, 24.8615],[67.0075, 24.861],[67.008, 24.8615],[67.0085, 24.861],[67.009, 24.8615],[67.0095, 24.861]],
    'coordinate3': [[67.001, 24.8605],[67.0015, 24.860],[67.002, 24.8605],[67.0025, 24.860],[67.003, 24.8605],[67.0035, 24.860],[67.004, 24.8605],[67.0045, 24.860],[67.005, 24.8605],[67.0055, 24.860],[67.006, 24.8605],[67.0065, 24.860],[67.007, 24.8605],[67.0075, 24.860],[67.008, 24.8605],[67.0085, 24.860],[67.009, 24.8605],[67.0095, 24.860]],
    'coordinate4':[[67.0005, 24.86],[67.001, 24.8595],[67.0015, 24.86],[67.002, 24.8595],[67.0025, 24.86],[67.003, 24.8595],[67.0035, 24.86],[67.004, 24.8595],[67.0045, 24.86],[67.005, 24.8595],[67.0055, 24.86],[67.006, 24.8595],[67.0065, 24.86],[67.007, 24.8595],[67.0075, 24.86],[67.008, 24.8595],[67.0085, 24.86],[67.009, 24.8595]]
}
df = pd.DataFrame(data)


fig = go.Figure()
colors = {"red":"rgba(255,0,0, 0.5)",
          "green":"rgba(0,255,0, 0.5)",
          "yellow":"rgba(255,255,0, 0.5)"
          }
for index,row in df.iterrows():
    if index<5:
        polygon_lat = [row[f'coordinate{i}'][1] for i in range(1, 5)]
        polygon_lon = [row[f'coordinate{i}'][0] for i in range(1, 5)]
        midpoint = (average(polygon_lat),average(polygon_lon))
        fillcolor = colors[row['color']]
        ( landmark, street_name, locality, sublocality, district, city, region, postal_code, country ) = get_street_name(midpoint[0], midpoint[1])
        # polygon trace
        polygon_trace = go.Scattermapbox(
            lat=polygon_lat,
            lon=polygon_lon,
            mode='lines',
            fill='toself',  
            fillcolor=fillcolor,  
            line=dict(color=fillcolor, width=2),  
            hoverinfo='none'
        )
        # hover trace
        hover_trace = go.Scattermapbox(
            lat=[midpoint[0]],
            lon=[midpoint[1]],
            mode='markers',
            hoverinfo='text',
            text=f"{ landmark if landmark+', ' is not None else '' }{street_name}",
            marker=dict(color=row['color'])
        )
        fig.add_trace(polygon_trace)
        fig.add_trace(hover_trace)

karachi_center = [24.8607, 67.0011]
fig.update_layout(
    mapbox=dict(
        style="satellite",
        accesstoken=mapbox_token,
        zoom=15,
        center={"lat": karachi_center[0], "lon": karachi_center[1]}
    )
)



# Get the HTML code
html_code = pio.to_html(fig)

# fig.write_html('file.html', auto_open=True)
# for i, trace in enumerate(fig.data):
    # print(f"Layer {i + 1}: {trace}")

