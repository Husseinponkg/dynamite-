import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';

import API from '../config';

export default function Income() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API}/income/summary`);
      const json = await res.json();
      if (!res.ok) throw new Error(json.detail || 'Failed');
      setData(json);
    } catch (e) {
      setError(e.message || 'Could not load income');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const inc = data?.income || {};
  const counts = data?.payment_counts || {};
  const methods = data?.by_method || [];
  const recent = data?.recent_transactions || [];

  const fmt = (n) => `TZS ${Number(n || 0).toLocaleString()}`;

  return (
    <Layout title="Income & Reports">
      {error && <div className="alert alert-error">{error}</div>}
      {loading ? (
        <div className="loading"><div className="spinner" /> Calculating income...</div>
      ) : (
        <>
          <div className="stats-grid">
            <div className="stat-card"><div className="label">Today</div><div className="value">{fmt(inc.today)}</div></div>
            <div className="stat-card"><div className="label">This Week</div><div className="value">{fmt(inc.this_week)}</div></div>
            <div className="stat-card"><div className="label">This Month</div><div className="value">{fmt(inc.this_month)}</div></div>
            <div className="stat-card"><div className="label">Total Income</div><div className="value">{fmt(inc.total_income)}</div>
              <div className="sub">Payments + vouchers</div>
            </div>
            <div className="stat-card"><div className="label">Available Balance</div><div className="value">{fmt(inc.available_balance)}</div>
              <div className="sub">After withdraws</div>
            </div>
            <div className="stat-card"><div className="label">Withdrawn</div><div className="value">{fmt(inc.withdrawn)}</div></div>
          </div>

          <div className="stats-grid">
            <div className="stat-card"><div className="label">Completed payments</div><div className="value">{counts.completed || 0}</div></div>
            <div className="stat-card"><div className="label">Pending</div><div className="value">{counts.pending || 0}</div></div>
            <div className="stat-card"><div className="label">Failed</div><div className="value">{counts.failed || 0}</div></div>
            <div className="stat-card"><div className="label">Voucher revenue</div><div className="value">{fmt(inc.voucher_revenue)}</div></div>
          </div>

          <div className="card">
            <div className="card-header">
              <h3>Revenue by Method</h3>
              <button className="btn btn-secondary btn-sm" onClick={load}>Refresh</button>
            </div>
            {methods.length === 0 ? (
              <div className="empty-state">No completed payments yet</div>
            ) : (
              <div className="table-wrap">
                <table>
                  <thead><tr><th>Method</th><th>Count</th><th>Total</th></tr></thead>
                  <tbody>
                    {methods.map((m) => (
                      <tr key={m.method}>
                        <td style={{ textTransform: 'uppercase', fontWeight: 600 }}>{m.method}</td>
                        <td>{m.count}</td>
                        <td style={{ color: 'var(--yellow)' }}>{fmt(m.total)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          <div className="card">
            <div className="card-header"><h3>Recent Transactions</h3></div>
            {recent.length === 0 ? (
              <div className="empty-state">No transactions</div>
            ) : (
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr><th>Ref</th><th>Phone</th><th>Method</th><th>Amount</th><th>Status</th><th>Date</th></tr>
                  </thead>
                  <tbody>
                    {recent.map((t) => (
                      <tr key={t.id}>
                        <td style={{ fontFamily: 'monospace', fontSize: 12 }}>{t.reference_number}</td>
                        <td>{t.phone_number}</td>
                        <td>{t.payment_method}</td>
                        <td>{fmt(t.amount)}</td>
                        <td><span className={`badge badge-${(t.status || '').toLowerCase()}`}>{t.status}</span></td>
                        <td>{t.created_at?.slice(0, 16).replace('T', ' ')}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </Layout>
  );
}
