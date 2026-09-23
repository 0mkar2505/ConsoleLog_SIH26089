import { useState, useEffect } from 'react';
import { 
  AlertCircle, 
  Radio, 
  ArrowDownLeft, 
  ArrowUpRight, 
  Send,
  Check
} from 'lucide-react';
import { adminApi } from '../api';
import Topbar from '../components/Topbar';

export default function DispatchOps() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Simulation form state
  const [phone, setPhone] = useState('+919844444403');
  const [replyChoice, setReplyChoice] = useState('1');
  const [simulating, setSimulating] = useState(false);
  const [simResult, setSimResult] = useState(null);

  const loadLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await adminApi.getSmsLogs(50);
      setLogs(data);
    } catch (err) {
      setError(err.message || 'Failed to load dispatch comm logs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, []);

  const handleSimulateReply = async (e) => {
    e.preventDefault();
    setSimulating(true);
    setSimResult(null);
    try {
      const res = await adminApi.simulateInboundSms(phone, replyChoice);
      setSimResult(res);
      await loadLogs();
    } catch (err) {
      alert(`Simulation failed: ${err.message}`);
    } finally {
      setSimulating(false);
    }
  };

  return (
    <div>
      <Topbar
        title="SMS & Feature Phone Gateway"
        subtitle="Keypad-based dispatch and response console for low-digital cooperative members"
        onRefresh={loadLogs}
        loading={loading}
      />

      <div className="page-content">
        {error && (
          <div className="error-banner">
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <AlertCircle size={15} />
              <span>{error}</span>
            </span>
            <button className="action-btn" onClick={loadLogs}>Retry</button>
          </div>
        )}

        {/* Simulator Terminal Card */}
        <div className="section-card" style={{ border: '1px solid #cbd5e1' }}>
          <div className="section-header">
            <div>
              <h3 className="section-title">
                <Radio size={16} />
                <span>Feature Phone Inbound Dispatch Terminal</span>
              </h3>
              <p className="section-subtitle">
                Simulate worker SMS response (Key 1 = Accept Job, Key 2 = Reject Job)
              </p>
            </div>
            <span style={{ fontSize: '0.6875rem', background: '#f1f5f9', color: '#475569', padding: '0.15rem 0.5rem', borderRadius: '4px', border: '1px solid #e2e8f0', fontWeight: 600 }}>
              Gateway Simulator
            </span>
          </div>

          <form onSubmit={handleSimulateReply} style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', alignItems: 'flex-end', marginTop: '0.5rem' }}>
            <div style={{ flex: '1 1 220px' }}>
              <label style={{ display: 'block', fontSize: '0.6875rem', fontWeight: 600, color: '#475569', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Registered Worker Phone
              </label>
              <select
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.45rem 0.65rem',
                  borderRadius: '4px',
                  border: '1px solid #cbd5e1',
                  background: 'white',
                  fontSize: '0.8125rem'
                }}
              >
                <option value="+919844444403">Sunita Shinde (+919844444403 · SMS/Voice)</option>
                <option value="+919844444404">Anil Jadhav (+919844444404 · SMS)</option>
                <option value="+919844444407">Santosh More (+919844444407 · SMS/Voice)</option>
                <option value="+919844444410">Rajesh Thorat (+919844444410 · SMS)</option>
              </select>
            </div>

            <div style={{ flex: '1 1 180px' }}>
              <label style={{ display: 'block', fontSize: '0.6875rem', fontWeight: 600, color: '#475569', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Keypad Reply
              </label>
              <select
                value={replyChoice}
                onChange={(e) => setReplyChoice(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.45rem 0.65rem',
                  borderRadius: '4px',
                  border: '1px solid #cbd5e1',
                  background: 'white',
                  fontSize: '0.8125rem',
                  fontWeight: 500
                }}
              >
                <option value="1">1 — Accept Offer</option>
                <option value="2">2 — Reject Offer</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={simulating}
              className="action-btn"
              style={{
                padding: '0.45rem 0.875rem',
                background: replyChoice === '1' ? '#0f172a' : '#991b1b',
                color: 'white',
                border: 'none',
                fontWeight: 600,
                fontSize: '0.75rem',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.35rem'
              }}
            >
              <Send size={12} />
              <span>{simulating ? 'Sending...' : `Send Reply (${replyChoice})`}</span>
            </button>
          </form>

          {simResult && (
            <div style={{ marginTop: '0.75rem', padding: '0.625rem 0.875rem', background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '4px', fontSize: '0.75rem' }}>
              <div style={{ fontWeight: 600, color: '#166534', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                <Check size={13} />
                <span>{simResult.message || `Status updated: ${simResult.action?.toUpperCase()}`}</span>
              </div>
              {simResult.confirmation_sent && (
                <div style={{ color: '#15803d', marginTop: '0.2rem', fontFamily: 'monospace' }}>
                  Gateway SMS: "{simResult.confirmation_sent}"
                </div>
              )}
            </div>
          )}
        </div>

        {/* Communication Audit Trail */}
        <div className="section-card">
          <div className="section-header">
            <div>
              <h3 className="section-title">Communication Audit Log ({logs.length})</h3>
              <p className="section-subtitle">Audit stream of outbound dispatch notifications and inbound keypad SMS</p>
            </div>
          </div>

          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Direction</th>
                  <th>Worker</th>
                  <th>Recipient Phone</th>
                  <th>Message Body</th>
                  <th>Status</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {logs.length === 0 ? (
                  <tr>
                    <td colSpan="6" style={{ textAlign: 'center', padding: '2.5rem' }}>
                      {loading ? <span className="loading-spinner"></span> : 'No communication records logged.'}
                    </td>
                  </tr>
                ) : (
                  logs.map((l) => (
                    <tr key={l.id}>
                      <td>
                        {l.direction === 'inbound' ? (
                          <span style={{ fontSize: '0.6875rem', fontWeight: 600, color: '#15803d', background: '#f0fdf4', padding: '0.15rem 0.45rem', borderRadius: '9999px', border: '1px solid #bbf7d0', display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                            <ArrowDownLeft size={10} />
                            Inbound
                          </span>
                        ) : (
                          <span style={{ fontSize: '0.6875rem', fontWeight: 600, color: '#1d4ed8', background: '#eff6ff', padding: '0.15rem 0.45rem', borderRadius: '9999px', border: '1px solid #bfdbfe', display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                            <ArrowUpRight size={10} />
                            Outbound
                          </span>
                        )}
                      </td>
                      <td>
                        <div style={{ fontWeight: 600 }}>{l.worker_name || 'Worker'}</div>
                        <div style={{ fontSize: '0.6875rem', color: '#64748b', fontFamily: 'monospace' }}>
                          {l.job_id ? `Job: ${l.job_id.slice(-6).toUpperCase()}` : ''}
                        </div>
                      </td>
                      <td style={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                        {l.recipient_phone || '—'}
                      </td>
                      <td style={{ maxWidth: 360 }}>
                        <pre style={{ 
                          whiteSpace: 'pre-wrap', 
                          fontFamily: 'var(--font-mono)', 
                          fontSize: '0.6875rem', 
                          background: '#f8fafc', 
                          padding: '0.35rem 0.5rem', 
                          borderRadius: '3px',
                          border: '1px solid #e2e8f0',
                          lineHeight: 1.4,
                          color: '#334155'
                        }}>
                          {l.message}
                        </pre>
                      </td>
                      <td>
                        <span style={{ fontSize: '0.6875rem', textTransform: 'uppercase', fontWeight: 600, color: '#16a34a' }}>
                          {l.status}
                        </span>
                      </td>
                      <td style={{ fontSize: '0.75rem', color: '#64748b', whiteSpace: 'nowrap' }}>
                        {l.formatted_time ? new Date(l.formatted_time).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' }) : '—'}
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
