import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import '../models/models.dart';

class ApiService {
  final http.Client _client;

  ApiService({http.Client? client}) : _client = client ?? http.Client();

  Uri _uri(String path, [Map<String, dynamic>? queryParams]) {
    final base = ApiConfig.baseUrl.replaceAll(RegExp(r'/+$'), '');
    final uri = Uri.parse('$base$path');
    if (queryParams != null && queryParams.isNotEmpty) {
      final cleanParams = queryParams.map(
        (key, value) => MapEntry(key, value?.toString() ?? ''),
      );
      return uri.replace(queryParameters: cleanParams);
    }
    return uri;
  }

  /// Get active services list from backend
  Future<List<ServiceItem>> fetchServices() async {
    try {
      final res = await _client.get(_uri('/api/services'));
      if (res.statusCode == 200) {
        final list = jsonDecode(res.body) as List<dynamic>;
        return list.map((e) => ServiceItem.fromJson(e as Map<String, dynamic>)).toList();
      } else {
        throw Exception('Failed to load services: HTTP ${res.statusCode}');
      }
    } catch (e) {
      debugPrint('Error fetching services: $e');
      rethrow;
    }
  }

  /// Fetch demo accounts for instant switching
  Future<Map<String, List<DemoUser>>> fetchDemoAccounts() async {
    try {
      final res = await _client.get(_uri('/api/auth/demo-accounts'));
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body) as Map<String, dynamic>;
        final customers = (data['customers'] as List<dynamic>? ?? [])
            .map((e) => DemoUser.fromJson(e as Map<String, dynamic>, 'customer'))
            .toList();
        final workers = (data['workers'] as List<dynamic>? ?? [])
            .map((e) => DemoUser.fromJson(e as Map<String, dynamic>, 'worker'))
            .toList();
        return {'customers': customers, 'workers': workers};
      } else {
        throw Exception('Failed to load demo accounts: HTTP ${res.statusCode}');
      }
    } catch (e) {
      debugPrint('Error fetching demo accounts: $e');
      rethrow;
    }
  }

  /// Submit customer service request to FastAPI
  Future<Map<String, dynamic>> createServiceRequest({
    required String serviceId,
    required String problemDescription,
    required String address,
    String? landmark,
    String? directions,
    String requestType = 'immediate',
    double? latitude,
    double? longitude,
    String? preferredDate,
    DateTime? preferredStartTime,
    String? customerId,
  }) async {
    final payload = <String, dynamic>{
      'service_id': serviceId,
      'problem_description': problemDescription,
      'address': address,
      'landmark': landmark,
      'directions': directions,
      'request_type': requestType,
      'latitude': latitude,
      'longitude': longitude,
      'preferred_date': preferredDate,
      'preferred_start_time': preferredStartTime?.toIso8601String(),
      if (customerId != null) 'customer_id': customerId,
    };

    final res = await _client.post(
      _uri('/api/requests'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    );

    if (res.statusCode == 201 || res.statusCode == 200) {
      return jsonDecode(res.body) as Map<String, dynamic>;
    } else {
      throw Exception('Failed to create request: ${res.statusCode} ${res.body}');
    }
  }

  /// Retrieve status of specific service request
  Future<Map<String, dynamic>> getRequestStatus(String requestId) async {
    final res = await _client.get(_uri('/api/requests/$requestId'));
    if (res.statusCode == 200) {
      return jsonDecode(res.body) as Map<String, dynamic>;
    } else {
      throw Exception('Failed to fetch request status: ${res.statusCode}');
    }
  }

  /// List customer requests
  Future<List<Map<String, dynamic>>> listCustomerRequests({String? customerId}) async {
    final params = customerId != null ? {'customer_id': customerId} : null;
    final res = await _client.get(_uri('/api/requests', params));
    if (res.statusCode == 200) {
      final list = jsonDecode(res.body) as List<dynamic>;
      return list.map((e) => e as Map<String, dynamic>).toList();
    } else {
      throw Exception('Failed to list requests: ${res.statusCode}');
    }
  }

  /// Retrieve assigned jobs for worker
  Future<List<WorkerJob>> fetchWorkerJobs({String? workerId}) async {
    final params = workerId != null ? {'worker_id': workerId} : null;
    final res = await _client.get(_uri('/api/worker/jobs', params));
    if (res.statusCode == 200) {
      final list = jsonDecode(res.body) as List<dynamic>;
      return list.map((e) => WorkerJob.fromJson(e as Map<String, dynamic>)).toList();
    } else {
      throw Exception('Failed to fetch worker jobs: ${res.statusCode}');
    }
  }

  /// Get specific job details
  Future<WorkerJob> getJobDetails(String bookingId) async {
    final res = await _client.get(_uri('/api/worker/jobs/$bookingId'));
    if (res.statusCode == 200) {
      final data = jsonDecode(res.body) as Map<String, dynamic>;
      return WorkerJob.fromJson(data);
    } else {
      throw Exception('Failed to get job details: ${res.statusCode}');
    }
  }

  /// Worker accepts assigned job
  Future<Map<String, dynamic>> acceptJob(String bookingId) async {
    final res = await _client.post(_uri('/api/worker/jobs/$bookingId/accept'));
    if (res.statusCode == 200) {
      return jsonDecode(res.body) as Map<String, dynamic>;
    } else {
      throw Exception('Failed to accept job: ${res.statusCode} ${res.body}');
    }
  }

  /// Worker updates job status (en_route, arrived, in_progress, completed)
  Future<Map<String, dynamic>> updateJobStatus(String bookingId, String status) async {
    final res = await _client.post(
      _uri('/api/worker/jobs/$bookingId/status'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'status': status}),
    );
    if (res.statusCode == 200) {
      return jsonDecode(res.body) as Map<String, dynamic>;
    } else {
      throw Exception('Failed to update job status: ${res.statusCode} ${res.body}');
    }
  }
}
