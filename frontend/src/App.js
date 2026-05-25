import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './hooks/useAuth';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Tenders from './pages/Tenders';
import Alerts from './pages/Alerts';
import Scraper from './pages/Scraper';
import Login from './pages/Login';
import './index.css';

function PrivateLayout({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', fontFamily: 'var(--mono)', color: 'var(--text3)' }}>Initializing...</div>;
  if (!user) return <Navigate to="/login" replace />;
  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">{children}</main>
    </div>
  );
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<PrivateLayout><Dashboard /></PrivateLayout>} />
      <Route path="/tenders" element={<PrivateLayout><Tenders /></PrivateLayout>} />
      <Route path="/alerts" element={<PrivateLayout><Alerts /></PrivateLayout>} />
      <Route path="/scraper" element={<PrivateLayout><Scraper /></PrivateLayout>} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
