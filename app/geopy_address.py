from geopy.geocoders import Nominatim

def get_street_name(latitude, longitude):
    geolocator = Nominatim(user_agent="your_app_name")
    location = geolocator.reverse((latitude, longitude), language="en")
    
    address = location.address if location else "Unknown"
    components = [component.strip() for component in address.split(',')]
    address =  [None] * (9 - len(components)) + components 
    # print(address)

    return address

print(get_street_name(34.032412964910364, -118.83242962970759))