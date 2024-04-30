
import requests
import time
import datetime
from dateutil import parser
# WEATHER - openweathermap
def unix_to_humanreadable(unix_timestamp):
    return datetime.datetime.utcfromtimestamp(unix_timestamp).strftime('%Y-%m-%d %H:%M:%S')


def convert_to_unix_timestamp(date_str):
    try:
        # Parse the date string into a datetime object
        datetime_obj = parser.parse(date_str)
        
        # Convert the datetime object to a Unix timestamp
        unix_timestamp = int(datetime_obj.timestamp())
        
        return unix_timestamp
    except Exception as e:
        # Handle any parsing errors
        print(f"Error: {e}")
        return None



def get_weather(city_name, date_str):
    api_key = "7f38900c01ca65bdb8d01da8d642cbf3"
    unix_timestamp = convert_to_unix_timestamp(date_str)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&dt={unix_timestamp}&appid={api_key}"
    data = requests.get(url).json()
    return {
        "city":city_name,
        "description":data["weather"][0]["description"],
        "temperature":int(data["main"]["temp"]-273),
        "wind":data["wind"]["speed"],
        "humidity":data["main"]["humidity"],
        "rain": data["rain"]["1h"] if "rain" in data.keys() else 0,
        "clouds":data["clouds"]["all"]
    }

def get_news():
    api_url = "https://api.reliefweb.int/v1/reports?appname=apidoc&preset=latest&query[value]=earthquake&limit=6"
    api_response = requests.get(api_url)
    if api_response.status_code == 200:
        api_response_json = api_response.json()
        reports = api_response_json.get("data", [])
        return reports
    else:
        return None






# POPULATION
""" 
world bank-> only countries data
# api ninja->made acc, outdated to atleast 2017, limit
# world pop->no acc, tif file being downloaded, need to see
# populationexplorer-> made acc, only till 2016 is free, sent email to delete
# airlab->resgitrations temporarily suspended
#  geodb city api->how to get key
"""


def get_population(city_name):
    api_url = 'https://api.api-ninjas.com/v1/city'
    headers = {
        'X-Api-Key': "am9l7fI4C8Ch+p5RmndfRg==RqvK1hBEKkwuZhhF"
    }
    params = {
        'name': city_name,
    }
    response = requests.get(api_url, 
                            headers=headers, 
                            params=params)
    if response.status_code == requests.codes.ok:
        data = response.json()
        if len(data)!=0:
            country_code = data[0]['country']
            population = int(data[0]['population'])
            if country_code=="PK":
                rate = 1.90
                population = int(population*(1+rate/100)**6)
            return(population)
        else: 
            return -1
    else:
        return -1
 
# print(get_population("Balakot"))


coordinates = [
    (19.0760, 72.8777),
    (24.8949, 91.8687),
    (-22.9068, -43.1729),
    (-13.5319, -71.9675),
    (6.5244, 3.3792),
    (-4.0435, 39.6682),
    (6.9271, 79.8612),
    (-3.1190, -60.0217),
    (-33.9249, 18.4241),
    (9.1450, 40.4897)
]


def format_address(address):
    components = list(address.keys()).copy()[::-1]    
    for component in address.keys():
        if "ISO" in component or component=="country_code" or component=="postcode" or component=="city_district" or component=="state_district":
            components.remove(component)
    final_components = ["country","state"]
    if (len(set(components)-set(final_components))):
        city_substitute = "city" if "city" in components else components[components.index("state") + 1]
        city_index = components.index("city")
        final_components.append(city_substitute)
        final_components.extend(components[city_index+1 : ])    
    formatted_address = {}
    for i in final_components:
        formatted_address[i] = address[i]
    return formatted_address


# for coordinate in coordinates:
#     base_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={coordinate[0]}&lon={coordinate[1]}&zoom=18&addressdetails=1&accept-language=en-US"
#     response = requests.get(base_url)
#     if response.status_code == 200:
#         try:
#             data = response.json()  
#             print(data["address"])  
#             print(format_address(data["address"]))  
#             print()
#         except ValueError as e:
#             print("Error decoding JSON:", e)
#     else:
#         print("Error:", response.status_code) 
