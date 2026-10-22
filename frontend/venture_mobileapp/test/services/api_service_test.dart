import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:venture_mobileapp/services/api_service.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('uses saved weather when the API connection fails', () async {
    SharedPreferences.setMockInitialValues({});
    var connected = true;
    final dio = Dio()
      ..interceptors.add(
        InterceptorsWrapper(
          onRequest: (options, handler) {
            if (!connected) {
              handler.reject(
                DioException(
                  requestOptions: options,
                  type: DioExceptionType.connectionError,
                ),
              );
              return;
            }
            handler.resolve(
              Response<Map<String, dynamic>>(
                requestOptions: options,
                data: {
                  'forecast_date': '2026-10-23',
                  'source': 'Open-Meteo',
                  'temperature_c': 30.0,
                  'feels_like_c': 32.0,
                  'condition': 'Partly cloudy',
                  'rain_chance': 20,
                  'precipitation_mm': 1.0,
                  'wind_speed_kmh': 10.0,
                  'wind_gust_kmh': 15.0,
                  'humidity': 70,
                },
              ),
            );
          },
        ),
      );
    final api = ApiService(dio: dio);
    final date = DateTime(2026, 10, 23);

    final online = await api.getWeather(
      trailName: 'Pidurangala',
      forecastDate: date,
    );
    expect(online.isCached, isFalse);
    expect(online.lastUpdatedAt, isNotNull);

    connected = false;
    final offline = await api.getWeather(
      trailName: 'Pidurangala',
      forecastDate: date,
    );
    expect(offline.isCached, isTrue);
    expect(offline.lastUpdatedAt, isNotNull);
    expect(offline.temperatureC, online.temperatureC);
  });
}
