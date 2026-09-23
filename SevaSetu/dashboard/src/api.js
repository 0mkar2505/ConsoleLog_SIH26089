/**
 * Centralized API client for the SevaSetu Admin / Cooperative Dashboard.
 * Connects directly to the FastAPI backend running on localhost:8000.
 */

const API_BASE = import.meta.env.VITE_API_URL || '';

async function fetchJson(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  try {
    const response = await fetch(url, {
      credentials: 'omit',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errBody = await response.text();
      throw new Error(`API Error [${response.status}]: ${errBody || response.statusText}`);
    }

    return await response.json();
  } catch (err) {
    console.error(`Failed to fetch ${url}:`, err);
    throw err;
  }
}

export const adminApi = {
  getOverview: () => fetchJson('/api/admin/overview'),
  getRequests: (limit = 50) => fetchJson(`/api/admin/requests?limit=${limit}`),
  getRequestDetail: (id) => fetchJson(`/api/admin/requests/${id}`),
  getWorkers: () => fetchJson('/api/admin/workers'),
  getCustomers: () => fetchJson('/api/admin/customers'),
  getServices: () => fetchJson('/api/admin/services'),
  getHealth: () => fetchJson('/api/health'),
  getSmsLogs: (limit = 50) => fetchJson(`/api/dispatch-ops/sms/logs?limit=${limit}`),
  simulateInboundSms: (sender_phone, message) => fetchJson('/api/dispatch-ops/sms/inbound', {
    method: 'POST',
    body: JSON.stringify({ sender_phone, message }),
  }),
};
