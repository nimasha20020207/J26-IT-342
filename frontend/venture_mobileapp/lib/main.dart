import 'package:flutter/material.dart';
import 'models/component02/hazard_data.dart';
import 'screens/component02/dashboard.dart';
import 'screens/component02/final_assessment.dart';
import 'screens/component02/heatmap.dart';
import 'screens/component02/social_intelligence.dart';
import 'screens/component02/temporal_trends.dart';
import 'screens/component02/trip_planning.dart';
import 'theme/app_theme.dart';
import 'widgets/forecast_page_scaffold.dart';

void main() {
  runApp(const VentureForecastApp());
}

class VentureForecastApp extends StatelessWidget {
  const VentureForecastApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Venture - Hazard Forecasting',
      debugShowCheckedModeBanner: false,
      theme: buildAppTheme(),
      home: const Screen1TripPlanning(),
      onGenerateRoute: (settings) {
        final forecast = settings.arguments;
        if (forecast is! ForecastData) return null;

        final page = switch (settings.name) {
          ForecastRoutes.overview => Screen3Dashboard(forecast: forecast),
          ForecastRoutes.map => Screen4Heatmap(forecast: forecast),
          ForecastRoutes.trends => Screen5TemporalTrends(forecast: forecast),
          ForecastRoutes.signals => Screen6SocialIntelligence(
            forecast: forecast,
          ),
          ForecastRoutes.assessment => Screen7FinalAssessment(
            forecast: forecast,
          ),
          _ => null,
        };
        return page == null
            ? null
            : MaterialPageRoute<void>(builder: (_) => page, settings: settings);
      },
    );
  }
}
