import 'package:flutter/material.dart';
import '../../models/component02/hazard_data.dart';
import 'heatmap.dart';

class Screen3Dashboard extends StatelessWidget {
  const Screen3Dashboard({super.key, required this.forecast});

  final ForecastData forecast;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF0B5563),
        foregroundColor: Colors.white,
        title: const Text('Hazard Forecast Dashboard', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        actions: [
          IconButton(
            icon: const Icon(Icons.map),
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (context) => Screen4Heatmap(forecast: forecast))),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Overall Risk Card
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: const LinearGradient(colors: [Color(0xFF0B5563), Color(0xFF137B8C)]),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Overall Risk Score', style: TextStyle(color: Colors.white70, fontSize: 13)),
                    SizedBox(height: 4),
                    Text('${forecast.overallRiskScore} / 100', style: TextStyle(color: Colors.white, fontSize: 28, fontWeight: FontWeight.bold)),
                    SizedBox(height: 4),
                    Text('Backend ${forecast.mode} forecast', style: TextStyle(color: Colors.white60, fontSize: 11)),
                  ],
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF59E0B),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    '${forecast.riskLevel} Risk',
                    style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Weather · ${forecast.weather.source} · ${forecast.weather.forecastDate.toIso8601String().split('T').first}',
                  style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF0B5563)),
                ),
                const SizedBox(height: 8),
                Text(
                  '${forecast.weather.temperatureC.toStringAsFixed(0)}°C · ${forecast.weather.condition} · Feels like ${forecast.weather.feelsLikeC.toStringAsFixed(0)}°C',
                  style: const TextStyle(fontSize: 13),
                ),
                const SizedBox(height: 4),
                Text(
                  'Rain ${forecast.weather.rainChance}% (${forecast.weather.precipitationMm.toStringAsFixed(1)} mm) · Wind ${forecast.weather.windSpeedKmh.toStringAsFixed(0)} km/h · Gusts ${forecast.weather.windGustKmh.toStringAsFixed(0)} km/h · Humidity ${forecast.weather.humidity}%',
                  style: const TextStyle(fontSize: 12, color: Colors.black54),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          const Text('Identified Hazard Probabilities', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF0B5563))),
          const SizedBox(height: 12),
          // Hazards List
          ...forecast.hazards.map((h) => Container(
                margin: const EdgeInsets.only(bottom: 12),
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 8, offset: const Offset(0, 2))],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(h.name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Color(0xFF0B5563))),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: h.severity == 'High'
                                ? const Color(0xFFEF4444).withOpacity(0.1)
                                : h.severity == 'Medium'
                                    ? const Color(0xFFF59E0B).withOpacity(0.1)
                                    : const Color(0xFF1BB98D).withOpacity(0.1),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            h.severity,
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.bold,
                              color: h.severity == 'High'
                                  ? const Color(0xFFEF4444)
                                  : h.severity == 'Medium'
                                      ? const Color(0xFFF59E0B)
                                      : const Color(0xFF1BB98D),
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    Row(
                      children: [
                        Expanded(
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(4),
                            child: LinearProgressIndicator(
                              value: h.probability,
                              minHeight: 8,
                              backgroundColor: Colors.grey.shade200,
                              color: h.probability > 0.7
                                  ? const Color(0xFFEF4444)
                                  : h.probability > 0.4
                                      ? const Color(0xFFF59E0B)
                                      : const Color(0xFF1BB98D),
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Text('${(h.probability * 100).toInt()}%', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                      ],
                    ),
                  ],
                ),
              )),
          const SizedBox(height: 12),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF0B5563),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            ),
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (context) => Screen4Heatmap(forecast: forecast))),
            child: const Text('View Environmental Risk Heatmap', style: TextStyle(fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }
}