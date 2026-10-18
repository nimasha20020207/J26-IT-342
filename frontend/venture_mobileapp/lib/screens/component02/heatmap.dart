import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import '../../models/component02/hazard_data.dart';
import '../../services/api_service.dart';
import 'temporal_trends.dart';

class Screen4Heatmap extends StatefulWidget {
  const Screen4Heatmap({super.key, required this.forecast, this.apiService});

  final ForecastData forecast;
  final ApiService? apiService;

  @override
  State<Screen4Heatmap> createState() => _Screen4HeatmapState();
}

class _Screen4HeatmapState extends State<Screen4Heatmap> {
  late final ApiService _apiService;
  List<HeatZoneItem> _heatZones = [];
  bool _isLoading = true;
  HeatZoneItem? _selectedZone;

  // Trail Coordinates Catalog
  static const Map<String, LatLng> _trailCoords = {
    'Pidurangala': LatLng(7.9662, 80.7617),
    'Sigiriya': LatLng(7.9567, 80.7599),
    'Alagalla': LatLng(7.2980, 80.4716),
    'Narangala': LatLng(7.0367, 81.0087),
    'Hanthana': LatLng(7.2535, 80.6280),
    'Lakegala': LatLng(7.4661, 80.8394),
    'Manigala': LatLng(7.5202, 80.7671),
    'Kirigalpoththa': LatLng(6.7990, 80.7664),
    "Little Adam's peak": LatLng(6.8651, 81.0630),
    'Pettigala': LatLng(7.2863, 80.7598),
    'Peacock hills': LatLng(7.0853, 80.6327),
    'Thotupala kanda': LatLng(6.8331, 80.8198),
    'Bathalegala': LatLng(7.1901, 80.4339),
    "Adam's peak": LatLng(6.8094, 80.4994),
    'Ella rock': LatLng(6.8536, 81.0450),
  };

  @override
  void initState() {
    super.initState();
    _apiService = widget.apiService ?? ApiService();
    _loadHeatZones();
  }

  Future<void> _loadHeatZones() async {
    try {
      final zones = await _apiService.getHeatZones();
      if (!mounted) return;
      setState(() {
        _heatZones = zones;
        _isLoading = false;
        // Select active forecast trail if found
        _selectedZone = zones.firstWhere(
          (z) => z.trailName.toLowerCase() == widget.forecast.trailName.toLowerCase(),
          orElse: () => zones.isNotEmpty ? zones.first : _fallbackActiveZone(),
        );
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _heatZones = _generateFallbackHeatZones();
        _selectedZone = _fallbackActiveZone();
        _isLoading = false;
      });
    }
  }

  HeatZoneItem _fallbackActiveZone() {
    final coords = _trailCoords[widget.forecast.trailName] ?? const LatLng(7.8731, 80.7718);
    return HeatZoneItem(
      trailName: widget.forecast.trailName,
      latitude: coords.latitude,
      longitude: coords.longitude,
      predictedHazard: widget.forecast.hazards.isNotEmpty ? widget.forecast.hazards.first.name : 'Environmental Hazard',
      hazardProbability: widget.forecast.hazards.isNotEmpty ? widget.forecast.hazards.first.probability : 0.60,
      predictedRiskScore: widget.forecast.overallRiskScore.toDouble(),
      riskLevel: widget.forecast.riskLevel,
      rainfall24hMm: widget.forecast.weather.precipitationMm,
      windGustKmh: widget.forecast.weather.windGustKmh,
      meanSocialReliability: 0.88,
    );
  }

  List<HeatZoneItem> _generateFallbackHeatZones() {
    return _trailCoords.entries.map((e) {
      final isCurrent = e.key.toLowerCase() == widget.forecast.trailName.toLowerCase();
      final score = isCurrent ? widget.forecast.overallRiskScore.toDouble() : 25.0;
      final level = score >= 50 ? 'High' : (score >= 25 ? 'Medium' : 'Low');
      return HeatZoneItem(
        trailName: e.key,
        latitude: e.value.latitude,
        longitude: e.value.longitude,
        predictedHazard: isCurrent ? (widget.forecast.hazards.firstOrNull?.name ?? 'Slippery trail') : 'Normal condition',
        hazardProbability: 0.5,
        predictedRiskScore: score,
        riskLevel: level,
        rainfall24hMm: 5.0,
        windGustKmh: 18.0,
        meanSocialReliability: 0.85,
      );
    }).toList();
  }

  Color _getRiskColor(String riskLevel) {
    switch (riskLevel.toLowerCase()) {
      case 'very high':
      case 'high':
        return const Color(0xFFEF4444);
      case 'medium':
        return const Color(0xFFF59E0B);
      default:
        return const Color(0xFF1BB98D);
    }
  }

