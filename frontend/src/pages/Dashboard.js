import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { getDashboard } from '../utils/api';
import { format } from 'date-fns';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboard().then(r => setStats(r.data)).finally(() => setLoading(false));
  }, []);

  if (loading) return <div style={{ color: 'var(--text3)', fontFamily: 'var(--mono)' }}>Loading...</div>;
  if (!stats) return null;

  const sourceData = Object.entries(stats.tenders_by_source).map(([name, count]) => ({ name: name.toUpperCase(), count }));
  const stateData = Object.entries(stats.tenders_by_state).map(([name, count]) => ({ name, count }));

  return (
    <div>
      <div className="page-header">
        <div className="page-title">
          Dashboard
          <span>Overview</span>
        </div>
      </div>

      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-label">Total Tenders</div>
          <div className="stat-value">{stats.total_tenders.toLocaleString()}</div>
          <div className="stat-sub">All sources</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">New Today</div>
          <div className="stat-value" style={{ color: 'var(--green)' }}>{stats.new_today}</div>
          <div className="stat-sub">Last 24 hours</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Active Alerts</div>
          <div className="stat-value" style={{ color: 'var(--accent)' }}>{stats.active_alerts}</div>
          <div className="stat-sub">Your alerts</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Sources</div>
          <div className="stat-value">{stats.sources_count}</div>
          <div className="stat-sub">Portals connected</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
        <div className="card">
          <div className="card-header">
            <div className="card-title">Tenders by Source</div>
          </div>
          {sourceData.length === 0
            ? <div style={{ color: 'var(--text3)', fontFamily: 'var(--mono)', fontSize: 12 }}>No data yet — trigger a scrape</div>
            : <ResponsiveContainer width="100%" height={180}>
                <BarChart data={sourceData} barSize={28}>
                  <XAxis dataKey="name" tick={{ fill: 'var(--text3)', fontSize: 11, fontFamily: 'IBM Plex Mono' }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: 'var(--text3)', fontSize: 11, fontFamily: 'IBM Plex Mono' }} axisLine={false} tickLine={false} />
                  <Tooltip
                    contentStyle={{ background: 'var(--bg3)', border: '1px solid var(--border)', borderRadius: 4, fontFamily: 'IBM Plex Mono', fontSize: 12 }}
                    cursor={{ fill: 'rgba(255,255,255,.03)' }}
                  />
                  <Bar dataKey="count" radius={[3, 3, 0, 0]}>
                    {sourceData.map((_, i) => <Cell key={i} fill="var(--accent)" />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
          }
        </div>

        <div className="card">
          <div className="card-header">
            <div className="card-title">Tenders by State</div>
          </div>
          {stateData.length === 0
            ? <div style={{ color: 'var(--text3)', fontFamily: 'var(--mono)', fontSize: 12 }}>No data yet</div>
            : <ResponsiveContainer width="100%" height={180}>
                <BarChart data={stateData} layout="vertical" barSize={14}>
                  <XAxis type="number" tick={{ fill: 'var(--text3)', fontSize: 11, fontFamily: 'IBM Plex Mono' }} axisLine={false} tickLine={false} />
                  <YAxis type="category" dataKey="name" width={90} tick={{ fill: 'var(--text3)', fontSize: 11, fontFamily: 'IBM Plex Mono' }} axisLine={false} tickLine={false} />
                  <Tooltip
                    contentStyle={{ background: 'var(--bg3)', border: '1px solid var(--border)', borderRadius: 4, fontFamily: 'IBM Plex Mono', fontSize: 12 }}
                    cursor={{ fill: 'rgba(255,255,255,.03)' }}
                  />
                  <Bar dataKey="count" radius={[0, 3, 3, 0]} fill="var(--green)" />
                </BarChart>
              </ResponsiveContainer>
          }
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <div className="card-title">Recent Scrape Activity</div>
        </div>
        <table>
          <thead>
            <tr>
              <th>Source</th>
              <th>Status</th>
              <th>Found</th>
              <th>New</th>
              <th>Started</th>
              <th>Error</th>
            </tr>
          </thead>
          <tbody>
            {stats.recent_scrapes.length === 0
              ? <tr><td colSpan={6} style={{ color: 'var(--text3)', fontFamily: 'var(--mono)' }}>No scrapes yet</td></tr>
              : stats.recent_scrapes.map(log => (
                  <tr key={log.id}>
                    <td className="primary" style={{ fontFamily: 'var(--mono)', textTransform: 'uppercase' }}>{log.source}</td>
                    <td>
                      <span className={`log-row log-${log.status}`}>{log.status}</span>
                    </td>
                    <td style={{ fontFamily: 'var(--mono)' }}>{log.tenders_found}</td>
                    <td style={{ fontFamily: 'var(--mono)', color: 'var(--green)' }}>+{log.tenders_new}</td>
                    <td style={{ fontFamily: 'var(--mono)', fontSize: 11 }}>
                      {format(new Date(log.started_at), 'dd MMM, HH:mm')}
                    </td>
                    <td style={{ color: 'var(--red)', fontSize: 11 }}>{log.error_message || '—'}</td>
                  </tr>
                ))
            }
          </tbody>
        </table>
      </div>
    </div>
  );
}
