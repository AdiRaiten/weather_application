from IPython.display import Markdown, clear_output, display
import datetime
import ipywidgets
from ipywidgets import interact, widgets
import requests, re
from ipyleaflet import Map, Marker

##################################################################################
def fetch_weather(location):
    display(Markdown(f"# Weather data for {location}:"))

    api_key = "4e1e50d1e07da9f968231b20bcdb3004"
    temp_units = "metric" # Units - default: kelvin, metric: Celsius, imperial: Fahrenheit. # standard, metric , imperial
    api_call = f"https://api.openweathermap.org/data/2.5/weather?q={location}&APPID={api_key}&units={temp_units}"

    #print("\nAPI call:")
    #print(api_call)

    response = requests.get(api_call)
    response_msg_dic = {
        "<Response [200]>":"Succesful response from server.",
        "<Response [400]>":"Failed to receive a response from server. Check your internet connection.",
        "<Response [404]>":"Not Found. Failed to receive a response from server. Check your internet connection."
    }
    #print(response_msg_dic[response.__str__()])
    ######################
    json_data = response.json()
    #display(json_data)

    # Weather data
    temp = json_data["main"]['temp']
    feels_like = json_data["main"]['feels_like']
    humidity = json_data["main"]['humidity']
    conditions = json_data["weather"][0].get('description')

    # Time information
    unix_time = json_data['dt'] + json_data['timezone']
    formatted_date_time = unix_to_standard_time(unix_time)

    # Geo-data
    lon = json_data['coord']["lon"]
    lat = json_data['coord']["lat"]
    # Create the map
    loc_map = Map(center=(lat, lon), zoom=6)
    # Add the market
    marker = Marker(location=(lat, lon))
    loc_map.add_layer(marker)

    degree_type = {"metric":"Celsius", "standard": "Kelvin", "imperial": "Fahrenheit"}[temp_units]

    # Output message
    markdown_output_msg = f"""### The temperature in {location} is {temp} degrees {degree_type}\n ### Humidity is {humidity}%\n### {conditions.capitalize()}"""
    markdown_time_msg = f"""### Time in {location} - {formatted_date_time}"""
    more_info_msg = "### For more information, visit [OpenWeather](https://openweathermap.org/)"
    markdown_output_msg +="\n "+markdown_time_msg +"\n" +more_info_msg

    # Display output
    display(Markdown(markdown_output_msg))
    display(loc_map)


def unix_to_standard_time(unix_format):
    date_time = datetime.datetime.fromtimestamp(unix_format)
    standard_time = date_time.strftime('%I:%M %p - %B %d, %Y')#('%Y-%m-%d %H:%M:%S')
    return standard_time


def logic(input_location):
    if input_location == "Click to select":
        clear_output()
    elif input_location == "Other":
        input_widget(prompt="Insert location:", callback=helper_function)
    else:
        launch_app(prompt=False, fetch=input_location)


def helper_function(input_textbox):
    other_location_input = input_textbox.value
    clear_output()
    launch_app()
    valid_pattern = "[a-zA-Z0-9' ,-]+"
    reg = re.fullmatch(valid_pattern, other_location_input)
    if reg is None:
        print("Input contains illegal characters. Please try again.\n")
        other_location_input = None
    elif "www" in other_location_input.lower():
        print("Input cannot contain 'www'. Please try again.\n")
        other_location_input = None
    if other_location_input is not None:
        input_location = other_location_input
        fetch_weather(input_location)


def input_widget(prompt, callback):
    label = widgets.Label(prompt)

    input_box = widgets.Text()
    input_box.on_submit(callback)

    box = widgets.HBox([label, input_box])
    display(box)


def launch_app(prompt=True, value=None, fetch=None):
    optional_locations = ["Click to select", "Tel Aviv", "Jerusalem", "Paris", "Tokyo", "Other"]
    # widget definition
    if value is None:
        selection = ipywidgets.Dropdown(options = optional_locations,description="Select option")
    else:
        selection = ipywidgets.Dropdown(options = optional_locations,description="Select option", value=value)
    # function-widget interaction
    output = ipywidgets.interactive_output(logic, {'input_location': selection})

    if prompt:
        display(Markdown("# Welcome to the weather application!"))
        # display widgets
        display(ipywidgets.VBox([selection,output]))
    if fetch is not None:
        fetch_weather(fetch)
