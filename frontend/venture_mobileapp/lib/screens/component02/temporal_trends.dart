import 'package:flutter/material.dart';
import 'social_intelligence.dart';

class Screen5TemporalTrends extends StatelessWidget {
  const Screen5TemporalTrends({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF0B5563),
        foregroundColor: Colors.white,
        title: const Text('Temporal Risk Trends', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('Hourly Risk Progression', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF0B5563))),
          const SizedBox(height: 12),
          // Hourly Timeline Card
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 8)],
            ),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: const [
                    _HourlyTrendItem(time: '06:00 AM', risk: 'Low', color: Color(0xFF1BB98D), score: '35%'),
                    _HourlyTrendItem(time: '09:00 AM', risk: 'Medium', color: Color(0xFFF59E0B), score: '55%'),
                    _HourlyTrendItem(time: '12:00 PM', risk: 'High', color: Color(0xFFEF4444), score: '78%'),
                    _HourlyTrendItem(time: '03:00 PM', risk: 'Medium', color: Color(0xFFF59E0B), score: '60%'),
                  ],
                ),
                const SizedBox(height: 16),
                const Text('Peak hazard window occurs between 11:00 AM and 1:00 PM due to sudden fog and mist buildup.', style: TextStyle(fontSize: 12, color: Colors.grey)),
              ],
            ),
          ),
          const SizedBox(height: 20),
          const Text('Daily Predictions (7-Day Forecast)', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF0B5563))),
          const SizedBox(height: 12),
          ...['Oct 17 (Today) - 68% Risk', 'Oct 18 - 45% Risk', 'Oct 19 - 30% Risk', 'Oct 20 - 72% Risk (Rain)', 'Oct 21 - 50% Risk'].map((day) => Container(
                margin: const EdgeInsets.only(bottom: 10),
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 8)],
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(day, style: const TextStyle(fontWeight: FontWeight.w600, color: Color(0xFF0B5563))),
                    const Icon(Icons.trending_up, color: Color(0xFFF59E0B), size: 20),
                  ],
                ),
              )),
          const SizedBox(height: 16),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF1BB98D),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            ),
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (context) => const Screen6SocialIntelligence())),
            child: const Text('View Social Hazard Intelligence', style: TextStyle(fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }
}

class _HourlyTrendItem extends StatelessWidget {
  final String time;
  final String risk;
  final Color color;
  final String score;
  const _HourlyTrendItem({required this.time, required this.risk, required this.color, required this.score});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(time, style: const TextStyle(fontSize: 11, color: Colors.grey)),
        const SizedBox(height: 8),
        Container(
          width: 40, height: 40,
          decoration: BoxDecoration(color: color.withOpacity(0.15), shape: BoxShape.circle),
          child: Center(child: Text(score, style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: color))),
        ),
        const SizedBox(height: 6),
        Text(risk, style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: color)),
      ],
    );
  }
}