import 'dart:async';
import 'package:flutter/material.dart';
import '../models/models.dart';
import '../services/api_service.dart';

class AppState extends ChangeNotifier {
  final ApiService api = ApiService();

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  String? _errorMessage;
  String? get errorMessage => _errorMessage;

  // Role: 'customer' or 'worker'
  String _currentRole = 'customer';
  String get currentRole => _currentRole;

  // Demo accounts
  List<DemoUser> _demoCustomers = [];
  List<DemoUser> get demoCustomers => _demoCustomers;

  List<DemoUser> _demoWorkers = [];
  List<DemoUser> get demoWorkers => _demoWorkers;

  DemoUser? _currentUser;
  DemoUser? get currentUser => _currentUser;

  // Services catalog
  List<ServiceItem> _services = [];
  List<ServiceItem> get services => _services;

  ServiceItem? _selectedService;
  ServiceItem? get selectedService => _selectedService;

  // Active Customer Request & Booking flow state
  ServiceRequest? _activeRequest;
  ServiceRequest? get activeRequest => _activeRequest;

  String? _activeRequestId;
  String? get activeRequestId => _activeRequestId ?? _activeRequest?.id;

  BookingInfo? _activeBooking;
  BookingInfo? get activeBooking => _activeBooking;

  String? _activeBookingId;
  String? get activeBookingId => _activeBookingId ?? _activeBooking?.id;

  WorkerProfile? _assignedWorker;
  WorkerProfile? get assignedWorker => _assignedWorker;

  String _currentStatus = 'pending';
  String get currentStatus => _currentStatus;

  // Active Worker Jobs (Worker portal only)
  List<WorkerJob> _workerJobs = [];
  List<WorkerJob> get workerJobs => _workerJobs;

  WorkerJob? _selectedJob;
  WorkerJob? get selectedJob => _selectedJob;

  Timer? _statusPollTimer;

  AppState() {
    initApp();
  }

  @override
  void dispose() {
    _statusPollTimer?.cancel();
    super.dispose();
  }

  Future<void> initApp() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      await Future.wait([
        loadDemoAccounts(),
        loadServices(),
      ]);
      if (_currentRole == 'customer') {
        await loadCustomerActiveRequest();
      }
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> loadDemoAccounts() async {
    try {
      final accounts = await api.fetchDemoAccounts();
      _demoCustomers = accounts['customers'] ?? [];
      _demoWorkers = accounts['workers'] ?? [];

      if (_currentUser == null) {
        if (_currentRole == 'customer' && _demoCustomers.isNotEmpty) {
          _currentUser = _demoCustomers.first;
        } else if (_currentRole == 'worker' && _demoWorkers.isNotEmpty) {
          _currentUser = _demoWorkers.first;
        }
      }
      notifyListeners();
    } catch (e) {
      debugPrint('Failed to load demo accounts: $e');
    }
  }

  Future<void> loadServices() async {
    try {
      _services = await api.fetchServices();
      notifyListeners();
    } catch (e) {
      debugPrint('Failed to load services: $e');
    }
  }

  /// Customer: Fetch customer's own active request/booking using customer endpoint (/api/requests)
  Future<void> loadCustomerActiveRequest() async {
    if (_currentRole != 'customer') return;
    final customerId = _currentUser?.customerId ?? _currentUser?.userId;
    if (customerId == null) return;

    try {
      final requests = await api.listCustomerRequests(customerId: customerId);
      if (requests.isNotEmpty) {
        final active = requests.firstWhere(
          (r) =>
              r['job_status'] != 'completed' &&
              r['job_status'] != 'fulfilled' &&
              r['job_status'] != 'cancelled',
          orElse: () => requests.first,
        );
        final reqId = active['id']?.toString() ?? active['_id']?.toString();
        if (reqId != null) {
          _activeRequestId = reqId;
          await pollRequestStatus(reqId);
        }
      }
    } catch (e) {
      debugPrint('Error loading customer requests: $e');
    }
  }

  void switchRole(String role) {
    _currentRole = role;
    if (role == 'customer') {
      _currentUser = _demoCustomers.isNotEmpty ? _demoCustomers.first : null;
      loadCustomerActiveRequest();
    } else {
      _currentUser = _demoWorkers.isNotEmpty ? _demoWorkers.first : null;
      stopStatusPolling();
      refreshWorkerJobs();
    }
    notifyListeners();
  }

  void setCurrentUser(DemoUser user) {
    _currentUser = user;
    _currentRole = user.role;
    if (_currentRole == 'worker') {
      stopStatusPolling();
      refreshWorkerJobs();
    } else {
      loadCustomerActiveRequest();
    }
    notifyListeners();
  }

  void selectService(ServiceItem service) {
    _selectedService = service;
    notifyListeners();
  }

  void clearSelectedService() {
    _selectedService = null;
    notifyListeners();
  }

