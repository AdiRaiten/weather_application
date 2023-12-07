import requests, re
from ipyleaflet import Map, Marker

def fetch_weather(location):
    api_key = "4e1e50d1e07da9f968231b20bcdb3004"
    # location = input_location
    temp_units = "metric" # Units - default: kelvin, metric: Celsius, imperial: Fahrenheit. # standard, metric , imperial
    api_call = f"https://api.openweathermap.org/data/2.5/weather?q={location}&APPID={api_key}&units={temp_units}"

    print("\nAPI call:")

    print(api_call)
    print("")

    response = requests.get(api_call)
    response_msg_dic = {
        "<Response [200]>":"Succesful response from server.",
        "<Response [400]>":"Failed to receive a response from server. Check your internet connection."
    }
    print(response_msg_dic[response.__str__()])
    ######################
    json_data = response.json()
    temp = json_data["main"]['temp']
    feels_like = json_data["main"]['feels_like']
    humidity = json_data["main"]['humidity']
    conditions = json_data["weather"][0].get('description')
    #####################
    lon = json_data['coord']["lon"]
    lat = json_data['coord']["lat"]

    # Create the map
    loc_map = Map(center=(lat, lon), zoom=6)
    # Add the market
    marker = Marker(location=(lat, lon))
    loc_map.add_layer(marker)
    #####################
    degree_type = {"metric":"Celsius", "standard": "Kelvin", "imperial": "Fahrenheit"}[temp_units]
    output_msg = f"The temperature in {location} is {temp} degrees {degree_type}.\nHumidity is {humidity}%, and the weather conditions are {conditions}"
    #############
    print(output_msg)
    display(loc_map)

def logic(selection):
    input_location = selection
    valid_pattern = "[a-zA-Z0-9' ,-]+"
    reg = re.fullmatch(valid_pattern, input_location)
    if input_location == "Click to select":
        pass
    elif reg is None:
        print("Input contains illegal characters. Please try again.\n")
    elif "www" in input_location.lower():
        print("Input cannot contain 'www'. Please try again.\n")
    else:
        print(f"Fetching weather data for {input_location}...")
        fetch_weather(input_location)