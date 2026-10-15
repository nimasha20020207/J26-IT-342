import 'package:flutter/material.dart';
import 'screens/component02/trip_planning.dart';

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
      theme: ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: const Color(0xFFF8FAFC),
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF0B5563),
          primary: const Color(0xFF0B5563),
          secondary: const Color(0xFF1BB98D),
        ),
      ),
      home: const Screen1TripPlanning(),
    );
  }
}