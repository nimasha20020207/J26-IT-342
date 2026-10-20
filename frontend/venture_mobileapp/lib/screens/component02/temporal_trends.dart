import 'package:flutter/material.dart';
import '../../models/component02/hazard_data.dart';
import '../../theme/app_theme.dart';
import '../../widgets/forecast_page_scaffold.dart';
import 'social_intelligence.dart';

class Screen5TemporalTrends extends StatelessWidget {
  const Screen5TemporalTrends({super.key, required this.forecast});

  final ForecastData forecast;

  @override
  Widget build(BuildContext context) {
    return ForecastPageScaffold(
      title: 'Risk trends',
      forecast: forecast,
      selectedDestination: 2,
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text(
            'Hourly risk progression',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: AppColors.text,
            ),
          ),
          const SizedBox(height: 12),
          // Hourly Timeline Card
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 8),
              ],
            ),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: forecast.hourlyTrends
                      .map(
                        (trend) => _HourlyTrendItem(
                          time: trend.time,
                          risk: trend.risk,
                          color: _riskColor(trend.risk),
                          score: '${trend.score}%',
                        ),
                      )
                      .toList(),
                ),
                const SizedBox(height: 16),
                const Text(
                  'Peak hazard window occurs between 11:00 AM and 1:00 PM due to sudden fog and mist buildup.',
                  style: TextStyle(fontSize: 12, color: Colors.grey),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          const Text(
            'Daily predictions · 7-day forecast',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: AppColors.text,
            ),
          ),
          const SizedBox(height: 12),
          ...forecast.dailyPredictions.map(
            (prediction) => Container(
              margin: const EdgeInsets.only(bottom: 10),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.04),
                    blurRadius: 8,
                  ),
                ],
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '${_formatDate(prediction.date)} - ${prediction.riskScore}% Risk',
                    style: const TextStyle(
                      fontWeight: FontWeight.w600,
                      color: AppColors.text,
                    ),
                  ),
                  Icon(
                    Icons.trending_up,
                    color: _riskColor(prediction.riskLevel),
                    size: 20,
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primary,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
            ),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) =>
                    Screen6SocialIntelligence(forecast: forecast),
              ),
            ),
            child: const Text(
              'View Social Hazard Intelligence',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
        ],
      ),
    );
  }
}

Color _riskColor(String risk) => switch (risk.toLowerCase()) {
  'high' => const Color(0xFFEF4444),
  'medium' => const Color(0xFFF59E0B),
  _ => AppColors.primary,
};

String _formatDate(DateTime date) =>
    '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';

class _HourlyTrendItem extends StatelessWidget {
  final String time;
  final String risk;
  final Color color;
  final String score;
  const _HourlyTrendItem({
    required this.time,
    required this.risk,
    required this.color,
    required this.score,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(time, style: const TextStyle(fontSize: 11, color: Colors.grey)),
        const SizedBox(height: 8),
        Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: color.withOpacity(0.15),
            shape: BoxShape.circle,
          ),
          child: Center(
            child: Text(
              score,
              style: TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ),
        ),
        const SizedBox(height: 6),
        Text(
          risk,
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }
}
