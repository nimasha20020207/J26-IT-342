import 'package:flutter/material.dart';
import '../../models/emergency_models.dart';

class EmergencySummaryScreen extends StatelessWidget {
  final FullEmergencyResponseModel response;

  const EmergencySummaryScreen({super.key, required this.response});

  @override
  Widget build(BuildContext context) {
    final assessment = response.assessment;
    final primaryAction = response.recommendedActions.isNotEmpty
        ? response.recommendedActions.first.title
        : 'Follow designated trail safety instructions.';
    final nearest = response.nearestResources.isNotEmpty
        ? '${response.nearestResources.first.name} (${response.nearestResources.first.distanceStr})'
        : 'Contact Central DMC Hotline (117)';

    return Scaffold(
      appBar: AppBar(title: const Text('Emergency Response Summary')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Final Incident Overview & Action Plan',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
            ),
            const SizedBox(height: 4),
            const Text(
              'Multimodal emergency synthesis ready for execution & responder dispatch.',
              style: TextStyle(color: Colors.grey, fontSize: 13),
            ),
            const SizedBox(height: 16),

            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: Colors.grey.shade300),
                boxShadow: [
                  BoxShadow(color: Colors.black.withValues(alpha: 0.04), blurRadius: 6, offset: const Offset(0, 2)),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _SummaryRow(label: 'Emergency Category', value: assessment.displayTitle, isBold: true),
                  const Divider(height: 20),
                  _SummaryRow(
                    label: 'Severity / Urgency',
                    value: 'Level ${assessment.severityLevel}/5 • ${assessment.urgency}',
                    valueColor: assessment.severityLevel >= 4 ? Colors.red : Colors.orange,
                    isBold: true,
                  ),
                  const Divider(height: 20),
                  _SummaryRow(label: 'GPS Location', value: response.contextSummary.coordinates),
                  const Divider(height: 20),
                  _SummaryRow(label: 'Nearest Resource', value: nearest, isBold: true),
                  const Divider(height: 20),
                  const Text('Primary Recommended Action:', style: TextStyle(color: Colors.grey, fontSize: 12)),
                  const SizedBox(height: 4),
                  Text(
                    primaryAction,
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Color(0xFF1E293B)),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Action Buttons
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton.icon(
                icon: const Icon(Icons.emergency),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red.shade700,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                onPressed: () {
                  final phone = response.nearestResources.isNotEmpty
                      ? response.nearestResources.first.phone
                      : '119';
                  showDialog(
                    context: context,
                    builder: (ctx) => AlertDialog(
                      title: const Row(
                        children: [
                          Icon(Icons.warning, color: Colors.red),
                          SizedBox(width: 8),
                          Text('Emergency SOS'),
                        ],
                      ),
                      content: Text(
                        'Dispatching automated distress payload and connecting call to $phone (Nearest Responder) and National 119 Hotline.\n\nCoordinates: ${response.contextSummary.coordinates}',
                      ),
                      actions: [
                        TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
                        ElevatedButton(
                          style: ElevatedButton.styleFrom(backgroundColor: Colors.red, foregroundColor: Colors.white),
                          onPressed: () {
                            Navigator.pop(ctx);
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Distress beacon broadcasted to Sri Lanka Emergency Network!'),
                                backgroundColor: Colors.red,
                              ),
                            );
                          },
                          child: const Text('Call Now'),
                        ),
                      ],
                    ),
                  );
                },
                label: const Text('Dispatch SOS & Call Responder', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              ),
            ),
            const SizedBox(height: 12),

            SizedBox(
              width: double.infinity,
              height: 50,
              child: OutlinedButton.icon(
                icon: const Icon(Icons.share),
                style: OutlinedButton.styleFrom(
                  side: const BorderSide(color: Color(0xFF10B981)),
                  foregroundColor: const Color(0xFF10B981),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Incident report for ${assessment.displayTitle} copied to clipboard!'),
                      backgroundColor: const Color(0xFF10B981),
                    ),
                  );
                },
                label: const Text('Share Emergency Details', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
              ),
            ),
            const SizedBox(height: 12),

            SizedBox(
              width: double.infinity,
              height: 48,
              child: TextButton.icon(
                icon: const Icon(Icons.home),
                style: TextButton.styleFrom(foregroundColor: Colors.grey.shade700),
                onPressed: () {
                  Navigator.popUntil(context, (route) => route.isFirst);
                },
                label: const Text('Return to Home / New Report'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SummaryRow extends StatelessWidget {
  final String label;
  final String value;
  final Color? valueColor;
  final bool isBold;

  const _SummaryRow({
    required this.label,
    required this.value,
    this.valueColor,
    this.isBold = false,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 13)),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            value,
            textAlign: TextAlign.end,
            style: TextStyle(
              fontWeight: isBold ? FontWeight.bold : FontWeight.w500,
              color: valueColor ?? const Color(0xFF1E293B),
              fontSize: 13,
            ),
          ),
        ),
      ],
    );
  }
}