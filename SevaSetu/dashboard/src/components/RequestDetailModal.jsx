import { X } from 'lucide-react';
import StatusBadge from './StatusBadge';
import DigitalAccessBadge from './DigitalAccessBadge';

export default function RequestDetailModal({ request, onClose }) {
  if (!request) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h3>Job Details</h3>
            <span style={{ fontSize: '0.6875rem', color: '#64748b', fontFamily: 'monospace' }}>
              Ref: {request.request_id || request.id}
            </span>
          </div>
          <button className="modal-close" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <div className="modal-body">
          <div className="detail-row">
            <span className="detail-label">Status</span>
            <span className="detail-val">
              <StatusBadge status={request.status || request.current_status} />
            </span>
          </div>

          <div className="detail-row">
            <span className="detail-label">Service</span>
            <span className="detail-val" style={{ fontWeight: 600 }}>
              {request.service || request.service_name}
            </span>
          </div>

          <div className="detail-row">
            <span className="detail-label">Customer</span>
            <span className="detail-val">
              {request.customer_name} {request.customer_phone ? `(${request.customer_phone})` : ''}
            </span>
          </div>

          <div className="detail-row">
            <span className="detail-label">Assigned Worker</span>
            <span className="detail-val">
              {request.worker_name || 'Unassigned'}
              {request.worker_phone ? ` (${request.worker_phone})` : ''}
            </span>
          </div>

          {request.worker_digital_access && (
            <div className="detail-row">
              <span className="detail-label">Channels</span>
              <span className="detail-val">
                <DigitalAccessBadge access={request.worker_digital_access} />
              </span>
            </div>
          )}

          <div className="detail-row">
            <span className="detail-label">Schedule Mode</span>
            <span className="detail-val" style={{ textTransform: 'capitalize' }}>
              {request.request_type || 'Immediate'}
              {request.preferred_date ? ` (${request.preferred_date})` : ''}
            </span>
          </div>

          <div className="detail-row">
            <span className="detail-label">Problem</span>
            <span className="detail-val" style={{ background: '#f8fafc', padding: '0.5rem', borderRadius: '4px', border: '1px solid #e2e8f0' }}>
              {request.problem_description || 'No description specified'}
            </span>
          </div>

          <div className="detail-row">
            <span className="detail-label">Address</span>
            <span className="detail-val">
              {request.address || 'Standard address on file'}
              {request.landmark ? `, Landmark: ${request.landmark}` : ''}
              {request.directions ? ` (${request.directions})` : ''}
            </span>
          </div>

          {request.estimated_price && (
            <div className="detail-row">
              <span className="detail-label">Estimated Rate</span>
              <span className="detail-val" style={{ color: '#0f766e', fontWeight: 600 }}>
                INR {request.estimated_price}
              </span>
            </div>
          )}

          {request.created_at && (
            <div className="detail-row">
              <span className="detail-label">Submitted</span>
              <span className="detail-val" style={{ fontSize: '0.75rem', color: '#64748b' }}>
                {new Date(request.created_at).toLocaleString()}
              </span>
            </div>
          )}

          {request.booking_id && (
            <div className="detail-row">
              <span className="detail-label">Booking ID</span>
              <span className="detail-val" style={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                {request.booking_id}
              </span>
            </div>
          )}
        </div>

        <div style={{ padding: '0.75rem 1.25rem', borderTop: '1px solid #e2e8f0', display: 'flex', justifyContent: 'flex-end', background: '#f8fafc' }}>
          <button 
            className="action-btn"
            onClick={onClose}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
