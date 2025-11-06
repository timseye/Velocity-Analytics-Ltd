
from prometheus_client import start_http_server, Gauge, Info, Counter
import requests
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Exporter info
exporter_info = Info('custom_exporter', 'Information about the custom exporter')

# Weather metrics with labels for multiple cities
weather_temperature = Gauge(
    'weather_temperature_celsius',
    'Current temperature',
    ['city', 'country']
)

weather_apparent_temperature = Gauge(
    'weather_apparent_temperature_celsius',
    'Feels-like temperature',
    ['city', 'country']
)

weather_windspeed = Gauge(
    'weather_windspeed_kmh',
    'Current wind speed in km/h',
    ['city', 'country']
)

weather_wind_direction = Gauge(
    'weather_wind_direction_degrees',
    'Wind direction in degrees',
    ['city', 'country']
)

weather_pressure = Gauge(
    'weather_pressure_hpa',
    'Atmospheric pressure at sea level in hPa',
    ['city', 'country']
)

weather_humidity = Gauge(
    'weather_humidity_percent',
    'Relative humidity in percent',
    ['city', 'country']
)

weather_precipitation = Gauge(
    'weather_precipitation_mm',
    'Precipitation amount in mm',
    ['city', 'country']
)

weather_cloud_cover = Gauge(
    'weather_cloud_cover_percent',
    'Cloud cover percentage',
    ['city', 'country']
)

weather_visibility = Gauge(
    'weather_visibility_meters',
    'Visibility in meters',
    ['city', 'country']
)

weather_uv_index = Gauge(
    'weather_uv_index',
    'UV index',
    ['city', 'country']
)

weather_is_day = Gauge(
    'weather_is_day',
    'Whether it is day (1) or night (0)',
    ['city', 'country']
)

# API status metrics
weather_api_status = Gauge(
    'weather_api_status',
    'Weather API status (1=up, 0=down)'
)

weather_api_response_time = Gauge(
    'weather_api_response_time_seconds',
    'API response time in seconds',
    ['city']
)

weather_api_requests_total = Counter(
    'weather_api_requests_total',
    'Total number of API requests',
    ['city', 'status']
)

# Cities to monitor
CITIES = [
    {'name': 'Astana', 'country': 'Kazakhstan', 'lat': 51.1694, 'lon': 71.4491},
    {'name': 'Almaty', 'country': 'Kazakhstan', 'lat': 43.2220, 'lon': 76.8512},
    {'name': 'London', 'country': 'UK', 'lat': 51.5074, 'lon': -0.1278},
]


def fetch_weather_data(city_info):
    """
    Fetch weather data for a specific city from Open-Meteo API
    """
    city = city_info['name']
    country = city_info['country']
    
    try:
        start_time = time.time()
        
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': city_info['lat'],
            'longitude': city_info['lon'],
            'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,'
                      'is_day,precipitation,cloud_cover,pressure_msl,surface_pressure,'
                      'wind_speed_10m,wind_direction_10m,wind_gusts_10m',
            'timezone': 'auto',
            'forecast_days': 1
        }
        
        response = requests.get(url, params=params, timeout=10)
        response_time = time.time() - start_time
        
        response.raise_for_status()
        data = response.json()
        
        current = data['current']
        
        # Update temperature metrics
        weather_temperature.labels(
            city=city,
            country=country
        ).set(current['temperature_2m'])
        
        weather_apparent_temperature.labels(
            city=city,
            country=country
        ).set(current['apparent_temperature'])
        
        # Update wind metrics
        weather_windspeed.labels(
            city=city,
            country=country
        ).set(current['wind_speed_10m'])
        
        weather_wind_direction.labels(
            city=city,
            country=country
        ).set(current['wind_direction_10m'])
        
        # Update atmospheric metrics
        weather_pressure.labels(
            city=city,
            country=country
        ).set(current['pressure_msl'])
        
        weather_humidity.labels(
            city=city,
            country=country
        ).set(current['relative_humidity_2m'])
        
        # Update weather condition metrics
        weather_precipitation.labels(
            city=city,
            country=country
        ).set(current['precipitation'])
        
        weather_cloud_cover.labels(
            city=city,
            country=country
        ).set(current['cloud_cover'])
        
        # Update day/night indicator
        weather_is_day.labels(
            city=city,
            country=country
        ).set(current['is_day'])
        
        # Update API performance metrics
        weather_api_response_time.labels(city=city).set(response_time)
        weather_api_requests_total.labels(city=city, status='success').inc()
        weather_api_status.set(1)
        
        logger.info(f"Successfully fetched data for {city}: {current['temperature_2m']}°C")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch data for {city}: {e}")
        weather_api_requests_total.labels(city=city, status='error').inc()
        weather_api_status.set(0)
        return False
    except Exception as e:
        logger.error(f"Unexpected error for {city}: {e}")
        weather_api_requests_total.labels(city=city, status='error').inc()
        return False


def collect_all_metrics():
    """
    Collect metrics for all cities
    """
    logger.info("Starting metric collection cycle")
    success_count = 0
    
    for city_info in CITIES:
        if fetch_weather_data(city_info):
            success_count += 1
        time.sleep(1)  # Small delay between cities to avoid rate limiting
    
    logger.info(f"Collection cycle complete: {success_count}/{len(CITIES)} cities updated")


if __name__ == '__main__':
    # Set exporter info
    exporter_info.info({
        'version': '1.0',
        'author': 'Student',
        'data_source': 'Open-Meteo API',
        'cities': ', '.join([c['name'] for c in CITIES]),
        'update_interval': '30s'
    })
    
    logger.info("Starting Custom Weather Exporter on port 8000")
    logger.info(f"Monitoring cities: {[c['name'] for c in CITIES]}")
    
    # Start HTTP server on port 8000
    start_http_server(8000)
    logger.info("HTTP server started successfully")
    
    # Infinite metrics collection loop
    while True:
        try:
            collect_all_metrics()
        except KeyboardInterrupt:
            logger.info("Shutting down exporter...")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        
        # Update every 30 seconds
        time.sleep(30)
