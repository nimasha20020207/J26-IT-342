import 'package:dio/dio.dart';
import 'package:flutter/material.dart';

import '../../models/component02/hazard_data.dart';
import '../../services/api_service.dart';
import '../../theme/app_theme.dart';
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
    'Adam\'s peak',
    'Ella rock',
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
      final detail = responseData is Map
          ? responseData['detail']?.toString()
          : null;
      setState(() {
        _weatherError =
            detail ??
            'Weather is unavailable. Check the backend connection and retry.';
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

  Future<void> _pickStartDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: startDate,
      firstDate: _today,
      lastDate: _lastForecastDate,
    );
    if (picked == null) return;

    setState(() {
      startDate = DateUtils.dateOnly(picked);
      if (endDate.isBefore(startDate)) endDate = startDate;
    });
    _loadWeather();
  }

  Future<void> _pickEndDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: endDate,
      firstDate: startDate,
      lastDate: _lastForecastDate,
    );
    if (picked != null) setState(() => endDate = DateUtils.dateOnly(picked));
  }

  void _analyzeRisk() {
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
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.canvas,
      body: SafeArea(
        bottom: false,
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 12, 20, 24),
          children: [
            Row(
              children: [
                Container(
                  width: 42,
                  height: 42,
                  decoration: BoxDecoration(
                    color: AppColors.primary,
                    borderRadius: BorderRadius.circular(15),
                  ),
                  child: const Icon(
                    Icons.terrain_rounded,
                    color: AppColors.accent,
                  ),
                ),
                const SizedBox(width: 10),
                const Text(
                  'venture',
                  style: TextStyle(
                    color: AppColors.primary,
                    fontSize: 21,
                    fontWeight: FontWeight.w800,
                    letterSpacing: -0.5,
                  ),
                ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 11,
                    vertical: 8,
                  ),
                  decoration: BoxDecoration(
                    color: AppColors.surface,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: AppColors.border),
                  ),
                  child: const Row(
                    children: [
                      Icon(
                        Icons.location_on_rounded,
                        size: 14,
                        color: AppColors.primary,
                      ),
                      SizedBox(width: 4),
                      Text(
                        'Sri Lanka',
                        style: TextStyle(
                          color: AppColors.text,
                          fontSize: 11,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 25),
            const Text(
              'Hazard & Weather Forecast',
              style: TextStyle(
                color: AppColors.primary,
                fontSize: 11,
                fontWeight: FontWeight.w800,
                letterSpacing: 1,
              ),
            ),
            const SizedBox(height: 7),
            const Text(
              'Plan your next\ntrail escape.',
              style: TextStyle(
                color: AppColors.text,
                fontSize: 31,
                height: 1.08,
                fontWeight: FontWeight.w800,
                letterSpacing: -1,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'A little planning. A safer adventure.',
              style: TextStyle(color: AppColors.muted, fontSize: 14),
            ),
            const SizedBox(height: 22),
            _TrailHeroCard(trailName: selectedTrail),
            const SizedBox(height: 25),
            Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Plan your hike',
                        style: TextStyle(
                          color: AppColors.text,
                          fontSize: 20,
                          fontWeight: FontWeight.w800,
                          letterSpacing: -0.4,
                        ),
                      ),
                      SizedBox(height: 3),
                      Text(
                        'Choose your trail and travel dates',
                        style: TextStyle(color: AppColors.muted, fontSize: 12),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 9,
                    vertical: 5,
                  ),
                  decoration: BoxDecoration(
                    color: AppColors.accent.withValues(alpha: 0.28),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Text(
                    'STEP 01',
                    style: TextStyle(
                      color: AppColors.primary,
                      fontSize: 9,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 0.5,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),
            Container(
              padding: const EdgeInsets.fromLTRB(15, 14, 12, 10),
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: AppColors.border),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'DESTINATION',
                    style: TextStyle(
                      color: AppColors.muted,
                      fontSize: 10,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 0.8,
                    ),
                  ),
                  DropdownButtonHideUnderline(
                    child: DropdownButton<String>(
                      value: selectedTrail,
                      isExpanded: true,
                      icon: const Icon(
                        Icons.keyboard_arrow_down_rounded,
                        color: AppColors.primary,
                      ),
                      items: trails.map((trail) {
                        return DropdownMenuItem<String>(
                          value: trail,
                          child: Row(
                            children: [
                              const Icon(
                                Icons.place_rounded,
                                color: AppColors.primary,
                                size: 19,
                              ),
                              const SizedBox(width: 9),
                              Text(
                                trail,
                                style: const TextStyle(
                                  color: AppColors.text,
                                  fontWeight: FontWeight.w700,
                                  fontSize: 14,
                                ),
                              ),
                            ],
                          ),
                        );
                      }).toList(),
                      onChanged: (value) {
                        if (value == null) return;
                        setState(() => selectedTrail = value);
                        _loadWeather();
                      },
                    ),
                  ),
                  const Divider(height: 12, color: AppColors.border),
                  Row(
                    children: [
                      Expanded(
                        child: _DateTile(
                          label: 'START',
                          date: startDate,
                          onTap: _pickStartDate,
                        ),
                      ),
                      Container(
                        width: 1,
                        height: 42,
                        color: AppColors.border,
                        margin: const EdgeInsets.symmetric(horizontal: 14),
                      ),
                      Expanded(
                        child: _DateTile(
                          label: 'END',
                          date: endDate,
                          onTap: _pickEndDate,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 21),
            Row(
              children: [
                const Expanded(
                  child: Text(
                    'Trail conditions',
                    style: TextStyle(
                      color: AppColors.text,
                      fontSize: 17,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
                Text(
                  _formatDate(startDate),
                  style: const TextStyle(
                    color: AppColors.muted,
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            _WeatherCard(
              weather: _weather,
              isLoading: _isLoadingWeather,
              error: _weatherError,
            ),
          ],
        ),
      ),
      bottomNavigationBar: SafeArea(
        top: false,
        child: Container(
          padding: const EdgeInsets.fromLTRB(20, 12, 20, 14),
          decoration: BoxDecoration(
            color: AppColors.surface,
            border: const Border(top: BorderSide(color: AppColors.border)),
            boxShadow: [
              BoxShadow(
                color: AppColors.primary.withValues(alpha: 0.06),
                blurRadius: 16,
                offset: const Offset(0, -5),
              ),
            ],
          ),
          child: ElevatedButton(
            onPressed: _analyzeRisk,
            child: const Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.shield_rounded, size: 19),
                SizedBox(width: 9),
                Text('Check trail safety'),
                SizedBox(width: 8),
                Icon(Icons.arrow_forward_rounded, size: 18),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _TrailHeroCard extends StatelessWidget {
  const _TrailHeroCard({required this.trailName});

  final String trailName;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 214,
      clipBehavior: Clip.antiAlias,
      decoration: BoxDecoration(
        color: AppColors.primaryDark,
        borderRadius: BorderRadius.circular(25),
        boxShadow: [
          BoxShadow(
            color: AppColors.primary.withValues(alpha: 0.16),
            blurRadius: 18,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Stack(
        fit: StackFit.expand,
        children: [
          Image.asset(
            _trailImagePath(trailName),
            fit: BoxFit.cover,
            errorBuilder: (context, error, stackTrace) =>
                const ColoredBox(color: AppColors.primaryDark),
          ),
          const DecoratedBox(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [Color(0x1A103B34), Color(0x99103B34)],
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 10,
                        vertical: 7,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.16),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(
                          color: Colors.white.withValues(alpha: 0.24),
                        ),
                      ),
                      child: const Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            Icons.explore_rounded,
                            size: 14,
                            color: AppColors.accent,
                          ),
                          SizedBox(width: 6),
                          Text(
                            'TRAIL SPOTLIGHT',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 10,
                              fontWeight: FontWeight.w800,
                              letterSpacing: 0.7,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 10,
                        vertical: 7,
                      ),
                      decoration: BoxDecoration(
                        color: AppColors.accent,
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: const Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            Icons.hiking_rounded,
                            size: 14,
                            color: AppColors.primaryDark,
                          ),
                          SizedBox(width: 5),
                          Text(
                            'Moderate',
                            style: TextStyle(
                              color: AppColors.primaryDark,
                              fontSize: 11,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const Spacer(),
                Text(
                  trailName,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 27,
                    height: 1.1,
                    fontWeight: FontWeight.w800,
                    letterSpacing: -0.5,
                    shadows: [Shadow(color: Color(0x55000000), blurRadius: 12)],
                  ),
                ),
                const SizedBox(height: 8),
                const Row(
                  children: [
                    Icon(
                      Icons.location_on_rounded,
                      size: 15,
                      color: AppColors.accent,
                    ),
                    SizedBox(width: 4),
                    Text(
                      'Sri Lanka',
                      style: TextStyle(color: Colors.white70, fontSize: 12),
                    ),
                    Spacer(),
                    Icon(Icons.route_rounded, size: 15, color: Colors.white70),
                    SizedBox(width: 5),
                    Text(
                      '9.5 km',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _DateTile extends StatelessWidget {
  const _DateTile({
    required this.label,
    required this.date,
    required this.onTap,
  });

  final String label;
  final DateTime date;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 6),
        child: Row(
          children: [
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                color: AppColors.canvas,
                borderRadius: BorderRadius.circular(11),
              ),
              child: const Icon(
                Icons.calendar_month_rounded,
                color: AppColors.primary,
                size: 18,
              ),
            ),
            const SizedBox(width: 9),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    label,
                    style: const TextStyle(
                      color: AppColors.muted,
                      fontSize: 9,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 0.7,
                    ),
                  ),
                  const SizedBox(height: 3),
                  Text(
                    _formatDate(date),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      color: AppColors.text,
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _WeatherCard extends StatelessWidget {
  const _WeatherCard({
    required this.weather,
    required this.isLoading,
    required this.error,
  });

  final WeatherSummary? weather;
  final bool isLoading;
  final String? error;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(15),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.border),
      ),
      child: isLoading
          ? const Row(
              children: [
                SizedBox(
                  width: 18,
                  height: 18,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    color: AppColors.primary,
                  ),
                ),
                SizedBox(width: 11),
                Text(
                  'Checking the forecast...',
                  style: TextStyle(color: AppColors.muted, fontSize: 12),
                ),
              ],
            )
          : error != null
          ? Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(
                  Icons.cloud_off_rounded,
                  size: 20,
                  color: AppColors.warning,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    error!,
                    style: const TextStyle(
                      color: AppColors.muted,
                      fontSize: 12,
                      height: 1.4,
                    ),
                  ),
                ),
              ],
            )
          : _WeatherDetails(weather: weather!),
    );
  }
}

class _WeatherDetails extends StatelessWidget {
  const _WeatherDetails({required this.weather});

  final WeatherSummary weather;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Row(
          children: [
            Container(
              width: 44,
              height: 44,
              decoration: BoxDecoration(
                color: const Color(0xFFFFF5DD),
                borderRadius: BorderRadius.circular(15),
              ),
              child: Icon(
                _weatherIcon(weather.condition),
                color: AppColors.warning,
                size: 25,
              ),
            ),
            const SizedBox(width: 11),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '${weather.temperatureC.toStringAsFixed(0)}°',
                    style: const TextStyle(
                      color: AppColors.text,
                      fontSize: 24,
                      height: 1,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${weather.condition} · Feels ${weather.feelsLikeC.toStringAsFixed(0)}°',
                    style: const TextStyle(
                      color: AppColors.muted,
                      fontSize: 11,
                    ),
                  ),
                ],
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 6),
              decoration: BoxDecoration(
                color: AppColors.canvas,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                '${weather.source} forecast',
                style: const TextStyle(
                  color: AppColors.primary,
                  fontSize: 9,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ],
        ),
        const Padding(
          padding: EdgeInsets.symmetric(vertical: 12),
          child: Divider(height: 1, color: AppColors.border),
        ),
        Row(
          children: [
            Expanded(
              child: _WeatherMetric(
                icon: Icons.water_drop_rounded,
                label: 'Rain',
                value: '${weather.rainChance}%',
              ),
            ),
            Expanded(
              child: _WeatherMetric(
                icon: Icons.air_rounded,
                label: 'Wind',
                value: '${weather.windSpeedKmh.toStringAsFixed(0)} km/h',
              ),
            ),
            Expanded(
              child: _WeatherMetric(
                icon: Icons.opacity_rounded,
                label: 'Humidity',
                value: '${weather.humidity}%',
              ),
            ),
          ],
        ),
      ],
    );
  }
}

String _formatDate(DateTime date) {
  const months = [
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'Jun',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec',
  ];
  return '${date.day} ${months[date.month - 1]} ${date.year}';
}

IconData _weatherIcon(String condition) {
  final normalized = condition.toLowerCase();
  if (normalized.contains('thunderstorm')) return Icons.thunderstorm_rounded;
  if (normalized.contains('rain') || normalized.contains('drizzle')) {
    return Icons.grain_rounded;
  }
  if (normalized.contains('cloud') ||
      normalized.contains('fog') ||
      normalized.contains('overcast')) {
    return Icons.cloud_rounded;
  }
  return Icons.wb_sunny_rounded;
}

String _trailImagePath(String trail) {
  final filename = trail
      .toLowerCase()
      .replaceAll("'", '')
      .replaceAll(RegExp(r'\s+'), '-');
  return 'assets/component02/$filename.jpg';
}

class _WeatherMetric extends StatelessWidget {
  const _WeatherMetric({
    required this.icon,
    required this.label,
    required this.value,
  });

  final IconData icon;
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 15, color: AppColors.primary),
        const SizedBox(width: 6),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              value,
              style: const TextStyle(
                color: AppColors.text,
                fontSize: 11,
                fontWeight: FontWeight.w800,
              ),
            ),
            Text(
              label,
              style: const TextStyle(color: AppColors.muted, fontSize: 9),
            ),
          ],
        ),
      ],
    );
  }
}
