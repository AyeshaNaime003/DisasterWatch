import requests
import time
import datetime

# WEATHER - openweathermap

def unix_to_humanreadable(unix_timestamp):
    return datetime.datetime.utcfromtimestamp(unix_timestamp).strftime('%Y-%m-%d %H:%M:%S')


api_key = "7f38900c01ca65bdb8d01da8d642cbf3"
city_name = "islamabad"
ISO_2_code = "PK"
current_time = int(time.time())
print(current_time, unix_to_humanreadable(current_time))

# Specify the desired time (e.g., 3 hours from now)
desired_time = current_time - (1 * 24 * 3600) 
print(desired_time, unix_to_humanreadable(desired_time))



# Construct the API request URL with the specified time
# url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&dt={current_time}&appid={api_key}"
# # url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}"

# response = requests.get(url)
# data = response.json()

# print(f"City: {data['name']}")
# print(f"Temperature: {(data['main']['temp'] - 273.15):.2f} C")
# print(f"Humidity: {data['main']['humidity']}%")
# print(f"Weather: {data['weather'][0]['description']}")
# print(f"Weather: {data}")


# POPULATION
""" 
world bank-> only countries data
# api ninja->made acc, outdated to atleast 2017, limit
# world pop->no acc, tif file being downloaded, need to see
# populationexplorer-> made acc, only till 2016 is free, sent email to delete
# airlab->resgitrations temporarily suspended
#  geodb city api->how to get key
"""
# api_url = 'https://api.api-ninjas.com/v1/city'
# headers = {
#     'X-Api-Key': "am9l7fI4C8Ch+p5RmndfRg==RqvK1hBEKkwuZhhF"
# }

# params = {
#     'name': 'Karachi',
#     # 'country': 'PK'
# }

# response = requests.get(api_url, headers=headers, params=params)

# if response.status_code == requests.codes.ok:
#     print(response.json())
    
# else:
#     print("Error:", response.status_code, response.text)

#import requests

def get_population(country_name):
    try:
        # Define the base URL for the API
        BASE_URL = 'https://countriesnow.space/api/v0.1/countries'
        
        # Send a GET request to fetch the countries data
        response = requests.get(BASE_URL)
        data = response.json()

        # Print the entire response to understand its structure
        # print(type(data))
        # print(type(data["data"]))
        print(data["data"][0])

        # Iterate through the countries data to find the population of the specified country
        for country in data['data']:
            if country['country'].lower() == country_name.lower():
                return country['population']

        return None  # Return None if country is not found
    except Exception as e:
        print(f"Error: {e}")
        return None

# # Call the function to get the population of Pakistan
# country_name = 'Pakistan'
# population = get_population(country_name)

# if population is not None:
#     print(f"Population of {country_name}: {population}")
# else:
#     print(f"Population data not found for {country_name}")
