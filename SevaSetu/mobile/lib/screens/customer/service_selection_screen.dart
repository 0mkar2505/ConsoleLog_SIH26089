import 'package:flutter/material.dart';
import '../../models/models.dart';
import '../../state/app_state.dart';
import 'request_form_screen.dart';

class ServiceSelectionScreen extends StatefulWidget {
  final AppState appState;

  const ServiceSelectionScreen({super.key, required this.appState});

  @override
  State<ServiceSelectionScreen> createState() => _ServiceSelectionScreenState();
}

class _ServiceSelectionScreenState extends State<ServiceSelectionScreen> {
  ServiceItem? _selected;

  @override
  void initState() {
    super.initState();
    _selected = widget.appState.selectedService ??
        (widget.appState.services.isNotEmpty ? widget.appState.services.first : null);
  }

  IconData _getServiceIcon(String name) {
    switch (name.toLowerCase()) {
      case 'plumbing':
        return Icons.plumbing;
      case 'electrical':
        return Icons.electric_bolt;
      case 'cleaning':
        return Icons.cleaning_services;
      case 'carpentry':
        return Icons.handyman;
      case 'painting':
        return Icons.format_paint;
      case 'appliance repair':
        return Icons.home_repair_service;
      default:
        return Icons.build;
    }
  }

  @override
  Widget build(BuildContext context) {
    final services = widget.appState.services;

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: const Text('Select a Service', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        elevation: 0.5,
      ),
      body: services.isEmpty
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                Expanded(
                  child: ListView.separated(
                    padding: const EdgeInsets.all(16),
                    itemCount: services.length,
                    separatorBuilder: (context, index) => const SizedBox(height: 12),
                    itemBuilder: (context, index) {
                      final item = services[index];
                      final isSelected = _selected?.id == item.id;

                      return Card(
                        elevation: isSelected ? 2 : 0.5,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                          side: BorderSide(
                            color: isSelected ? const Color(0xFF1E40AF) : Colors.grey.shade200,
                            width: isSelected ? 2 : 1,
                          ),
                        ),
                        child: InkWell(
                          borderRadius: BorderRadius.circular(14),
                          onTap: () {
                            setState(() {
                              _selected = item;
                            });
                            widget.appState.selectService(item);
                          },
                          child: Padding(
                            padding: const EdgeInsets.all(16.0),
                            child: Row(
                              children: [
                                Container(
                                  padding: const EdgeInsets.all(12),
                                  decoration: BoxDecoration(
                                    color: isSelected
                                        ? const Color(0xFF1E40AF).withOpacity(0.12)
                                        : Colors.grey.shade100,
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  child: Icon(
                                    _getServiceIcon(item.name),
                                    color: isSelected ? const Color(0xFF1E40AF) : Colors.black87,
                                    size: 28,
                                  ),
                                ),
                                const SizedBox(width: 16),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Row(
                                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                        children: [
                                          Text(
                                            item.name,
                                            style: const TextStyle(
                                              fontSize: 16,
                                              fontWeight: FontWeight.bold,
                                              color: Color(0xFF0F172A),
                                            ),
                                          ),
                                          Text(
                                            '₹${item.basePrice.toStringAsFixed(0)}',
                                            style: const TextStyle(
                                              fontSize: 15,
                                              fontWeight: FontWeight.bold,
                                              color: Colors.green,
                                            ),
                                          ),
                                        ],
                                      ),
                                      const SizedBox(height: 4),
                                      Text(
                                        item.description,
                                        style: TextStyle(
                                          fontSize: 12,
                                          color: Colors.grey.shade600,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Radio<String>(
                                  value: item.id,
                                  groupValue: _selected?.id,
                                  activeColor: const Color(0xFF1E40AF),
                                  onChanged: (val) {
                                    setState(() {
                                      _selected = item;
                                    });
                                    widget.appState.selectService(item);
                                  },
                                ),
                              ],
                            ),
                          ),
                        ),
                      );
                    },
                  ),
                ),
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
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF1E40AF),
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        onPressed: _selected == null
                            ? null
                            : () {
                                widget.appState.selectService(_selected!);
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (context) => RequestFormScreen(
                                      appState: widget.appState,
                                      service: _selected!,
                                    ),
                                  ),
                                );
                              },
                        child: Text(
                          'Continue with ${_selected?.name ?? "Selected Service"}',
                          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
    );
  }
}

