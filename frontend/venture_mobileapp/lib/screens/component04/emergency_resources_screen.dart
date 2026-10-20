import 'package:flutter/material.dart';
import '../../models/emergency_models.dart';
import 'recommendation_explanation_screen.dart';

class EmergencyResourcesScreen extends StatelessWidget {
  final FullEmergencyResponseModel response;

  const EmergencyResourcesScreen({super.key, required this.response});

  @override
  Widget build(BuildContext context) {
    final resources = response.nearestResources;

    return Scaffold(
      appBar: AppBar(title: const Text('Emergency Resources')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Active Location Banner
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFF1E293B),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  const Icon(Icons.location_on, color: Color(0xFF10B981)),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Current GPS Fix (Sri Lanka Grid)',
                          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13),
                        ),
                        Text(
                          '${response.contextSummary.coordinates} • ${response.contextSummary.trailName?.replaceAll('_', ' ') ?? 'Central Province'}',
                          style: const TextStyle(color: Colors.white70, fontSize: 11),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            const Text('Nearby Assistance & Rescue Teams', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 4),
            const Text(
              'Ranked by Haversine distance with mountain terrain dispatch estimates.',
              style: TextStyle(color: Colors.grey, fontSize: 12),
            ),
            const SizedBox(height: 12),

            if (resources.isEmpty)
              const Text('No verified resources within 50km radius.')
            else
              ...resources.map((res) => _ResourceTile(
                name: res.name,
                type: res.type,
                distance: res.distanceStr,
                time: res.estimatedTimeStr,
                phone: res.phone,
                services: res.services.join(', '),
              )),

            const SizedBox(height: 20),
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
                      builder: (context) => RecommendationExplanationScreen(response: response),
                    ),
                  );
                },
                child: const Text('View Explainable AI (XAI) Insights', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ResourceTile extends StatelessWidget {
  final String name;
  final String type;
  final String distance;
  final String time;
  final String phone;
  final String services;

  const _ResourceTile({
    required this.name,
    required this.type,
    required this.distance,
    required this.time,
    required this.phone,
    required this.services,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade300),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF1E293B))),
                const SizedBox(height: 3),
                Text('$type • $distance away • Est. $time', style: const TextStyle(color: Colors.grey, fontSize: 11)),
                if (services.isNotEmpty) ...[
                  const SizedBox(height: 3),
                  Text('Capabilities: $services', style: TextStyle(color: Colors.grey.shade600, fontSize: 10, fontStyle: FontStyle.italic)),
                ],
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.phone, color: Color(0xFF10B981)),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Dialing $name ($phone)...'),
                  backgroundColor: const Color(0xFF10B981),
                  duration: const Duration(seconds: 2),
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}