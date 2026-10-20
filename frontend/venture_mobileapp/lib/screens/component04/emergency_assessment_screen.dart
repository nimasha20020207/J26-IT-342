import 'package:flutter/material.dart';
import '../../models/emergency_models.dart';
import 'context_analysis_screen.dart';

class EmergencyAssessmentScreen extends StatelessWidget {
  final FullEmergencyResponseModel response;

  const EmergencyAssessmentScreen({super.key, required this.response});

  @override
  Widget build(BuildContext context) {
    final assessment = response.assessment;
    final isCritical = assessment.severityLevel >= 4;

    return Scaffold(
      appBar: AppBar(title: const Text('Emergency Assessment')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Category & Urgency Card
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
                        const Text('Detected Category (AI Fused)', style: TextStyle(color: Colors.grey, fontSize: 12)),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: isCritical ? Colors.red.shade100 : Colors.orange.shade100,
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            assessment.urgency,
                            style: TextStyle(
                              color: isCritical ? Colors.red.shade800 : Colors.orange.shade800,
                              fontWeight: FontWeight.bold,
                              fontSize: 11,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(
                      assessment.displayTitle,
                      style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
                    ),
                    const Divider(height: 24),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Severity Score: ${assessment.severityLevel} / 5',
                          style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
                        ),
                        Text(
                          'Confidence: ${assessment.confidencePct}%',
                          style: const TextStyle(color: Color(0xFF10B981), fontWeight: FontWeight.bold, fontSize: 14),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            const Text('Evaluated Contextual Risk Factors', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),

            // Dynamic Active Hazards from Knowledge Graph
            Row(
              children: [
                Expanded(
                  child: _RiskCard(
                    title: 'Active Hazards Detected',
                    level: response.activeHazards.isNotEmpty
                        ? response.activeHazards.map((h) => h.replaceAll('_', ' ')).join(', ')
                        : 'Standard Trail Hazard',
                    color: Colors.red,
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: _RiskCard(
                    title: 'Weather Impact',
                    level: response.contextSummary.weather,
                    color: Colors.orange,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                Expanded(
                  child: _RiskCard(
                    title: 'Terrain Profile',
                    level: response.contextSummary.terrain,
                    color: Colors.deepOrange,
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: _RiskCard(
                    title: 'Remote Isolation',
                    level: response.contextSummary.remoteArea ? 'High Wilderness Risk' : 'Standard Cell Zone',
                    color: response.contextSummary.remoteArea ? Colors.red : const Color(0xFF10B981),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Next button: Context Analysis
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
                      builder: (context) => ContextAnalysisScreen(response: response),
                    ),
                  );
                },
                child: const Text('View Context Analysis Dashboard', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
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
          Text(title, style: const TextStyle(fontSize: 11, color: Colors.grey)),
          const SizedBox(height: 6),
          Text(
            level,
            style: TextStyle(fontWeight: FontWeight.bold, color: color, fontSize: 12),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}