import cv2
import rasterio 
import numpy as np
import requests

def get_tif_transform(file_name):
    with rasterio.open(file_name) as tif:
        return tif.transform

def pixels_to_coordinates(transform, pixel):
    longitude, latitude = transform * pixel
    return latitude, longitude

def get_address(latitude, longitude):
    FORMAT="json"
    LANG="en-US"
    base_url = f"https://nominatim.openstreetmap.org/reverse?format={FORMAT}&lat={latitude}&lon={longitude}&zoom=18&addressdetails=1&accept-language={LANG}"
    # Send a GET request to the API
    response = requests.get(base_url)
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        try:
            data = response.json()  
            return(data["address"])  
        except ValueError as e:
            print("Error decoding JSON:", e)
    else:
        print("Error:", response.status_code) 

def format_address(address):
    components = list(address.keys()).copy()[::-1]
    try:    
        for component in address.keys():
            if "ISO" in component or component=="country_code" or component=="postcode" or component=="city_district" or component=="state_district":
                components.remove(component)
        final_components = ["country"]
        if (len(set(components)-set(final_components))):
            state_substitute = "state" if "state" in components else components[components.index("country") + 1]
            city_substitute = "city" if "city" in components else components[components.index(state_substitute) + 1]
            city_index = components.index(city_substitute)
            final_components.append(city_substitute)
            final_components.extend(components[city_index+1 : ])    
        formatted_address = {}
        for i in final_components:
            formatted_address[i] = address[i]
        return formatted_address
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def get_polygons(mask, transform, rdp=True):
    print("IN mask_to_polygons```````````````````````````````````````````````````````")
    LAT_OFFSET, LONG_OFFSET = 0.0003994844315009516, 0.0004862524671978008  

    # GET THE CONTOURS IN THE MASK
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"number of contours in the mask {len(contours)}")
    # GET THE COORDINATES, CENTER LAT, CENTER LONG, AND ADDRESS OF EACH POLYGON 
    polygons = []
    for contour in contours:
        contour_points = np.squeeze(contour)
        if len(contour_points)>6:
            approx = np.squeeze(cv2.approxPolyDP(contour_points, 0.001, True)).tolist()

            coordinates_of_polygon=[]
            for x,y in approx:
                approx_lat, approx_long = pixels_to_coordinates(transform, (x, y))   
                correct_lat, correct_long = approx_lat+LAT_OFFSET, approx_long+LONG_OFFSET
                coordinates_of_polygon.append((correct_lat, correct_long))
            
            # CENTRE OF POLYGON
            center_lat = sum(point[0] for point in coordinates_of_polygon) / len(coordinates_of_polygon)
            center_long = sum(point[1] for point in coordinates_of_polygon) / len(coordinates_of_polygon)
            
            # ADDRESS
            address = get_address(center_lat, center_long)
            if address is None:
                continue
            else: 
                formatted_address = format_address(address)
                
                # APPEND ALL DATA OF THE POLYGON IN POLYGONS
                polygons.append({
                    'coordinates': coordinates_of_polygon,
                    'center_lat': center_lat,
                    'center_long': center_long,
                    'address': formatted_address
                })
    return polygons