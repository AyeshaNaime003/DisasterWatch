import cv2
import numpy as np
import rasterio
from geopy.geocoders import Nominatim

def get_location(latitude, longitude):
    geolocator = Nominatim(user_agent="DisasterWatch")
    location = geolocator.reverse((latitude, longitude), 
                                  language="en")
    address = location.address if location else "Unknown"
    components = [component.strip() for component in address.split(',')]
    address = [''] * (9 - len(components)) + ['' if component is None else component for component in components] 
    return location.raw

def print_dictionary(dictionary):
    for key, value in dictionary.items():
        print(f"{key}: {value}")
    print()


def get_country_province(city_name):
    geolocator = Nominatim(user_agent="DisasterWatch")
    location = geolocator.geocode(city_name, exactly_one=True)
    if location:
        return {
            'country': location.raw.get('address', {}).get('country'),
            'state': location.raw.get('address', {}).get('state'),
            'city': location.raw.get('address', {}).get('city')
        }
    else:
        return {
            'country': 'Unknown',
            'state': 'Unknown',
            'city': city_name
        }

def extract_address_components(address):
    extracted_components = {
    'country': address.get('country', ""),
    'state': address.get('state', ""),
    'city': address.get('city', ""),
    'town': address.get('town', ""),
    'suburb_municipality': (
        address.get('suburb', '') +
        (', ' + address['municipality'] if 'municipality' in address and address['suburb'] else '') if 'suburb' in address or 'municipality' in address else ""
    ),
    'neighbourhood': address.get('neighbourhood', ""),
    'road': address.get('road', "")
    }
    for key in address:
        if key not in extracted_components and not "ISO" in key and key!="country_code" and key!="postcode" and key!="city_district":
            extracted_components["name"] =  key.capitalize() + ": " + address[key]
    return extracted_components

# print(get_street_name(34.032412964910364, -118.83242962970759))
# karachi-patel hospital

# patelhospital = get_street_name(24.93555926321077, 67.09717674474203)
# print_dictionary(extract_address_components(patelhospital['address']))
# hajilemogoth = get_street_name(24.934930604953006, 67.09454227030362)
# print_dictionary(extract_address_components(hajilemogoth['address']))
# centaurus = get_street_name(33.70789764984663, 73.04975970848382)
# print_dictionary(extract_address_components(centaurus['address']))

# woosley_address = get_street_name(34.032412964910364, -118.83242962970759)
# print_dictionary(extract_address_components(woosley_address['address']))

# school = get_street_name(24.944825175109454, 67.05061532893578)
# print_dictionary(extract_address_components(school['address']))
# print(get_street_name(33.65623583955007, 72.99861595930268))
# print(get_street_name(33.532791117455794, 73.16296485833928))
# print(get_street_name(33.532489425413125, 73.16314399994715))


def get_tif_transform(file_name):
    # Open the TIFF file using rasterio
    with rasterio.open(file_name) as tif:
        return tif.transform

def pixels_to_coordinates(transform, pixel):
    longitude, latitude = transform * pixel
    return latitude, longitude

# FUNCTION TO GET IMAGE FROM TIF PATH
def tif_to_img(tif_file):
  disaster_img = np.dstack((tif_file.GetRasterBand(1).ReadAsArray(),
                  tif_file.GetRasterBand(2).ReadAsArray(),
                  tif_file.GetRasterBand(3).ReadAsArray()))
  return disaster_img

def mask_to_polygons(mask, transform, rdp=True):
    lat_offset, long_offset = 0.0003994844315009516, 0.0004862524671978008  
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    polygons_in_mask = []
    for contour in contours:
        contour_points = np.squeeze(contour)
        epsilon = 0.01 * cv2.arcLength(contour_points, True)
        approx = np.squeeze(cv2.approxPolyDP(contour_points, epsilon, True)).tolist()
        coordinates=[]
        for x,y in approx:
            approx_lat, approx_long = pixels_to_coordinates(transform, (x, y))   
            correct_lat, correct_long = approx_lat+lat_offset, approx_long+long_offset
            coordinates.append((correct_lat, correct_long))
        
        # Calculate the center of the polygon
        center_lat = sum(point[0] for point in coordinates) / len(coordinates)
        center_long = sum(point[1] for point in coordinates) / len(coordinates)

        # Get the street name using the center coordinates
        address = extract_address_components(get_location(center_lat, center_long)["address"])

        # Save the polygon data along with the location details
        polygons_in_mask.append({
            'coordinates': coordinates,
            'center_lat': center_lat,
            'center_long': center_long,
            'address': address
        })
    return polygons_in_mask

def polygons_to_masks(polygons, image_shape=(1024,1024)):
    mask = np.zeros(image_shape, dtype=np.uint8)
    for polygon in polygons:
        cv2.fillPoly(mask, [polygon], 255)  # Fill each polygon with white color (255)
    return mask

def one_hot_encoding_mask(mask):
    # convert mask to hsv
    hsv = cv2.cvtColor(mask, cv2.COLOR_BGR2HSV)
    # define color ranges
    lower_red = np.array([0, 50, 50])
    upper_red = np.array([10, 255, 255])
    lower_yellow = np.array([20, 50, 50])
    upper_yellow = np.array([30, 255, 255])
    lower_orange = np.array([10, 50, 50])
    upper_orange = np.array([20, 255, 255])
    lower_green = np.array([31, 50, 50])
    upper_green = np.array([80, 255, 255])
    # Create masks for each class using inRange function
    mskr = cv2.inRange(hsv, lower_red, upper_red)
    msky = cv2.inRange(hsv, lower_yellow, upper_yellow)
    msko = cv2.inRange(hsv, lower_orange, upper_orange)
    mskg = cv2.inRange(hsv, lower_green, upper_green)
    # Stack the masks along the channel axis to create one-hot encoded representation
    one_hot_encoded = np.stack([mskr, msko, msky, mskg])
    return one_hot_encoded
