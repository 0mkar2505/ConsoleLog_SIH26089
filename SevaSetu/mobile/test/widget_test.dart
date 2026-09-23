import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/main.dart';

void main() {
  testWidgets('SevaSetu app loads smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const SevaSetuApp());
    expect(find.byType(SevaSetuApp), findsOneWidget);
  });
}
