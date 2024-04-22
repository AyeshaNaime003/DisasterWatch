# from    
# from geopy.exc import GeocoderUnavailable
import requests





def get_country(lat, lon):
    url = f'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=en&zoom=3'
    try:
        result = requests.get(url=url)
        result_json = result.json()
        return result_json['display_name']
    except:
        return None

# print(get_country(32.782023,35.478867)) 


from geopy.geocoders import Nominatim

def get_address(lat, lon):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.reverse((lat, lon), language='en')
    return location.address if location else None

print(get_address(32.782023, 35.478867))
print(get_address(33.707839789411885, 73.04977849036582))
#