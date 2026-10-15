import 'package:flutter/material.dart';
import 'recommendation_explanation_screen.dart';

class EmergencyResourcesScreen extends StatelessWidget {
  const EmergencyResourcesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Emergency Resources')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Map Placeholder
            Container(
              height: 140,
              width: double.infinity,
              decoration: BoxDecoration(
                color: Colors.grey.shade200,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.grey.shade400),
              ),
              child: const Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.map, size: 40, color: Colors.grey),
                    SizedBox(height: 4),
                    Text('GPS Map Placeholder (Nearby Assistance Units)', style: TextStyle(color: Colors.grey)),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            const Text('Nearby Assistance & Rescue Teams', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 10),
            
            const _ResourceTile(name: 'Nuwara Eliya Base Hospital', type: 'Hospital', distance: '4.2 km', time: '18 mins', phone: '+94 52 222 2233'),
            const _ResourceTile(name: 'Horton Plains Ranger Station', type: 'Ranger Post', distance: '1.5 km', time: '6 mins', phone: '+94 52 223 4411'),
            const _ResourceTile(name: 'Mountain Rescue Team Alpha', type: 'Rescue Unit', distance: '3.0 km', time: '12 mins', phone: '+94 77 123 4567'),
            const _ResourceTile(name: 'Police Station Ohiya', type: 'Police', distance: '6.8 km', time: '25 mins', phone: '+94 52 333 1122'),
            
            const SizedBox(height: 20),
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
                    MaterialPageRoute(builder: (context) => const RecommendationExplanationScreen()),
                  );
                },
                child: const Text('View Recommendation Explanation', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ResourceTile extends StatelessWidget {
  final String name;
  final String type;
  final String distance;
  final String time;
  final String phone;

  const _ResourceTile({required this.name, required this.type, required this.distance, required this.time, required this.phone});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade300),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                const SizedBox(height: 2),
                Text('$type • $distance away • Est. $time', style: const TextStyle(color: Colors.grey, fontSize: 12)),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.phone, color: Color(0xFF10B981)),
            onPressed: () {},
          ),
        ],
      ),
    );
  }
}