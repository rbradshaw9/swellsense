# Shared constants between frontend and backend
SURF_CONDITIONS = {
    "FLAT": 0,
    "POOR": 1,
    "FAIR": 2,
    "GOOD": 3,
    "EXCELLENT": 4,
    "EPIC": 5
}

WAVE_HEIGHT_RANGES = {
    "FLAT": (0, 0.5),
    "SMALL": (0.5, 2.0),
    "MODERATE": (2.0, 4.0),
    "LARGE": (4.0, 8.0),
    "HUGE": (8.0, 15.0),
    "MASSIVE": (15.0, float('inf'))
}

WIND_DIRECTIONS = [
    "N", "NNE", "NE", "ENE", 
    "E", "ESE", "SE", "SSE",
    "S", "SSW", "SW", "WSW",
    "W", "WNW", "NW", "NNW"
]

API_ENDPOINTS = {
    "NOAA_BUOY": "https://www.ndbc.noaa.gov/data/realtime2/",
    "NOAA_TIDES": "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter",
    "OPENWEATHER": "https://api.openweathermap.org/data/2.5/"
}

# Common surf spot data structure
SURF_SPOT_SCHEMA = {
    "id": "string",
    "name": "string", 
    "location": {
        "latitude": "float",
        "longitude": "float",
        "country": "string",
        "region": "string"
    },
    "characteristics": {
        "break_type": "string",  # beach, reef, point
        "skill_level": "string",  # beginner, intermediate, advanced
        "ideal_swell_direction": "string",
        "ideal_wind_direction": "string"
    }
}