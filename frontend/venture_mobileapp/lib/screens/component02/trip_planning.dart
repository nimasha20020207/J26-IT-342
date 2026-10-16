import 'package:flutter/material.dart';

import 'package:dio/dio.dart';
import '../../models/component02/hazard_data.dart';
import '../../services/api_service.dart';
import 'processing.dart';

class Screen1TripPlanning extends StatefulWidget {
  const Screen1TripPlanning({super.key, this.apiService});

  final ApiService? apiService;

  @override
  State<Screen1TripPlanning> createState() => _Screen1TripPlanningState();
}

class _Screen1TripPlanningState extends State<Screen1TripPlanning> {
  String selectedTrail = 'Pidurangala';
  late DateTime startDate;
  late DateTime endDate;
  late final ApiService _apiService;
  WeatherSummary? _weather;
  bool _isLoadingWeather = true;
  String? _weatherError;
  int _weatherRequestSequence = 0;

  final List<String> trails = [
    'Pidurangala',
    'Sigiriya',
    'Alagalla',
    'Narangala',
    'Hanthana',
    'Lakegala',
    'Manigala',
    'Kirigalpoththa',
    'Little Adam\'s peak',
    'Pettigala',
    'Peacock hills',
    'Thotupala kanda',
    'Bathalegala',
  ];

  DateTime get _today => DateUtils.dateOnly(DateTime.now());
  DateTime get _lastForecastDate => _today.add(const Duration(days: 15));

  @override
  void initState() {
    super.initState();
    _apiService = widget.apiService ?? ApiService();
    startDate = _today.add(const Duration(days: 1));
    endDate = startDate;
    _loadWeather();
  }

