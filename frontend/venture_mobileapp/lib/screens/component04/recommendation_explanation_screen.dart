import 'package:flutter/material.dart';
import '../../models/emergency_models.dart';
import 'emergency_summary_screen.dart';

class RecommendationExplanationScreen extends StatelessWidget {
  final FullEmergencyResponseModel response;

  const RecommendationExplanationScreen({super.key, required this.response});

  @override
  Widget build(BuildContext context) {
    final xai = response.explainability;
    final factors = xai.topContributingFactors;
    final narratives = xai.explanatoryNarrative;
    final reasoningPaths = response.reasoningPaths;

    return Scaffold(
      appBar: AppBar(title: const Text('Explainable AI (XAI) Insights')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Why was this recommendation generated?',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
            ),
            const SizedBox(height: 4),
            Text(
              'Interpretable AI using ${xai.interpretabilityFramework}',
              style: const TextStyle(color: Colors.grey, fontSize: 12),
            ),
            const SizedBox(height: 16),

            // SHAP Feature Impact Bars Card
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: Colors.grey.shade300),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'SHAP Factor Importance Attribution',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF10B981)),
                      ),
                      Text('Impact %', style: TextStyle(fontSize: 11, color: Colors.grey, fontWeight: FontWeight.bold)),
                    ],
                  ),
                  const SizedBox(height: 12),
                  if (factors.isEmpty)
                    const Text('Factor data unavailable.')
                  else
                    ...factors.map((f) => Padding(
                      padding: const EdgeInsets.only(bottom: 10),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(f.factor, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
                              Text('${f.impactPercentage}%', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF10B981))),
                            ],
                          ),
                          const SizedBox(height: 4),
                          LinearProgressIndicator(
                            value: (f.impactPercentage / 100).clamp(0.0, 1.0),
                            backgroundColor: Colors.grey.shade200,
                            color: const Color(0xFF10B981),
                            minHeight: 6,
                            borderRadius: BorderRadius.circular(4),
                          ),
                        ],
                      ),
                    )),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Explanatory Narrative
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: Colors.grey.shade300),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Contextual Explanation & Findings',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF10B981)),
                  ),
                  const SizedBox(height: 8),
                  if (narratives.isEmpty)
                    const Text('No narrative available.')
                  else
                    ...narratives.map((n) => Padding(
                      padding: const EdgeInsets.only(bottom: 6),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('• ', style: TextStyle(color: Color(0xFF10B981), fontWeight: FontWeight.bold, fontSize: 14)),
                          Expanded(
                            child: Text(n, style: const TextStyle(fontSize: 12, color: Color(0xFF334155), height: 1.3)),
                          ),
                        ],
                      ),
                    )),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Knowledge Graph Reasoning Flow Card
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: Colors.grey.shade300),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Knowledge Graph Reasoning Traversal Path',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF10B981)),
                  ),
                  const SizedBox(height: 8),
                  if (reasoningPaths.isEmpty)
                    const Text('No traversal paths recorded.')
                  else
                    ...reasoningPaths.map((p) => Container(
                      margin: const EdgeInsets.only(bottom: 6),
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                      decoration: BoxDecoration(
                        color: Colors.grey.shade50,
                        borderRadius: BorderRadius.circular(6),
                        border: Border.all(color: Colors.grey.shade200),
                      ),
                      child: Text(
                        p,
                        style: const TextStyle(fontSize: 11, fontFamily: 'monospace', color: Color(0xFF1E293B)),
                      ),
                    )),
                ],
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
                    MaterialPageRoute(
                      builder: (context) => EmergencySummaryScreen(response: response),
                    ),
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