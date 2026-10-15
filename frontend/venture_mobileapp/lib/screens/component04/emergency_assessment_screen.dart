import 'package:flutter/material.dart';
import 'context_analysis_screen.dart';

class EmergencyAssessmentScreen extends StatelessWidget {
  const EmergencyAssessmentScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Emergency Assessment')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Category & Urgency Cards
            Card(
              color: Colors.white,
              elevation: 2,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Detected Category', style: TextStyle(color: Colors.grey, fontSize: 12)),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(color: Colors.red.shade100, borderRadius: BorderRadius.circular(4)),
                          child: const Text('URGENT', style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold, fontSize: 11)),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    const Text('Lower Limb Trauma (Severe Sprain / Fracture Risk)', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                    const Divider(height: 24),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Severity Score: 8.5 / 10', style: TextStyle(fontWeight: FontWeight.w600)),
                        const Text('Confidence: 94.2%', style: TextStyle(color: Color(0xFF10B981), fontWeight: FontWeight.bold)),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            const Text('Evaluated Risk Factors', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            
            // Risk Cards Grid / List
            const Row(
              children: [
                Expanded(child: _RiskCard(title: 'Weather Impact', level: 'High Rain / Wind', color: Colors.orange)),
                SizedBox(width: 10),
                Expanded(child: _RiskCard(title: 'Terrain Impact', level: 'Steep / Rocky Ridge', color: Colors.red)),
              ],
            ),
            const SizedBox(height: 10),
            const Row(
              children: [
                Expanded(child: _RiskCard(title: 'Environmental Hazard', level: 'Slippery Trail Path', color: Colors.orange)),
                SizedBox(width: 10),
                Expanded(child: _RiskCard(title: 'Location Risk', level: 'Remote / Low Signal', color: Colors.red)),
              ],
            ),
            const SizedBox(height: 24),

            // Next button
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
                    MaterialPageRoute(builder: (context) => const ContextAnalysisScreen()),
                  );
                },
                child: const Text('View Context Analysis', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _RiskCard extends StatelessWidget {
  final String title;
  final String level;
  final Color color;

  const _RiskCard({required this.title, required this.level, required this.color});

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
        children: [
          Text(title, style: const TextStyle(fontSize: 12, color: Colors.grey)),
          const SizedBox(height: 6),
          Text(level, style: TextStyle(fontWeight: FontWeight.bold, color: color, fontSize: 13)),
        ],
      ),
    );
  }
}