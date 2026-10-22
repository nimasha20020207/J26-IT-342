import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

import '../models/component02/hazard_data.dart';
import 'offline_cache.dart';

class ApiService {
  ApiService({Dio? dio, OfflineCache? cache})
    : _dio = dio ?? Dio(BaseOptions(baseUrl: baseUrl)),
      _cache = cache ?? OfflineCache();

  final Dio _dio;
  final OfflineCache _cache;

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
    final cacheKey =
        'forecast:${trailName.toLowerCase()}:${_dateOnly(startDate)}:${_dateOnly(endDate)}';
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        '/api/v1/forecasts',
        data: {
          'trail_name': trailName,
          'start_date': _dateOnly(startDate),
          'end_date': _dateOnly(endDate),
        },
      );

      final data = response.data;
      if (data == null) {
        throw const FormatException('The backend returned an empty forecast.');
      }
      final updatedAt = DateTime.now();
      await _cache.save(cacheKey, data);
      return ForecastData.fromJson(
        data,
      ).withCacheMetadata(isCached: false, lastUpdatedAt: updatedAt);
    } on DioException catch (error) {
      if (!_canUseOfflineCopy(error)) rethrow;
      final cached = await _cache.read(cacheKey);
      if (cached == null) rethrow;
      return ForecastData.fromJson(
        cached.data,
      ).withCacheMetadata(isCached: true, lastUpdatedAt: cached.updatedAt);
    }
  }

  Future<WeatherSummary> getWeather({
    required String trailName,
    required DateTime forecastDate,
  }) async {
    final cacheKey =
        'weather:${trailName.toLowerCase()}:${_dateOnly(forecastDate)}';
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        '/api/v1/weather',
        queryParameters: {
          'trail_name': trailName,
          'forecast_date': _dateOnly(forecastDate),
        },
      );

      final data = response.data;
      if (data == null) {
        throw const FormatException('The backend returned empty weather data.');
      }
      final updatedAt = DateTime.now();
      await _cache.save(cacheKey, data);
      return WeatherSummary.fromJson(
        data,
      ).withCacheMetadata(isCached: false, lastUpdatedAt: updatedAt);
    } on DioException catch (error) {
      if (!_canUseOfflineCopy(error)) rethrow;
      final cached = await _cache.read(cacheKey);
      if (cached == null) rethrow;
      return WeatherSummary.fromJson(
        cached.data,
      ).withCacheMetadata(isCached: true, lastUpdatedAt: cached.updatedAt);
    }
  }

  Future<List<HeatZoneItem>> getHeatZones() async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/forecasts/heat-zones',
    );
    final data = response.data;
    if (data == null) return [];

    final features = data['features'] as List<dynamic>? ?? [];
    return features.map((f) {
      final props =
          (f as Map<String, dynamic>)['properties'] as Map<String, dynamic>;
      return HeatZoneItem.fromJson(props);
    }).toList();
  }

  static String _dateOnly(DateTime value) =>
      '${value.year.toString().padLeft(4, '0')}-${value.month.toString().padLeft(2, '0')}-${value.day.toString().padLeft(2, '0')}';

  static bool _canUseOfflineCopy(DioException error) =>
      error.type == DioExceptionType.connectionError ||
      error.type == DioExceptionType.connectionTimeout ||
      error.type == DioExceptionType.receiveTimeout ||
      error.type == DioExceptionType.sendTimeout ||
      (error.response?.statusCode ?? 0) >= 500;
}
