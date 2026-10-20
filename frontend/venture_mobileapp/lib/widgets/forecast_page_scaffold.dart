import 'package:flutter/material.dart';

import '../models/component02/hazard_data.dart';
import '../theme/app_theme.dart';

class ForecastRoutes {
  static const overview = '/forecast';
  static const map = '/map';
  static const trends = '/trends';
  static const signals = '/signals';
  static const assessment = '/assessment';
}

class ForecastPageScaffold extends StatelessWidget {
  const ForecastPageScaffold({
    super.key,
    required this.title,
    required this.forecast,
    required this.selectedDestination,
    required this.body,
    this.actions,
    this.showNavigationBar = true,
  });

  final String title;
  final ForecastData forecast;
  final int selectedDestination;
  final Widget body;
  final List<Widget>? actions;
  final bool showNavigationBar;

  static const _routes = [
    ForecastRoutes.overview,
    ForecastRoutes.map,
    ForecastRoutes.trends,
    ForecastRoutes.signals,
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.canvas,
      appBar: AppBar(title: Text(title), actions: actions),
      body: body,
      bottomNavigationBar: showNavigationBar
          ? NavigationBar(
              selectedIndex: selectedDestination,
              onDestinationSelected: (index) {
                if (index == selectedDestination) return;
                Navigator.pushNamed(
                  context,
                  _routes[index],
                  arguments: forecast,
                );
              },
              destinations: const [
                NavigationDestination(
                  icon: Icon(Icons.dashboard_outlined),
                  selectedIcon: Icon(Icons.dashboard_rounded),
                  label: 'Overview',
                ),
                NavigationDestination(
                  icon: Icon(Icons.map_outlined),
                  selectedIcon: Icon(Icons.map_rounded),
                  label: 'Map',
                ),
                NavigationDestination(
                  icon: Icon(Icons.show_chart_rounded),
                  label: 'Trends',
                ),
                NavigationDestination(
                  icon: Icon(Icons.forum_outlined),
                  selectedIcon: Icon(Icons.forum_rounded),
                  label: 'Signals',
                ),
              ],
            )
          : null,
    );
  }
}
