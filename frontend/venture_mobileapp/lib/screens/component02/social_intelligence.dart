import 'package:flutter/material.dart';
import '../../models/component02/hazard_data.dart';
import 'final_assessment.dart';

class Screen6SocialIntelligence extends StatelessWidget {
  const Screen6SocialIntelligence({super.key, required this.forecast});

  final ForecastData forecast;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF0B5563),
        foregroundColor: Colors.white,
        title: const Text('Social Hazard Intelligence', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('Extracted News & Hiker Signals (BERT Verified)', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF0B5563))),
          const SizedBox(height: 12),
          ...forecast.socialReports.map((r) => Container(
                margin: const EdgeInsets.only(bottom: 14),
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 8)],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            Icon(r.type == 'News' ? Icons.newspaper : Icons.person, size: 16, color: const Color(0xFF0B5563)),
                            const SizedBox(width: 6),
                            Text(r.source, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF0B5563))),
                          ],
                        ),
                        Text(r.timeAgo, style: const TextStyle(fontSize: 11, color: Colors.grey)),
                      ],
                    ),
                    const SizedBox(height: 10),
                    Text('"${r.content}"', style: const TextStyle(fontSize: 13, color: Colors.black87, fontStyle: FontStyle.italic)),
                    const SizedBox(height: 12),
                    const Divider(color: Colors.black12),
                    const SizedBox(height: 6),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.verified, size: 14, color: Color(0xFF1BB98D)),
                            const SizedBox(width: 4),
                            Text('Reliability: ${(r.reliabilityScore * 100).toInt()}%', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF1BB98D))),
                          ],
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(color: Colors.grey.shade100, borderRadius: BorderRadius.circular(8)),
                          child: Text(r.confidenceIndicator, style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Colors.grey)),
                        ),
                      ],
                    ),
                  ],
                ),
              )),
          const SizedBox(height: 12),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF1BB98D),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            ),
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (context) => Screen7FinalAssessment(forecast: forecast))),
            child: const Text('View Final Risk Assessment', style: TextStyle(fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }
}