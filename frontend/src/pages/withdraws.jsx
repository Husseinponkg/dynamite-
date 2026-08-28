import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';

import API from '../config';

export default function Withdraws() {
  const [withdraws, setWithdraws] = useState([]);
  const [balance, setBalance] = useState(0);
  const [pending, setPending] = useState(0);
  const [withdrawn, setWithdrawn] = useState(0);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [form, setForm] = useState({
    amount: '',
    method: 'mpesa',
    account_number: '',
    account_name: '',
    notes: '',
  });

  const load = async () => {
    try {
      const [wRes, iRes] = await Promise.all([
        fetch(`${API}/withdraws/`),
        fetch(`${API}/income/summary`),
      ]);
      if (wRes.ok) {
        const d = await wRes.json();
        setWithdraws(d.withdraws || []);
      }
      if (iRes.ok) {
        const d = await iRes.json();
        setBalance(d.income?.available_balance || 0);
        setPending(d.income?.pending_withdraw || 0);
        setWithdrawn(d.income?.withdrawn || 0);
      }
    } catch (_) {}
  };

  useEffect(() => { load(); }, []);

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    setError('');
    try {
      const res = await fetch(`${API}/withdraws/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount: Number(form.amount),
          method: form.method,
          account_number: form.account_number,
          account_name: form.account_name || undefined,
          notes: form.notes || undefined,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || 'Failed');
      setMessage(data.message || 'Request submitted');
      setForm({ amount: '', method: 'mpesa', account_number: '', account_name: '', notes: '' });
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateStatus = async (id, status) => {
    try {
      const res = await fetch(`${API}/withdraws/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed');
      setMessage(`Marked as ${status}`);
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  const fmt = (n) => `TZS ${Number(n || 0).toLocaleString()}`;

  return (
    <Layout title="Withdraws">
      {message && <div className="alert alert-success">{message}</div>}
      {error && <div className="alert alert-error">{error}</div>}

      <div className="stats-grid">
        <div className="stat-card"><div className="label">Available Balance</div><div className="value">{fmt(balance)}</div></div>
        <div className="stat-card"><div className="label">Pending Requests</div><div className="value">{fmt(pending)}</div></div>
        <div className="stat-card"><div className="label">Total Withdrawn</div><div className="value">{fmt(withdrawn)}</div></div>
      </div>

      <div className="card">
        <div className="card-header"><h3>Request Withdrawal</h3></div>
        <form onSubmit={submit}>
          <div className="form-grid">
            <div className="form-group">
              <label>Amount (TZS) *</label>
              <input type="number" min="1" step="0.01" required value={form.amount}
                onChange={(e) => setForm({ ...form, amount: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Method</label>
              <select value={form.method} onChange={(e) => setForm({ ...form, method: e.target.value })}>
                <option value="mpesa">M-Pesa</option>
                <option value="airtel">Airtel Money</option>
                <option value="tigo">Tigo Pesa</option>
                <option value="halotel">HaloPesa</option>
                <option value="bank_transfer">Bank Transfer</option>
                <option value="cash">Cash</option>
              </select>
            </div>
            <div className="form-group">
              <label>Account / Phone *</label>
              <input required value={form.account_number}
                onChange={(e) => setForm({ ...form, account_number: e.target.value })} placeholder="2557... or account no" />
            </div>
            <div className="form-group">
              <label>Account Name</label>
              <input value={form.account_name}
                onChange={(e) => setForm({ ...form, account_name: e.target.value })} />
            </div>
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label>Notes</label>
              <textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
            </div>
          </div>
          <div style={{ marginTop: 12 }}>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Submitting...' : 'Submit Withdraw Request'}
            </button>
          </div>
        </form>
      </div>

      <div className="card">
        <div className="card-header"><h3>History</h3></div>
        {withdraws.length === 0 ? (
          <div className="empty-state"><div className="icon">🏦</div>No withdrawals yet</div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>Amount</th><th>Method</th><th>Account</th><th>Status</th><th>Date</th><th>Actions</th></tr>
              </thead>
              <tbody>
                {withdraws.map((w) => (
                  <tr key={w.id}>
                    <td style={{ color: 'var(--yellow)', fontWeight: 600 }}>{fmt(w.amount)}</td>
                    <td>{w.method}</td>
                    <td>{w.account_number}<br /><span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{w.account_name}</span></td>
                    <td><span className={`badge badge-${w.status}`}>{w.status}</span></td>
                    <td>{w.created_at?.slice(0, 16).replace('T', ' ')}</td>
                    <td style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                      {w.status === 'pending' && (
                        <>
                          <button className="btn btn-primary btn-sm" onClick={() => updateStatus(w.id, 'completed')}>Complete</button>
                          <button className="btn btn-danger btn-sm" onClick={() => updateStatus(w.id, 'rejected')}>Reject</button>
                        </>
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
