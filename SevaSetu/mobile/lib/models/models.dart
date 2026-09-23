class ServiceItem {
  final String id;
  final String name;
  final String description;
  final double basePrice;
  final String category;
  final bool isActive;

  ServiceItem({
    required this.id,
    required this.name,
    required this.description,
    required this.basePrice,
    required this.category,
    this.isActive = true,
  });

  factory ServiceItem.fromJson(Map<String, dynamic> json) {
    return ServiceItem(
      id: json['id']?.toString() ?? json['_id']?.toString() ?? '',
      name: json['name']?.toString() ?? '',
      description: json['description']?.toString() ?? '',
      basePrice: (json['base_price'] as num?)?.toDouble() ?? 350.0,
      category: json['category']?.toString() ?? 'General',
      isActive: json['is_active'] ?? true,
    );
  }
}

class DemoUser {
  final String userId;
  final String? customerId;
  final String? workerId;
  final String name;
  final String email;
  final String phone;
  final String role; // 'customer' or 'worker'
  final List<String> digitalAccess;
  final String? serviceArea;

  DemoUser({
    required this.userId,
    this.customerId,
    this.workerId,
    required this.name,
    required this.email,
    required this.phone,
    required this.role,
    this.digitalAccess = const ['smartphone'],
    this.serviceArea,
  });

