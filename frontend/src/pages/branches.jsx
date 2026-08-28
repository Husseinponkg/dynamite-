import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';

import API from '../config';

export default function Branches() {
  const [branches, setBranches] = useState([]);
  const [form, setForm] = useState({ name: '', location: '', manager_name: '', phone: '' });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const load = async () => {
    try {
      const res = await fetch(`${API}/admin/branches`);
      if (res.ok) {
        const d = await res.json();
        setBranches(d.branches || []);
      }
    } catch (_) {}
  };

  useEffect(() => { load(); }, []);

  const add = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');
    try {
      const res = await fetch(`${API}/admin/branches`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || 'Failed');
      setMessage('Branch added');
      setForm({ name: '', location: '', manager_name: '', phone: '' });
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <Layout title="Branches">
      {message && <div className="alert alert-success">{message}</div>}
      {error && <div className="alert alert-error">{error}</div>}
      <div className="card">
        <div className="card-header"><h3>Add Branch</h3></div>
        <form onSubmit={add}>
          <div className="form-grid">
            <div className="form-group"><label>Name *</label><input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></div>
            <div className="form-group"><label>Location</label><input value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} /></div>
            <div className="form-group"><label>Manager</label><input value={form.manager_name} onChange={(e) => setForm({ ...form, manager_name: e.target.value })} /></div>
            <div className="form-group"><label>Phone</label><input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} /></div>
          </div>
          <div style={{ marginTop: '1rem' }}><button type="submit" className="btn btn-primary">Add Branch</button></div>
        </form>
      </div>
      <div className="card">
        <div className="card-header"><h3>All Branches</h3></div>
        {branches.length === 0 ? (
          <div className="empty-state"><div className="icon">🏢</div>No branches yet</div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Name</th><th>Location</th><th>Manager</th><th>Phone</th><th>Status</th></tr></thead>
              <tbody>
                {branches.map((b) => (
                  <tr key={b.id}>
                    <td style={{ fontWeight: 600 }}>{b.name}</td>
                    <td>{b.location || '—'}</td>
                    <td>{b.manager_name || '—'}</td>
                    <td>{b.phone || '—'}</td>
                    <td><span className={`badge badge-${b.status}`}>{b.status}</span></td>
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
