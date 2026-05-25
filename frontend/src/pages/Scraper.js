import { useState, useEffect } from 'react';
import { getSources, triggerScrape, getScrapeLogs } from '../utils/api';
import { format } from 'date-fns';

export default function Scraper() {
  const [sources, setSources] = useState([]);
  const [logs, setLogs] = useState([]);
  const [triggering, setTriggering] = useState({});
  const [message, setMessage] = useState('');

  const load = () => {
    getSources().then(r => setSources(r.data));
    getScrapeLogs().then(r => setLogs(r.data));
  };

  useEffect(() => { load(); }, []);

  const handleScrape = async (sourceId) => {
    setTriggering(t => ({ ...t, [sourceId]: true }));
    setMessage('');
    try {
      const r = await triggerScrape({ source_id: sourceId });
      setMessage(`✓ ${r.data.message}`);
      setTimeout(load, 3000);
    } catch (e) {
      setMessage(`✗ ${e.response?.data?.detail || 'Failed to trigger scrape'}`);
    } finally {
      setTriggering(t => ({ ...t, [sourceId]: false }));
    }
  };

  return (
    <div>
      <div className="page-header">
        <div className="page-title">
          Scraper
          <span>Admin Controls</span>
        </div>
        <button className="btn btn-ghost btn-sm" onClick={load}>↻ Refresh</button>
      </div>

      {message && (
        <div style={{
          padding: '10px 14px',
          marginBottom: 16,
          background: message.startsWith('✓') ? 'rgba(34,197,94,.1)' : 'rgba(239,68,68,.1)',
          border: `1px solid ${message.startsWith('✓') ? 'rgba(34,197,94,.2)' : 'rgba(239,68,68,.2)'}`,
          borderRadius: 'var(--radius)',
          fontFamily: 'var(--mono)',
          fontSize: 12,
          color: message.startsWith('✓') ? 'var(--green)' : 'var(--red)',
        }}>
          {message}
        </div>
      )}

      <div className="card" style={{ marginBottom: 20 }}>
        <div className="card-header">
          <div className="card-title">Available Sources</div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {sources.map(s => (
            <div key={s.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid var(--border)' }}>
              <div>
                <div style={{ fontWeight: 500, color: 'var(--text)', marginBottom: 2 }}>{s.name}</div>
                <div style={{ fontSize: 12, color: 'var(--text3)', fontFamily: 'var(--mono)' }}>{s.url}</div>
                <div style={{ fontSize: 12, color: 'var(--text3)', marginTop: 2 }}>{s.description}</div>
              </div>
              <button
                className="btn btn-primary btn-sm"
                disabled={triggering[s.id]}
                onClick={() => handleScrape(s.id)}
              >
                {triggering[s.id] ? '⟳ Triggering...' : '▶ Scrape Now'}
              </button>
            </div>
          ))}
        </div>
        <div style={{ marginTop: 14, padding: '10px 12px', background: 'var(--bg3)', borderRadius: 'var(--radius)', fontSize: 11, color: 'var(--text3)', fontFamily: 'var(--mono)' }}>
          SCHEDULE: GeM scrapes automatically at 07:00 and 13:00 IST daily
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <div className="card-title">Scrape History</div>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Source</th>
                <th>Status</th>
                <th>Found</th>
                <th>New</th>
                <th>Duration</th>
                <th>Started</th>
                <th>Error</th>
              </tr>
            </thead>
            <tbody>
              {logs.length === 0
                ? <tr><td colSpan={7} style={{ color: 'var(--text3)', fontFamily: 'var(--mono)' }}>No scrape history yet</td></tr>
                : logs.map(log => {
                    const duration = log.finished_at
                      ? Math.round((new Date(log.finished_at) - new Date(log.started_at)) / 1000)
                      : null;
                    return (
                      <tr key={log.id}>
                        <td className="primary" style={{ fontFamily: 'var(--mono)', textTransform: 'uppercase' }}>{log.source}</td>
                        <td><span className={`log-row log-${log.status}`}>{log.status}</span></td>
                        <td style={{ fontFamily: 'var(--mono)' }}>{log.tenders_found}</td>
                        <td style={{ fontFamily: 'var(--mono)', color: 'var(--green)' }}>+{log.tenders_new}</td>
                        <td style={{ fontFamily: 'var(--mono)', fontSize: 11 }}>{duration != null ? `${duration}s` : '—'}</td>
                        <td style={{ fontFamily: 'var(--mono)', fontSize: 11 }}>{format(new Date(log.started_at), 'dd MMM, HH:mm')}</td>
                        <td style={{ color: 'var(--red)', fontSize: 11, maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>{log.error_message || '—'}</td>
                      </tr>
                    );
                  })
              }
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
