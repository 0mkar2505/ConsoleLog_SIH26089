import { useState, useEffect } from 'react';
import { 
  ClipboardList, 
  Activity, 
  UserCheck, 
  Users, 
  CheckCircle2, 
  Clock, 
  AlertCircle
} from 'lucide-react';
import { adminApi } from '../api';
import Topbar from '../components/Topbar';
import StatusBadge from '../components/StatusBadge';
import RequestDetailModal from '../components/RequestDetailModal';

export default function Overview() {
  const [data, setData] = useState(null);
  const [recentRequests, setRecentRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedReq, setSelectedReq] = useState(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [overviewRes, reqsRes] = await Promise.all([
        adminApi.getOverview(),
        adminApi.getRequests(8),
      ]);
      setData(overviewRes);
      setRecentRequests(reqsRes);
    } catch (err) {
      setError(err.message || 'Failed to load dashboard data from backend.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const stats = data?.stats || {};
  const capacity = data?.capacity_by_service || [];

  return (
    <div>
      <Topbar
        title="Operations Overview"
        subtitle="Real-time cooperative workforce deployment and platform metrics"
        onRefresh={loadData}
        loading={loading}
      />

      <div className="page-content">
        {error && (
          <div className="error-banner">
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <AlertCircle size={15} />
              <span>{error}</span>
            </span>
            <button className="action-btn" onClick={loadData}>Retry</button>
          </div>
        )}

        {/* Top-Level Summary Cards */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-header">
              <span className="stat-title">Active Requests</span>
              <span className="stat-icon">
                <ClipboardList size={14} />
              </span>
            </div>
            <div className="stat-value">{stats.active_requests ?? '—'}</div>
            <div className="stat-subtext">Pending and in-flight orders</div>
          </div>

          <div className="stat-card">
            <div className="stat-header">
              <span className="stat-title">Active Jobs</span>
              <span className="stat-icon">
                <Activity size={14} />
              </span>
            </div>
            <div className="stat-value">{stats.active_jobs ?? '—'}</div>
            <div className="stat-subtext">Assigned or in progress</div>
          </div>

          <div className="stat-card">
            <div className="stat-header">
              <span className="stat-title">Available Workers</span>
              <span className="stat-icon" style={{ color: '#16a34a' }}>
                <UserCheck size={14} />
              </span>
            </div>
            <div className="stat-value">{stats.available_workers ?? '—'}</div>
            <div className="stat-subtext">Ready for immediate allocation</div>
          </div>

          <div className="stat-card">
            <div className="stat-header">
              <span className="stat-title">Total Workforce</span>
              <span className="stat-icon">
                <Users size={14} />
              </span>
            </div>
            <div className="stat-value">{stats.total_workers ?? '—'}</div>
            <div className="stat-subtext">Across active cooperatives</div>
          </div>

          <div className="stat-card">
            <div className="stat-header">
              <span className="stat-title">Completed Jobs</span>
              <span className="stat-icon" style={{ color: '#2563eb' }}>
                <CheckCircle2 size={14} />
              </span>
            </div>
            <div className="stat-value">{stats.completed_jobs ?? '—'}</div>
            <div className="stat-subtext">Delivered and reconciled</div>
          </div>

          <div className="stat-card">
            <div className="stat-header">
              <span className="stat-title">Pending Queue</span>
              <span className="stat-icon" style={{ color: '#d97706' }}>
                <Clock size={14} />
              </span>
            </div>
            <div className="stat-value">{stats.pending_requests ?? '—'}</div>
            <div className="stat-subtext">Awaiting matching</div>
          </div>
        </div>

        {/* Cooperative Workforce Capacity Section */}
        <div className="section-card">
          <div className="section-header">
            <div>
              <h3 className="section-title">Cooperative Workforce Capacity</h3>
              <p className="section-subtitle">
                Current trade capacity calculated live across member cooperatives
              </p>
            </div>
          </div>

          {capacity.length === 0 ? (
            <div className="empty-state">
              {loading ? <span className="loading-spinner"></span> : 'No capacity records available.'}
            </div>
          ) : (
            <div className="capacity-grid">
              {capacity.map((c) => {
                const total = c.total_workers || 0;
                const availPct = total > 0 ? (c.available / total) * 100 : 0;
                const busyPct = total > 0 ? (c.busy / total) * 100 : 0;

                return (
                  <div key={c.service_id} className="capacity-card">
                    <div className="capacity-title">
                      <span>{c.service_name}</span>
                      <span style={{ fontSize: '0.6875rem', color: '#64748b' }}>₹{c.base_price} base</span>
                    </div>

                    <div className="capacity-metrics">
                      <div className="cap-col">
                        <span className="cap-label">Available</span>
                        <div className="cap-num cap-avail">{c.available}</div>
                      </div>
                      <div className="cap-col">
                        <span className="cap-label">Busy</span>
                        <div className="cap-num cap-busy">{c.busy}</div>
                      </div>
                      <div className="cap-col">
                        <span className="cap-label">Total</span>
                        <div className="cap-num" style={{ color: '#334155' }}>{c.total_workers}</div>
                      </div>
                    </div>

                    <div className="capacity-progress">
                      <div className="cap-bar-avail" style={{ width: `${availPct}%` }}></div>
                      <div className="cap-bar-busy" style={{ width: `${busyPct}%` }}></div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Recent Active Requests Table */}
        <div className="section-card">
          <div className="section-header">
            <div>
              <h3 className="section-title">Recent Service Requests</h3>
              <p className="section-subtitle">Live request feed — click row for dispatch details</p>
            </div>
          </div>

          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Ref ID</th>
                  <th>Service</th>
                  <th>Customer</th>
                  <th>Worker</th>
                  <th>Status</th>
                  <th>Mode</th>
                  <th>Address</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                {recentRequests.length === 0 ? (
                  <tr>
                    <td colSpan="8" style={{ textAlign: 'center', padding: '2rem' }}>
                      {loading ? <span className="loading-spinner"></span> : 'No active requests in queue.'}
                    </td>
                  </tr>
                ) : (
                  recentRequests.map((req) => (
                    <tr 
                      key={req.request_id} 
                      className="clickable-row"
                      onClick={() => setSelectedReq(req)}
                    >
                      <td style={{ fontFamily: 'monospace', fontWeight: 600, color: '#0f172a' }}>
                        {req.request_id.slice(-6).toUpperCase()}
                      </td>
                      <td style={{ fontWeight: 600 }}>{req.service}</td>
                      <td>
                        <div style={{ fontWeight: 500 }}>{req.customer_name}</div>
                        {req.customer_phone && (
                          <div style={{ fontSize: '0.6875rem', color: '#64748b' }}>{req.customer_phone}</div>
                        )}
                      </td>
                      <td>
                        <div style={{ fontWeight: 500 }}>{req.worker_name}</div>
                        {req.worker_phone && (
                          <div style={{ fontSize: '0.6875rem', color: '#64748b' }}>{req.worker_phone}</div>
                        )}
                      </td>
                      <td>
                        <StatusBadge status={req.status} />
                      </td>
                      <td>
                        <span style={{ fontSize: '0.75rem', textTransform: 'capitalize' }}>
                          {req.request_type}
                        </span>
                      </td>
                      <td style={{ maxWidth: 220, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {req.address || '—'}
                      </td>
                      <td style={{ fontSize: '0.75rem', color: '#64748b' }}>
                        {req.created_at ? new Date(req.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '—'}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {selectedReq && (
        <RequestDetailModal 
          request={selectedReq} 
          onClose={() => setSelectedReq(null)} 
        />
      )}
    </div>
  );
}
