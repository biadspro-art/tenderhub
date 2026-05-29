import { useState, useEffect, useCallback } from 'react';
import { getTenders } from '../utils/api';
import { format } from 'date-fns';

const SOURCES = ['gem', 'cppp', 'maharashtra', 'delhi'];

export default function Tenders() {
  const [tenders, setTenders] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);

  const [filters, setFilters] = useState({
    keyword: 'DG Set',
    source: '',
    state: '',
    department: '',
    status: 'active',
  });

  const load = useCallback(() => {
    setLoading(true);
    const params = { page, per_page: 50 };
    Object.entries(filters).forEach(([k, v]) => { if (v) params[k] = v; });
    getTenders(params)
      .then(r => { setTenders(r.data.tenders); setTotal(r.data.total); })
      .finally(() => setLoading(false));
  }, [filters, page]);

  useEffect(() => { load(); }, [load]);

  const set = (k, v) => { setFilters(f => ({ ...f, [k]: v })); setPage(1); };
  const totalPages = Math.ceil(total / 50);

  return (
    <div>
      <div className="page-header">
        <div className="page-title">
          Tenders
          <span>{total.toLocaleString()} results</span>
        </div>
      </div>

      <div className="filter-bar">
        <input
          className="input"
          placeholder="Search keyword..."
          value={filters.keyword}
          onChange={e => set('keyword', e.target.value)}
          style={{ minWidth: 180 }}
        />
        <select className="select" value={filters.source} onChange={e => set('source', e.target.value)} style={{ minWidth: 120 }}>
          <option value="">All sources</option>
          {SOURCES.map(s => <option key={s} value={s}>{s.toUpperCase()}</option>)}
        </select>
        <input className="input" placeholder="State..." value={filters.state} onChange={e => set('state', e.target.value)} style={{ minWidth: 120 }} />
        <input className="input" placeholder="Department..." value={filters.department} onChange={e => set('department', e.target.value)} style={{ minWidth: 150 }} />
        <select className="select" value={filters.status} onChange={e => set('status', e.target.value)} style={{ minWidth: 100 }}>
          <option value="active">Active</option>
          <option value="closed">Closed</option>
          <option value="">All</option>
        </select>
      </div>

      <div className="card" style={{ padding: 0 }}>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Title</th>
                <th>Reference</th>
                <th>Source</th>
                <th>Department</th>
                <th>Deadline</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {loading
                ? <tr><td colSpan={6} style={{ color: 'var(--text3)', fontFamily: 'var(--mono)' }}>Loading...</td></tr>
                : tenders.length === 0
                  ? <tr><td colSpan={6} style={{ color: 'var(--text3)' }}>No tenders found. Trigger a scrape to populate data.</td></tr>
                  : tenders.map(t => (
                      <tr key={t.id}>
                        <td className="primary" style={{ maxWidth: 300 }}>
                          {t.tender_url
                            ? <a href={t.tender_url} target="_blank" rel="noreferrer">{t.title}</a>
                            : t.title
                          }
                        </td>
                        <td style={{ fontFamily: 'var(--mono)', fontSize: 11, whiteSpace: 'nowrap' }}>{t.reference_no}</td>
                        <td><span className={`badge badge-${t.source}`}>{t.source.toUpperCase()}</span></td>
                        <td style={{ maxWidth: 160, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{t.department || '—'}</td>
                        <td style={{ fontFamily: 'var(--mono)', fontSize: 12, whiteSpace: 'nowrap', color: t.bid_submission_deadline && new Date(t.bid_submission_deadline) < new Date() ? 'var(--red)' : 'var(--text2)' }}>
                          {t.bid_submission_deadline ? format(new Date(t.bid_submission_deadline), 'dd MMM yyyy') : '—'}
                        </td>
                        <td><span className={`badge badge-${t.status}`}>{t.status}</span></td>
                      </tr>
                    ))
              }
            </tbody>
          </table>
        </div>

        {totalPages > 1 && (
          <div style={{ padding: '12px 14px', borderTop: '1px solid var(--border)' }}>
            <div className="pagination">
              <button className="page-btn" disabled={page === 1} onClick={() => setPage(p => p - 1)}>‹</button>
              {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => i + 1).map(p => (
                <button key={p} className={`page-btn ${page === p ? 'active' : ''}`} onClick={() => setPage(p)}>{p}</button>
              ))}
              {totalPages > 7 && <span style={{ color: 'var(--text3)', fontFamily: 'var(--mono)' }}>...{totalPages}</span>}
              <button className="page-btn" disabled={page === totalPages} onClick={() => setPage(p => p + 1)}>›</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
