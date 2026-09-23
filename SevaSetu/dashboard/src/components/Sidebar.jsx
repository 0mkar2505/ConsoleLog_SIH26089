import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Layers, 
  Users, 
  UserCheck, 
  Briefcase, 
  Radio,
  Building2
} from 'lucide-react';

export default function Sidebar() {
  const navItems = [
    { path: '/', label: 'Overview', icon: LayoutDashboard },
    { path: '/requests', label: 'Requests & Jobs', icon: Layers },
    { path: '/workers', label: 'Cooperative Workforce', icon: UserCheck },
    { path: '/customers', label: 'Customer Accounts', icon: Users },
    { path: '/services', label: 'Service Catalogue', icon: Briefcase },
    { path: '/sms-dispatch', label: 'SMS & Feature Phone Gateway', icon: Radio },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="brand-wrapper">
          <div className="brand-icon-box">SS</div>
          <div>
            <div className="brand-name">SevaSetu</div>
            <div className="brand-caption">Cooperative Portal</div>
          </div>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section-label">Operations</div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              <span className="nav-link-icon">
                <Icon size={16} strokeWidth={1.8} />
              </span>
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-footer-row">
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: '#cbd5e1' }}>
            <Building2 size={13} strokeWidth={1.8} />
            <span>Cooperative Network</span>
          </span>
          <span style={{ fontSize: '0.6875rem', background: '#334155', padding: '0.1rem 0.35rem', borderRadius: '4px', color: '#f8fafc' }}>
            v0.2.0
          </span>
        </div>
      </div>
    </aside>
  );
}
