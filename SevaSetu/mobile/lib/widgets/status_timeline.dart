import 'package:flutter/material.dart';

class StatusTimelineWidget extends StatelessWidget {
  final String currentStatus;

  const StatusTimelineWidget({super.key, required this.currentStatus});

  static const List<Map<String, String>> steps = [
    {'status': 'pending', 'label': 'Requested', 'desc': 'Request created'},
    {'status': 'assigned', 'label': 'Assigned', 'desc': 'Worker matched'},
    {'status': 'accepted', 'label': 'Accepted', 'desc': 'Worker accepted job'},
    {'status': 'en_route', 'label': 'En Route', 'desc': 'Worker on the way'},
    {'status': 'arrived', 'label': 'Arrived', 'desc': 'Worker at location'},
    {'status': 'in_progress', 'label': 'In Progress', 'desc': 'Service underway'},
    {'status': 'completed', 'label': 'Completed', 'desc': 'Work done & verified'},
  ];

  int _getStatusIndex(String status) {
    switch (status.toLowerCase()) {
      case 'pending':
        return 0;
      case 'assigned':
      case 'allocated':
      case 'dispatching':
        return 1;
      case 'accepted':
        return 2;
      case 'en_route':
        return 3;
      case 'arrived':
        return 4;
      case 'in_progress':
        return 5;
      case 'completed':
      case 'fulfilled':
        return 6;
      default:
        return 0;
    }
  }

  @override
  Widget build(BuildContext context) {
    final currentIndex = _getStatusIndex(currentStatus);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Job Progress Timeline',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: currentIndex == 6 ? Colors.green.shade50 : Colors.blue.shade50,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: currentIndex == 6 ? Colors.green.shade300 : Colors.blue.shade300,
                  ),
                ),
                child: Text(
                  steps[currentIndex]['label']!.toUpperCase(),
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                    color: currentIndex == 6 ? Colors.green.shade700 : Colors.blue.shade700,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ...List.generate(steps.length, (index) {
            final isDone = index <= currentIndex;
            final isCurrent = index == currentIndex;
            final isLast = index == steps.length - 1;
            final step = steps[index];

            return Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Column(
                  children: [
                    Container(
                      width: 24,
                      height: 24,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: isCurrent
                            ? (index == 6 ? Colors.green : const Color(0xFF1E40AF))
                            : isDone
                                ? Colors.green
                                : Colors.grey.shade300,
                        border: isCurrent
                            ? Border.all(
                                color: (index == 6 ? Colors.green : const Color(0xFF1E40AF))
                                    .withOpacity(0.3),
                                width: 4,
                              )
                            : null,
                      ),
                      child: Center(
                        child: isDone
                            ? const Icon(Icons.check, size: 14, color: Colors.white)
                            : Container(
                                width: 8,
                                height: 8,
                                decoration: const BoxDecoration(
                                  shape: BoxShape.circle,
                                  color: Colors.white,
                                ),
                              ),
                      ),
                    ),
                    if (!isLast)
                      Container(
                        width: 2,
                        height: 28,
                        color: index < currentIndex ? Colors.green : Colors.grey.shade300,
                      ),
                  ],
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.only(top: 2.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          step['label']!,
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: isCurrent ? FontWeight.bold : FontWeight.w600,
                            color: isCurrent
                                ? (index == 6 ? Colors.green.shade800 : const Color(0xFF1E40AF))
                                : isDone
                                    ? Colors.grey.shade800
                                    : Colors.grey.shade400,
                          ),
                        ),
                        Text(
                          step['desc']!,
                          style: TextStyle(
                            fontSize: 12,
                            color: isCurrent ? Colors.grey.shade700 : Colors.grey.shade500,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            );
          }),
        ],
      ),
    );
  }
}
