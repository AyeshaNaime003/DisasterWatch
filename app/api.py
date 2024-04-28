
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
        "temperature":data["main"]["temp"],
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
