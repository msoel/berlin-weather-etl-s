import json
import logging
from pathlib import Path
from datetime import datetime

import requests

#----------------------------------------------
# 1. WWeather API Configuration 
# the weather data extraction from the Open-Meteo API for Berlin, Germany
# timezone: Europe/Berlin
# documentation: https://open-meteo.com/en/docs
#----------------------------------------------

API_URL = "https://api.open-meteo.com/v1/forecast"

PARAMS = {
    "latitude": 52.52,
    "longitude": 13.405,
    "current": (
        "temperature_2m,"
        "relative_humidity_2m,"
        "apparent_temperature,"
        "precipitation,"
        "weather_code,"
        "wind_speed_10m"
    ),
    "timezone": "Europe/Berlin"
}

# Project directories to save logs and raw data
# raw data directory: data/raw
# log directory: logs
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
LOG_DIR = PROJECT_ROOT / "logs"


# --------------------------------------------------
# 2. Logging configuration
# --------------------------------------------------

LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            LOG_DIR / "extraction.log",
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ],
    force=True
)

logger = logging.getLogger(__name__)

# --------------------------------------------------
# 3. Extract weather data
# --------------------------------------------------

def extract_weather_data():

    logger.info("Starting weather data extraction...")

    try:
        # Create raw data directory if it doesn't exist
        RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

        # Send API request

        # Log the request time for debugging purposes
        logger.info("Sending request to Open-Meteo API...")

        response = requests.get(
            API_URL,
            params=PARAMS,
            timeout=15
        )

        # Raise an exception for HTTP errors
        response.raise_for_status()

        # Convert response into Python dictionary
        weather_data = response.json()

        # Basic response validation: check if the response is a dictionary as expected
        if not isinstance(weather_data, dict):
            raise ValueError("Unexpected API response format.")

        # check if the response contains the expected data like 'current' key
        if "current" not in weather_data:
            raise ValueError("API response does not contain current weather data.")

        # Log the successful extraction with timestamp
        logger.info("Weather data extracted successfully.")

        # ......................................................... 
        # Save the raw response as JSON in the "data/raw" directory
        # ...........................................................

        # Generate timestamp for unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # making the output file path with timestamp 
        # filename format: berlin_weather_YYYYMMDD_HHMMSS.json
        # file path: data/raw/berlin_weather_YYYYMMDD_HHMMSS.json
        output_file = RAW_DATA_DIR / f"berlin_weather_{timestamp}.json"

        # Now, Save raw response as JSON in the "data/raw" directory
        with output_file.open("w", encoding="utf-8") as file:
            json.dump(
                weather_data,
                file,
                indent=4,
                ensure_ascii=False
            )

        logger.info("JSON data saved successfully: %s", output_file)

        return weather_data
    
    # refined exception handling for various potential issues during the extraction process

    # requests.exceptions.Timeout: Raised when the request times out.
    except requests.exceptions.Timeout:
        logger.error("API request timed out.")

    # requests.exceptions.HTTPError: Raised for HTTP error responses (4xx or 5xx).
    except requests.exceptions.HTTPError as error:
        logger.error("HTTP error occurred: %s", error)

    # requests.exceptions.ConnectionError: Raised for network-related errors (e.g., DNS failure, refused connection).
    except requests.exceptions.ConnectionError as error:
        logger.error("Connection error: %s", error)

    # requests.exceptions.RequestException: A base class for all other request-related exceptions.
    except requests.exceptions.RequestException as error:
        logger.error("API request failed: %s", error)

    # requests.exceptions.JSONDecodeError: Raised when the response is not valid JSON.
    except requests.exceptions.JSONDecodeError as error:
        logger.error("Invalid JSON response: %s", error)

    # ValueError: Raised for unexpected API response formats or missing expected data.
    except (ValueError, OSError) as error:
        logger.error("Data validation or file storage error: %s", error)

    # Catch-all for any other unexpected exceptions that may occur during the extraction process.
    except Exception:
        logger.exception("Unexpected error during extraction.")

    return None
