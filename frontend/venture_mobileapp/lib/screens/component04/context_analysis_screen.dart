import 'package:flutter/material.dart';
import '../../models/emergency_models.dart';
import 'recommended_response_screen.dart';

class ContextAnalysisScreen extends StatelessWidget {
  final FullEmergencyResponseModel response;

  const ContextAnalysisScreen({super.key, required this.response});

  @override
  Widget build(BuildContext context) {
    final ctx = response.contextSummary;

    return Scaffold(
      appBar: AppBar(title: const Text('Context Analysis Dashboard')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Environmental & Situational Context',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            const Text(
              'Multimodal contextual integration feeding into the Knowledge Graph.',
              style: TextStyle(color: Colors.grey, fontSize: 13),
            ),
            const SizedBox(height: 16),

            GridView.count(
              crossAxisCount: 2,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
              childAspectRatio: 1.25,
              children: [
                _ContextCard(
                  icon: Icons.location_on,
                  title: 'GPS Coordinates',
                  subtitle: ctx.coordinates,
                ),
                _ContextCard(
                  icon: Icons.hiking,
                  title: 'Trail Area',
                  subtitle: ctx.trailName?.replaceAll('_', ' ') ?? 'Central Highlands Trail',
                ),
                _ContextCard(
                  icon: Icons.cloud,
                  title: 'Weather Telemetry',
                  subtitle: ctx.weather,
                ),
                _ContextCard(
                  icon: Icons.terrain,
                  title: 'Terrain Profile',
                  subtitle: ctx.terrain,
                ),
                _ContextCard(
                  icon: Icons.battery_alert,
                  title: 'Hiker Status',
                  subtitle: ctx.hikerStatus,
                ),
                _ContextCard(
                  icon: Icons.warning_amber_rounded,
                  title: 'Active Inferred Hazards',
                  subtitle: response.activeHazards.isNotEmpty
                      ? response.activeHazards.join(', ').replaceAll('_', ' ')
                      : 'None Detected',
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Next button: Recommended Response
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
                    MaterialPageRoute(
                      builder: (context) => RecommendedResponseScreen(response: response),
                    ),
                  );
                },
                child: const Text('View Recommended Response Actions', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
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
          const SizedBox(height: 4),
          Text(
            subtitle,
            style: const TextStyle(color: Colors.grey, fontSize: 11),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}