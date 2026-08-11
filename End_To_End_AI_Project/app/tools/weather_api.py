
"""
tools/weather_api.py — Weather API Tool
========================================


Fetches current weather using:
1. Open-Meteo Geocoding API → converts location name to coordinates
2. Open-Meteo Weather API → gets current weather data

No API key is required.
"""

import re
import requests

from app.utils.logger import get_logger


logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# API configuration
# ---------------------------------------------------------------------------

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

TIMEOUT_SECONDS = 10


# ---------------------------------------------------------------------------
# WMO weather code descriptions
# ---------------------------------------------------------------------------

WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Icy fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight showers",
    81: "Moderate showers",
    82: "Violent showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Heavy thunderstorm",
}


# ---------------------------------------------------------------------------
# Main tool function
# ---------------------------------------------------------------------------

def run(query: str) -> dict:
    """
    Fetch current weather for the location mentioned in the query.
    """

    logger.info(f"Weather tool received: {query!r}")

    # Step 1: Extract location from user's natural-language query
    location = _extract_location(query)

    logger.info(f"Extracted location: {location!r}")

    if not location:
        return _error_response(
            "Could not identify a location in your query."
        )

    # Step 2: Convert location name → latitude/longitude
    coords = _geocode(location)

    if not coords:
        return _error_response(
            f"Could not find coordinates for location: {location!r}"
        )

    # Step 3: Use coordinates → get current weather
    weather = _fetch_weather(
        coords["lat"],
        coords["lon"]
    )

    if not weather:
        return _error_response(
            f"Could not fetch weather data for {location}."
        )

    # Step 4: Return standardized structured output
    output = {
        "location": coords["name"],
        "temperature": weather["temperature"],
        "feels_like": weather["feels_like"],
        "condition": weather["condition"],
        "wind_speed": weather["wind_speed"],
        "humidity": weather["humidity"],
        "unit": "C",
        "error": None,
    }

    logger.info(
        f"Weather result: "
        f"{output['location']} — "
        f"{output['temperature']}°C, "
        f"{output['condition']}"
    )

    return output


# ---------------------------------------------------------------------------
# Location extraction
# ---------------------------------------------------------------------------

def _extract_location(query: str) -> str | None:
    """
    Extract the location from a natural-language weather query.

    Examples:
        "Weather in Tokyo?"               -> "Tokyo"
        "What is the weather in Atlanta?" -> "Atlanta"
        "Weather for London"              -> "London"
        "Temperature in Paris today"      -> "Paris"
        "Weather at New York now"         -> "New York"
    """

    query_clean = query.strip().rstrip("?.")

    # Look for:
    #   in <location>
    #   for <location>
    #   at <location>
    #
    # The location is everything after the keyword until the end,
    # except common time words such as "today" or "now".
    match = re.search(
        r"\b(?:in|for|at)\s+(.+?)(?:\s+(?:today|now|currently|right now))?$",
        query_clean,
        re.IGNORECASE,
    )

    if match:
        location = match.group(1).strip()

        # Remove accidental trailing punctuation
        location = location.rstrip("?,.!")

        return location if location else None

    return None


# ---------------------------------------------------------------------------
# Geocoding
# ---------------------------------------------------------------------------

def _geocode(location: str) -> dict | None:
    """
    Convert a location name into latitude/longitude.

    Returns:
        {
            "lat": latitude,
            "lon": longitude,
            "name": resolved location name
        }

    Returns None if the location cannot be found.
    """

    try:
        response = requests.get(
            GEOCODING_URL,
            params={
                "name": location,
                "count": 1,
                "language": "en",
                "format": "json",
            },
            timeout=TIMEOUT_SECONDS,
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("results"):
            logger.warning(
                f"Geocoding: no results for {location!r}"
            )
            return None

        result = data["results"][0]

        return {
            "lat": result["latitude"],
            "lon": result["longitude"],
            "name": (
                f"{result['name']}, "
                f"{result.get('country', '')}"
            ).strip(", "),
        }

    except requests.RequestException as e:
        logger.error(
            f"Geocoding request failed: {e}"
        )
        return None


# ---------------------------------------------------------------------------
# Weather API
# ---------------------------------------------------------------------------

def _fetch_weather(lat: float, lon: float) -> dict | None:
    """
    Fetch current weather for the given coordinates.
    """

    try:
        response = requests.get(
            WEATHER_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": (
                    "temperature_2m,"
                    "apparent_temperature,"
                    "weather_code,"
                    "wind_speed_10m,"
                    "relative_humidity_2m"
                ),
                "temperature_unit": "celsius",
                "wind_speed_unit": "kmh",
                "timezone": "auto",
            },
            timeout=TIMEOUT_SECONDS,
        )

        response.raise_for_status()

        data = response.json()

        current = data.get("current", {})

        weather_code = current.get("weather_code", 0)

        return {
            "temperature": round(
                current.get("temperature_2m", 0),
                1,
            ),
            "feels_like": round(
                current.get("apparent_temperature", 0),
                1,
            ),
            "condition": WMO_CODES.get(
                weather_code,
                "Unknown",
            ),
            "wind_speed": round(
                current.get("wind_speed_10m", 0),
                1,
            ),
            "humidity": current.get(
                "relative_humidity_2m",
                0,
            ),
        }

    except requests.RequestException as e:
        logger.error(
            f"Weather API request failed: {e}"
        )
        return None


# ---------------------------------------------------------------------------
# Standardized error response
# ---------------------------------------------------------------------------

def _error_response(message: str) -> dict:
    """
    Return a consistent error structure.
    """

    logger.warning(
        f"Weather tool error: {message}"
    )

    return {
        "location": None,
        "temperature": None,
        "feels_like": None,
        "condition": None,
        "wind_speed": None,
        "humidity": None,
        "unit": "C",
        "error": message,
    }