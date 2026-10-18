import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

import '../models/component02/hazard_data.dart';

class ApiService {
  ApiService({Dio? dio}) : _dio = dio ?? Dio(BaseOptions(baseUrl: baseUrl));

  final Dio _dio;

  static const _configuredBaseUrl = String.fromEnvironment('API_BASE_URL');

  static String get baseUrl {
    if (_configuredBaseUrl.isNotEmpty) return _configuredBaseUrl;
    if (kIsWeb || defaultTargetPlatform != TargetPlatform.android) {
      return 'http://127.0.0.1:8000';
    }
    return 'http://10.0.2.2:8000';
  }

  Future<ForecastData> createForecast({
    required String trailName,
    required DateTime startDate,
    required DateTime endDate,
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/forecasts',
      data: {
        'trail_name': trailName,
        'start_date': _dateOnly(startDate),
        'end_date': _dateOnly(endDate),
      },
    );

    final data = response.data;
    if (data == null) throw const FormatException('The backend returned an empty forecast.');
    return ForecastData.fromJson(data);
  }

  Future<WeatherSummary> getWeather({
    required String trailName,
    required DateTime forecastDate,
  }) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/weather',
      queryParameters: {
        'trail_name': trailName,
        'forecast_date': _dateOnly(forecastDate),
      },
    );

    final data = response.data;
    if (data == null) throw const FormatException('The backend returned empty weather data.');
    return WeatherSummary.fromJson(data);
  }

  Future<List<HeatZoneItem>> getHeatZones() async {
    final response = await _dio.get<Map<String, dynamic>>('/api/v1/forecasts/heat-zones');
    final data = response.data;
    if (data == null) return [];

    final features = data['features'] as List<dynamic>? ?? [];
    return features.map((f) {
      final props = (f as Map<String, dynamic>)['properties'] as Map<String, dynamic>;
      return HeatZoneItem.fromJson(props);
    }).toList();
  }

  static String _dateOnly(DateTime value) =>
      '${value.year.toString().padLeft(4, '0')}-${value.month.toString().padLeft(2, '0')}-${value.day.toString().padLeft(2, '0')}';
}