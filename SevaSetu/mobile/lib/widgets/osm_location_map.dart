import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

/// Reusable OpenStreetMap component for SevaSetu Customer and Worker applications.
/// Renders standard OSM tiles via flutter_map without requiring paid map APIs.
class OsmLocationMap extends StatefulWidget {
  final double latitude;
  final double longitude;
  final bool isInteractive;
  final ValueChanged<LatLng>? onLocationChanged;
  final double height;
  final String? markerLabel;
  final Color markerColor;
  final IconData markerIcon;
  final double initialZoom;
  final bool showRecenterButton;

  const OsmLocationMap({
    super.key,
    required this.latitude,
    required this.longitude,
    this.isInteractive = false,
    this.onLocationChanged,
    this.height = 220,
    this.markerLabel,
    this.markerColor = Colors.red,
    this.markerIcon = Icons.location_on,
    this.initialZoom = 15.0,
    this.showRecenterButton = true,
  });

  @override
  State<OsmLocationMap> createState() => _OsmLocationMapState();
}

class _OsmLocationMapState extends State<OsmLocationMap> {
  late MapController _mapController;
  late LatLng _currentLocation;

  @override
  void initState() {
    super.initState();
    _mapController = MapController();
    _currentLocation = LatLng(widget.latitude, widget.longitude);
  }

  @override
  void didUpdateWidget(covariant OsmLocationMap oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.latitude != widget.latitude ||
        oldWidget.longitude != widget.longitude) {
      _currentLocation = LatLng(widget.latitude, widget.longitude);
      _mapController.move(_currentLocation, widget.initialZoom);
    }
  }

  @override
  void dispose() {
    _mapController.dispose();
    super.dispose();
  }

  void _handleTap(TapPosition tapPosition, LatLng point) {
    if (!widget.isInteractive) return;
    setState(() {
      _currentLocation = point;
    });
    if (widget.onLocationChanged != null) {
      widget.onLocationChanged!(point);
    }
  }

  void _recenter() {
    _mapController.move(_currentLocation, widget.initialZoom);
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: widget.height,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.grey.shade300),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 6,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      clipBehavior: Clip.antiAlias,
      child: Stack(
        children: [
          FlutterMap(
            mapController: _mapController,
            options: MapOptions(
              initialCenter: _currentLocation,
              initialZoom: widget.initialZoom,
              minZoom: 4,
              maxZoom: 19,
              onTap: _handleTap,
              interactionOptions: InteractionOptions(
                flags: widget.isInteractive
                    ? InteractiveFlag.all
                    : (InteractiveFlag.pinchZoom | InteractiveFlag.drag),
              ),
            ),
            children: [
              TileLayer(
                urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                userAgentPackageName: 'com.consolelog.sevasetu',
                maxZoom: 19,
              ),
              MarkerLayer(
                markers: [
                  Marker(
                    point: _currentLocation,
                    width: 46,
                    height: 46,
                    alignment: Alignment.topCenter,
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          widget.markerIcon,
                          color: widget.markerColor,
                          size: 34,
                          shadows: const [
                            Shadow(
                              color: Colors.black38,
                              blurRadius: 4,
                              offset: Offset(0, 2),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ],
          ),

          // OSM Attribution Tag
          Positioned(
            bottom: 4,
            left: 6,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.8),
                borderRadius: BorderRadius.circular(4),
              ),
              child: const Text(
                '© OpenStreetMap contributors',
                style: TextStyle(fontSize: 9, color: Colors.black87),
              ),
            ),
          ),

          // Hint banner for interactive mode
          if (widget.isInteractive)
            Positioned(
              top: 8,
              left: 8,
              right: 8,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.black.withValues(alpha: 0.72),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.touch_app, color: Colors.white, size: 14),
                    SizedBox(width: 6),
                    Expanded(
                      child: Text(
                        'Tap anywhere on map to pin service location',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 11,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),

          // Recenter FAB button
          if (widget.showRecenterButton)
            Positioned(
              bottom: 8,
              right: 8,
              child: Material(
                color: Colors.white,
                shape: const CircleBorder(),
                elevation: 2,
                child: InkWell(
                  customBorder: const CircleBorder(),
                  onTap: _recenter,
                  child: const Padding(
                    padding: EdgeInsets.all(8.0),
                    child: Icon(Icons.my_location, size: 18, color: Color(0xFF1E40AF)),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
