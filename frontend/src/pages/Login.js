import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login, register } from '../utils/api';
import { useAuth } from '../hooks/useAuth';

export default function Login() {
  const [mode, setMode] = useState('login');
  const [form, setForm] = useState({ email: '', password: '', full_name: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { signin } = useAuth();
  const navigate = useNavigate();

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handleSubmit = async () => {
    setLoading(true);
    setError('');
    try {
      if (mode === 'login') {
        const r = await login(form.email, form.password);
        signin(r.data.access_token, r.data.user);
        navigate('/');
      } else {
        await register({ email: form.email, password: form.password, full_name: form.full_name });
        const r = await login(form.email, form.password);
        signin(r.data.access_token, r.data.user);
        navigate('/');
      }
    } catch (e) {
      setError(e.response?.data?.detail || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-wrap">
      <div className="login-card">
        <div className="login-title"><span style={{ color: 'var(--accent)', fontFamily: 'var(--mono)' }}>TENDER</span>HUB</div>
        <div className="login-sub">{mode === 'login' ? 'Sign in to your account' : 'Create your account'}</div>

        {mode === 'register' && (
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <input className="input" value={form.full_name} onChange={e => set('full_name', e.target.value)} placeholder="Your name" />
          </div>
        )}

        <div className="form-group">
          <label className="form-label">Email</label>
          <input className="input" type="email" value={form.email} onChange={e => set('email', e.target.value)} placeholder="you@example.com" />
        </div>

        <div className="form-group">
          <label className="form-label">Password</label>
          <input className="input" type="password" value={form.password} onChange={e => set('password', e.target.value)} placeholder="••••••••"
            onKeyDown={e => e.key === 'Enter' && handleSubmit()} />
        </div>

        {error && <div className="error-msg">{error}</div>}

        <button className="btn btn-primary" style={{ width: '100%', marginTop: 16, justifyContent: 'center' }} onClick={handleSubmit} disabled={loading}>
          {loading ? 'Please wait...' : mode === 'login' ? 'Sign In' : 'Create Account'}
        </button>

        <div style={{ marginTop: 16, textAlign: 'center', fontSize: 12, color: 'var(--text3)' }}>
          {mode === 'login'
            ? <>No account? <span style={{ color: 'var(--accent)', cursor: 'pointer' }} onClick={() => setMode('register')}>Create one</span></>
            : <>Have an account? <span style={{ color: 'var(--accent)', cursor: 'pointer' }} onClick={() => setMode('login')}>Sign in</span></>
          }
        </div>
      </div>
    </div>
  );
}
