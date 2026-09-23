import { useState, useEffect } from 'react';
import { AlertCircle, MapPin } from 'lucide-react';
import { adminApi } from '../api';
import Topbar from '../components/Topbar';
import StatusBadge from '../components/StatusBadge';

export default function Customers() {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadCustomers = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await adminApi.getCustomers();
      setCustomers(data);
    } catch (err) {
      setError(err.message || 'Failed to load customers.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCustomers();
  }, []);

  return (
    <div>
      <Topbar
        title="Customer Directory"
        subtitle="Citizen accounts, service frequency, and verified household addresses"
        onRefresh={loadCustomers}
        loading={loading}
      />

      <div className="page-content">
        {error && (
          <div className="error-banner">
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <AlertCircle size={15} />
              <span>{error}</span>
            </span>
            <button className="action-btn" onClick={loadCustomers}>Retry</button>
          </div>
        )}

        <div className="section-card">
          <div className="section-header">
            <div>
              <h3 className="section-title">Customer Accounts ({customers.length})</h3>
              <p className="section-subtitle">Track service requests, household locations, and contact records</p>
            </div>
          </div>

          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Customer Name</th>
                  <th>Contact Details</th>
                  <th>Total Requests</th>
                  <th>Recent Activity</th>
                  <th>Primary Address</th>
                  <th>Saved Locations</th>
                </tr>
              </thead>
              <tbody>
                {customers.length === 0 ? (
                  <tr>
                    <td colSpan="6" style={{ textAlign: 'center', padding: '2.5rem' }}>
                      {loading ? <span className="loading-spinner"></span> : 'No customer records found.'}
                    </td>
                  </tr>
                ) : (
                  customers.map((c) => (
                    <tr key={c.id}>
                      <td>
                        <div style={{ fontWeight: 600, color: '#0f172a' }}>{c.name}</div>
                        <div style={{ fontSize: '0.6875rem', color: '#64748b', fontFamily: 'monospace' }}>
                          ID: {c.id.slice(-6).toUpperCase()}
                        </div>
                      </td>
                      <td>
                        <div style={{ fontWeight: 500 }}>{c.phone || '—'}</div>
                        <div style={{ fontSize: '0.6875rem', color: '#64748b' }}>{c.email || '—'}</div>
                      </td>
                      <td>
                        <span style={{ 
                          fontWeight: 600, 
                          fontSize: '0.8125rem',
                          color: c.requests_count > 0 ? '#0f766e' : '#94a3b8' 
                        }}>
                          {c.requests_count} {c.requests_count === 1 ? 'request' : 'requests'}
                        </span>
                      </td>
                      <td>
                        {c.recent_request ? (
                          <div>
                            <div style={{ fontWeight: 500, fontSize: '0.75rem' }}>
                              {c.recent_request.service}
                            </div>
                            <div style={{ marginTop: '0.15rem' }}>
                              <StatusBadge status={c.recent_request.status} />
                            </div>
                          </div>
                        ) : (
                          <span style={{ color: '#94a3b8', fontSize: '0.75rem' }}>No activity</span>
                        )}
                      </td>
                      <td style={{ maxWidth: 260 }}>
                        <div style={{ fontSize: '0.75rem', color: '#334155' }}>
                          {c.primary_address}
                        </div>
                      </td>
                      <td>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                          {c.saved_addresses && c.saved_addresses.map((a, idx) => (
                            <span 
                              key={idx}
                              style={{
                                fontSize: '0.6875rem',
                                background: '#f1f5f9',
                                color: '#475569',
                                padding: '0.1rem 0.35rem',
                                borderRadius: '3px',
                                border: '1px solid #e2e8f0',
                                fontWeight: 500,
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '0.2rem'
                              }}
                            >
                              <MapPin size={9} />
                              {a.label || `Addr ${idx + 1}`}
                            </span>
                          ))}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
