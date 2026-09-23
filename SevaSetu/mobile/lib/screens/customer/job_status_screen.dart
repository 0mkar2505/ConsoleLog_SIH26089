import 'package:flutter/material.dart';
import '../../state/app_state.dart';
import '../../widgets/app_bar_actions.dart';
import '../../widgets/status_timeline.dart';
import '../../widgets/osm_location_map.dart';
import 'job_completed_screen.dart';

class JobStatusScreen extends StatefulWidget {
  final AppState appState;

  const JobStatusScreen({super.key, required this.appState});

  @override
  State<JobStatusScreen> createState() => _JobStatusScreenState();
}

class _JobStatusScreenState extends State<JobStatusScreen> {
  bool _isRefreshing = false;

  @override
  void initState() {
    super.initState();
    final reqId = widget.appState.activeRequestId;
    if (reqId != null) {
      widget.appState.startStatusPolling(reqId);
    }
  }

  @override
  void dispose() {
    widget.appState.stopStatusPolling();
    super.dispose();
  }

  Future<void> _manualRefresh() async {
    setState(() => _isRefreshing = true);
    final reqId = widget.appState.activeRequestId;
    if (reqId != null) {
      await widget.appState.pollRequestStatus(reqId);
    }
    if (mounted) {
      setState(() => _isRefreshing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final status = widget.appState.currentStatus;
    final worker = widget.appState.assignedWorker;
    final booking = widget.appState.activeBooking;
    final request = widget.appState.activeRequest;

    final isCompleted = status.toLowerCase() == 'completed' || status.toLowerCase() == 'fulfilled';

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: const Text('Live Job Tracking', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        elevation: 0.5,
        actions: [
          IconButton(
            icon: _isRefreshing
                ? const SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.refresh),
            tooltip: 'Refresh Status',
            onPressed: _manualRefresh,
          ),
          AppBarModeSwitcher(appState: widget.appState),
          const SizedBox(width: 8),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Completed Banner Card (if job is completed)
              if (isCompleted) ...[
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.green.shade50,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: Colors.green.shade300),
                  ),
                  child: Column(
                    children: [
                      const Row(
                        children: [
                          Icon(Icons.check_circle, color: Colors.green, size: 28),
                          SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Service Completed!',
                                  style: TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.green,
                                  ),
                                ),
                                Text(
                                  'The technician has marked this job as completed.',
                                  style: TextStyle(fontSize: 12, color: Colors.black87),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton.icon(
                          icon: const Icon(Icons.receipt_long, size: 18),
                          label: const Text('View Completion Receipt'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.green,
                            foregroundColor: Colors.white,
                          ),
                          onPressed: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (context) => JobCompletedScreen(appState: widget.appState),
                              ),
                            );
                          },
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
              ],

              // Live Service Location Map
              OsmLocationMap(
                latitude: request?.latitude ?? 19.0400,
                longitude: request?.longitude ?? 72.8625,
                isInteractive: false,
                height: 180,
                markerLabel: 'Service Address',
                markerColor: Colors.red,
                markerIcon: Icons.location_on,
              ),
              const SizedBox(height: 16),

              // Service & Worker Brief Card
              Card(
                elevation: 0.5,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
                  side: BorderSide(color: Colors.grey.shade200),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                request?.serviceName ?? 'Service Request',
                                style: const TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                  color: Color(0xFF0F172A),
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                request?.problemDescription ?? 'Issue reported',
                                style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                              ),
                            ],
                          ),
                          Text(
                            '₹${booking?.estimatedPrice.toStringAsFixed(0) ?? "350"}',
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: Colors.green,
                            ),
                          ),
                        ],
                      ),
                      const Divider(height: 20),
                      Row(
                        children: [
                          CircleAvatar(
                            radius: 20,
                            backgroundColor: const Color(0xFF1E40AF).withOpacity(0.1),
                            child: Text(
                              (worker?.name.isNotEmpty ?? false) ? worker!.name[0] : 'W',
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                color: Color(0xFF1E40AF),
                              ),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  worker?.name ?? 'Assigned Worker',
                                  style: const TextStyle(
                                    fontWeight: FontWeight.bold,
                                    fontSize: 14,
                                  ),
                                ),
                                Text(
                                  '${worker?.phone ?? "+919844444401"} • Rating ${worker?.ratingAverage.toStringAsFixed(1) ?? "4.8"}★',
                                  style: const TextStyle(fontSize: 12, color: Colors.grey),
                                ),
                              ],
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: Colors.green.shade50,
                              shape: BoxShape.circle,
                            ),
                            child: const Icon(Icons.phone, color: Colors.green, size: 20),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 16),

              // Status Timeline Widget
              StatusTimelineWidget(currentStatus: status),

              const SizedBox(height: 16),

              // Demo Mode Switcher Helper Card
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: Colors.amber.shade50,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.amber.shade200),
                ),
                child: Row(
                  children: [
                    Icon(Icons.sync_alt, color: Colors.amber.shade900, size: 20),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        'Demo Sync: In Worker Mode, advance this job step-by-step (Accept → En Route → Arrived → In Progress → Completed) to see this timeline update live!',
                        style: TextStyle(fontSize: 12, color: Colors.amber.shade900),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // Return Home Button
              OutlinedButton(
                onPressed: () {
                  Navigator.popUntil(context, (route) => route.isFirst);
                },
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text('Back to Home'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
