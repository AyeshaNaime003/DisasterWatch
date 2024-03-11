# import plotly.graph_objects as go
# from numpy import average
# from PIL import Image
# import matplotlib.pyplot as plt

# import rasterio
# from rasterio.transform import from_origin
# from rasterio.crs import CRS

# from .geopy_address import get_street_name

# import plotly.io as pio

# # manually
# # top_left_lon = -95.32313692483139
# # top_left_lat = 29.442661879769132    
# # bottom_right_lon = -95.32148503013677
# # bottom_right_lat = 29.44090998507452
# # RESTERIO FOR GETTING LAT AND LONG
# with rasterio.open('hurricane-florence_00000004_post_disaster.tif') as tif:
#     transform = tif.transform
#     top_left_lon, top_left_lat = transform * (0, 0)
#     bottom_right_lon, bottom_right_lat = transform * (tif.width, tif.height)

# # print("top left coordinates: ",top_left_lat, top_left_lon)
# # print("Bottom right coordinates: ",bottom_right_lat, bottom_right_lon)

# center_lat, center_lon = average([top_left_lat, bottom_right_lat]), average([top_left_lon, bottom_right_lon])
# # print("Center coordinates: ",center_lat, center_lon)


# # polygons
# # data = [
# #     {
# #         "id": 1, 
# #         "class": "undamaged",
# #         "polygons": [
# #             (232.5173770256123, 845.8363458843754), 
# #             (239.3562863812729, 843.1007821418067), 
# #             (238.7700941502514, 841.1468080412766), 
# #             (264.5625522872949, 833.5263090463677), 
# #             (275.1140124319841, 847.7903199859203), 
# #             (276.4817943022538, 867.3300609942661), 
# #             (246.781387966433, 876.1229444537547), 
# #             (243.2642345838553, 875.7321496301988), 
# #             (232.5173770256123, 845.8363458843754)
# #         ]
# #     },
# #     {
# #         "id": 2, 
# #         "class": "undamaged",
# #         "polygons": [
# #             (272.3606943939114, 828.7269851763605), 
# #             (301.7877835981718, 819.2504649224168), 
# #             (315.0050355282862, 836.7072127523271), 
# #             (318.7457672064864, 858.9022207142826), 
# #             (302.0371657092231, 863.8898629495154), 
# #             (300.5408730378415, 862.1441881663214), 
# #             (285.5779463235185, 866.1343019553195), 
# #             (272.3606943939114, 828.7269851763605)
# #         ]
# #     }
# # ]



