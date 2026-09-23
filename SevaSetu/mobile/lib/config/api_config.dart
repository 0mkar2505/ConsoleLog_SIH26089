import 'package:flutter/foundation.dart';

class ApiConfig {
  // Allow dynamic base URL adjustment in demo mode
  static String _overrideBaseUrl = '';

  static String get defaultBaseUrl {
    if (kIsWeb) {
      return 'http://127.0.0.1:8000';
    }
    // For Android physical or Windows desktop
    return 'http://127.0.0.1:8000';
  }

  static String get baseUrl {
    if (_overrideBaseUrl.isNotEmpty) {
      return _overrideBaseUrl;
    }
    const envUrl = String.fromEnvironment('API_BASE_URL');
    if (envUrl.isNotEmpty) {
      return envUrl;
    }
    return defaultBaseUrl;
  }

  static void setBaseUrl(String url) {
    _overrideBaseUrl = url.trim();
  }
}
