import json
import logging

from src.extract import extract_weather_data


logger = logging.getLogger(__name__)


def main():

    # start the ETL process and log the start time
    logger.info("Starting Berlin Weather ETL application...>")

    # call the extract_weather_data function to retrieve weather data
    data = extract_weather_data()

    if data:
        print("\nWeather data extracted successfully!")

        # print the extracted data in a readable JSON format for verification
        print("\nExtracted Weather Data:")
        print(json.dumps(data, indent=4, ensure_ascii=False))

    else:
        # log a warning if the extraction process failed and no data was retrieved
        logger.warning("Weather data extraction failed.")

    # log the completion of the ETL process with a timestamp
    logger.info("Weather ETL application finishedy...<")


if __name__ == "__main__":
    main()
