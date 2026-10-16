import 'package:flutter/material.dart';
import 'package:dio/dio.dart';

import '../../services/api_service.dart';
import 'dashboard.dart';

class Screen2Processing extends StatefulWidget {
  const Screen2Processing({
    super.key,
    required this.trailName,
    required this.startDate,
    required this.endDate,
  });

  final String trailName;
  final DateTime startDate;
  final DateTime endDate;

  @override
  State<Screen2Processing> createState() => _Screen2ProcessingState();
}

class _Screen2ProcessingState extends State<Screen2Processing> with SingleTickerProviderStateMixin {
  final _apiService = ApiService();
  String? _errorMessage;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    createForecast();
  }

  Future<void> createForecast() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final forecast = await _apiService.createForecast(
        trailName: widget.trailName,
        startDate: widget.startDate,
        endDate: widget.endDate,
      );
      if (!mounted) return;
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => Screen3Dashboard(forecast: forecast)),
      );
    } on DioException catch (error) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _errorMessage = error.response?.data is Map<String, dynamic>
            ? (error.response!.data as Map<String, dynamic>)['detail']?.toString()
            : 'Could not reach the backend at ${ApiService.baseUrl}. Start the API and try again.';
      });
    } on FormatException catch (error) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _errorMessage = error.message;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0B5563),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.psychology, size: 64, color: Color(0xFF1BB98D)),
              const SizedBox(height: 24),
              const Text(
                'Analyzing Trail Hazards',
                style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Text(
                _isLoading
                    ? 'Requesting a forecast for ${widget.trailName}'
                    : 'The forecast could not be loaded.',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.white70, fontSize: 14),
              ),
              const SizedBox(height: 48),
              LinearProgressIndicator(
                value: _isLoading ? null : 0,
                backgroundColor: Colors.white24,
                color: const Color(0xFF1BB98D),
                minHeight: 8,
                borderRadius: BorderRadius.circular(4),
              ),
              const SizedBox(height: 24),
              if (_errorMessage != null) ...[
                Text(
                  _errorMessage!,
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.white, fontSize: 13),
                ),
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    OutlinedButton.icon(
                      onPressed: () => Navigator.pop(context),
                      icon: const Icon(Icons.arrow_back),
                      label: const Text('Back'),
                    ),
                    const SizedBox(width: 12),
                    FilledButton.icon(
                      onPressed: createForecast,
                      icon: const Icon(Icons.refresh),
                      label: const Text('Retry'),
                    ),
                  ],
                ),
              ],
              if (_isLoading)
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.05),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.white12),
                ),
                child: Column(
                  children: [
                    Row(
                      children: [
                          const SizedBox(
                          width: 16, height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF1BB98D)),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            'Waiting for the backend forecast response...',
                            style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w500),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}