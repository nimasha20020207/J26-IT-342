import 'package:flutter/material.dart';
import '../../models/emergency_models.dart';
import '../../services/api_service.dart';
import 'emergency_assessment_screen.dart';

class EmergencyAnalysisScreen extends StatefulWidget {
  final IncidentInputModel input;

  const EmergencyAnalysisScreen({super.key, required this.input});

  @override
  State<EmergencyAnalysisScreen> createState() => _EmergencyAnalysisScreenState();
}

class _EmergencyAnalysisScreenState extends State<EmergencyAnalysisScreen> {
  final EmergencyApiService _apiService = EmergencyApiService();
  int _activeStep = 0;
  String? _errorMessage;

  final List<String> _stepTitles = [
    'Natural Language Processing (NLP extraction)',
    'Emergency Classification (Random Forest & XGBoost)',
    'Severity & Urgency Estimation',
    'Context Integration (Telemetry, Terrain & Weather)',
    'Knowledge Graph Multi-Hop Reasoning',
    'Explainable AI (SHAP Feature Importance & Geo-Resources)',
  ];

  @override
  void initState() {
    super.initState();
    _startLiveAnalysis();
  }

  Future<void> _startLiveAnalysis() async {
    // Step progression animation timer
    for (int i = 0; i < _stepTitles.length - 1; i++) {
      await Future.delayed(const Duration(milliseconds: 350));
      if (!mounted) return;
      setState(() {
        _activeStep = i + 1;
      });
    }

    try {
      final response = await _apiService.analyzeEmergency(widget.input);
      if (!mounted) return;
      setState(() {
        _activeStep = _stepTitles.length;
      });

      await Future.delayed(const Duration(milliseconds: 400));
      if (!mounted) return;

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => EmergencyAssessmentScreen(response: response),
        ),
      );
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _errorMessage = 'Analysis error: $e';
      });
    }
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
            const SizedBox(height: 10),
            const CircularProgressIndicator(color: Color(0xFF10B981), strokeWidth: 4),
            const SizedBox(height: 20),
            const Text(
              'Running Multimodal AI & Knowledge Graph...',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
            ),
            const SizedBox(height: 4),
            const Text(
              'Synthesizing incident text, telemetry, weather, terrain, and domain graph.',
              style: TextStyle(color: Colors.grey, fontSize: 13),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),

            if (_errorMessage != null)
              Container(
                padding: const EdgeInsets.all(12),
                margin: const EdgeInsets.only(bottom: 16),
                decoration: BoxDecoration(
                  color: Colors.red.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.red.shade200),
                ),
                child: Text(_errorMessage!, style: const TextStyle(color: Colors.red, fontSize: 13)),
              ),

            Expanded(
              child: ListView.builder(
                itemCount: _stepTitles.length,
                itemBuilder: (context, index) {
                  final isDone = index < _activeStep;
                  final isCurrent = index == _activeStep;
                  return Container(
                    margin: const EdgeInsets.only(bottom: 10),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: isDone
                            ? const Color(0xFF10B981).withValues(alpha: 0.5)
                            : (isCurrent ? Colors.orange : Colors.grey.shade300),
                      ),
                    ),
                    child: Row(
                      children: [
                        Icon(
                          isDone
                              ? Icons.check_circle
                              : (isCurrent ? Icons.sync : Icons.radio_button_unchecked),
                          color: isDone
                              ? const Color(0xFF10B981)
                              : (isCurrent ? Colors.orange : Colors.grey),
                          size: 20,
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            _stepTitles[index],
                            style: TextStyle(
                              fontWeight: isCurrent || isDone ? FontWeight.bold : FontWeight.normal,
                              color: isCurrent || isDone ? const Color(0xFF1E293B) : Colors.grey,
                              fontSize: 13,
                            ),
                          ),
                        ),
                        Text(
                          isDone ? 'Completed' : (isCurrent ? 'Processing...' : 'Pending'),
                          style: TextStyle(
                            fontSize: 11,
                            color: isDone ? const Color(0xFF10B981) : Colors.grey,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}