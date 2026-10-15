import 'package:flutter/material.dart';
import 'dashboard.dart';

class Screen2Processing extends StatefulWidget {
  const Screen2Processing({super.key});

  @override
  State<Screen2Processing> createState() => _Screen2ProcessingState();
}

class _Screen2ProcessingState extends State<Screen2Processing> with SingleTickerProviderStateMixin {
  double progress = 0.0;
  String currentStatusText = 'Initializing AI Multi-Source Data Fusion Pipeline...';

  @override
  void initState() {
    super.initState();
    startProcessingSimulation();
  }

  void startProcessingSimulation() async {
    await Future.delayed(const Duration(milliseconds: 600));
    setState(() { progress = 0.25; currentStatusText = 'Collecting Weather & Terrain Data APIs...'; });
    
    await Future.delayed(const Duration(milliseconds: 800));
    setState(() { progress = 0.50; currentStatusText = 'Extracting Social & News Signals via BERT/Topic Modelling...'; });

    await Future.delayed(const Duration(milliseconds: 800));
    setState(() { progress = 0.75; currentStatusText = 'Running Social Signal Reliability & Credibility Assessment...'; });

    await Future.delayed(const Duration(milliseconds: 800));
    setState(() { progress = 1.0; currentStatusText = 'Generating Unified Risk Vector & Forecast Dashboard...'; });

    await Future.delayed(const Duration(milliseconds: 500));
    if (mounted) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => const Screen3Dashboard()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0B5563),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.psychology, size: 64, color: Color(0xFF1BB98D)),
              const SizedBox(height: 24),
              const Text(
                'Analyzing Trail Hazards',
                style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text(
                'Venture AI is fusing multi-source environmental and social intelligence',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.white70, fontSize: 14),
              ),
              const SizedBox(height: 48),
              LinearProgressIndicator(
                value: progress,
                backgroundColor: Colors.white24,
                color: const Color(0xFF1BB98D),
                minHeight: 8,
                borderRadius: BorderRadius.circular(4),
              ),
              const SizedBox(height: 24),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.05),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.white12),
                ),
                child: Column(
                  children: [
                    Row(
                      children: [
                        const SizedBox(
                          width: 16, height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF1BB98D)),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            currentStatusText,
                            style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w500),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),
                    _StatusItem(title: 'Environmental data collection', done: progress >= 0.25),
                    _StatusItem(title: 'Weather & terrain status', done: progress >= 0.50),
                    _StatusItem(title: 'News & social signal analysis (BERT)', done: progress >= 0.75),
                    _StatusItem(title: 'Reliability & credibility evaluation', done: progress >= 1.0),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _StatusItem extends StatelessWidget {
  final String title;
  final bool done;
  const _StatusItem({required this.title, required this.done});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6.0),
      child: Row(
        children: [
          Icon(
            done ? Icons.check_circle : Icons.radio_button_unchecked,
            color: done ? const Color(0xFF1BB98D) : Colors.white38,
            size: 18,
          ),
          const SizedBox(width: 10),
          Text(
            title,
            style: TextStyle(color: done ? Colors.white : Colors.white60, fontSize: 13),
          ),
        ],
      ),
    );
  }
}