import 'package:flutter/material.dart';
import '../../models/models.dart';
import '../../state/app_state.dart';
import '../../widgets/status_timeline.dart';
import '../../widgets/osm_location_map.dart';

class WorkerJobDetailsScreen extends StatefulWidget {
  final AppState appState;
  final WorkerJob job;

  const WorkerJobDetailsScreen({
    super.key,
    required this.appState,
    required this.job,
  });

  @override
  State<WorkerJobDetailsScreen> createState() => _WorkerJobDetailsScreenState();
}

class _WorkerJobDetailsScreenState extends State<WorkerJobDetailsScreen> {
  late WorkerJob _currentJob;
  bool _isProcessing = false;

  @override
  void initState() {
    super.initState();
    _currentJob = widget.job;
  }

  Future<void> _handleAccept() async {
    setState(() => _isProcessing = true);
    final success = await widget.appState.acceptCurrentJob(_currentJob.bookingId);
    if (mounted) {
      setState(() => _isProcessing = false);
      if (success) {
        setState(() {
          _currentJob = WorkerJob(
            bookingId: _currentJob.bookingId,
            requestId: _currentJob.requestId,
            workerId: _currentJob.workerId,
            serviceName: _currentJob.serviceName,
            customerName: _currentJob.customerName,
            customerPhone: _currentJob.customerPhone,
            problemDescription: _currentJob.problemDescription,
            requestType: _currentJob.requestType,
            address: _currentJob.address,
            landmark: _currentJob.landmark,
            directions: _currentJob.directions,
            status: 'accepted',
            estimatedPrice: _currentJob.estimatedPrice,
            createdAt: _currentJob.createdAt,
          );
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Job Accepted! MongoDB status updated to "accepted".'),
            backgroundColor: Colors.blue,
          ),
        );
      }
    }
  }

