import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';

import API from '../config';

export default function Vouchers() {
  const [vouchers, setVouchers] = useState([]);
  const [packages, setPackages] = useState([]);
  const [routers, setRouters] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(false);
  const [fetchLoading, setFetchLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [filter, setFilter] = useState({ status: '', search: '' });
  const [generated, setGenerated] = useState([]);
  const [form, setForm] = useState({
    package_id: '',
    router_id: '',
    quantity: 10,
    prefix: 'DYN',
    code_length: 8,
    expire_days: 30,
  });

  const load = async () => {
    setFetchLoading(true);
    setError('');
    try {
      const params = new URLSearchParams();
      if (filter.status) params.set('status', filter.status);
      if (filter.search) params.set('search', filter.search);

      const [vRes, pRes, rRes, sRes] = await Promise.all([
        fetch(`${API}/vouchers/?${params}`),
        fetch(`${API}/packages`),
        fetch(`${API}/routing`).catch(() => ({ ok: false })),
        fetch(`${API}/vouchers/stats`),
      ]);

      if (vRes.ok) {
        const d = await vRes.json();
        setVouchers(d.vouchers || []);
      }
      if (pRes.ok) {
        const d = await pRes.json();
        setPackages(Array.isArray(d) ? d : d.packages || []);
      }
      if (rRes.ok) {
        const d = await rRes.json();
        setRouters(Array.isArray(d) ? d : d.routers || []);
      }
      if (sRes.ok) {
        const d = await sRes.json();
        setStats(d.stats || {});
      }
    } catch (e) {
      setError(e.message || 'Failed to load data');
    } finally {
      setFetchLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleGenerate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    setError('');
    setGenerated([]);
    try {
      const res = await fetch(`${API}/vouchers/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          package_id: Number(form.package_id),
          router_id: Number(form.router_id),
          quantity: Number(form.quantity),
          prefix: form.prefix,
          code_length: Number(form.code_length),
          expire_days: Number(form.expire_days),
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || 'Failed');
      setMessage(data.message);
      setGenerated(data.vouchers || []);
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const cancelVoucher = async (id) => {
    if (!confirm('Cancel this voucher?')) return;
    try {
      const res = await fetch(`${API}/vouchers/${id}/cancel`, { method: 'POST' });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed');
      setMessage(data.message);
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <Layout title="Vouchers">
      <div className="stats-grid">
        <div className="stat-card"><div className="label">Active</div><div className="value">{stats.active || 0}</div></div>
        <div className="stat-card"><div className="label">Used</div><div className="value">{stats.used || 0}</div></div>
        <div className="stat-card"><div className="label">Expired</div><div className="value">{stats.expired || 0}</div></div>
        <div className="stat-card"><div className="label">Total</div><div className="value">{stats.total || 0}</div></div>
      </div>

      {message && <div className="alert alert-success">{message}</div>}
      {error && <div className="alert alert-error">{error}</div>}

      <div className="card no-print">
        <div className="card-header"><h3>Generate Vouchers</h3></div>
        <form onSubmit={handleGenerate}>
          <div className="form-grid">
            <div className="form-group">
              <label>Package *</label>
              <select required value={form.package_id} onChange={(e) => setForm({ ...form, package_id: e.target.value })}>
                <option value="">Select package</option>
                {packages.map((p) => (
                  <option key={p.id} value={p.id}>{p.package_name} — TZS {p.price}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Router *</label>
              <select required value={form.router_id} onChange={(e) => setForm({ ...form, router_id: e.target.value })}>
                <option value="">Select router</option>
                {routers.map((r) => (
                  <option key={r.id} value={r.id}>{r.router_name || r.name} ({r.router_ip || r.ip})</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Quantity</label>
              <input type="number" min="1" max="500" value={form.quantity} onChange={(e) => setForm({ ...form, quantity: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Prefix</label>
              <input value={form.prefix} maxLength={10} onChange={(e) => setForm({ ...form, prefix: e.target.value.toUpperCase() })} />
            </div>
            <div className="form-group">
              <label>Code Length</label>
              <input type="number" min="6" max="16" value={form.code_length} onChange={(e) => setForm({ ...form, code_length: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Expire Days</label>
              <input type="number" min="1" max="365" value={form.expire_days} onChange={(e) => setForm({ ...form, expire_days: e.target.value })} />
            </div>
          </div>
          <div style={{ marginTop: '1rem' }}>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Generating...' : '🎟️ Generate'}
            </button>
          </div>
        </form>
      </div>

      {generated.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h3>Newly Generated ({generated.length})</h3>
            <button className="btn btn-secondary btn-sm no-print" onClick={() => window.print()}>🖨️ Print</button>
          </div>
          <div className="voucher-grid">
            {generated.map((v) => (
              <div key={v.id} className="voucher-ticket">
                <div style={{ fontSize: '0.7rem', color: 'var(--yellow)' }}>DYNAMITE NETWORKS</div>
                <div className="code">{v.voucher_code}</div>
                <div className="pkg">{v.package_name}</div>
                <div className="meta">TZS {v.price} · Exp {v.expire_at?.slice(0, 10)}</div>
                <div className="meta">{v.router_name}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="card no-print">
        <div className="card-header">
          <h3>All Vouchers</h3>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <select value={filter.status} onChange={(e) => setFilter({ ...filter, status: e.target.value })} style={{ background: 'var(--bg-input)', border: '1px solid var(--border)', borderRadius: 8, padding: '0.4rem 0.6rem', color: 'var(--text-primary)' }}>
              <option value="">All status</option>
              <option value="active">Active</option>
              <option value="used">Used</option>
              <option value="expired">Expired</option>
              <option value="cancelled">Cancelled</option>
            </select>
            <input placeholder="Search code..." value={filter.search} onChange={(e) => setFilter({ ...filter, search: e.target.value })} style={{ background: 'var(--bg-input)', border: '1px solid var(--border)', borderRadius: 8, padding: '0.4rem 0.6rem', color: 'var(--text-primary)' }} />
            <button className="btn btn-secondary btn-sm" onClick={load}>Filter</button>
          </div>
        </div>

        {fetchLoading ? (
          <div className="loading"><div className="spinner" /> Loading...</div>
        ) : vouchers.length === 0 ? (
          <div className="empty-state"><div className="icon">🎟️</div>No vouchers found</div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Code</th>
                  <th>Package</th>
                  <th>Router</th>
                  <th>Price</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Expires</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {vouchers.map((v) => (
                  <tr key={v.id}>
                    <td style={{ fontFamily: 'monospace', fontWeight: 600, color: 'var(--yellow)' }}>{v.voucher_code}</td>
                    <td>{v.package_name || '—'}</td>
                    <td>{v.router_name || '—'}</td>
                    <td>{v.price != null ? `TZS ${v.price}` : '—'}</td>
                    <td><span className={`badge badge-${v.status}`}>{v.status}</span></td>
                    <td>{v.created_at?.slice(0, 10)}</td>
                    <td>{v.expire_at?.slice(0, 10)}</td>
                    <td>
                      {v.status === 'active' && (
                        <button className="btn btn-danger btn-sm" onClick={() => cancelVoucher(v.id)}>Cancel</button>
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
