import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../models/models.dart';
import '../../state/app_state.dart';
import '../../widgets/osm_location_map.dart';
import 'request_confirmation_screen.dart';

class RequestFormScreen extends StatefulWidget {
  final AppState appState;
  final ServiceItem service;

  const RequestFormScreen({
    super.key,
    required this.appState,
    required this.service,
  });

  @override
  State<RequestFormScreen> createState() => _RequestFormScreenState();
}

class _RequestFormScreenState extends State<RequestFormScreen> {
  final _formKey = GlobalKey<FormState>();

  final _problemController = TextEditingController(text: 'Kitchen pipe is leaking.');
  final _addressController = TextEditingController(text: '12 Station Road, Sion East, Mumbai');
  final _landmarkController = TextEditingController(text: 'Opposite Sion Railway Station');
  final _directionsController = TextEditingController(text: 'Gate 2, 3rd Floor, Flat 301');

  String _requestType = 'immediate'; // 'immediate' or 'scheduled'
  DateTime _scheduledDate = DateTime.now().add(const Duration(days: 1));
  TimeOfDay _scheduledTime = const TimeOfDay(hour: 10, minute: 0);

  double _latitude = 19.0400;
  double _longitude = 72.8625;

  final List<Map<String, dynamic>> _addressPresets = [
    {
      'label': 'Sion East (Rahul Home)',
      'address': '12 Station Road, Sion East, Mumbai',
      'landmark': 'Opposite Sion Railway Station',
      'directions': 'Gate 2, 3rd Floor, Flat 301',
      'lat': 19.0400,
      'lng': 72.8625,
    },
    {
      'label': 'Bandra West (Priya Home)',
      'address': 'Flat 402, Sea View Apartments, Bandra West, Mumbai',
      'landmark': 'Near Carter Road Promenade',
      'directions': 'Ring doorbell at main entrance',
      'lat': 19.0600,
      'lng': 72.8250,
    },
    {
      'label': 'Dadar West (Amit Home)',
      'address': '7 Hill Road, Dadar West, Mumbai',
      'landmark': 'Next to Plaza Cinema',
      'directions': '2nd Floor, Room 14',
      'lat': 19.0200,
      'lng': 72.8450,
    },
  ];

  @override
  void dispose() {
    _problemController.dispose();
    _addressController.dispose();
    _landmarkController.dispose();
    _directionsController.dispose();
    super.dispose();
  }

