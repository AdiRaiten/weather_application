from IPython.display import Markdown, clear_output, display
import datetime
import ipywidgets
from ipywidgets import interact, widgets
import requests, re
from ipyleaflet import Map, Marker
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def json_to_pandas(json_data):
    ser_ls = []  # Aggregator for pd.Series objects (rows)
    for i, d in enumerate(json_data["list"]):
        d = {k: v for k, v in d.items() if k in ['main', 'weather', 'dt_txt']}
        d = {k: (v if k != "weather" else v[0]["description"]) for k, v in d.items()}
        main_d = d["main"]
        main_d = {k: v for k, v in main_d.items() if k in ['temp', 'feels_like', 'temp_min', 'temp_max', 'humidity']}
        main_d["weather"] = d["weather"]
        main_d["dt_txt"] = d["dt_txt"]
        ser = pd.Series(main_d)
        ser_ls.append(ser)
    return pd.DataFrame(ser_ls)


def plot_forecast_data(dataframe, location="Chosen Location"):
    plot_df = dataframe.copy()
    plot_df = plot_df.set_index("dt_txt")
    plot_df.index.name = "Date"
    plot_df = plot_df[["temp", "temp_min", "temp_max"]]

    range_min = plot_df.temp_min.min() - 10
    range_max = plot_df.temp_max.max() + 10
    y_range = (range_min, range_max)

    plot_df["temp_min"] = plot_df.apply(lambda row: row["temp"] - row["temp_min"], axis=1)
    plot_df["temp_max"] = plot_df.apply(lambda row: row["temp_max"] - row["temp"], axis=1)

    title = f"5-days Temperature Forecast in {location}"

    fig = px.line(plot_df, error_y="temp_max", error_y_minus="temp_min", range_y=y_range)

    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        yaxis_title="Temperatue [Celsius]",
        showlegend=False)

    return fig


class StopExecution(Exception):
    def _render_traceback_(self):
        return []


def fetch_weather(location):
    ''' Get a response from the API call
    Parameters:
    location -
    '''
    display(Markdown(f"# Weather data for {location}:"))

    api_key = "4e1e50d1e07da9f968231b20bcdb3004"
    temp_units = "metric"  # Units - default: kelvin, metric: Celsius, imperial: Fahrenheit. # standard, metric , imperial

    # Current weather
    api_call = f"https://api.openweathermap.org/data/2.5/weather?q={location}&APPID={api_key}&units={temp_units}"
    response = requests.get(api_call)

    json_data = response.json()

    if json_data['cod'] == '404':
        print("Invalid city name, please try again")
        raise StopExecution

    # Time information
    unix_time = json_data['dt'] + json_data['timezone']
    formatted_date_time = unix_to_standard_time(unix_time)

    # Weather data
    temp = json_data["main"]['temp']
    feels_like = json_data["main"]['feels_like']
    humidity = json_data["main"]['humidity']
    conditions = json_data["weather"][0].get('description')
    # Geo-data
    lon = json_data['coord']["lon"]
    lat = json_data['coord']["lat"]

    # Forecast
    forecast_call = f"https://api.openweathermap.org/data/2.5/forecast?q={location}&&APPID={api_key}&units={temp_units}"
    response_forecast = requests.get(forecast_call)
    json_data_forecast = response_forecast.json()

    # JSON to Pandas
    orig_df = json_to_pandas(json_data_forecast)

    # Plot data
    fig = plot_forecast_data(dataframe=orig_df, location=location)

    # Create the map
    loc_map = Map(center=(lat, lon), zoom=6)
    # Add the marker
    marker = Marker(location=(lat, lon))
    loc_map.add_layer(marker)

    degree_type = {"metric": "Celsius", "standard": "Kelvin", "imperial": "Fahrenheit"}[temp_units]

    # Output message
    markdown_output_msg = f"""### Temperature  {round(temp)}&deg; [{degree_type}]\t * Humidity {humidity}%\t * {conditions.capitalize()}"""
    markdown_time_msg = f"""### Time in {location} - {formatted_date_time}"""
    more_info_msg = "### For more information, visit [OpenWeather](https://openweathermap.org/)"
    markdown_output_msg += "\n " + markdown_time_msg + "\n" + more_info_msg

    # Display output
    display(Markdown(markdown_output_msg))
    # display(loc_map)
    box = widgets.HBox([go.FigureWidget(fig), loc_map])
    display(box)


def unix_to_standard_time(unix_format):
    date_time = datetime.datetime.fromtimestamp(unix_format)
    standard_time = date_time.strftime('%I:%M %p - %B %d, %Y')
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
    optional_locations = ["Click to select", "Tel Aviv", "Paris", "London", "New York", "Los Angeles", "Tokyo", "Other"]
    # widget definition
    if value is None:
        selection = ipywidgets.Dropdown(options=optional_locations, description="Select option")
    else:
        selection = ipywidgets.Dropdown(options=optional_locations, description="Select option", value=value)
    # function-widget interaction
    output = ipywidgets.interactive_output(logic, {'input_location': selection})

    if prompt:
        display(Markdown("# Welcome to the weather application!"))
        # display widgets
        display(ipywidgets.VBox([selection, output]))
    if fetch is not None:
        fetch_weather(fetch)
