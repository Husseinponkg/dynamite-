import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';

import API from '../config';

export default function Payments() {
  const [payments, setPayments] = useState([]);
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [counts, setCounts] = useState({});

  const load = async () => {
    setLoading(true);
    try {
      const params = filter ? `?status=${filter}` : '';
      const [pRes, iRes] = await Promise.all([
        fetch(`${API}/income/payments${params}`),
        fetch(`${API}/income/summary`),
      ]);
      if (pRes.ok) {
        const d = await pRes.json();
        setPayments(d.payments || []);
      }
      if (iRes.ok) {
        const d = await iRes.json();
        setCounts(d.payment_counts || {});
      }
    } catch (_) {}
    setLoading(false);
  };

  useEffect(() => { load(); }, [filter]);

  const fmt = (n) => `TZS ${Number(n || 0).toLocaleString()}`;

  return (
    <Layout title="Payments">
      <div className="stats-grid">
        <div className="stat-card"><div className="label">Completed</div><div className="value">{counts.completed || 0}</div></div>
        <div className="stat-card"><div className="label">Pending</div><div className="value">{counts.pending || 0}</div></div>
        <div className="stat-card"><div className="label">Failed</div><div className="value">{counts.failed || 0}</div></div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Payment History</h3>
          <div style={{ display: 'flex', gap: 8 }}>
            <select value={filter} onChange={(e) => setFilter(e.target.value)}
              style={{ background: 'var(--bg-input)', border: '1px solid var(--border)', borderRadius: 8, padding: '0.4rem 0.6rem', color: 'var(--text-primary)' }}>
              <option value="">All</option>
              <option value="completed">Completed</option>
              <option value="pending">Pending</option>
              <option value="failed">Failed</option>
            </select>
            <button className="btn btn-secondary btn-sm" onClick={load}>Refresh</button>
          </div>
        </div>
        {loading ? (
          <div className="loading"><div className="spinner" /> Loading...</div>
        ) : payments.length === 0 ? (
          <div className="empty-state">
            <div className="icon">💳</div>
            <p>No payments yet. They appear when users pay via captive portal or admin initiates checkout.</p>
          </div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>Ref</th><th>Phone</th><th>Method</th><th>Amount</th><th>Status</th><th>Date</th></tr>
              </thead>
              <tbody>
                {payments.map((p) => (
                  <tr key={p.id}>
                    <td style={{ fontFamily: 'monospace', fontSize: 12 }}>{p.reference_number}</td>
                    <td>{p.phone_number}</td>
                    <td>{p.payment_method}</td>
                    <td style={{ color: 'var(--yellow)' }}>{fmt(p.amount)}</td>
                    <td><span className={`badge badge-${(p.status || '').toLowerCase()}`}>{p.status}</span></td>
                    <td>{p.created_at?.slice(0, 16).replace('T', ' ')}</td>
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
