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

  static String _dateOnly(DateTime value) =>
      '${value.year.toString().padLeft(4, '0')}-${value.month.toString().padLeft(2, '0')}-${value.day.toString().padLeft(2, '0')}';
}