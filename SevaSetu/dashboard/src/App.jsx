import { Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Overview from './pages/Overview';
import Requests from './pages/Requests';
import Workers from './pages/Workers';
import Customers from './pages/Customers';
import Services from './pages/Services';
import DispatchOps from './pages/DispatchOps';
import './index.css';

export default function App() {
  return (
    <div className="app-container">
      <Sidebar />
      <div className="main-wrapper">
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/requests" element={<Requests />} />
          <Route path="/workers" element={<Workers />} />
          <Route path="/customers" element={<Customers />} />
          <Route path="/services" element={<Services />} />
          <Route path="/sms-dispatch" element={<DispatchOps />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </div>
  );
}
