import 'package:flutter/material.dart';
import 'screens/component04/emergency_report_screen.dart';

void main() {
  runApp(const VentureEmergencyApp());
}

class VentureEmergencyApp extends StatelessWidget {
  const VentureEmergencyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Venture Emergency Module',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primaryColor: const Color(0xFF10B981), // Venture Emerald Teal
        scaffoldBackgroundColor: const Color(0xFFF8FAFC),
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF10B981),
          primary: const Color(0xFF10B981),
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF1E293B),
          foregroundColor: Colors.white,
          elevation: 0,
        ),
      ),
      home: const EmergencyReportScreen(),
    );
  }
}