  Future<void> _loadWeather() async {
    final requestSequence = ++_weatherRequestSequence;
    setState(() {
      _isLoadingWeather = true;
      _weatherError = null;
      _weather = null;
    });

    try {
      final weather = await _apiService.getWeather(
        trailName: selectedTrail,
        forecastDate: startDate,
      );
      if (!mounted || requestSequence != _weatherRequestSequence) return;
      setState(() {
        _weather = weather;
        _isLoadingWeather = false;
      });
    } on DioException catch (error) {
      if (!mounted || requestSequence != _weatherRequestSequence) return;
      final responseData = error.response?.data;
      final detail = responseData is Map ? responseData['detail']?.toString() : null;
      setState(() {
        _weatherError = detail ?? 'Weather is unavailable. Check the backend connection and retry.';
        _isLoadingWeather = false;
      });
    } on FormatException catch (error) {
      if (!mounted || requestSequence != _weatherRequestSequence) return;
      setState(() {
        _weatherError = error.message;
        _isLoadingWeather = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        color: const Color(0xFF0B5563),
        child: SafeArea(
          child: Column(
            children: [
              // Header
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.terrain, color: Color(0xFF1BB98D), size: 28),
                        const SizedBox(width: 8),
                        const Text(
                          'venture',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 1.2,
                          ),
                        ),
                      ],
                    ),
                    IconButton(
                      icon: const Icon(Icons.help_outline, color: Colors.white70),
                      onPressed: () {},
                    ),
                  ],
                ),
              ),
              const Padding(
                padding: EdgeInsets.symmetric(horizontal: 16.0, vertical: 4.0),
                child: Align(
                  alignment: Alignment.centerLeft,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Hazard & Weather Forecast',
                        style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
                      ),
                      SizedBox(height: 4),
                      Text(
                        'A little planning. A safer adventure.',
                        style: TextStyle(color: Colors.white70, fontSize: 14),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              // Body Sheet
              Expanded(
                child: Container(
                  padding: const EdgeInsets.all(20),
                  decoration: const BoxDecoration(
                    color: Color(0xFFF8FAFC),
                    borderRadius: BorderRadius.only(
                      topLeft: Radius.circular(24),
                      topRight: Radius.circular(24),
                    ),
                  ),
                  child: ListView(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: const [
                          Text('Plan your hike', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF0B5563))),
                          Row(
                            children: [
                              Icon(Icons.location_on, size: 16, color: Color(0xFF1BB98D)),
                              SizedBox(width: 4),
                              Text('Sri Lanka', style: TextStyle(color: Colors.grey, fontWeight: FontWeight.w500)),
                            ],
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      // Trail Dropdown
                      const Text('Hiking trail', style: TextStyle(fontSize: 12, color: Colors.grey, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 6),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: Colors.grey.shade300),
                        ),
                        child: DropdownButtonHideUnderline(
                          child: DropdownButton<String>(
                            value: selectedTrail,
                            isExpanded: true,
                            items: trails.map((String trail) {
                              return DropdownMenuItem<String>(
                                value: trail,
                                child: Row(
                                  children: [
                                    const Icon(Icons.location_pin, color: Color(0xFF0B5563), size: 20),
                                    const SizedBox(width: 10),
                                    Text(trail, style: const TextStyle(fontWeight: FontWeight.w600, color: Color(0xFF0B5563))),
                                  ],
                                ),
                              );
                            }).toList(),
                            onChanged: (val) {
                              if (val == null) return;
                              setState(() => selectedTrail = val);
                              _loadWeather();
                            },
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),
                      // Dates
                      Row(
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text('Start date', style: TextStyle(fontSize: 12, color: Colors.grey, fontWeight: FontWeight.bold)),
                                const SizedBox(height: 6),
                                InkWell(
                                  onTap: () async {
                                    DateTime? picked = await showDatePicker(
                                      context: context,
                                      initialDate: startDate,
                                      firstDate: _today,
                                      lastDate: _lastForecastDate,
                                    );
                                    if (picked != null) {
                                      setState(() {
                                        startDate = DateUtils.dateOnly(picked);
                                        if (endDate.isBefore(startDate)) endDate = startDate;
                                      });
                                      _loadWeather();
                                    }
                                  },
                                  child: Container(
                                    padding: const EdgeInsets.all(14),
                                    decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16), border: Border.all(color: Colors.grey.shade300)),
                                    child: Row(
                                      children: [
                                        const Icon(Icons.calendar_today, size: 18, color: Color(0xFF0B5563)),
                                        const SizedBox(width: 8),
                                        Text(_formatDate(startDate), style: const TextStyle(fontWeight: FontWeight.w600)),
                                      ],
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text('End date', style: TextStyle(fontSize: 12, color: Colors.grey, fontWeight: FontWeight.bold)),
                                const SizedBox(height: 6),
                                InkWell(
                                  onTap: () async {
                                    DateTime? picked = await showDatePicker(
                                      context: context,
                                      initialDate: endDate,
                                      firstDate: startDate,
                                      lastDate: _lastForecastDate,
                                    );
                                    if (picked != null) setState(() => endDate = picked);
                                  },
                                  child: Container(
                                    padding: const EdgeInsets.all(14),
                                    decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16), border: Border.all(color: Colors.grey.shade300)),
                                    child: Row(
                                      children: [
                                        const Icon(Icons.calendar_today, size: 18, color: Color(0xFF0B5563)),
                                        const SizedBox(width: 8),
                                        Text(_formatDate(endDate), style: const TextStyle(fontWeight: FontWeight.w600)),
                                      ],
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      // Trail Info Card
                      Container(
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(16),
                          boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 10, offset: const Offset(0, 4))],
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Stack(
                              children: [
                                ClipRRect(
                                  borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
                                  child: Image.asset(
                                    _trailImagePath(selectedTrail),
                                    height: 120,
                                    width: double.infinity,
                                    fit: BoxFit.cover,
                                    errorBuilder: (context, error, stackTrace) => const ColoredBox(
                                      color: Color(0xFF0B5563),
                                      child: Center(
                                        child: Icon(Icons.image, size: 48, color: Colors.white),
                                      ),
                                    ),
                                  ),
                                ),
                                Positioned(
                                  top: 12,
                                  right: 12,
                                  child: Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                    decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(20)),
                                    child: const Row(
                                      children: [
                                        Icon(Icons.hiking, size: 14, color: Color(0xFFF59E0B)),
                                        SizedBox(width: 4),
                                        Text('Moderate', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF0B5563))),
                                      ],
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            Padding(
                              padding: const EdgeInsets.all(16.0),
                              child: Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(selectedTrail, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF0B5563))),
                                      const SizedBox(height: 2),
                                      const Text('Trail forecast location · Sri Lanka', style: TextStyle(fontSize: 12, color: Colors.grey)),
                                    ],
                                  ),
                                  const Row(
                                    children: [
                                      Icon(Icons.straighten, size: 16, color: Colors.grey),
                                      SizedBox(width: 4),
                                      Text('9.5 km', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                                    ],
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 16),
                      // Weather Summary Card
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(16),
                          boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 10, offset: const Offset(0, 4))],
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                  Text('$selectedTrail · ${_formatDate(startDate)}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Color(0xFF0B5563))),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                  decoration: BoxDecoration(color: Colors.grey.shade100, borderRadius: BorderRadius.circular(12)),
                                    child: Text(
                                      _isLoadingWeather ? 'Loading' : _weather?.source ?? 'Unavailable',
                                      style: const TextStyle(fontSize: 10, color: Colors.grey, fontWeight: FontWeight.bold),
                                    ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 12),
                              if (_isLoadingWeather)
                                const Row(
                                  children: [
                                    SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2)),
                                    SizedBox(width: 10),
                                    Text('Fetching the selected trail forecast...'),
                                  ],
                                )
                              else if (_weatherError != null)
                                Text(_weatherError!, style: const TextStyle(color: Color(0xFFB42318), fontSize: 13))
                              else if (_weather != null) ...[
                                Row(
                                  children: [
                                    Icon(_weatherIcon(_weather!.condition), color: const Color(0xFFF59E0B), size: 36),
                                    const SizedBox(width: 16),
                                    Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text('${_weather!.temperatureC.toStringAsFixed(0)}°C max', style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Color(0xFF0B5563))),
                                        Text('${_weather!.condition} · Feels like ${_weather!.feelsLikeC.toStringAsFixed(0)}°C max', style: const TextStyle(fontSize: 12, color: Colors.grey)),
                                      ],
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 12),
                                const Divider(color: Colors.black12),
                                const SizedBox(height: 8),
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                                  children: [
                                    _WeatherMetric(icon: Icons.water_drop, label: 'Rain chance', value: '${_weather!.rainChance}%'),
                                    _WeatherMetric(icon: Icons.air, label: 'Max wind', value: '${_weather!.windSpeedKmh.toStringAsFixed(0)} km/h'),
                                    _WeatherMetric(icon: Icons.opacity, label: 'Humidity at noon', value: '${_weather!.humidity}%'),
                                  ],
                                ),
                                const SizedBox(height: 8),
                                Center(
                                  child: Text(
                                    'Rain ${_weather!.precipitationMm.toStringAsFixed(1)} mm · Gusts ${_weather!.windGustKmh.toStringAsFixed(0)} km/h',
                                    style: const TextStyle(fontSize: 11, color: Colors.grey),
                                  ),
                                ),
                              ],
                          ],
                        ),
                      ),
                      const SizedBox(height: 24),
                      // Primary CTA
                      ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF1BB98D),
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                          elevation: 0,
                        ),
                        onPressed: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => Screen2Processing(
                                trailName: selectedTrail,
                                startDate: startDate,
                                endDate: endDate,
                              ),
                            ),
                          );
                        },
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: const [
                            Icon(Icons.security, size: 20),
                            SizedBox(width: 8),
                            Text('Analyze Risk', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                            SizedBox(width: 8),
                            Icon(Icons.arrow_forward, size: 20),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

String _formatDate(DateTime date) {
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  return '${date.day} ${months[date.month - 1]} ${date.year}';
}

IconData _weatherIcon(String condition) {
  final normalized = condition.toLowerCase();
  if (normalized.contains('thunderstorm')) return Icons.thunderstorm;
  if (normalized.contains('rain') || normalized.contains('drizzle')) return Icons.grain;
  if (normalized.contains('cloud') || normalized.contains('fog') || normalized.contains('overcast')) return Icons.cloud;
  return Icons.wb_sunny;
}

String _trailImagePath(String trail) {
  final filename = trail
      .toLowerCase()
      .replaceAll("'", '')
      .replaceAll(RegExp(r'\s+'), '-');
  return 'assets/component02/$filename.jpg';
}

class _WeatherMetric extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  const _WeatherMetric({required this.icon, required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(icon, size: 18, color: const Color(0xFF0B5563)),
        const SizedBox(height: 4),
        Text(value, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF0B5563))),
        Text(label, style: const TextStyle(fontSize: 10, color: Colors.grey)),
      ],
    );
  }
}