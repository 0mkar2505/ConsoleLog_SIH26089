import { RefreshCw } from 'lucide-react';

export default function Topbar({ title, subtitle, onRefresh, loading }) {
  return (
    <header className="topbar">
      <div className="topbar-left">
        <h2>{title}</h2>
        <p>{subtitle}</p>
      </div>

      <div className="topbar-right">
        <div className="live-indicator">
          <span className="live-dot"></span>
          <span>MongoDB Atlas Connected</span>
        </div>

        <button 
          className="action-btn" 
          onClick={onRefresh} 
          disabled={loading}
          title="Refresh real data from backend"
        >
          <RefreshCw 
            size={13} 
            strokeWidth={2} 
            className={loading ? 'loading-spinner' : ''} 
          />
          <span>Refresh</span>
        </button>
      </div>
    </header>
  );
}