# data = [
#     {
#         "id": 1,
#         "class": "undamaged",
#         "polygons": [
#             (232.5173770256123, 845.8363458843754),
#             (239.3562863812729, 843.1007821418067),
#             (238.7700941502514, 841.1468080412766),
#             (264.5625522872949, 833.5263090463677),
#             (275.1140124319841, 847.7903199859203),
#             (276.4817943022538, 867.3300609942661),
#             (246.781387966433, 876.1229444537547),
#             (243.2642345838553, 875.7321496301988),
#             (232.5173770256123, 845.8363458843754)
#         ]
#     },
#     {
#         "id": 2,
#         "class": "undamaged",
#         "polygons": [
#             (272.3606943939114, 828.7269851763605),
#             (301.7877835981718, 819.2504649224168),
#             (315.0050355282862, 836.7072127523271),
#             (318.7457672064864, 858.9022207142826),
#             (302.0371657092231, 863.8898629495154),
#             (300.5408730378415, 862.1441881663214),
#             (285.5779463235185, 866.1343019553195),
#             (272.3606943939114, 828.7269851763605)
#         ]
#     },
#     {
#         "id": 3,
#         "class": "undamaged",
#         "polygons": [
#             (320.7408241017464, 839.6997980961049),
#             (324.730937890237, 832.7170989633291),
#             (352.9111165346745, 824.4874892760574),
#             (361.3901083378172, 834.9615379731919),
#             (362.3876367860814, 854.1639605873108),
#             (347.674092184078, 860.1491312738518),
#             (342.6864499458012, 859.400984935878),
#             (328.970433793584, 864.887391396765),
#             (320.7408241017464, 839.6997980961049)
#         ]
#     },
#     {
#         "id": 4,
#         "class": "undamaged",
#         "polygons": [
#             (354.9061734286661, 806.282595106144),
#             (383.335734182633, 796.5566927429246),
#             (398.5480430090221, 839.9491802134982),
#             (397.5505145607579, 842.1936192182875),
#             (386.5777016387305, 845.4355866723557),
#             (386.5757298158347, 847.1792896334148),
#             (385.4667422217043, 849.598804650743),
#             (369.6959959520779, 853.3544031121215),
#             (354.9061734286661, 806.282595106144)
#         ]
#     },
#     {
#         "id": 5,
#         "class": "undamaged",
#         "polygons": [
#             (395.6839184554995, 798.7602185657071),
#             (403.9512635725221, 795.8513378773144),
#             (404.4105605242287, 794.3203480399832),
#             (402.2671747519651, 787.8901907221773),
#             (414.9538591090786, 784.7208646254234),
#             (417.5770731217259, 792.0238632855084),
#             (424.466527386165, 789.7273785300188),
#             (426.7630121431766, 790.9521703968397),
#             (438.1838420543398, 828.8054512769535),
#             (437.2857794408716, 831.7017213291174),
#             (409.0698138824822, 840.7345613678498),
#             (395.6839184554995, 798.7602185657071)
#         ]
#     },
#     {
#         "id": 6,
#         "class": "undamaged",
#         "polygons": [
#             (432.0179708388125, 779.2151484093232),
#             (462.0072357823718, 770.458283045407),
#             (474.0029417605058, 787.2522714121567),
#             (479.9488596205092, 814.7323188664128),
#             (476.1188141130443, 816.3029479559025),
#             (472.8341502386447, 819.8201013364509),
#             (465.8567408716384, 819.6247039251803),
#             (449.2479610112975, 825.2912288175295),
#             (446.5123972684752, 823.337254718014),
#             (432.0179708388125, 779.2151484093232)
#         ]
#     },
#     {
#         "id": 7,
#         "class": "undamaged",
#         "polygons": [
#             (472.6197900145518, 770.5919413758089),
#             (498.6466172395432, 762.0183982877686),
#             (502.7802897995765, 763.5493881261145),
#             (517.1715942687143, 803.6613218499876),
#             (489.6137772036013, 813.6127557860452),
#             (485.6332036278085, 811.622468998022),
#             (472.6197900145518, 770.5919413758089)
#         ]
#     },
#     {
#         "id": 8,
#         "class": "undamaged",
#         "polygons": [
#             (513.3441196743715, 761.252903367581),
#             (542.5860255572511, 750.8421724808313),
#             (553.7622513652029, 766.9175657641846),
#             (559.120715795355, 790.4948092529977),
#             (529.7257109264592, 801.2117381092429),
#             (526.2044343031341, 799.5276492886859),
#             (513.3441196743715, 761.252903367581)
#         ]
#     },
#     {
#         "id": 9,
#         "class": "undamaged",
#         "polygons": [
#             (554.3697226409148, 746.080230694751),
#             (583.547429730065, 737.1024746705202),
#             (601.0041775627654, 759.2974826253729),
#             (602.001706009254, 775.5073199018021),
#             (568.2530358164041, 785.6214974199172),
#             (565.1026214440187, 783.2571013537637),
#             (554.3697226409148, 746.080230694751)
#         ]
#     },
#     {
#         "id": 10,
#         "class": "undamaged",
#         "polygons": [
#             (595.4947675476537, 730.1868865438072),
#             (622.4401886755512, 721.9195414222185),
#             (634.6881073686202, 760.5004853118044),
#             (633.3102165152758, 764.1748609203846),
#             (608.2019831919222, 772.7484040043662),
#             (595.4947675476537, 730.1868865438072)
#         ]
#     },
#     {
#         "id": 11,
#         "class": "undamaged",
#         "polygons": [
#             (631.0148589507373, 715.7386468703133),
#             (632.5458487913663, 711.2987763445894),
#             (659.5038805521948, 702.3732827320074),
#             (677.242831369711, 754.1870230633209),
#             (663.7780414599861, 759.0656592551187),
#             (661.9408536554423, 754.0133927904036),
#             (647.1896780110902, 759.9968637917168),
#             (643.9083155069422, 757.9529037901111),
#             (631.0148589507373, 715.7386468703133)
#         ]
#     },
#     {
#         "id": 12,
#         "class": "undamaged",
#         "polygons": [
#             (702.5116186314909, 697.669310951232),
#             (715.0170528792471, 737.7257800242769),
#             (713.8446684189797, 740.2659463545602),
#             (698.6036704296697, 744.9554841956298),
#             (697.8220807894069, 742.610715276617),
#             (686.6844284157254, 746.3232660674214),
#             (682.5810827990821, 744.3692919668913),
#             (671.052635603113, 708.2207710949067),
#             (702.5116186314909, 697.669310951232)
#         ]
#     }
# ] 


