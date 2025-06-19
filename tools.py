from agents import function_tool, WebSearchTool
from datetime import datetime

@function_tool
def get_current_weather(city: str) -> str:
    """Get the current weather for a given city."""
    return f"The weather in {city} is sunny."

@function_tool
def get_current_time() -> str:
    """Get the current time."""
    return f"The current time is {datetime.now().strftime('%H:%M:%S')}"

@function_tool
def get_current_date() -> str:
    """Get the current date."""
    return f"The current date is {datetime.now().strftime('%Y-%m-%d')}"

@function_tool
def get_current_temperature() -> str:
    """Get the current temperature."""
    return "The current temperature is 72°F."

@function_tool
def get_seven_day_forecast() -> str:
    """Get the weather forecast for the next 7 days."""
    forecast = [
        "Monday: Sunny, 75°F",
        "Tuesday: Partly Cloudy, 72°F", 
        "Wednesday: Rain, 68°F",
        "Thursday: Cloudy, 70°F",
        "Friday: Sunny, 76°F",
        "Saturday: Clear, 74°F", 
        "Sunday: Partly Cloudy, 73°F"
    ]
    return "\n".join(forecast)





# keep a dictionary of tools
all_tools = {
    "get_current_weather": get_current_weather,
    "get_current_time": get_current_time,
    "get_current_temperature": get_current_temperature,
    "get_seven_day_forecast": get_seven_day_forecast,
    "get_current_date": get_current_date,
    "web_search": WebSearchTool() # requires WebSearchTool import
} 