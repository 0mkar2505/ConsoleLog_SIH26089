import { useState, useEffect } from 'react';
import { AlertCircle } from 'lucide-react';
import { adminApi } from '../api';
import Topbar from '../components/Topbar';
import StatusBadge from '../components/StatusBadge';
import DigitalAccessBadge from '../components/DigitalAccessBadge';
import RequestDetailModal from '../components/RequestDetailModal';

export default function Requests() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');
  const [selectedReq, setSelectedReq] = useState(null);

  const loadRequests = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await adminApi.getRequests(100);
      setRequests(data);
    } catch (err) {
      setError(err.message || 'Failed to load requests.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRequests();
  }, []);

  const filtered = requests.filter((r) => {
    if (filter === 'all') return true;
    if (filter === 'pending') return ['pending', 'open', 'broadcasting'].includes(r.status);
    if (filter === 'active') return ['assigned', 'accepted', 'en_route', 'arrived', 'in_progress'].includes(r.status);
    if (filter === 'completed') return ['completed', 'fulfilled'].includes(r.status);
    return true;
  });

  return (
    <div>
      <Topbar
        title="Requests & Dispatched Jobs"
        subtitle="End-to-end dispatch and execution lifecycle across municipal service trades"
        onRefresh={loadRequests}
        loading={loading}
      />

      <div className="page-content">
        {error && (
          <div className="error-banner">
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <AlertCircle size={15} />
              <span>{error}</span>
            </span>
            <button className="action-btn" onClick={loadRequests}>Retry</button>
          </div>
        )}

        <div className="section-card">
          <div className="section-header" style={{ flexWrap: 'wrap', gap: '0.75rem' }}>
            <div>
              <h3 className="section-title">Dispatch Queue ({filtered.length})</h3>
              <p className="section-subtitle">Real-time status updates from customer requests and assigned workers</p>
            </div>

            {/* Filter pills */}
            <div style={{ display: 'flex', gap: '0.375rem' }}>
              {['all', 'pending', 'active', 'completed'].map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  style={{
                    padding: '0.3rem 0.65rem',
                    borderRadius: '4px',
                    fontSize: '0.75rem',
                    fontWeight: 500,
                    textTransform: 'capitalize',
                    border: '1px solid',
                    borderColor: filter === f ? '#0f172a' : '#e2e8f0',
                    background: filter === f ? '#0f172a' : '#ffffff',
                    color: filter === f ? '#ffffff' : '#475569',
                    cursor: 'pointer',
                    transition: 'all 0.1s'
                  }}
                >
                  {f}
                </button>
              ))}
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
                  <th>Schedule</th>
                  <th>Address</th>
                  <th>Created</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filtered.length === 0 ? (
                  <tr>
                    <td colSpan="9" style={{ textAlign: 'center', padding: '2.5rem' }}>
                      {loading ? <span className="loading-spinner"></span> : 'No records matching the filter.'}
                    </td>
                  </tr>
                ) : (
                  filtered.map((req) => (
                    <tr key={req.request_id} className="clickable-row" onClick={() => setSelectedReq(req)}>
                      <td style={{ fontFamily: 'monospace', fontWeight: 600, color: '#0f172a' }}>
                        {req.request_id.slice(-6).toUpperCase()}
                      </td>
                      <td style={{ fontWeight: 600 }}>{req.service}</td>
                      <td>
                        <div style={{ fontWeight: 500 }}>{req.customer_name}</div>
                        <div style={{ fontSize: '0.6875rem', color: '#64748b' }}>{req.customer_phone || 'No phone'}</div>
                      </td>
                      <td>
                        <div style={{ fontWeight: 500 }}>{req.worker_name}</div>
                        {req.worker_digital_access && req.worker_digital_access.length > 0 && (
                          <div style={{ marginTop: '0.15rem' }}>
                            <DigitalAccessBadge access={req.worker_digital_access} />
                          </div>
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
                      <td style={{ fontSize: '0.75rem', color: '#64748b', whiteSpace: 'nowrap' }}>
                        {req.created_at ? new Date(req.created_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' }) : '—'}
                      </td>
                      <td>
                        <button
                          className="action-btn"
                          style={{ padding: '0.25rem 0.5rem', fontSize: '0.6875rem' }}
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedReq(req);
                          }}
                        >
                          View
                        </button>
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
