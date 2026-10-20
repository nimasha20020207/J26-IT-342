import 'package:flutter/material.dart';
import '../../models/emergency_models.dart';
import 'emergency_analysis_screen.dart';

class EmergencyReportScreen extends StatefulWidget {
  const EmergencyReportScreen({super.key});

  @override
  State<EmergencyReportScreen> createState() => _EmergencyReportScreenState();
}

class _EmergencyReportScreenState extends State<EmergencyReportScreen> {
  final TextEditingController _descriptionController = TextEditingController(
    text: 'A hiker slipped on steep wet rocks near the cliff edge, suffering a severe ankle injury and unable to walk. Heavy mist and rainfall.',
  );

  String _selectedEmergencyType = 'Injury / Physical Trauma';
  String _selectedTerrain = 'rocky';
  String _selectedTrail = 'Horton_Plains';
  double _severitySlider = 4.0;
  double _rainfallMm = 35.0;
  double _phoneBatteryPct = 20.0;
  int _fatigueScore = 7;
  final double _lat = 6.8096;
  final double _lon = 80.8028;

  @override
  void dispose() {
    _descriptionController.dispose();
    super.dispose();
  }

  void _submitEmergencyReport() {
    final input = IncidentInputModel(
      incidentText: _descriptionController.text.trim(),
      latitude: _lat,
      longitude: _lon,
      trailName: _selectedTrail,
      elevationM: _selectedTrail == 'Horton_Plains' ? 2100.0 : 1200.0,
      slopeDegrees: _selectedTerrain == 'steep' ? 35.0 : 25.0,
      rainfallMm: _rainfallMm,
      temperatureC: 17.5,
      windSpeedKmh: 20.0,
      visibilityPct: 25.0,
      hoursHiking: 5.0,
      distanceFromTrailheadKm: 5.8,
      phoneBatteryPct: _phoneBatteryPct,
      fatigueScore1to10: _fatigueScore,
      waterRemainingL: 0.4,
      remoteArea: 1,
      terrainType: _selectedTerrain,
    );

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => EmergencyAnalysisScreen(input: input),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Emergency Report - Venture Safety'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Report an Emergency Situation',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
            ),
            const SizedBox(height: 4),
            const Text(
              'Provide details to trigger multimodal AI classification & response recommendations.',
              style: TextStyle(color: Colors.grey, fontSize: 13),
            ),
            const SizedBox(height: 16),

            // Emergency Type Dropdown
            const Text('Emergency Category', style: TextStyle(fontWeight: FontWeight.w600)),
            const SizedBox(height: 6),
            DropdownButtonFormField<String>(
              initialValue: _selectedEmergencyType,
              decoration: _inputDecoration(),
              items: [
                'Injury / Physical Trauma',
                'Lost Hiker / Disoriented',
                'Severe Weather / Landslide',
                'Flash Flooding / Fast Water',
                'Extreme Fatigue / Dehydration',
                'Wildlife Encounter'
              ].map((type) => DropdownMenuItem(value: type, child: Text(type))).toList(),
              onChanged: (val) => setState(() => _selectedEmergencyType = val!),
            ),
            const SizedBox(height: 16),

            // Description Text Area
            const Text('Emergency Description (NLP Analysis)', style: TextStyle(fontWeight: FontWeight.w600)),
            const SizedBox(height: 6),
            TextField(
              controller: _descriptionController,
              maxLines: 4,
              decoration: _inputDecoration().copyWith(
                hintText: 'Describe symptoms, injuries, weather conditions, hazards...',
              ),
            ),
            const SizedBox(height: 16),

            // Location & Trail Info
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Hiking Trail Area', style: TextStyle(fontWeight: FontWeight.w600)),
                      const SizedBox(height: 6),
                      DropdownButtonFormField<String>(
                        initialValue: _selectedTrail,
                        decoration: _inputDecoration(),
                        items: [
                          'Horton_Plains', 'Knuckles', 'Adam_Peak',
                          'Ella_Rock', 'Sinharaja', 'Riverston', 'Pidurangala'
                        ].map((t) => DropdownMenuItem(value: t, child: Text(t.replaceAll('_', ' ')))).toList(),
                        onChanged: (val) => setState(() => _selectedTrail = val!),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Terrain Condition', style: TextStyle(fontWeight: FontWeight.w600)),
                      const SizedBox(height: 6),
                      DropdownButtonFormField<String>(
                        initialValue: _selectedTerrain,
                        decoration: _inputDecoration(),
                        items: ['rocky', 'steep', 'forest', 'ridge', 'grassland']
                            .map((t) => DropdownMenuItem(value: t, child: Text(t.toUpperCase()))).toList(),
                        onChanged: (val) => setState(() => _selectedTerrain = val!),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Current GPS Location Field
            const Text('Current GPS Telemetry', style: TextStyle(fontWeight: FontWeight.w600)),
            const SizedBox(height: 6),
            TextField(
              readOnly: true,
              decoration: _inputDecoration().copyWith(
                hintText: '$_lat° N, $_lon° E (World’s End, Central Highlands)',
                suffixIcon: const Icon(Icons.gps_fixed, color: Color(0xFF10B981)),
              ),
            ),
            const SizedBox(height: 16),

            // Telemetry Sliders: Rainfall & Battery
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Rainfall: ${_rainfallMm.toInt()} mm', style: const TextStyle(fontWeight: FontWeight.w600)),
                      Slider(
                        value: _rainfallMm,
                        min: 0,
                        max: 80,
                        activeColor: const Color(0xFF10B981),
                        onChanged: (v) => setState(() => _rainfallMm = v),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Battery: ${_phoneBatteryPct.toInt()}%', style: const TextStyle(fontWeight: FontWeight.w600)),
                      Slider(
                        value: _phoneBatteryPct,
                        min: 5,
                        max: 100,
                        activeColor: _phoneBatteryPct < 20 ? Colors.red : const Color(0xFF10B981),
                        onChanged: (v) => setState(() => _phoneBatteryPct = v),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Initial Severity Estimation
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Perceived Severity Urgency (1 - 5):', style: TextStyle(fontWeight: FontWeight.w600)),
                Text(
                  _severitySlider >= 4 ? 'HIGH / CRITICAL' : (_severitySlider == 3 ? 'MODERATE' : 'LOW'),
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: _severitySlider >= 4 ? Colors.red : Colors.orange,
                  ),
                ),
              ],
            ),
            Slider(
              value: _severitySlider,
              min: 1,
              max: 5,
              divisions: 4,
              label: '${_severitySlider.toInt()}',
              activeColor: _severitySlider >= 4 ? Colors.red : const Color(0xFF10B981),
              onChanged: (v) => setState(() => _severitySlider = v),
            ),
            const SizedBox(height: 20),

            // Submit Button
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton.icon(
                icon: const Icon(Icons.analytics_outlined),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF10B981),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                onPressed: _submitEmergencyReport,
                label: const Text('Analyze Emergency with AI', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  InputDecoration _inputDecoration() {
    return InputDecoration(
      filled: true,
      fillColor: Colors.white,
      contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: Colors.grey.shade300)),
      enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: Colors.grey.shade300)),
    );
  }
}