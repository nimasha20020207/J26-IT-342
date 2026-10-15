import 'package:flutter/material.dart';
import 'emergency_analysis_screen.dart';

class EmergencyReportScreen extends StatefulWidget {
  const EmergencyReportScreen({super.key});

  @override
  State<EmergencyReportScreen> createState() => _EmergencyReportScreenState();
}

class _EmergencyReportScreenState extends State<EmergencyReportScreen> {
  String? _selectedEmergencyType = 'Injury / Physical Trauma';
  String? _selectedTerrain = 'Steep Mountain Ridge';
  String? _selectedSeverity = 'High (Critical / Severe Trauma)';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {},
        ),
        title: const Text('Emergency Report'),
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
            const SizedBox(height: 16),
            
            // Emergency Type Dropdown
            const Text('Emergency Type', style: TextStyle(fontWeight: FontWeight.w600)),
            const SizedBox(height: 6),
            DropdownButtonFormField<String>(
              initialValue: _selectedEmergencyType,
              decoration: _inputDecoration(),
              items: ['Injury / Physical Trauma', 'Lost Hiker / Disoriented', 'Severe Weather / Landslide', 'Extreme Fatigue / Dehydration']
                  .map((type) => DropdownMenuItem(value: type, child: Text(type)))
                  .toList(),
              onChanged: (val) => setState(() => _selectedEmergencyType = val),
            ),
            const SizedBox(height: 16),

            // Description Text Area
            const Text('Emergency Description', style: TextStyle(fontWeight: FontWeight.w600)),
            const SizedBox(height: 6),
            TextField(
              maxLines: 4,
              decoration: _inputDecoration().copyWith(hintText: 'Describe what happened and symptoms...'),
            ),
            const SizedBox(height: 16),

            // Current GPS Location Field
            const Text('Current GPS Location', style: TextStyle(fontWeight: FontWeight.w600)),
            const SizedBox(height: 6),
            TextField(
              readOnly: true,
              decoration: _inputDecoration().copyWith(
                hintText: '7.3148° N, 80.6358° E (Nuwara Eliya Trail)',
                suffixIcon: const Icon(Icons.gps_fixed, color: Color(0xFF10B981)),
              ),
            ),
            const SizedBox(height: 16),

            // Terrain Condition Selector
            const Text('Terrain Condition', style: TextStyle(fontWeight: FontWeight.w600)),
            const SizedBox(height: 6),
            DropdownButtonFormField<String>(
              initialValue: _selectedTerrain,
              decoration: _inputDecoration(),
              items: ['Steep Mountain Ridge', 'Dense Forest / Canopy', 'Rocky Slopes / Loose Scree', 'Wet / Slippery Waterfall Path']
                  .map((terrain) => DropdownMenuItem(value: terrain, child: Text(terrain)))
                  .toList(),
              onChanged: (val) => setState(() => _selectedTerrain = val),
            ),
            const SizedBox(height: 16),

            // Injury Severity Selector
            const Text('Injury Severity', style: TextStyle(fontWeight: FontWeight.w600)),
            const SizedBox(height: 6),
            DropdownButtonFormField<String>(
              initialValue: _selectedSeverity,
              decoration: _inputDecoration(),
              items: ['Low (Minor Scratch/Fatigue)', 'Moderate (Sprain/Unable to walk)', 'High (Critical / Severe Trauma)']
                  .map((sev) => DropdownMenuItem(value: sev, child: Text(sev)))
                  .toList(),
              onChanged: (val) => setState(() => _selectedSeverity = val),
            ),
            const SizedBox(height: 16),

            // Photo Upload Placeholder
            const Text('Evidence / Injury Photo', style: TextStyle(fontWeight: FontWeight.w600)),
            const SizedBox(height: 6),
            Container(
              height: 100,
              width: double.infinity,
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey.shade400),
                borderRadius: BorderRadius.circular(8),
                color: Colors.grey.shade100,
              ),
              child: const Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.camera_alt, size: 36, color: Colors.grey),
                  SizedBox(height: 4),
                  Text('Tap to capture or upload photo placeholder', style: TextStyle(color: Colors.grey)),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Analyze Emergency Button
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
                    MaterialPageRoute(builder: (context) => const EmergencyAnalysisScreen()),
                  );
                },
                child: const Text('Analyze Emergency', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
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