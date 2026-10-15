import 'package:flutter/material.dart';
import 'emergency_resources_screen.dart';

class RecommendedResponseScreen extends StatelessWidget {
  const RecommendedResponseScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Recommended Response')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('AI & Knowledge Graph Recommendations', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            const _RecommendationCard(
              title: '1. Seek Medical Assistance & Splint Limb',
              priority: 'Priority: High (1)',
              urgency: 'Urgency: Immediate Action',
              effectiveness: 'Expected Effectiveness: 96%',
              isPrimary: true,
            ),
            const SizedBox(height: 10),
            const _RecommendationCard(
              title: '2. Contact Rescue Services / Park Ranger',
              priority: 'Priority: High (2)',
              urgency: 'Urgency: Within 15 Mins',
              effectiveness: 'Expected Effectiveness: 91%',
              isPrimary: false,
            ),
            const SizedBox(height: 10),
            const _RecommendationCard(
              title: '3. Move to Safe Sheltered Area Nearby',
              priority: 'Priority: Medium (3)',
              urgency: 'Urgency: If Able',
              effectiveness: 'Expected Effectiveness: 78%',
              isPrimary: false,
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
                    MaterialPageRoute(builder: (context) => const EmergencyResourcesScreen()),
                  );
                },
                child: const Text('View Nearby Resources', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _RecommendationCard extends StatelessWidget {
  final String title;
  final String priority;
  final String urgency;
  final String effectiveness;
  final bool isPrimary;

  const _RecommendationCard({
    required this.title,
    required this.priority,
    required this.urgency,
    required this.effectiveness,
    required this.isPrimary,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: isPrimary ? const Color(0xFF10B981) : Colors.grey.shade300, width: isPrimary ? 2 : 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(priority, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: Color(0xFF10B981))),
              Text(effectiveness, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Colors.grey)),
            ],
          ),
          const SizedBox(height: 6),
          Text(title, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
          const SizedBox(height: 6),
          Text(urgency, style: const TextStyle(color: Colors.red, fontSize: 12, fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }
}