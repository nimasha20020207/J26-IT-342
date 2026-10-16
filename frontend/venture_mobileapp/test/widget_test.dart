// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';

import 'package:venture_mobileapp/main.dart';

void main() {
  testWidgets('Trip planning screen smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const VentureForecastApp());

    expect(find.text('Hazard & Weather Forecast'), findsOneWidget);
    expect(find.text('Plan your hike'), findsOneWidget);

    final dropdown = tester.widget<DropdownButton<String>>(
      find.byType(DropdownButton<String>),
    );
    expect(dropdown.value, 'Pidurangala');
    final trailImage = tester.widget<Image>(find.byType(Image));
    expect(
      (trailImage.image as AssetImage).assetName,
      'assets/component02/pidurangala.jpg',
    );
    expect(
      dropdown.items!.map((item) => item.value).toList(),
      [
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
      ],
    );
  });
}
