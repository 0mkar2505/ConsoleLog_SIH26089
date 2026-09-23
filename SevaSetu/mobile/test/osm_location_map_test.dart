import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:mobile/widgets/osm_location_map.dart';

void main() {
  testWidgets('OsmLocationMap renders OpenStreetMap FlutterMap and Marker', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: OsmLocationMap(
            latitude: 19.0400,
            longitude: 72.8625,
            isInteractive: true,
            height: 200,
          ),
        ),
      ),
    );

    // Verify FlutterMap widget is mounted
    expect(find.byType(FlutterMap), findsOneWidget);

    // Verify TileLayer is mounted
    expect(find.byType(TileLayer), findsOneWidget);

    // Verify MarkerLayer is mounted
    expect(find.byType(MarkerLayer), findsOneWidget);

    // Verify pin icon is rendered
    expect(find.byIcon(Icons.location_on), findsOneWidget);

    // Verify interaction banner is rendered
    expect(find.text('Tap anywhere on map to pin service location'), findsOneWidget);
  });
}