  /// Submit request from customer
  Future<bool> submitServiceRequest({
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
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final res = await api.createServiceRequest(
        serviceId: serviceId,
        problemDescription: problemDescription,
        address: address,
        landmark: landmark,
        directions: directions,
        requestType: requestType,
        latitude: latitude,
        longitude: longitude,
        preferredDate: preferredDate,
        preferredStartTime: preferredStartTime,
        customerId: _currentUser?.customerId ?? _currentUser?.userId,
      );

      final reqData = res['request'] as Map<String, dynamic>?;
      final dispatchData = res['dispatch'] as Map<String, dynamic>?;

      if (reqData != null) {
        _activeRequest = ServiceRequest.fromJson(reqData);
      }

      if (dispatchData != null) {
        _assignedWorker = WorkerProfile(
          workerId: dispatchData['worker_id']?.toString() ?? '',
          name: dispatchData['worker_name']?.toString() ?? 'Assigned Worker',
          phone: dispatchData['worker_phone']?.toString() ?? '+919844444401',
          ratingAverage: 4.8,
        );

        _activeBooking = BookingInfo(
          id: dispatchData['booking_id']?.toString() ?? '',
          requestId: _activeRequest?.id,
          customerId: _activeRequest?.customerId ?? '',
          workerId: _assignedWorker!.workerId,
          serviceId: serviceId,
          address: address,
          landmark: landmark,
          directions: directions,
          status: dispatchData['status']?.toString() ?? 'assigned',
          estimatedPrice: (dispatchData['estimated_price'] as num?)?.toDouble() ?? 350.0,
        );

        _currentStatus = _activeBooking!.status;
      } else {
        _currentStatus = 'pending';
      }

      // Store IDs and start customer polling
      _activeRequestId = _activeRequest?.id ?? dispatchData?['request_id']?.toString();
      _activeBookingId = dispatchData?['booking_id']?.toString() ?? _activeBooking?.id;

      _isLoading = false;
      notifyListeners();

      // Start customer status polling using customer request ID
      if (_activeRequestId != null && _currentRole == 'customer') {
        startStatusPolling(_activeRequestId!);
      }

      return true;
    } catch (e) {
      _errorMessage = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// Customer: Start polling status of active request via GET /api/requests/{id}
  void startStatusPolling(String requestId) {
    if (_currentRole != 'customer') return;
    _statusPollTimer?.cancel();
    _statusPollTimer = Timer.periodic(const Duration(seconds: 3), (timer) async {
      if (_currentRole != 'customer') {
        stopStatusPolling();
        return;
      }
      await pollRequestStatus(requestId);
    });
  }

  void stopStatusPolling() {
    _statusPollTimer?.cancel();
    _statusPollTimer = null;
  }

  /// Customer: Poll single request/booking status from GET /api/requests/{id}
  Future<void> pollRequestStatus(String requestId) async {
    try {
      final res = await api.getRequestStatus(requestId);
      final reqData = res['request'] as Map<String, dynamic>?;
      final bookingData = res['booking'] as Map<String, dynamic>?;
      final workerData = res['worker'] as Map<String, dynamic>?;
      final status = res['current_status']?.toString() ?? 'pending';

      if (reqData != null) {
        _activeRequest = ServiceRequest.fromJson(reqData);
        _activeRequestId = _activeRequest!.id;
      }
      if (bookingData != null) {
        _activeBooking = BookingInfo.fromJson(bookingData);
        _activeBookingId = _activeBooking!.id;
      }
      if (workerData != null) {
        _assignedWorker = WorkerProfile.fromJson(workerData);
      }
      _currentStatus = status;

      if (status == 'completed' || status == 'fulfilled' || status == 'cancelled') {
        stopStatusPolling();
      }
      notifyListeners();
    } catch (e) {
      debugPrint('Polling error on request $requestId: $e');
    }
  }

  /// Worker: Refresh assigned jobs via GET /api/worker/jobs?worker_id=... (WORKER PORTAL ONLY)
  Future<void> refreshWorkerJobs() async {
    // STRICT GUARD: Customer portal must NEVER call worker jobs endpoint!
    if (_currentRole != 'worker') {
      return;
    }
    final workerId = _currentUser?.workerId;
    if (workerId == null || workerId.isEmpty) {
      return;
    }
    try {
      _workerJobs = await api.fetchWorkerJobs(workerId: workerId);
      notifyListeners();
    } catch (e) {
      debugPrint('Error fetching worker jobs: $e');
    }
  }

  void selectJob(WorkerJob job) {
    _selectedJob = job;
    notifyListeners();
  }

  /// Worker: Accept job
  Future<bool> acceptCurrentJob(String bookingId) async {
    _isLoading = true;
    notifyListeners();
    try {
      await api.acceptJob(bookingId);
      await refreshWorkerJobs();
      if (_selectedJob != null && _selectedJob!.bookingId == bookingId) {
        _selectedJob = await api.getJobDetails(bookingId);
      }
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// Worker: Update status (en_route, arrived, in_progress, completed)
  Future<bool> updateJobStatusStep(String bookingId, String newStatus) async {
    _isLoading = true;
    notifyListeners();
    try {
      await api.updateJobStatus(bookingId, newStatus);
      await refreshWorkerJobs();
      if (_selectedJob != null && _selectedJob!.bookingId == bookingId) {
        _selectedJob = await api.getJobDetails(bookingId);
      }
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  void resetFlow() {
    _activeRequest = null;
    _activeBooking = null;
    _assignedWorker = null;
    _selectedService = null;
    _currentStatus = 'pending';
    stopStatusPolling();
    notifyListeners();
  }
}
