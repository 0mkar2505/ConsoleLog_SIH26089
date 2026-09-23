import 'package:flutter/material.dart';
import 'state/app_state.dart';
import 'screens/customer/customer_home_screen.dart';
import 'screens/worker/worker_home_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const SevaSetuApp());
}

class SevaSetuApp extends StatefulWidget {
  const SevaSetuApp({super.key});

  @override
  State<SevaSetuApp> createState() => _SevaSetuAppState();
}

class _SevaSetuAppState extends State<SevaSetuApp> {
  late final AppState _appState;

  @override
  void initState() {
    super.initState();
    _appState = AppState();
  }

  @override
  void dispose() {
    _appState.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SevaSetu',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1E40AF),
          primary: const Color(0xFF1E40AF),
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        scaffoldBackgroundColor: const Color(0xFFF8FAFC),
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.white,
          foregroundColor: Color(0xFF0F172A),
          elevation: 0.5,
        ),
        cardTheme: CardThemeData(
          color: Colors.white,
          elevation: 1,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
        ),
      ),
      home: ListenableBuilder(
        listenable: _appState,
        builder: (context, _) => _buildHomeBody(),
      ),
    );
  }

  Widget _buildHomeBody() {
    if (_appState.isLoading && _appState.services.isEmpty) {
      return Scaffold(
        backgroundColor: Colors.white,
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 64,
                height: 64,
                decoration: BoxDecoration(
                  color: const Color(0xFF1E40AF).withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.handshake_rounded,
                  size: 36,
                  color: Color(0xFF1E40AF),
                ),
              ),
              const SizedBox(height: 20),
              const Text(
                'Connecting to SevaSetu...',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 6),
              const Text(
                'Fetching services & cooperative workers from MongoDB Atlas',
                style: TextStyle(fontSize: 12, color: Colors.grey),
              ),
              const SizedBox(height: 20),
              const CircularProgressIndicator(),
            ],
          ),
        ),
      );
    }

    if (_appState.currentRole == 'worker') {
      return WorkerHomeScreen(appState: _appState);
    } else {
      return CustomerHomeScreen(appState: _appState);
    }
  }
}
