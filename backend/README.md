# Backend API

## Run locally

From the repository root in PowerShell:

```powershell
python -m pip install -r backend/requirements.txt
Set-Location backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API is available at `http://127.0.0.1:8000`. Interactive endpoint documentation is at `/docs`.

## Demo forecast

`POST /api/v1/forecasts` accepts a trail and trip dates. It returns demo hazards, recommendations, social reports, and risk trends, together with live weather for the selected trail and start date. Its `mode: "demo"` indicates the hazard/model results are placeholders; the weather has its own `source: "Open-Meteo"` field. Replace `generate_demo_forecast` in `services/component02/forecast_service.py` with the model pipeline when it is ready, preserving the response schema or updating the mobile decoder alongside it. Component 02's API routes, schemas, and services are grouped in their respective `component02` subfolders.

Example body:

```json
{
  "trail_name": "Horton Plains National Park",
  "start_date": "2026-10-17",
  "end_date": "2026-10-17"
}
```

`GET /health` returns the API health status.

## Trail weather

`GET /api/v1/weather?trail_name=Pidurangala&forecast_date=2026-10-17` fetches the selected date's daily weather from Open-Meteo. The date must be today through 15 days ahead in Sri Lanka time. The response includes maximum temperature and apparent temperature, condition, maximum precipitation chance and amount, maximum wind and gusts, and noon relative humidity.

Trail coordinates are stored in `services/component02/trail_locations.py`. They are representative summit or trail-area points, not route-wide measurements; verify them against your field/GIS data. Coordinate references were checked against OpenStreetMap data (© OpenStreetMap contributors, ODbL). Open-Meteo's free API is for non-commercial use; review its current terms before deployment.

## Run the mobile app

Run the backend first, then start Flutter. Web uses `127.0.0.1`; the Android emulator uses `10.0.2.2` automatically. For the iOS simulator, use HTTPS or configure a debug-only App Transport Security exception before connecting over HTTP.

```powershell
Set-Location frontend/venture_mobileapp
flutter run
```

For a physical device, pass the backend computer's LAN address and allow port 8000 through its firewall:

```powershell
flutter run --dart-define=API_BASE_URL=http://192.168.1.10:8000
```

Replace the sample address with the host computer's reachable IP. The HTTP cleartext exception is enabled only for Android debug builds; use HTTPS for production.