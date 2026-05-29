import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
const NAV = [
  { path: '/', label: 'Dashboard', icon: '▦' },
  { path: '/tenders', label: 'Tenders', icon: '◈' },
  { path: '/alerts', label: 'Alerts', icon: '◎' },
  { path: '/scraper', label: 'Scraper', icon: '⟳', adminOnly: true },
];
export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, signout } = useAuth();
  return (
    <div className="sidebar">
      <div className="sidebar-logo">
        <span>TENDER</span>HUB
      </div>
      <nav className="sidebar-nav">
        {NAV.filter(n => !n.adminOnly || user?.is_admin).map(n => (
          <div
            key={n.path}
            className={`nav-item ${location.pathname === n.path ? 'active' : ''}`}
            onClick={() => navigate(n.path)}
          >
            <span style={{ fontFamily: 'monospace', fontSize: 15 }}>{n.icon}</span>
            {n.label}
          </div>
        ))}
      </nav>
      <div className="sidebar-bottom">
        <div style={{ marginBottom: 6, color: 'var(--text2)', fontSize: 12 }}>{user?.full_name}</div>
        <div style={{ color: 'var(--text3)', fontSize: 11, marginBottom: 10 }}>{user?.email}</div>
        <div
          style={{ cursor: 'pointe
