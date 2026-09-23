import 'package:flutter/material.dart';
import '../../models/models.dart';
import '../../state/app_state.dart';
import 'worker_assigned_screen.dart';

class FindingWorkerScreen extends StatefulWidget {
  final AppState appState;
  final ServiceItem service;
  final String problemDescription;
  final String address;
  final String? landmark;
  final String? directions;
  final String requestType;
  final double? latitude;
  final double? longitude;
  final String? scheduledDate;
  final DateTime? scheduledStartTime;

  const FindingWorkerScreen({
    super.key,
    required this.appState,
    required this.service,
    required this.problemDescription,
    required this.address,
    this.landmark,
    this.directions,
    required this.requestType,
    this.latitude,
    this.longitude,
    this.scheduledDate,
    this.scheduledStartTime,
  });

  @override
  State<FindingWorkerScreen> createState() => _FindingWorkerScreenState();
}

class _FindingWorkerScreenState extends State<FindingWorkerScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _animController;
  late Animation<double> _scaleAnimation;
  String _statusText = 'Contacting SevaSetu Dispatch Engine...';
  bool _hasFailed = false;
  String? _errorDetail;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat(reverse: true);

    _scaleAnimation = Tween<double>(begin: 0.9, end: 1.15).animate(
      CurvedAnimation(parent: _animController, curve: Curves.easeInOut),
    );

    _triggerDispatch();
  }

  @override
  void dispose() {
    _animController.dispose();
    super.dispose();
  }

  Future<void> _triggerDispatch() async {
    setState(() {
      _hasFailed = false;
      _errorDetail = null;
      _statusText = 'Submitting request to MongoDB Atlas...';
    });

    await Future.delayed(const Duration(milliseconds: 600));
    if (!mounted) return;

    setState(() {
      _statusText = 'Finding a suitable verified worker...';
    });

    final success = await widget.appState.submitServiceRequest(
      serviceId: widget.service.id,
      problemDescription: widget.problemDescription,
      address: widget.address,
      landmark: widget.landmark,
      directions: widget.directions,
      requestType: widget.requestType,
      latitude: widget.latitude,
      longitude: widget.longitude,
      preferredDate: widget.scheduledDate,
      preferredStartTime: widget.scheduledStartTime,
    );

    if (!mounted) return;

    if (success) {
      setState(() {
        _statusText = 'Worker assigned! Redirecting...';
      });
      await Future.delayed(const Duration(milliseconds: 700));
      if (!mounted) return;

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => WorkerAssignedScreen(appState: widget.appState),
        ),
      );
    } else {
      setState(() {
        _hasFailed = true;
        _errorDetail = widget.appState.errorMessage ?? 'Unable to connect to backend';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text('Dispatching Service', style: TextStyle(fontWeight: FontWeight.bold)),
        centerTitle: true,
        automaticallyImplyLeading: false,
        backgroundColor: Colors.white,
        elevation: 0,
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              if (!_hasFailed) ...[
                ScaleTransition(
                  scale: _scaleAnimation,
                  child: Container(
                    width: 120,
                    height: 120,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: const Color(0xFF1E40AF).withOpacity(0.08),
                    ),
                    child: Center(
                      child: Container(
                        width: 80,
                        height: 80,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: const Color(0xFF1E40AF).withOpacity(0.15),
                        ),
                        child: const Center(
                          child: Icon(
                            Icons.radar,
                            size: 44,
                            color: Color(0xFF1E40AF),
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 36),
                const Text(
                  'Finding Suitable Worker...',
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF0F172A),
                  ),
                ),
                const SizedBox(height: 10),
                Text(
                  _statusText,
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 14, color: Color(0xFF64748B)),
                ),
                const SizedBox(height: 24),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  decoration: BoxDecoration(
                    color: Colors.blue.shade50,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const SizedBox(
                        width: 14,
                        height: 14,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      ),
                      const SizedBox(width: 10),
                      Text(
                        'Checking local cooperatives...',
                        style: TextStyle(fontSize: 12, color: Colors.blue.shade900),
                      ),
                    ],
                  ),
                ),
              ] else ...[
                Icon(Icons.error_outline, size: 64, color: Colors.red.shade400),
                const SizedBox(height: 16),
                const Text(
                  'Dispatch Failed',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                Text(
                  _errorDetail ?? 'Could not dispatch worker.',
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 13, color: Colors.grey),
                ),
                const SizedBox(height: 24),
                ElevatedButton.icon(
                  icon: const Icon(Icons.refresh),
                  label: const Text('Retry Dispatch'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF1E40AF),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                  ),
                  onPressed: _triggerDispatch,
                ),
                const SizedBox(height: 8),
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('Back to Form'),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
