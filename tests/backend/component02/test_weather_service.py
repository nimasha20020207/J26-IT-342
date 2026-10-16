import json
from datetime import datetime, timedelta
from unittest import TestCase
from unittest.mock import patch

from services.component02.weather_service import (
    SRI_LANKA_TIMEZONE,
    get_trail_weather,
)


class TrailWeatherTests(TestCase):
    def test_parses_open_meteo_daily_forecast(self):
        forecast_date = datetime.now(SRI_LANKA_TIMEZONE).date() + timedelta(days=1)
        response_data = {
            "daily": {
                "time": [forecast_date.isoformat()],
                "weather_code": [95],
                "temperature_2m_max": [30.2],
                "apparent_temperature_max": [36.4],
                "precipitation_probability_max": [80],
                "precipitation_sum": [11.3],
                "wind_speed_10m_max": [13.6],
                "wind_gusts_10m_max": [24.1],
            },
            "hourly": {
                "time": [f"{forecast_date.isoformat()}T12:00"],
                "relative_humidity_2m": [68],
            },
        }
        with patch("services.component02.weather_service.urlopen") as open_url:
            open_url.return_value.__enter__.return_value.read.return_value = json.dumps(
                response_data
            ).encode("utf-8")
            weather = get_trail_weather("Pidurangala", forecast_date)

        self.assertEqual(weather.source, "Open-Meteo")
        self.assertEqual(weather.forecast_date, forecast_date)
        self.assertEqual(weather.condition, "Thunderstorm")
        self.assertEqual(weather.rain_chance, 80)
        self.assertEqual(weather.precipitation_mm, 11.3)
        self.assertEqual(weather.humidity, 68)

    def test_rejects_dates_outside_forecast_window_without_request(self):
        forecast_date = datetime.now(SRI_LANKA_TIMEZONE).date() + timedelta(days=16)
        with patch("services.component02.weather_service.urlopen") as open_url:
            with self.assertRaisesRegex(ValueError, "up to 16 days ahead"):
                get_trail_weather("Pidurangala", forecast_date)

        open_url.assert_not_called()