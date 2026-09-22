import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/main.dart';

void main() {
  testWidgets('SevaSetu app shell smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const SevaSetuApp());

    // Verify that the title and shell status are present.
    expect(find.text('SevaSetu'), findsOneWidget);
    expect(find.text('Application Shell Active'), findsOneWidget);
  });
}
