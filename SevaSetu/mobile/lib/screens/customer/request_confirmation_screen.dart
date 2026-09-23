import 'package:flutter/material.dart';
import '../../models/models.dart';
import '../../state/app_state.dart';
import 'finding_worker_screen.dart';

class RequestConfirmationScreen extends StatelessWidget {
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

  const RequestConfirmationScreen({
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
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: const Text('Confirm Request', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        elevation: 0.5,
      ),
      body: Column(
        children: [
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Verification Shield Banner
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.green.shade50,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: Colors.green.shade200),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.verified_user, color: Colors.green, size: 28),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Cooperative Guaranteed Service',
                                style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  color: Colors.green.shade900,
                                  fontSize: 14,
                                ),
                              ),
                              Text(
                                'Dispatching to verified local workers with fair pay standards.',
                                style: TextStyle(
                                  color: Colors.green.shade800,
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 20),

                  // Summary Details Card
                  Card(
                    elevation: 1,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14),
                      side: BorderSide(color: Colors.grey.shade200),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(18),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Request Summary',
                            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                          ),
                          const Divider(height: 24),
                          _buildDetailRow(
                            icon: Icons.handyman,
                            label: 'Service',
                            value: service.name,
                          ),
                          const SizedBox(height: 12),
                          _buildDetailRow(
                            icon: Icons.notes,
                            label: 'Problem',
                            value: problemDescription,
                          ),
                          const SizedBox(height: 12),
                          _buildDetailRow(
                            icon: Icons.schedule,
                            label: 'Timing',
                            value: requestType == 'immediate'
                                ? 'Immediate (ASAP Dispatch)'
                                : 'Scheduled: $scheduledDate',
                          ),
                          const SizedBox(height: 12),
                          _buildDetailRow(
                            icon: Icons.location_on,
                            label: 'Address',
                            value: address,
                          ),
                          if (landmark != null && landmark!.isNotEmpty) ...[
                            const SizedBox(height: 12),
                            _buildDetailRow(
                              icon: Icons.flag,
                              label: 'Landmark',
                              value: landmark!,
                            ),
                          ],
                          if (directions != null && directions!.isNotEmpty) ...[
                            const SizedBox(height: 12),
                            _buildDetailRow(
                              icon: Icons.directions,
                              label: 'Directions',
                              value: directions!,
                            ),
                          ],
                          const Divider(height: 24),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              const Text(
                                'Estimated Base Price',
                                style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
                              ),
                              Text(
                                '₹${service.basePrice.toStringAsFixed(0)}',
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

                  const SizedBox(height: 20),

                  // Dispatch Policy Note
                  Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: Colors.blue.shade50.withOpacity(0.5),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.blue.shade100),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Icon(Icons.info_outline, size: 20, color: Color(0xFF1E40AF)),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            'When you tap "Request Service", our deterministic dispatch engine will find the nearest available verified worker from your local cooperative.',
                            style: TextStyle(fontSize: 12, color: Colors.blue.shade900),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Bottom Request CTA
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 10,
                  offset: const Offset(0, -4),
                ),
              ],
            ),
            child: SafeArea(
              child: SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  icon: const Icon(Icons.send_rounded, size: 20),
                  label: const Text(
                    'SUBMIT SERVICE REQUEST',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF1E40AF),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  onPressed: () {
                    Navigator.pushReplacement(
                      context,
                      MaterialPageRoute(
                        builder: (context) => FindingWorkerScreen(
                          appState: appState,
                          service: service,
                          problemDescription: problemDescription,
                          address: address,
                          landmark: landmark,
                          directions: directions,
                          requestType: requestType,
                          latitude: latitude,
                          longitude: longitude,
                          scheduledDate: scheduledDate,
                          scheduledStartTime: scheduledStartTime,
                        ),
                      ),
                    );
                  },
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailRow({
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
          width: 80,
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
