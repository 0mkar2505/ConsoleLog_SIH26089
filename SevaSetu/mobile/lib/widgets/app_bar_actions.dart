import 'package:flutter/material.dart';
import '../config/api_config.dart';
import '../state/app_state.dart';

class AppBarModeSwitcher extends StatelessWidget {
  final AppState appState;

  const AppBarModeSwitcher({super.key, required this.appState});

  @override
  Widget build(BuildContext context) {
    final isCustomer = appState.currentRole == 'customer';

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Role Toggle Button
        ActionChip(
          avatar: Icon(
            isCustomer ? Icons.person : Icons.engineering,
            size: 16,
            color: isCustomer ? const Color(0xFF1E40AF) : Colors.orange.shade800,
          ),
          label: Text(
            isCustomer ? 'Customer' : 'Worker',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: isCustomer ? const Color(0xFF1E40AF) : Colors.orange.shade900,
            ),
          ),
          backgroundColor: isCustomer ? Colors.blue.shade50 : Colors.orange.shade50,
          side: BorderSide(
            color: isCustomer ? Colors.blue.shade200 : Colors.orange.shade200,
          ),
          onPressed: () {
            _showUserSwitchDialog(context);
          },
        ),
        const SizedBox(width: 4),
        // Settings / Switcher Menu
        PopupMenuButton<String>(
          icon: const Icon(Icons.more_vert, size: 20),
          tooltip: 'App Options',
          onSelected: (value) {
            if (value == 'switch_mode') {
              appState.switchRole(isCustomer ? 'worker' : 'customer');
            } else if (value == 'switch_user') {
              _showUserSwitchDialog(context);
            } else if (value == 'api_config') {
              _showApiConfigDialog(context);
            } else if (value == 'reset') {
              appState.resetFlow();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Flow state reset to start.')),
              );
            }
          },
          itemBuilder: (context) => [
            PopupMenuItem(
              value: 'switch_mode',
              child: Row(
                children: [
                  Icon(
                    isCustomer ? Icons.engineering : Icons.person,
                    size: 18,
                    color: Colors.blue.shade700,
                  ),
                  const SizedBox(width: 8),
                  Text('Switch to ${isCustomer ? "Worker" : "Customer"} Mode'),
                ],
              ),
            ),
            const PopupMenuItem(
              value: 'switch_user',
              child: Row(
                children: [
                  Icon(Icons.switch_account, size: 18, color: Colors.blue),
                  SizedBox(width: 8),
                  Text('Select Demo Account'),
                ],
              ),
            ),
            const PopupMenuItem(
              value: 'api_config',
              child: Row(
                children: [
                  Icon(Icons.cloud_sync, size: 18, color: Colors.grey),
                  SizedBox(width: 8),
                  Text('Backend API Settings'),
                ],
              ),
            ),
            const PopupMenuItem(
              value: 'reset',
              child: Row(
                children: [
                  Icon(Icons.refresh, size: 18, color: Colors.grey),
                  SizedBox(width: 8),
                  Text('Reset Current Flow'),
                ],
              ),
            ),
          ],
        ),
      ],
    );
  }

  void _showUserSwitchDialog(BuildContext context) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return StatefulBuilder(
          builder: (modalCtx, setModalState) {
            return Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Select Demo Profile',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      IconButton(
                        icon: const Icon(Icons.close),
                        onPressed: () => Navigator.pop(ctx),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton.icon(
                          icon: const Icon(Icons.person, size: 18),
                          label: const Text('Customer Mode'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: appState.currentRole == 'customer'
                                ? const Color(0xFF1E40AF)
                                : Colors.grey.shade100,
                            foregroundColor: appState.currentRole == 'customer'
                                ? Colors.white
                                : Colors.black87,
                            elevation: 0,
                          ),
                          onPressed: () {
                            appState.switchRole('customer');
                            setModalState(() {});
                          },
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: ElevatedButton.icon(
                          icon: const Icon(Icons.engineering, size: 18),
                          label: const Text('Worker Mode'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: appState.currentRole == 'worker'
                                ? Colors.orange.shade700
                                : Colors.grey.shade100,
                            foregroundColor: appState.currentRole == 'worker'
                                ? Colors.white
                                : Colors.black87,
                            elevation: 0,
                          ),
                          onPressed: () {
                            appState.switchRole('worker');
                            setModalState(() {});
                          },
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    'Available Demo Accounts:',
                    style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Colors.grey),
                  ),
                  const SizedBox(height: 8),
                  Expanded(
                    child: ListView(
                      children: (appState.currentRole == 'customer'
                              ? appState.demoCustomers
                              : appState.demoWorkers)
                          .map((user) {
                        final isSelected = appState.currentUser?.userId == user.userId;
                        return ListTile(
                          contentPadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          leading: CircleAvatar(
                            backgroundColor: isSelected
                                ? (user.role == 'customer'
                                    ? const Color(0xFF1E40AF)
                                    : Colors.orange.shade700)
                                : Colors.grey.shade200,
                            child: Text(
                              user.name.isNotEmpty ? user.name[0] : 'U',
                              style: TextStyle(
                                color: isSelected ? Colors.white : Colors.black87,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          title: Text(
                            user.name,
                            style: TextStyle(
                              fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
                            ),
                          ),
                          subtitle: Text(
                            '${user.role.toUpperCase()} • ${user.phone}${user.serviceArea != null ? " • ${user.serviceArea}" : ""}',
                            style: const TextStyle(fontSize: 12),
                          ),
                          trailing: isSelected
                              ? const Icon(Icons.check_circle, color: Colors.green)
                              : null,
                          onTap: () {
                            appState.setCurrentUser(user);
                            Navigator.pop(ctx);
                          },
                        );
                      }).toList(),
                    ),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }

  void _showApiConfigDialog(BuildContext context) {
    final controller = TextEditingController(text: ApiConfig.baseUrl);

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Backend API URL'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Specify the FastAPI server base URL:',
              style: TextStyle(fontSize: 13, color: Colors.grey),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: controller,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                hintText: 'http://127.0.0.1:8000',
                labelText: 'Base URL',
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Default: ${ApiConfig.defaultBaseUrl}',
              style: const TextStyle(fontSize: 11, color: Colors.grey),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              ApiConfig.setBaseUrl(controller.text);
              Navigator.pop(ctx);
              appState.initApp();
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('API URL updated to: ${ApiConfig.baseUrl}')),
              );
            },
            child: const Text('Save & Reload'),
          ),
        ],
      ),
    );
  }
}
