import 'package:flutter/material.dart';
import 'emergency_assessment_screen.dart';

class EmergencyAnalysisScreen extends StatefulWidget {
  const EmergencyAnalysisScreen({super.key});

  @override
  State<EmergencyAnalysisScreen> createState() => _EmergencyAnalysisScreenState();
}

class _EmergencyAnalysisScreenState extends State<EmergencyAnalysisScreen> {
  @override
  void initState() {
    super.initState();
    // Simulate auto-navigation after brief AI loading simulation
    Future.delayed(const Duration(seconds: 3), () {
      if (mounted) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => const EmergencyAssessmentScreen()),
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('AI Emergency Processing')),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            const SizedBox(height: 20),
            const CircularProgressIndicator(color: Color(0xFF10B981), strokeWidth: 4),
            const SizedBox(height: 20),
            const Text(
              'Running Multimodal AI & Knowledge Graph...',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
            ),
            const Text(
              'Synthesizing incident report, GPS, weather, and terrain context.',
              style: TextStyle(color: Colors.grey, fontSize: 13),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 30),
            Expanded(
              child: ListView(
                children: const [
                  _AnalysisStepTile(title: 'Information Extraction (NLP)', status: 'Completed', isDone: true),
                  _AnalysisStepTile(title: 'Emergency Classification', status: 'Completed (Injury / Trauma)', isDone: true),
                  _AnalysisStepTile(title: 'Severity Estimation Model', status: 'Completed (High Urgency)', isDone: true),
                  _AnalysisStepTile(title: 'Context Integration (Weather & Terrain)', status: 'Completed', isDone: true),
                  _AnalysisStepTile(title: 'Knowledge Graph Reasoning', status: 'Processing nodes & rescue actions...', isDone: false),
                  _AnalysisStepTile(title: 'Recommendation Generation', status: 'Pending...', isDone: false),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _AnalysisStepTile extends StatelessWidget {
  final String title;
  final String status;
  final bool isDone;

  const _AnalysisStepTile({required this.title, required this.status, required this.isDone});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: isDone ? const Color(0xFF10B981).withValues(alpha: 0.5) : Colors.grey.shade300),
      ),
      child: Row(
        children: [
          Icon(
            isDone ? Icons.check_circle : Icons.hourglass_top,
            color: isDone ? const Color(0xFF10B981) : Colors.orange,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
                Text(status, style: TextStyle(color: Colors.grey.shade600, fontSize: 12)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}