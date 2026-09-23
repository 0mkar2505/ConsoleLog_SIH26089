import { Routes, Route, Link } from 'react-router-dom'
import './index.css'

function Home() {
  return (
    <div className="card">
      <h2>Cooperative Management Overview</h2>
      <p style={{ marginTop: '0.5rem', color: '#4b5563' }}>
        This is the administrative dashboard shell for the SevaSetu Cooperative Gig Services Platform.
      </p>
      <div style={{ marginTop: '1rem' }}>
        <span className="status-badge">System Status: Scaffold Active</span>
      </div>
    </div>
  )
}

function Status() {
  return (
    <div className="card">
      <h2>Platform Health & Telemetry</h2>
      <p style={{ marginTop: '0.5rem', color: '#4b5563' }}>
        Backend communication and admin modules will be connected in upcoming milestones.
      </p>
    </div>
  )
}

export default function App() {
  return (
    <div className="dashboard-shell">
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #e5e7eb', paddingBottom: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#111827' }}>SevaSetu Admin Dashboard</h1>
          <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>PS 26089 — Cooperative Gig Services Platform | Team Console Log</p>
        </div>
        <nav style={{ display: 'flex', gap: '1rem' }}>
          <Link to="/" style={{ color: '#2563eb', textDecoration: 'none', fontWeight: 500 }}>Home</Link>
          <Link to="/status" style={{ color: '#2563eb', textDecoration: 'none', fontWeight: 500 }}>Status</Link>
        </nav>
      </header>

      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/status" element={<Status />} />
        </Routes>
      </main>
    </div>
  )
}
