import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';

import API from '../config';

export default function Router() {
  const empty = {
    router_name: '', router_ip: '', router_port: 8728, username: '', password: '',
    api_type: 'mikrotik', location: '', max_users: 500,
  };
  const [form, setForm] = useState(empty);
  const [routers, setRouters] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [editingId, setEditingId] = useState(null);

  const load = async () => {
    try {
      const res = await fetch(`${API}/routing`);
      if (res.ok) {
        const d = await res.json();
        setRouters(Array.isArray(d) ? d : d.routers || []);
      }
    } catch (_) {}
  };

  useEffect(() => { load(); }, []);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    setError('');
    try {
      const payload = {
        ...form,
        router_port: Number(form.router_port),
        max_users: Number(form.max_users),
      };
      const url = editingId ? `${API}/routing/${editingId}` : `${API}/routing/create`;
      const method = editingId ? 'PUT' : 'POST';
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || 'Failed');
      setMessage(data.message || 'Saved');
      setForm(empty);
      setEditingId(null);
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const edit = (r) => {
    setEditingId(r.id);
    setForm({
      router_name: r.router_name || '',
      router_ip: r.router_ip || '',
      router_port: r.router_port || 8728,
      username: r.username || '',
      password: '',
      api_type: r.api_type || 'mikrotik',
      location: r.location || '',
      max_users: r.max_users || 500,
    });
  };

  const remove = async (id) => {
    if (!confirm('Delete router?')) return;
    try {
      const res = await fetch(`${API}/routing/${id}`, { method: 'DELETE' });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed');
      setMessage(data.message || 'Deleted');
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <Layout title="Routers">
      {message && <div className="alert alert-success">{message}</div>}
      {error && <div className="alert alert-error">{error}</div>}

      <div className="card">
        <div className="card-header">
          <h3>{editingId ? 'Edit Router' : 'Add Router'}</h3>
          {editingId && (
            <button className="btn btn-ghost btn-sm" onClick={() => { setEditingId(null); setForm(empty); }}>Cancel</button>
          )}
        </div>
        <form onSubmit={submit}>
          <div className="form-grid">
            <div className="form-group"><label>Name *</label><input name="router_name" value={form.router_name} onChange={handleChange} required /></div>
            <div className="form-group"><label>IP Address *</label><input name="router_ip" value={form.router_ip} onChange={handleChange} required placeholder="192.168.88.1" /></div>
            <div className="form-group"><label>API Port</label><input name="router_port" type="number" value={form.router_port} onChange={handleChange} /></div>
            <div className="form-group"><label>Username *</label><input name="username" value={form.username} onChange={handleChange} required /></div>
            <div className="form-group"><label>Password *</label><input name="password" type="password" value={form.password} onChange={handleChange} required={!editingId} /></div>
            <div className="form-group"><label>API Type</label>
              <select name="api_type" value={form.api_type} onChange={handleChange}>
                <option value="mikrotik">MikroTik API</option>
                <option value="rest_api">REST API</option>
              </select>
            </div>
            <div className="form-group"><label>Location</label><input name="location" value={form.location} onChange={handleChange} /></div>
            <div className="form-group"><label>Max Users</label><input name="max_users" type="number" value={form.max_users} onChange={handleChange} /></div>
          </div>
          <div style={{ marginTop: '1rem' }}>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Saving...' : editingId ? 'Update' : 'Add Router'}
            </button>
          </div>
        </form>
      </div>

      <div className="card">
        <div className="card-header"><h3>Registered Routers</h3></div>
        {routers.length === 0 ? (
          <div className="empty-state"><div className="icon">📡</div>No routers registered</div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>Name</th><th>IP</th><th>Port</th><th>Location</th><th>Status</th><th>Max Users</th><th>Actions</th></tr>
              </thead>
              <tbody>
                {routers.map((r) => (
                  <tr key={r.id}>
                    <td style={{ fontWeight: 600 }}>{r.router_name}</td>
                    <td>{r.router_ip}</td>
                    <td>{r.router_port}</td>
                    <td>{r.location || '—'}</td>
                    <td><span className={`badge badge-${r.status || 'offline'}`}>{r.status || 'unknown'}</span></td>
                    <td>{r.max_users}</td>
                    <td style={{ display: 'flex', gap: '0.4rem' }}>
                      <button className="btn btn-secondary btn-sm" onClick={() => edit(r)}>Edit</button>
                      <button className="btn btn-danger btn-sm" onClick={() => remove(r.id)}>Delete</button>
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
