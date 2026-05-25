import { useState, useEffect } from 'react';
import { getAlerts, createAlert, toggleAlert, deleteAlert } from '../utils/api';
import { format } from 'date-fns';

const EMPTY = { name: '', keywords: '', states: '', categories: '', min_value: '', max_value: '', sources: ['gem'] };

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(EMPTY);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const load = () => getAlerts().then(r => setAlerts(r.data));
  useEffect(() => { load(); }, []);

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handleCreate = async () => {
    if (!form.name.trim()) { setError('Alert name is required'); return; }
    if (!form.keywords.trim()) { setError('At least one keyword is required'); return; }
    setSaving(true);
    setError('');
    try {
      await createAlert({
        name: form.name,
        keywords: form.keywords.split(',').map(k => k.trim()).filter(Boolean),
        states: form.states.split(',').map(s => s.trim()).filter(Boolean),
        categories: form.categories.split(',').map(c => c.trim()).filter(Boolean),
        min_value: form.min_value ? parseInt(form.min_value) : null,
        max_value: form.max_value ? parseInt(form.max_value) : null,
        sources: form.sources,
      });
      setForm(EMPTY);
      setShowForm(false);
      load();
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to create alert');
    } finally {
      setSaving(false);
    }
  };

  const handleToggle = async (id) => {
    await toggleAlert(id);
    load();
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this alert?')) return;
    await deleteAlert(id);
    load();
  };

  return (
    <div>
      <div className="page-header">
        <div className="page-title">
          Alerts
          <span>{alerts.length} configured</span>
        </div>
        <button className="btn btn-primary" onClick={() => setShowForm(v => !v)}>
          {showForm ? '✕ Cancel' : '+ New Alert'}
        </button>
      </div>

      {showForm && (
        <div className="card" style={{ marginBottom: 20 }}>
          <div className="card-title" style={{ marginBottom: 16 }}>Create Alert</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div className="form-group" style={{ gridColumn: '1/-1' }}>
              <label className="form-label">Alert Name *</label>
              <input className="input" value={form.name} onChange={e => set('name', e.target.value)} placeholder="e.g. DG Set - Maharashtra" />
            </div>
            <div className="form-group">
              <label className="form-label">Keywords * (comma-separated)</label>
              <input className="input" value={form.keywords} onChange={e => set('keywords', e.target.value)} placeholder="DG Set, diesel generator, genset" />
            </div>
            <div className="form-group">
              <label className="form-label">States (comma-separated, blank = all)</label>
              <input className="input" value={form.states} onChange={e => set('states', e.target.value)} placeholder="Maharashtra, Delhi" />
            </div>
            <div className="form-group">
              <label className="form-label">Min Value (₹)</label>
              <input className="input" type="number" value={form.min_value} onChange={e => set('min_value', e.target.value)} placeholder="e.g. 100000" />
            </div>
            <div className="form-group">
              <label className="form-label">Max Value (₹)</label>
              <input className="input" type="number" value={form.max_value} onChange={e => set('max_value', e.target.value)} placeholder="e.g. 50000000" />
            </div>
          </div>
          {error && <div className="error-msg">{error}</div>}
          <div style={{ marginTop: 14, display: 'flex', gap: 8 }}>
            <button className="btn btn-primary" onClick={handleCreate} disabled={saving}>
              {saving ? 'Saving...' : 'Create Alert'}
            </button>
            <button className="btn btn-ghost" onClick={() => setShowForm(false)}>Cancel</button>
          </div>
        </div>
      )}

      {alerts.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 48 }}>
          <div style={{ fontFamily: 'var(--mono)', color: 'var(--text3)', fontSize: 13 }}>No alerts yet</div>
          <div style={{ color: 'var(--text3)', fontSize: 12, marginTop: 6 }}>Create an alert to get email notifications when new tenders are found</div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {alerts.map(a => (
            <div key={a.id} className="card" style={{ padding: '16px 20px' }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 16 }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                    <div className="alert-row">
                      <div className={`dot ${a.is_active ? 'dot-green' : 'dot-gray'}`} />
                    </div>
                    <div style={{ fontWeight: 500, color: 'var(--text)' }}>{a.name}</div>
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {a.keywords.map(k => (
                      <span key={k} style={{ background: 'var(--accent-glow)', color: 'var(--accent)', border: '1px solid rgba(47,110,245,.2)', borderRadius: 3, padding: '1px 7px', fontSize: 11, fontFamily: 'var(--mono)' }}>
                        {k}
                      </span>
                    ))}
                    {a.states.map(s => (
                      <span key={s} style={{ background: 'var(--bg3)', color: 'var(--text3)', borderRadius: 3, padding: '1px 7px', fontSize: 11, fontFamily: 'var(--mono)' }}>
                        {s}
                      </span>
                    ))}
                    {a.min_value && <span style={{ background: 'var(--bg3)', color: 'var(--text3)', borderRadius: 3, padding: '1px 7px', fontSize: 11, fontFamily: 'var(--mono)' }}>₹{a.min_value.toLocaleString()}+</span>}
                  </div>
                  <div style={{ marginTop: 8, fontSize: 11, color: 'var(--text3)', fontFamily: 'var(--mono)' }}>
                    Created {format(new Date(a.created_at), 'dd MMM yyyy')}
                    {a.last_triggered_at && ` · Last triggered ${format(new Date(a.last_triggered_at), 'dd MMM, HH:mm')}`}
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <label className="toggle">
                    <input type="checkbox" checked={a.is_active} onChange={() => handleToggle(a.id)} />
                    <span className="toggle-slider" />
                  </label>
                  <button className="btn btn-danger btn-sm" onClick={() => handleDelete(a.id)}>Delete</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
