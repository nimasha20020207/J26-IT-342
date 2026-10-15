import 'package:flutter/material.dart';
import 'temporal_trends.dart';

class Screen4Heatmap extends StatelessWidget {
  const Screen4Heatmap({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF0B5563),
        foregroundColor: Colors.white,
        title: const Text('Environmental Risk Heatmap', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
      ),
      body: Stack(
        children: [
          // Map Background Placeholder
          Container(
            color: const Color(0xFFE2E8F0),
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.map, size: 80, color: Colors.grey.shade400),
                  const SizedBox(height: 12),
                  Text('Horton Plains Topographical GIS Heatmap', style: TextStyle(color: Colors.grey.shade600, fontWeight: FontWeight.w600)),
                ],
              ),
            ),
          ),
          // Simulated Heatmap Overlays
          Positioned(
            top: 120,
            left: 80,
            child: _HeatmapMarker(color: const Color(0xFFEF4444), label: 'High Risk: World\'s End Cliff (Fog/Leaches)'),
          ),
          Positioned(
            bottom: 220,
            right: 60,
            child: _HeatmapMarker(color: const Color(0xFFF59E0B), label: 'Medium Risk: Baker\'s Falls (Slippery)'),
          ),
          Positioned(
            top: 250,
            left: 140,
            child: _HeatmapMarker(color: const Color(0xFF1BB98D), label: 'Safe Area: Park Entrance'),
          ),
          // Map Legend & Bottom Sheet
          Positioned(
            bottom: 16,
            left: 16,
            right: 16,
            child: Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.1), blurRadius: 10, offset: const Offset(0, 4))],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text('Spatial Risk Legend', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Color(0xFF0B5563))),
                  const SizedBox(height: 12),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: const [
                      _LegendItem(color: Color(0xFFEF4444), label: 'High-risk zone'),
                      _LegendItem(color: Color(0xFFF59E0B), label: 'Medium-risk'),
                      _LegendItem(color: Color(0xFF1BB98D), label: 'Safe area'),
                    ],
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF1BB98D),
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                      onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (context) => const Screen5TemporalTrends())),
                      child: const Text('View Temporal Risk Trends', style: TextStyle(fontWeight: FontWeight.bold)),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _HeatmapMarker extends StatelessWidget {
  final Color color;
  final String label;
  const _HeatmapMarker({required this.color, required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color, width: 2),
        boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 4)],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(width: 8, height: 8, decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
          const SizedBox(width: 6),
          Text(label, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}

class _LegendItem extends StatelessWidget {
  final Color color;
  final String label;
  const _LegendItem({required this.color, required this.label});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(width: 12, height: 12, decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(3))),
        const SizedBox(width: 6),
        Text(label, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500)),
      ],
    );
  }
}