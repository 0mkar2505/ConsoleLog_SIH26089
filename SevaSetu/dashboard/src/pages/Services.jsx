import { useState, useEffect } from 'react';
import { 
  AlertCircle, 
  Wrench, 
  Sparkles, 
  Hammer, 
  Paintbrush, 
  Cpu, 
  Layers 
} from 'lucide-react';
import { adminApi } from '../api';
import Topbar from '../components/Topbar';

export default function Services() {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadServices = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await adminApi.getServices();
      setServices(data);
    } catch (err) {
      setError(err.message || 'Failed to load services.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadServices();
  }, []);

  const getCategoryIcon = (category) => {
    switch (category?.toLowerCase()) {
      case 'maintenance': return <Wrench size={16} />;
      case 'sanitation': return <Sparkles size={16} />;
      case 'furniture': return <Hammer size={16} />;
      case 'renovation': return <Paintbrush size={16} />;
      default: return <Layers size={16} />;
    }
  };

  return (
    <div>
      <Topbar
        title="Service Catalogue"
        subtitle="Standardized municipal and home service trades offered by member cooperatives"
        onRefresh={loadServices}
        loading={loading}
      />

      <div className="page-content">
        {error && (
          <div className="error-banner">
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <AlertCircle size={15} />
              <span>{error}</span>
            </span>
            <button className="action-btn" onClick={loadServices}>Retry</button>
          </div>
        )}

        <div className="section-card">
          <div className="section-header">
            <div>
              <h3 className="section-title">Standardized Catalogue ({services.length})</h3>
              <p className="section-subtitle">
                Skill profiles mapped across participating cooperatives and verified workers
              </p>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem' }}>
            {services.length === 0 ? (
              <div className="empty-state" style={{ gridColumn: '1 / -1' }}>
                {loading ? <span className="loading-spinner"></span> : 'No services configured.'}
              </div>
            ) : (
              services.map((s) => (
                <div 
                  key={s.id} 
                  style={{
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    padding: '1.125rem',
                    background: '#ffffff',
                    boxShadow: '0 1px 2px rgba(0,0,0,0.03)',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between'
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.625rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <div style={{ 
                          width: 32, 
                          height: 32, 
                          borderRadius: '6px', 
                          background: '#f1f5f9', 
                          display: 'flex', 
                          alignItems: 'center', 
                          justifyContent: 'center',
                          color: '#475569'
                        }}>
                          {getCategoryIcon(s.category)}
                        </div>
                        <div>
                          <h4 style={{ fontSize: '0.9375rem', fontWeight: 600, color: '#0f172a' }}>{s.name}</h4>
                          <span style={{ 
                            fontSize: '0.6875rem', 
                            textTransform: 'uppercase', 
                            fontWeight: 600, 
                            color: '#64748b',
                            background: '#f8fafc',
                            padding: '0.1rem 0.35rem',
                            borderRadius: '3px',
                            border: '1px solid #e2e8f0'
                          }}>
                            {s.category}
                          </span>
                        </div>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '1.0625rem', fontWeight: 700, color: '#0f172a' }}>
                          ₹{s.base_price}
                        </div>
                        <div style={{ fontSize: '0.6875rem', color: '#64748b' }}>Base rate</div>
                      </div>
                    </div>

                    <p style={{ fontSize: '0.75rem', color: '#475569', lineHeight: 1.45, marginBottom: '1rem' }}>
                      {s.description || 'Standard service delivered by verified cooperative members.'}
                    </p>
                  </div>

                  <div style={{ 
                    borderTop: '1px solid #f1f5f9', 
                    paddingTop: '0.75rem',
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    fontSize: '0.6875rem'
                  }}>
                    <div>
                      <span style={{ color: '#64748b' }}>Total Workforce: </span>
                      <strong style={{ color: '#0f172a' }}>{s.total_workers} skilled</strong>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', color: '#16a34a', fontWeight: 500 }}>
                      <span style={{ width: 5, height: 5, background: '#22c55e', borderRadius: '50%' }}></span>
                      {s.available_workers} Available
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
