import 'package:flutter/material.dart';
import 'recommended_response_screen.dart';

class ContextAnalysisScreen extends StatelessWidget {
  const ContextAnalysisScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Context Analysis Dashboard')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Environmental & Situational Context', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            GridView.count(
              crossAxisCount: 2,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
              childAspectRatio: 1.3,
              children: const [
                _ContextCard(icon: Icons.location_on, title: 'Current Location', subtitle: 'Horton Plains, Nuwara Eliya'),
                _ContextCard(icon: Icons.cloud, title: 'Weather Condition', subtitle: '18°C, 82% Humidity, Wind 12km/h'),
                _ContextCard(icon: Icons.warning, title: 'Hazard Forecast', subtitle: 'Moderate Landslide & Rain Risk'),
                _ContextCard(icon: Icons.hiking, title: 'Nearby Trail Info', subtitle: 'World’s End Loop - 9.5 km'),
                _ContextCard(icon: Icons.terrain, title: 'Terrain Condition', subtitle: 'Slippery rock & steep incline'),
                _ContextCard(icon: Icons.history, title: 'Historical Incidents', subtitle: '3 recorded falls in past year'),
              ],
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF10B981),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => const RecommendedResponseScreen()),
                  );
                },
                child: const Text('View Recommended Response', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ContextCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;

  const _ContextCard({required this.icon, required this.title, required this.subtitle});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade300),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: const Color(0xFF10B981), size: 22),
          const SizedBox(height: 6),
          Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
          const SizedBox(height: 2),
          Text(subtitle, style: const TextStyle(color: Colors.grey, fontSize: 11), maxLines: 2, overflow: TextOverflow.ellipsis),
        ],
      ),
    );
  }
}