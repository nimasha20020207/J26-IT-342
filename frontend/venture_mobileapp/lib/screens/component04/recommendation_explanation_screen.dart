import 'package:flutter/material.dart';
import 'emergency_summary_screen.dart';

class RecommendationExplanationScreen extends StatelessWidget {
  const RecommendationExplanationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Explainable AI (XAI) Insights')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Why was this recommendation generated?', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 10),
            
            // Explanation Panel
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.grey.shade300),
              ),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Decision Factors (SHAP Analysis)', style: TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF10B981))),
                  SizedBox(height: 8),
                  Text('• Severe weather rain factor contributed +42% to urgency rating.'),
                  Text('• Steep rocky terrain profile increased injury classification weight by +35%.'),
                  Text('• Historical incident cluster in sector 4 raised proximity risk score.'),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Chart Placeholders
            Container(
              height: 130,
              width: double.infinity,
              decoration: BoxDecoration(
                color: Colors.grey.shade200,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.grey.shade400),
              ),
              child: const Center(
                child: Text('Feature Importance Chart Placeholder (SHAP Values)', style: TextStyle(color: Colors.grey)),
              ),
            ),
            const SizedBox(height: 16),

            Container(
              height: 130,
              width: double.infinity,
              decoration: BoxDecoration(
                color: Colors.grey.shade200,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.grey.shade400),
              ),
              child: const Center(
                child: Text('Knowledge Graph Reasoning Flow Diagram Placeholder', style: TextStyle(color: Colors.grey)),
              ),
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
                    MaterialPageRoute(builder: (context) => const EmergencySummaryScreen()),
                  );
                },
                child: const Text('Proceed to Emergency Summary', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}