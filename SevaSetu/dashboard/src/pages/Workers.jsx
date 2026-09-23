import { useState, useEffect } from 'react';
import { Star, ShieldCheck, AlertCircle } from 'lucide-react';
import { adminApi } from '../api';
import Topbar from '../components/Topbar';
import DigitalAccessBadge from '../components/DigitalAccessBadge';

export default function Workers() {
  const [workers, setWorkers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterCoop, setFilterCoop] = useState('all');

  const loadWorkers = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await adminApi.getWorkers();
      setWorkers(data);
    } catch (err) {
      setError(err.message || 'Failed to load workers.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadWorkers();
  }, []);

  const cooperatives = ['all', ...new Set(workers.map((w) => w.cooperative_name).filter(Boolean))];

  const filtered = workers.filter((w) => {
    if (filterCoop === 'all') return true;
    return w.cooperative_name === filterCoop;
  });

  return (
    <div>
      <Topbar
        title="Cooperative Workforce Directory"
        subtitle="Manage member tradespeople, communication modes, and field assignment status"
        onRefresh={loadWorkers}
        loading={loading}
      />

      <div className="page-content">
        {error && (
          <div className="error-banner">
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <AlertCircle size={15} />
              <span>{error}</span>
            </span>
            <button className="action-btn" onClick={loadWorkers}>Retry</button>
          </div>
        )}

        <div className="section-card">
          <div className="section-header" style={{ flexWrap: 'wrap', gap: '0.75rem' }}>
            <div>
              <h3 className="section-title">Registered Workforce ({filtered.length})</h3>
              <p className="section-subtitle">Real-time availability, verification status, and communication channels</p>
            </div>

            {/* Cooperative Filter */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 500 }}>Cooperative:</span>
              <select
                value={filterCoop}
                onChange={(e) => setFilterCoop(e.target.value)}
                style={{
                  padding: '0.35rem 0.65rem',
                  borderRadius: '4px',
                  border: '1px solid #cbd5e1',
                  background: 'white',
                  fontSize: '0.75rem',
                  fontWeight: 500,
                  color: '#0f172a',
                  outline: 'none',
                }}
              >
                {cooperatives.map((c) => (
                  <option key={c} value={c}>
                    {c === 'all' ? 'All Cooperatives' : c}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Worker Name</th>
                  <th>Cooperative</th>
                  <th>Skills / Services</th>
                  <th>Verification</th>
                  <th>Availability</th>
                  <th>Digital Access</th>
                  <th>Active Assignment</th>
                  <th>Rating & Volume</th>
                </tr>
              </thead>
              <tbody>
                {filtered.length === 0 ? (
                  <tr>
                    <td colSpan="8" style={{ textAlign: 'center', padding: '2.5rem' }}>
                      {loading ? <span className="loading-spinner"></span> : 'No worker records found.'}
                    </td>
                  </tr>
                ) : (
                  filtered.map((w) => (
                    <tr key={w.id}>
                      <td>
                        <div style={{ fontWeight: 600, color: '#0f172a' }}>{w.name}</div>
                        <div style={{ fontSize: '0.6875rem', color: '#64748b' }}>{w.phone || w.email}</div>
                      </td>
                      <td>
                        <span style={{ 
                          fontSize: '0.75rem', 
                          fontWeight: 500,
                          color: '#0f766e',
                          background: '#f0fdfa',
                          padding: '0.15rem 0.45rem',
                          borderRadius: '4px',
                          border: '1px solid #ccfbf1',
                          display: 'inline-block'
                        }}>
                          {w.cooperative_name}
                        </span>
                      </td>
                      <td>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                          {w.skills && w.skills.map((s) => (
                            <span 
                              key={s}
                              style={{
                                fontSize: '0.6875rem',
                                background: '#f1f5f9',
                                color: '#334155',
                                padding: '0.1rem 0.35rem',
                                borderRadius: '3px',
                                fontWeight: 500
                              }}
                            >
                              {s}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td>
                        {w.is_verified ? (
                          <span style={{ 
                            fontSize: '0.6875rem', 
                            fontWeight: 600, 
                            color: '#15803d', 
                            background: '#f0fdf4', 
                            padding: '0.15rem 0.45rem', 
                            borderRadius: '9999px', 
                            border: '1px solid #bbf7d0',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '0.25rem'
                          }}>
                            <ShieldCheck size={11} />
                            Verified
                          </span>
                        ) : (
                          <span style={{ fontSize: '0.6875rem', fontWeight: 500, color: '#b45309', background: '#fefce8', padding: '0.15rem 0.45rem', borderRadius: '9999px', border: '1px solid #fef08a' }}>
                            Unverified
                          </span>
                        )}
                      </td>
                      <td>
                        {w.is_available && w.current_workload === 0 ? (
                          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', color: '#16a34a', fontWeight: 500, fontSize: '0.75rem' }}>
                            <span style={{ width: 6, height: 6, background: '#22c55e', borderRadius: '50%' }}></span>
                            Available
                          </span>
                        ) : (
                          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', color: '#d97706', fontWeight: 500, fontSize: '0.75rem' }}>
                            <span style={{ width: 6, height: 6, background: '#f59e0b', borderRadius: '50%' }}></span>
                            Engaged
                          </span>
                        )}
                      </td>
                      <td>
                        <DigitalAccessBadge access={w.digital_access} />
                      </td>
                      <td>
                        {w.current_job ? (
                          <div>
                            <span className="badge badge-in_progress" style={{ fontSize: '0.6875rem' }}>
                              <span className="badge-dot"></span>
                              <span>{w.current_job.status}</span>
                            </span>
                            <div style={{ fontSize: '0.6875rem', color: '#64748b', marginTop: '0.15rem', fontFamily: 'monospace' }}>
                              #{w.current_job.booking_id.slice(-6).toUpperCase()}
                            </div>
                          </div>
                        ) : (
                          <span style={{ color: '#94a3b8', fontSize: '0.75rem' }}>Idle</span>
                        )}
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontWeight: 600, color: '#0f172a' }}>
                          <Star size={11} fill="#eab308" color="#eab308" />
                          <span>{w.rating}</span>
                        </div>
                        <div style={{ fontSize: '0.6875rem', color: '#64748b' }}>
                          {w.completed_jobs} jobs
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
