import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';

import API from '../config';

export default function Sessions() {
  const [sessions, setSessions] = useState([]);
  const [stats, setStats] = useState({});
  const [filter, setFilter] = useState('active');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const [sRes, stRes] = await Promise.all([
        fetch(`${API}/sessions/?status=${filter || ''}&limit=200`),
        fetch(`${API}/sessions/stats`),
      ]);
      if (sRes.ok) {
        const d = await sRes.json();
        setSessions(d.sessions || []);
      }
      if (stRes.ok) {
        const d = await stRes.json();
        setStats(d.stats || {});
      }
    } catch (e) {
      setError(e.message || 'Failed to load sessions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [filter]);

  const endSession = async (sessionId) => {
    if (!confirm('Terminate this session?')) return;
    try {
      const res = await fetch(`${API}/sessions/end`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed');
      setMessage('Session terminated');
      await load();
    } catch (e) {
      setError(e.message);
    }
  };

  const fmtMB = (b) => `${((b || 0) / 1024 / 1024).toFixed(1)} MB`;

  return (
    <Layout title="Active Sessions">
      {message && <div className="alert alert-success">{message}</div>}
      {error && <div className="alert alert-error">{error}</div>}

      <div className="stats-grid">
        <div className="stat-card"><div className="label">Active Now</div><div className="value">{stats.active_now || 0}</div></div>
        <div className="stat-card"><div className="label">Sessions Today</div><div className="value">{stats.today || 0}</div></div>
        <div className="stat-card"><div className="label">Active Usage</div><div className="value">{stats.active_usage_mb || 0} MB</div></div>
        <div className="stat-card"><div className="label">Total Usage</div><div className="value">{stats.total_usage_mb || 0} MB</div></div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Connected Users</h3>
          <div style={{ display: 'flex', gap: 8 }}>
            <select value={filter} onChange={(e) => setFilter(e.target.value)}
              style={{ background: 'var(--bg-input)', border: '1px solid var(--border)', borderRadius: 8, padding: '0.4rem 0.6rem', color: 'var(--text-primary)' }}>
              <option value="active">Active</option>
              <option value="terminated">Terminated</option>
              <option value="inactive">Inactive</option>
              <option value="">All</option>
            </select>
            <button className="btn btn-secondary btn-sm" onClick={load}>Refresh</button>
          </div>
        </div>

        {loading ? (
          <div className="loading"><div className="spinner" /> Loading sessions...</div>
        ) : sessions.length === 0 ? (
          <div className="empty-state">
            <div className="icon">🔗</div>
            <p>No sessions. Users appear here after redeeming a voucher or completing payment on the captive portal.</p>
          </div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>User / Session</th>
                  <th>IP</th>
                  <th>MAC</th>
                  <th>Router</th>
                  <th>Usage</th>
                  <th>Started</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {sessions.map((s) => (
                  <tr key={s.id}>
                    <td>
                      <div style={{ fontWeight: 600 }}>{s.username || s.session_id?.slice(0, 20)}</div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'monospace' }}>{s.session_id}</div>
                    </td>
                    <td>{s.ip_address || '—'}</td>
                    <td style={{ fontFamily: 'monospace', fontSize: 12 }}>{s.mac_address || '—'}</td>
                    <td>{s.router_name || s.router_id}</td>
                    <td>{fmtMB(s.total_usage)}</td>
                    <td>{s.start_time?.slice(0, 16).replace('T', ' ')}</td>
                    <td><span className={`badge badge-${s.status}`}>{s.status}</span></td>
                    <td>
                      {s.status === 'active' && (
                        <button className="btn btn-danger btn-sm" onClick={() => endSession(s.session_id)}>End</button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Layout>
  );
}