  Future<void> _selectDate(BuildContext context) async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _scheduledDate,
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 30)),
    );
    if (picked != null) {
      setState(() {
        _scheduledDate = picked;
      });
    }
  }

  Future<void> _selectTime(BuildContext context) async {
    final picked = await showTimePicker(
      context: context,
      initialTime: _scheduledTime,
    );
    if (picked != null) {
      setState(() {
        _scheduledTime = picked;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final dateFormat = DateFormat('EEE, dd MMM yyyy');

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: Text('${widget.service.name} Request', style: const TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        elevation: 0.5,
      ),
      body: Form(
        key: _formKey,
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Service Header Card
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.blue.shade50,
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: Colors.blue.shade100),
                      ),
                      child: Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(10),
                            decoration: BoxDecoration(
                              color: const Color(0xFF1E40AF),
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: const Icon(Icons.build, color: Colors.white, size: 22),
                          ),
                          const SizedBox(width: 14),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  widget.service.name,
                                  style: const TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                    color: Color(0xFF0F172A),
                                  ),
                                ),
                                Text(
                                  'Base Rate: ₹${widget.service.basePrice.toStringAsFixed(0)} • Fair Cooperative Allocation',
                                  style: TextStyle(fontSize: 12, color: Colors.blue.shade800),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 20),

                    // Immediate vs Scheduled Selector
                    const Text(
                      'Service Timing',
                      style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
                    ),
                    const SizedBox(height: 10),
                    Row(
                      children: [
                        Expanded(
                          child: InkWell(
                            onTap: () => setState(() => _requestType = 'immediate'),
                            borderRadius: BorderRadius.circular(12),
                            child: Container(
                              padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 12),
                              decoration: BoxDecoration(
                                color: _requestType == 'immediate'
                                    ? const Color(0xFF1E40AF)
                                    : Colors.white,
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(
                                  color: _requestType == 'immediate'
                                      ? const Color(0xFF1E40AF)
                                      : Colors.grey.shade300,
                                ),
                              ),
                              child: Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(
                                    Icons.flash_on,
                                    size: 18,
                                    color: _requestType == 'immediate' ? Colors.white : Colors.black87,
                                  ),
                                  const SizedBox(width: 6),
                                  Text(
                                    'Immediate (ASAP)',
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 13,
                                      color: _requestType == 'immediate' ? Colors.white : Colors.black87,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: InkWell(
                            onTap: () => setState(() => _requestType = 'scheduled'),
                            borderRadius: BorderRadius.circular(12),
                            child: Container(
                              padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 12),
                              decoration: BoxDecoration(
                                color: _requestType == 'scheduled'
                                    ? const Color(0xFF1E40AF)
                                    : Colors.white,
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(
                                  color: _requestType == 'scheduled'
                                      ? const Color(0xFF1E40AF)
                                      : Colors.grey.shade300,
                                ),
                              ),
                              child: Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(
                                    Icons.calendar_today,
                                    size: 16,
                                    color: _requestType == 'scheduled' ? Colors.white : Colors.black87,
                                  ),
                                  const SizedBox(width: 6),
                                  Text(
                                    'Schedule Later',
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 13,
                                      color: _requestType == 'scheduled' ? Colors.white : Colors.black87,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),

                    if (_requestType == 'scheduled') ...[
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Expanded(
                            child: OutlinedButton.icon(
                              icon: const Icon(Icons.date_range, size: 16),
                              label: Text(dateFormat.format(_scheduledDate), style: const TextStyle(fontSize: 12)),
                              style: OutlinedButton.styleFrom(
                                padding: const EdgeInsets.symmetric(vertical: 12),
                                backgroundColor: Colors.white,
                              ),
                              onPressed: () => _selectDate(context),
                            ),
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: OutlinedButton.icon(
                              icon: const Icon(Icons.access_time, size: 16),
                              label: Text(_scheduledTime.format(context), style: const TextStyle(fontSize: 12)),
                              style: OutlinedButton.styleFrom(
                                padding: const EdgeInsets.symmetric(vertical: 12),
                                backgroundColor: Colors.white,
                              ),
                              onPressed: () => _selectTime(context),
                            ),
                          ),
                        ],
                      ),
                    ],

                    const SizedBox(height: 20),

                    // Problem Description
                    const Text(
                      'Problem Description',
                      style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
                    ),
                    const SizedBox(height: 8),
                    TextFormField(
                      controller: _problemController,
                      maxLines: 3,
                      decoration: InputDecoration(
                        hintText: 'Describe the issue (e.g., Kitchen pipe is leaking)',
                        filled: true,
                        fillColor: Colors.white,
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: BorderSide(color: Colors.grey.shade300),
                        ),
                      ),
                      validator: (value) {
                        if (value == null || value.trim().isEmpty) {
                          return 'Please enter problem description';
                        }
                        return null;
                      },
                    ),

                    const SizedBox(height: 20),

                    // Address & Location Section
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'Service Location / Address',
                          style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
                        ),
                        PopupMenuButton<Map<String, dynamic>>(
                          tooltip: 'Choose Preset Address',
                          child: const Padding(
                            padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                            child: Row(
                              children: [
                                Icon(Icons.bookmark_border, size: 16, color: Color(0xFF1E40AF)),
                                SizedBox(width: 4),
                                Text('Presets', style: TextStyle(color: Color(0xFF1E40AF), fontSize: 13, fontWeight: FontWeight.bold)),
                              ],
                            ),
                          ),
                          onSelected: (preset) {
                            setState(() {
                              _addressController.text = preset['address'];
                              _landmarkController.text = preset['landmark'];
                              _directionsController.text = preset['directions'];
                              _latitude = preset['lat'];
                              _longitude = preset['lng'];
                            });
                          },
                          itemBuilder: (context) => _addressPresets
                              .map(
                                (p) => PopupMenuItem(
                                  value: p,
                                  child: Text(p['label'] as String, style: const TextStyle(fontSize: 13)),
                                ),
                              )
                              .toList(),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),

                    // Interactive OpenStreetMap Location Picker
                    OsmLocationMap(
                      latitude: _latitude,
                      longitude: _longitude,
                      isInteractive: true,
                      height: 200,
                      onLocationChanged: (newPoint) {
                        setState(() {
                          _latitude = newPoint.latitude;
                          _longitude = newPoint.longitude;
                        });
                      },
                    ),
                    const SizedBox(height: 8),

                    // Coordinate indicator chip
                    Row(
                      children: [
                        Icon(Icons.gps_fixed, size: 13, color: Colors.blue.shade700),
                        const SizedBox(width: 4),
                        Text(
                          'Pinned: ${_latitude.toStringAsFixed(4)}, ${_longitude.toStringAsFixed(4)}',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w600,
                            color: Colors.blue.shade900,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _addressController,
                      decoration: InputDecoration(
                        labelText: 'Street Address',
                        prefixIcon: const Icon(Icons.location_on_outlined),
                        filled: true,
                        fillColor: Colors.white,
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: BorderSide(color: Colors.grey.shade300),
                        ),
                      ),
                      validator: (value) {
                        if (value == null || value.trim().isEmpty) {
                          return 'Please enter address';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _landmarkController,
                      decoration: InputDecoration(
                        labelText: 'Landmark',
                        hintText: 'e.g., Opposite Sion Railway Station',
                        prefixIcon: const Icon(Icons.flag_outlined),
                        filled: true,
                        fillColor: Colors.white,
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: BorderSide(color: Colors.grey.shade300),
                        ),
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _directionsController,
                      decoration: InputDecoration(
                        labelText: 'Additional Directions / Flat No.',
                        hintText: 'e.g., Gate 2, 3rd Floor, Flat 301',
                        prefixIcon: const Icon(Icons.directions_outlined),
                        filled: true,
                        fillColor: Colors.white,
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: BorderSide(color: Colors.grey.shade300),
                        ),
                      ),
                    ),
                  ],
                ),
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
                    onPressed: () {
                      if (_formKey.currentState?.validate() ?? false) {
                        DateTime? scheduledDateTime;
                        if (_requestType == 'scheduled') {
                          scheduledDateTime = DateTime(
                            _scheduledDate.year,
                            _scheduledDate.month,
                            _scheduledDate.day,
                            _scheduledTime.hour,
                            _scheduledTime.minute,
                          );
                        }

                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => RequestConfirmationScreen(
                              appState: widget.appState,
                              service: widget.service,
                              problemDescription: _problemController.text.trim(),
                              address: _addressController.text.trim(),
                              landmark: _landmarkController.text.trim().isNotEmpty
                                  ? _landmarkController.text.trim()
                                  : null,
                              directions: _directionsController.text.trim().isNotEmpty
                                  ? _directionsController.text.trim()
                                  : null,
                              requestType: _requestType,
                              latitude: _latitude,
                              longitude: _longitude,
                              scheduledDate: _requestType == 'scheduled'
                                  ? DateFormat('yyyy-MM-dd').format(_scheduledDate)
                                  : null,
                              scheduledStartTime: scheduledDateTime,
                            ),
                          ),
                        );
                      }
                    },
                    child: const Text(
                      'Review Request Details',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