  Future<void> _handleStatusUpdate(String nextStatus) async {
    setState(() => _isProcessing = true);
    final success = await widget.appState.updateJobStatusStep(_currentJob.bookingId, nextStatus);
    if (mounted) {
      setState(() => _isProcessing = false);
      if (success) {
        setState(() {
          _currentJob = WorkerJob(
            bookingId: _currentJob.bookingId,
            requestId: _currentJob.requestId,
            workerId: _currentJob.workerId,
            serviceName: _currentJob.serviceName,
            customerName: _currentJob.customerName,
            customerPhone: _currentJob.customerPhone,
            problemDescription: _currentJob.problemDescription,
            requestType: _currentJob.requestType,
            address: _currentJob.address,
            landmark: _currentJob.landmark,
            directions: _currentJob.directions,
            status: nextStatus,
            estimatedPrice: _currentJob.estimatedPrice,
            createdAt: _currentJob.createdAt,
          );
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Status updated to "$nextStatus" in MongoDB Atlas!'),
            backgroundColor: nextStatus == 'completed' ? Colors.green : Colors.blue,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final status = _currentJob.status.toLowerCase();

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: Text('${_currentJob.serviceName} Job', style: const TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        elevation: 0.5,
      ),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Status Badge Banner
                    Container(
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: status == 'completed' ? Colors.green.shade50 : Colors.blue.shade50,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: status == 'completed' ? Colors.green.shade200 : Colors.blue.shade200,
                        ),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Row(
                            children: [
                              Icon(
                                status == 'completed' ? Icons.check_circle : Icons.info,
                                color: status == 'completed' ? Colors.green : const Color(0xFF1E40AF),
                                size: 20,
                              ),
                              const SizedBox(width: 8),
                              const Text('Current Status:', style: TextStyle(fontSize: 13)),
                            ],
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                            decoration: BoxDecoration(
                              color: status == 'completed' ? Colors.green : const Color(0xFF1E40AF),
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: Text(
                              _currentJob.status.toUpperCase(),
                              style: const TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                                color: Colors.white,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 16),

                    // OpenStreetMap of Customer Service Location
                    OsmLocationMap(
                      latitude: _currentJob.latitude ?? 19.0400,
                      longitude: _currentJob.longitude ?? 72.8625,
                      isInteractive: false,
                      height: 190,
                      markerLabel: _currentJob.customerName,
                      markerColor: const Color(0xFF1E40AF),
                      markerIcon: Icons.location_on,
                    ),

                    const SizedBox(height: 16),

                    // Customer & Problem Info Card
                    Card(
                      elevation: 0.5,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(14),
                        side: BorderSide(color: Colors.grey.shade200),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Customer & Problem Details',
                              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                            ),
                            const Divider(height: 20),
                            _buildInfoItem(
                              icon: Icons.person,
                              label: 'Customer Name',
                              value: _currentJob.customerName,
                            ),
                            const SizedBox(height: 12),
                            _buildInfoItem(
                              icon: Icons.phone,
                              label: 'Customer Phone',
                              value: _currentJob.customerPhone,
                            ),
                            const SizedBox(height: 12),
                            _buildInfoItem(
                              icon: Icons.notes,
                              label: 'Issue Reported',
                              value: _currentJob.problemDescription,
                            ),
                            const SizedBox(height: 12),
                            _buildInfoItem(
                              icon: Icons.location_on,
                              label: 'Service Address',
                              value: _currentJob.address,
                            ),
                            if (_currentJob.landmark != null && _currentJob.landmark!.isNotEmpty) ...[
                              const SizedBox(height: 12),
                              _buildInfoItem(
                                icon: Icons.flag,
                                label: 'Landmark',
                                value: _currentJob.landmark!,
                              ),
                            ],
                            if (_currentJob.directions != null && _currentJob.directions!.isNotEmpty) ...[
                              const SizedBox(height: 12),
                              _buildInfoItem(
                                icon: Icons.directions,
                                label: 'Directions',
                                value: _currentJob.directions!,
                              ),
                            ],
                            const Divider(height: 20),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                const Text(
                                  'Agreed Compensation',
                                  style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
                                ),
                                Text(
                                  '₹${_currentJob.estimatedPrice.toStringAsFixed(0)}',
                                  style: const TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.green,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),

                    const SizedBox(height: 16),

                    // Progress Timeline
                    StatusTimelineWidget(currentStatus: _currentJob.status),
                  ],
                ),
              ),
            ),

            // Worker Action Panel (Status Step Transitions)
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.06),
                    blurRadius: 10,
                    offset: const Offset(0, -4),
                  ),
                ],
              ),
              child: SafeArea(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    if (_isProcessing)
                      const Center(
                        child: Padding(
                          padding: EdgeInsets.all(12.0),
                          child: CircularProgressIndicator(),
                        ),
                      )
                    else ...[
                      // Step 1: Assigned -> Accept
                      if (status == 'assigned') ...[
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton.icon(
                            icon: const Icon(Icons.check_circle_outline, size: 20),
                            label: const Text(
                              'ACCEPT THIS JOB OFFER',
                              style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
                            ),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.green.shade700,
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 16),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                            onPressed: _handleAccept,
                          ),
                        ),
                      ]
                      // Step 2: Accepted -> En Route
                      else if (status == 'accepted') ...[
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton.icon(
                            icon: const Icon(Icons.directions_bike, size: 20),
                            label: const Text(
                              'START TRAVEL (SET EN ROUTE)',
                              style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
                            ),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.indigo.shade700,
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 16),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                            onPressed: () => _handleStatusUpdate('en_route'),
                          ),
                        ),
                      ]
                      // Step 3: En Route -> Arrived
                      else if (status == 'en_route') ...[
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton.icon(
                            icon: const Icon(Icons.place, size: 20),
                            label: const Text(
                              'I HAVE ARRIVED AT LOCATION',
                              style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
                            ),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.teal.shade700,
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 16),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                            onPressed: () => _handleStatusUpdate('arrived'),
                          ),
                        ),
                      ]
                      // Step 4: Arrived -> In Progress
                      else if (status == 'arrived') ...[
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton.icon(
                            icon: const Icon(Icons.build_circle, size: 20),
                            label: const Text(
                              'START WORK (SET IN PROGRESS)',
                              style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
                            ),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.purple.shade700,
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 16),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                            onPressed: () => _handleStatusUpdate('in_progress'),
                          ),
                        ),
                      ]
                      // Step 5: In Progress -> Completed
                      else if (status == 'in_progress') ...[
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton.icon(
                            icon: const Icon(Icons.verified, size: 20),
                            label: const Text(
                              'MARK JOB AS COMPLETED',
                              style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
                            ),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.green.shade700,
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 16),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                            onPressed: () => _handleStatusUpdate('completed'),
                          ),
                        ),
                      ]
                      // Step 6: Completed
                      else if (status == 'completed') ...[
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: Colors.green.shade50,
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: const Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.check_circle, color: Colors.green, size: 20),
                              SizedBox(width: 8),
                              Text(
                                'Job Successfully Completed & Persisted',
                                style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  color: Colors.green,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ],
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoItem({
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 18, color: Colors.grey.shade600),
        const SizedBox(width: 10),
        SizedBox(
          width: 110,
          child: Text(
            label,
            style: const TextStyle(fontSize: 13, color: Colors.grey, fontWeight: FontWeight.w500),
          ),
        ),
        Expanded(
          child: Text(
            value,
            style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF0F172A)),
          ),
        ),
      ],
    );
  }
}