  @override
  Widget build(BuildContext context) {
    final activeCoords = _trailCoords[widget.forecast.trailName] ?? const LatLng(7.8731, 80.7718);

    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF0B5563),
        foregroundColor: Colors.white,
        title: const Text('Environmental Risk Heatmap', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              setState(() => _isLoading = true);
              _loadHeatZones();
            },
          ),
        ],
      ),
      body: Stack(
        children: [
          // Interactive OpenStreetMap Layer
          FlutterMap(
            options: MapOptions(
              initialCenter: activeCoords,
              initialZoom: 9.5,
              minZoom: 6.0,
              maxZoom: 16.0,
            ),
            children: [
              TileLayer(
                urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                userAgentPackageName: 'com.example.venture_mobileapp',
              ),
              // Heat Zone Trail Markers
              MarkerLayer(
                markers: _heatZones.map((zone) {
                  final color = _getRiskColor(zone.riskLevel);
                  final isSelected = _selectedZone?.trailName.toLowerCase() == zone.trailName.toLowerCase();

                  return Marker(
                    point: LatLng(zone.latitude, zone.longitude),
                    width: isSelected ? 120 : 44,
                    height: isSelected ? 65 : 44,
                    child: GestureDetector(
                      onTap: () => setState(() => _selectedZone = zone),
                      child: isSelected
                          ? Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                  decoration: BoxDecoration(
                                    color: Colors.white,
                                    borderRadius: BorderRadius.circular(10),
                                    border: Border.all(color: color, width: 2),
                                    boxShadow: const [BoxShadow(color: Colors.black26, blurRadius: 6)],
                                  ),
                                  child: Text(
                                    '${zone.trailName} (${zone.predictedRiskScore.toInt()})',
                                    style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: color),
                                  ),
                                ),
                                const SizedBox(height: 2),
                                Icon(Icons.location_on, color: color, size: 28),
                              ],
                            )
                          : Container(
                              decoration: BoxDecoration(
                                color: color.withValues(alpha: 0.25),
                                shape: BoxShape.circle,
                              ),
                              child: Center(
                                child: Container(
                                  width: 22,
                                  height: 22,
                                  decoration: BoxDecoration(
                                    color: color,
                                    shape: BoxShape.circle,
                                    border: Border.all(color: Colors.white, width: 2),
                                    boxShadow: const [BoxShadow(color: Colors.black26, blurRadius: 4)],
                                  ),
                                ),
                              ),
                            ),
                    ),
                  );
                }).toList(),
              ),
            ],
          ),

          // Loading overlay
          if (_isLoading)
            Positioned(
              top: 16,
              left: 16,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 4)],
                ),
                child: const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF0B5563))),
                    SizedBox(width: 8),
                    Text('Updating live heat zones...', style: TextStyle(fontSize: 11, color: Color(0xFF0B5563))),
                  ],
                ),
              ),
            ),

          // Selected Trail Detail Card & Legend
          Positioned(
            bottom: 16,
            left: 16,
            right: 16,
            child: Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 10, offset: Offset(0, 4))],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  // Trail Risk Header
                  if (_selectedZone != null) ...[
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                _selectedZone!.trailName,
                                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Color(0xFF0B5563)),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                'Hazard: ${_selectedZone!.predictedHazard} · Risk ${_selectedZone!.predictedRiskScore.toInt()}/100',
                                style: TextStyle(fontSize: 12, color: Colors.grey.shade700),
                              ),
                            ],
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: _getRiskColor(_selectedZone!.riskLevel),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            '${_selectedZone!.riskLevel} Risk',
                            style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 11),
                          ),
                        ),
                      ],
                    ),
                    const Divider(height: 20),
                  ],

                  // Legend
                  const Text('Spatial Risk Legend', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF0B5563))),
                  const SizedBox(height: 8),
                  const Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      _LegendItem(color: Color(0xFFEF4444), label: 'High-risk zone'),
                      _LegendItem(color: Color(0xFFF59E0B), label: 'Medium-risk'),
                      _LegendItem(color: Color(0xFF1BB98D), label: 'Safe area'),
                    ],
                  ),
                  const SizedBox(height: 14),

                  // Button to Temporal Trends
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF1BB98D),
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        padding: const EdgeInsets.symmetric(vertical: 12),
                      ),
                      onPressed: () => Navigator.push(
                        context,
                        MaterialPageRoute(builder: (context) => Screen5TemporalTrends(forecast: widget.forecast)),
                      ),
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