# transform = from_origin(top_left_lon, top_left_lat, (top_left_lon-bottom_right_lon)/1024, (top_left_lat-bottom_right_lat)/1024)
# # print(transform)


# # DISPLAY PURPOSES
# # for entry in data:
# #     polygons = entry["polygons"]
# #     x_coords, y_coords = zip(*polygons)
# #     lon, lat = rasterio.transform.xy(transform, x_coords, y_coords)
# #     for i in list(zip(lat, lon)):
#         # print(i)
# #     print()

# latitudes = []
# longitudes = []
# for entry in data:
#     polygons = entry["polygons"]
#     x_coords, y_coords = zip(*polygons)
#     lon, lat = rasterio.transform.xy(transform, x_coords, y_coords)
#     latitudes.append(list(lat))
#     longitudes.append(list(lon))

# class_colors = {"undamaged":"green"}
# colors = {"red":"rgba(255,0,0, 0.5)",
#           "green":"rgba(0,255,0, 0.5)",
#           "yellow":"rgba(255,255,0, 0.5)"}


# mapbox_token = "pk.eyJ1IjoiYW5haW1lIiwiYSI6ImNscWdpeGhwZTEyMG4ydW1rY3l1aXRmdWYifQ.1NbqsFXFOcooQaqxAZ-DSA"
# fig = go.Figure()

# buttons = [
#    dict(label="Satellite", method="update", 
#          args=[{"mapbox.style": "satellite"}, {"mapbox.style": "open-street-map"}]),
#     dict(label="Open Street Map", method="update", 
#          args=[{"mapbox.style": "open-street-map"}, {"mapbox.style": "satellite"}])
# ]
# updatemenu = dict(
#     type="buttons",
#     direction="right",
#     buttons=buttons,
#     showactive=True,
#     x=0.5,
#     xanchor="center",
#     y=1.0,
#     yanchor="top",
# )
# fig.update_layout(
#     width=1000, height=500, 
#     margin=dict(l=10, r=10, t=30, b=10),
#     mapbox=dict(
#         style="satellite",
#         accesstoken=mapbox_token,
#         zoom=15,
#         center={"lat": center_lat, "lon": center_lon},
#         bearing=0
#     ),
#     updatemenus=[updatemenu],
# )

# fig.add_trace(go.Scattermapbox(
#     lat=[center_lat],
#     lon=[center_lon],
#     mode='markers',
#     fill='toself',  
#     line=dict(color='blue', width=2)))
    
# for i in range(len(data)):
#     polygon_lat = latitudes[i]
#     polygon_lon = longitudes[i]
#     midpoint = (average(polygon_lat),average(polygon_lon))
    
#     poly_color = class_colors[data[i]['class']]
#     fillcolor = colors[poly_color]
    
#     # polygon trace
#     polygon_trace = go.Scattermapbox(
#         lat=polygon_lat,
#         lon=polygon_lon,
#         mode='lines',
#         fill='toself',  
#         fillcolor=fillcolor,  
#         line=dict(color=fillcolor, width=2),  
#         hoverinfo='none',
#     )
#     # hover trace
#     hover_trace = go.Scattermapbox(
#         lat=[midpoint[0]],
#         lon=[midpoint[1]],
#         mode='markers',
#         hoverinfo='text',
#         text=f"{get_street_name(midpoint[0], midpoint[1])}",
#         marker=dict(color=poly_color)
#     )
#     fig.add_trace(polygon_trace)
#     fig.add_trace(hover_trace)

# # fig.write_html("./file.html", auto_open=True)

# # Get the HTML code
# html_code = pio.to_html(fig)
# pio.write_html(fig, file='file.html')
