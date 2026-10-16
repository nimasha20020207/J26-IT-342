import json
from datetime import date, datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from schemas.component02.forecast import WeatherSummary
from services.component02.trail_locations import TRAIL_COORDINATES

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
SRI_LANKA_TIMEZONE = timezone(timedelta(hours=5, minutes=30))
FORECAST_DAYS = 16


class WeatherProviderError(RuntimeError):
    pass


def get_trail_weather(trail_name: str, forecast_date: date) -> WeatherSummary:
    coordinates = TRAIL_COORDINATES.get(trail_name)
    if coordinates is None:
        raise ValueError(f"No coordinates are configured for trail '{trail_name}'.")

    today = datetime.now(SRI_LANKA_TIMEZONE).date()
    last_forecast_date = today + timedelta(days=FORECAST_DAYS - 1)
    if forecast_date < today or forecast_date > last_forecast_date:
        raise ValueError(
            f"Choose a date from {today.isoformat()} through {last_forecast_date.isoformat()}; "
            "Open-Meteo forecasts up to 16 days ahead."
        )

    latitude, longitude = coordinates
    query = urlencode(
        {
            "latitude": latitude,
            "longitude": longitude,
            "daily": ",".join(
                [
                    "weather_code",
                    "temperature_2m_max",
                    "apparent_temperature_max",
                    "precipitation_probability_max",
                    "precipitation_sum",
                    "wind_speed_10m_max",
                    "wind_gusts_10m_max",
                ]
            ),
            "hourly": "relative_humidity_2m",
            "forecast_days": FORECAST_DAYS,
            "timezone": "Asia/Colombo",
        }
    )
    request = Request(
        f"{OPEN_METEO_URL}?{query}",
        headers={"User-Agent": "VentureHazardForecast/1.0"},
    )

    try:
        with urlopen(request, timeout=12) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raise WeatherProviderError(f"Open-Meteo returned HTTP {error.code}.") from error
    except (OSError, json.JSONDecodeError) as error:
        raise WeatherProviderError("Could not retrieve weather from Open-Meteo.") from error

    try:
        daily = payload["daily"]
        day_index = daily["time"].index(forecast_date.isoformat())
        hourly = payload["hourly"]
        noon_index = hourly["time"].index(f"{forecast_date.isoformat()}T12:00")
        humidity = round(hourly["relative_humidity_2m"][noon_index])

        return WeatherSummary(
            forecast_date=forecast_date,
            source="Open-Meteo",
            temperature_c=_daily_value(daily, "temperature_2m_max", day_index),
            feels_like_c=_daily_value(daily, "apparent_temperature_max", day_index),
            condition=_weather_description(int(_daily_value(daily, "weather_code", day_index))),
            rain_chance=round(_daily_value(daily, "precipitation_probability_max", day_index)),
            precipitation_mm=_daily_value(daily, "precipitation_sum", day_index),
            wind_speed_kmh=_daily_value(daily, "wind_speed_10m_max", day_index),
            wind_gust_kmh=_daily_value(daily, "wind_gusts_10m_max", day_index),
            humidity=humidity,
        )
    except (KeyError, IndexError, ValueError, TypeError) as error:
        raise WeatherProviderError("Open-Meteo returned incomplete weather data.") from error


def _daily_value(daily: dict, variable: str, index: int) -> float:
    value = daily[variable][index]
    if value is None:
        raise ValueError(f"Open-Meteo did not return {variable} for the selected date.")
    return float(value)


def _weather_description(code: int) -> str:
    descriptions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snowfall",
        73: "Moderate snowfall",
        75: "Heavy snowfall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }
    return descriptions.get(code, "Unknown conditions")