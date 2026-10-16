// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';

import 'package:venture_mobileapp/models/component02/hazard_data.dart';
import 'package:venture_mobileapp/screens/component02/trip_planning.dart';
import 'package:venture_mobileapp/services/api_service.dart';

void main() {
  testWidgets('Trip planning screen smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(home: Screen1TripPlanning(apiService: _FakeApiService())),
    );
    await tester.pumpAndSettle();

    expect(find.text('Hazard & Weather Forecast'), findsOneWidget);
    expect(find.text('Plan your hike'), findsOneWidget);

    final dropdown = tester.widget<DropdownButton<String>>(
      find.byType(DropdownButton<String>),
    );
    expect(dropdown.value, 'Pidurangala');
    final trailImage = tester.widget<Image>(find.byType(Image));
    expect(
      (trailImage.image as AssetImage).assetName,
      'assets/component02/pidurangala.jpg',
    );
    expect(
      dropdown.items!.map((item) => item.value).toList(),
      [
        'Pidurangala',
        'Sigiriya',
        'Alagalla',
        'Narangala',
        'Hanthana',
        'Lakegala',
        'Manigala',
        'Kirigalpoththa',
        'Little Adam\'s peak',
        'Pettigala',
        'Peacock hills',
        'Thotupala kanda',
        'Bathalegala',
      ],
    );
  });
}

class _FakeApiService extends ApiService {
  @override
  Future<WeatherSummary> getWeather({
    required String trailName,
    required DateTime forecastDate,
  }) async {
    return WeatherSummary(
      forecastDate: forecastDate,
      source: 'Open-Meteo',
      temperatureC: 30,
      feelsLikeC: 36,
      condition: 'Partly cloudy',
      rainChance: 30,
      precipitationMm: 2,
      windSpeedKmh: 12,
      windGustKmh: 20,
      humidity: 68,
    );
  }
}