  factory DemoUser.fromJson(Map<String, dynamic> json, String role) {
    return DemoUser(
      userId: json['user_id']?.toString() ?? '',
      customerId: json['customer_id']?.toString(),
      workerId: json['worker_id']?.toString(),
      name: json['name']?.toString() ?? '',
      email: json['email']?.toString() ?? '',
      phone: json['phone']?.toString() ?? '',
      role: role,
      digitalAccess: (json['digital_access'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          ['smartphone'],
      serviceArea: json['service_area']?.toString(),
    );
  }
}

class CustomerAddress {
  final String id;
  final String label;
  final String address;
  final String? landmark;
  final String? directions;
  final double? latitude;
  final double? longitude;

  CustomerAddress({
    required this.id,
    required this.label,
    required this.address,
    this.landmark,
    this.directions,
    this.latitude,
    this.longitude,
  });

  factory CustomerAddress.fromJson(Map<String, dynamic> json) {
    double? lat;
    double? lng;
    if (json['location'] != null && json['location']['coordinates'] is List) {
      final coords = json['location']['coordinates'] as List;
      if (coords.length >= 2) {
        lng = (coords[0] as num).toDouble();
        lat = (coords[1] as num).toDouble();
      }
    }
    return CustomerAddress(
      id: json['id']?.toString() ?? '',
      label: json['label']?.toString() ?? 'Address',
      address: json['address']?.toString() ?? '',
      landmark: json['landmark']?.toString(),
      directions: json['additional_directions']?.toString(),
      latitude: lat,
      longitude: lng,
    );
  }
}

class WorkerProfile {
  final String workerId;
  final String name;
  final String phone;
  final double ratingAverage;
  final List<String> digitalAccess;
  final String? serviceArea;

  WorkerProfile({
    required this.workerId,
    required this.name,
    required this.phone,
    required this.ratingAverage,
    this.digitalAccess = const ['smartphone'],
    this.serviceArea,
  });

  factory WorkerProfile.fromJson(Map<String, dynamic> json) {
    return WorkerProfile(
      workerId: json['worker_id']?.toString() ?? '',
      name: json['name']?.toString() ?? 'Assigned Worker',
      phone: json['phone']?.toString() ?? '+919844444401',
      ratingAverage: (json['rating_average'] as num?)?.toDouble() ?? 4.8,
      digitalAccess: (json['digital_access'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          ['smartphone'],
      serviceArea: json['service_area']?.toString(),
    );
  }
}

class BookingInfo {
  final String id;
  final String? requestId;
  final String customerId;
  final String workerId;
  final String serviceId;
  final String address;
  final String? landmark;
  final String? directions;
  final String status;
  final double estimatedPrice;
  final String? scheduledStart;
  final String? completedAt;

  BookingInfo({
    required this.id,
    this.requestId,
    required this.customerId,
    required this.workerId,
    required this.serviceId,
    required this.address,
    this.landmark,
    this.directions,
    required this.status,
    required this.estimatedPrice,
    this.scheduledStart,
    this.completedAt,
  });

  factory BookingInfo.fromJson(Map<String, dynamic> json) {
    return BookingInfo(
      id: json['id']?.toString() ?? json['_id']?.toString() ?? '',
      requestId: json['request_id']?.toString(),
      customerId: json['customer_id']?.toString() ?? '',
      workerId: json['worker_id']?.toString() ?? '',
      serviceId: json['service_id']?.toString() ?? '',
      address: json['address']?.toString() ?? '',
      landmark: json['landmark']?.toString(),
      directions: json['directions']?.toString(),
      status: json['status']?.toString() ?? 'assigned',
      estimatedPrice: (json['estimated_price'] as num?)?.toDouble() ?? 350.0,
      scheduledStart: json['scheduled_start']?.toString(),
      completedAt: json['completed_at']?.toString(),
    );
  }
}

class ServiceRequest {
  final String id;
  final String customerId;
  final String serviceId;
  final String serviceName;
  final String problemDescription;
  final String requestType;
  final String address;
  final String? landmark;
  final String? directions;
  final String status;
  final double? latitude;
  final double? longitude;
  final String? preferredDate;
  final String? preferredStartTime;
  final String? createdAt;

  ServiceRequest({
    required this.id,
    required this.customerId,
    required this.serviceId,
    required this.serviceName,
    required this.problemDescription,
    required this.requestType,
    required this.address,
    this.landmark,
    this.directions,
    required this.status,
    this.latitude,
    this.longitude,
    this.preferredDate,
    this.preferredStartTime,
    this.createdAt,
  });

  factory ServiceRequest.fromJson(Map<String, dynamic> json) {
    double? lat;
    double? lng;
    if (json['location'] != null && json['location']['coordinates'] is List) {
      final coords = json['location']['coordinates'] as List;
      if (coords.length >= 2) {
        lng = (coords[0] as num).toDouble();
        lat = (coords[1] as num).toDouble();
      }
    }
    return ServiceRequest(
      id: json['id']?.toString() ?? json['_id']?.toString() ?? '',
      customerId: json['customer_id']?.toString() ?? '',
      serviceId: json['service_id']?.toString() ?? '',
      serviceName: json['service_name']?.toString() ?? 'Service',
      problemDescription: json['problem_description']?.toString() ?? '',
      requestType: json['request_type']?.toString() ?? 'immediate',
      address: json['address']?.toString() ?? '',
      landmark: json['landmark']?.toString(),
      directions: json['directions']?.toString(),
      status: json['status']?.toString() ?? 'pending',
      latitude: lat,
      longitude: lng,
      preferredDate: json['preferred_date']?.toString(),
      preferredStartTime: json['preferred_start_time']?.toString(),
      createdAt: json['created_at']?.toString(),
    );
  }
}

class WorkerJob {
  final String bookingId;
  final String? requestId;
  final String? workerId;
  final String serviceName;
  final String customerName;
  final String customerPhone;
  final String problemDescription;
  final String requestType;
  final String address;
  final String? landmark;
  final String? directions;
  final String status;
  final double estimatedPrice;
  final double? latitude;
  final double? longitude;
  final String? createdAt;

  WorkerJob({
    required this.bookingId,
    this.requestId,
    this.workerId,
    required this.serviceName,
    required this.customerName,
    required this.customerPhone,
    required this.problemDescription,
    required this.requestType,
    required this.address,
    this.landmark,
    this.directions,
    this.latitude,
    this.longitude,
    required this.status,
    required this.estimatedPrice,
    this.createdAt,
  });

  factory WorkerJob.fromJson(Map<String, dynamic> json) {
    double? lat = (json['latitude'] as num?)?.toDouble();
    double? lng = (json['longitude'] as num?)?.toDouble();
    if ((lat == null || lng == null) && json['location'] != null && json['location']['coordinates'] is List) {
      final coords = json['location']['coordinates'] as List;
      if (coords.length >= 2) {
        lng = (coords[0] as num).toDouble();
        lat = (coords[1] as num).toDouble();
      }
    }

    return WorkerJob(
      bookingId: json['booking_id']?.toString() ?? json['id']?.toString() ?? json['_id']?.toString() ?? '',
      requestId: json['request_id']?.toString(),
      workerId: json['worker_id']?.toString(),
      serviceName: json['service_name']?.toString() ?? 'Service',
      customerName: json['customer_name']?.toString() ?? 'Customer',
      customerPhone: json['customer_phone']?.toString() ?? '+919811111111',
      problemDescription: json['problem_description']?.toString() ?? '',
      requestType: json['request_type']?.toString() ?? 'immediate',
      address: json['address']?.toString() ?? '',
      landmark: json['landmark']?.toString(),
      directions: json['directions']?.toString(),
      latitude: lat,
      longitude: lng,
      status: json['status']?.toString() ?? 'assigned',
      estimatedPrice: (json['estimated_price'] as num?)?.toDouble() ?? 350.0,
      createdAt: json['created_at']?.toString(),
    );
  }
}
