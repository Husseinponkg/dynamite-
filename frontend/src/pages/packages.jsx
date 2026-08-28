import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';

import API from '../config';

export default function Packages() {
  const [packages, setPackages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [fetchLoading, setFetchLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [editingId, setEditingId] = useState(null);

  const emptyForm = {
    package_name: '', package_desc: '', price: '', validity_days: '',
    validity_hours: '0', bandwidth_up: '', bandwidth_down: '',
    data_limit: '0', concurrent_logins: '1', status: 'active',
  };
  const [formdata, setFormData] = useState(emptyForm);

  const handleChange = (e) => {
    setFormData((p) => ({ ...p, [e.target.name]: e.target.value }));
  };

  const getPackages = async () => {
    setFetchLoading(true);
    setError('');
    try {
      const res = await fetch(`${API}/packages`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed');
      setPackages(Array.isArray(data) ? data : data.packages || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setFetchLoading(false);
    }
  };

  useEffect(() => { getPackages(); }, []);

  const createPackage = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    setError('');
    try {
      const payload = {
        package_name: formdata.package_name,
        package_desc: formdata.package_desc,
        price: Number(formdata.price),
        validity_days: Number(formdata.validity_days),
        validity_hours: Number(formdata.validity_hours),
        bandwidth_up: Number(formdata.bandwidth_up),
        bandwidth_down: Number(formdata.bandwidth_down),
        data_limit: Number(formdata.data_limit),
        concurrent_logins: Number(formdata.concurrent_logins),
        status: formdata.status,
      };
      const url = editingId ? `${API}/packages/${editingId}` : `${API}/packages/create`;
      const res = await fetch(url, {
        method: editingId ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || 'Failed');
      setMessage(data.message || (editingId ? 'Updated' : 'Created'));
      setFormData(emptyForm);
      setEditingId(null);
      await getPackages();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const editPkg = (p) => {
    setEditingId(p.id);
    setFormData({
      package_name: p.package_name || '',
      package_desc: p.package_desc || '',
      price: String(p.price ?? ''),
      validity_days: String(p.validity_days ?? ''),
      validity_hours: String(p.validity_hours ?? 0),
      bandwidth_up: String(p.bandwidth_up ?? ''),
      bandwidth_down: String(p.bandwidth_down ?? ''),
      data_limit: String(p.data_limit ?? 0),
      concurrent_logins: String(p.concurrent_logins ?? 1),
      status: p.status || 'active',
    });
  };

  const deletePkg = async (id) => {
    if (!confirm('Delete this package?')) return;
    try {
      const res = await fetch(`${API}/packages/${id}`, { method: 'DELETE' });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed');
      setMessage(data.message || 'Deleted');
      await getPackages();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <Layout title="Packages">
      {message && <div className="alert alert-success">{message}</div>}
      {error && <div className="alert alert-error">{error}</div>}

      <div className="card">
        <div className="card-header">
          <h3>{editingId ? 'Edit Package' : 'Create Package'}</h3>
          {editingId && (
            <button className="btn btn-ghost btn-sm" onClick={() => { setEditingId(null); setFormData(emptyForm); }}>Cancel edit</button>
          )}
        </div>
        <form onSubmit={createPackage}>
          <div className="form-grid">
            <div className="form-group"><label>Name *</label><input name="package_name" value={formdata.package_name} onChange={handleChange} required /></div>
            <div className="form-group"><label>Price (TZS) *</label><input name="price" type="number" step="0.01" value={formdata.price} onChange={handleChange} required /></div>
            <div className="form-group"><label>Validity Days *</label><input name="validity_days" type="number" value={formdata.validity_days} onChange={handleChange} required /></div>
            <div className="form-group"><label>Validity Hours</label><input name="validity_hours" type="number" min="0" max="23" value={formdata.validity_hours} onChange={handleChange} /></div>
            <div className="form-group"><label>Upload (Kbps)</label><input name="bandwidth_up" type="number" value={formdata.bandwidth_up} onChange={handleChange} /></div>
            <div className="form-group"><label>Download (Kbps)</label><input name="bandwidth_down" type="number" value={formdata.bandwidth_down} onChange={handleChange} /></div>
            <div className="form-group"><label>Data Limit (MB, 0=∞)</label><input name="data_limit" type="number" value={formdata.data_limit} onChange={handleChange} /></div>
            <div className="form-group"><label>Concurrent Logins</label><input name="concurrent_logins" type="number" min="1" value={formdata.concurrent_logins} onChange={handleChange} /></div>
            <div className="form-group"><label>Status</label>
              <select name="status" value={formdata.status} onChange={handleChange}>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label>Description</label>
              <textarea name="package_desc" value={formdata.package_desc} onChange={handleChange} />
            </div>
          </div>
          <div style={{ marginTop: '1rem' }}>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Saving...' : editingId ? 'Update Package' : 'Create Package'}
            </button>
          </div>
        </form>
      </div>

      <div className="card">
        <div className="card-header"><h3>All Packages</h3></div>
        {fetchLoading ? (
          <div className="loading"><div className="spinner" /> Loading...</div>
        ) : packages.length === 0 ? (
          <div className="empty-state"><div className="icon">📦</div>No packages yet</div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Name</th><th>Price</th><th>Validity</th><th>Bandwidth</th>
                  <th>Data</th><th>Status</th><th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {packages.map((p) => (
                  <tr key={p.id}>
                    <td style={{ fontWeight: 600 }}>{p.package_name}</td>
                    <td>TZS {p.price}</td>
                    <td>{p.validity_days}d {p.validity_hours ? `${p.validity_hours}h` : ''}</td>
                    <td>{p.bandwidth_down}/{p.bandwidth_up} Kbps</td>
                    <td>{p.data_limit ? `${p.data_limit} MB` : 'Unlimited'}</td>
                    <td><span className={`badge badge-${p.status}`}>{p.status}</span></td>
                    <td style={{ display: 'flex', gap: '0.4rem' }}>
                      <button className="btn btn-secondary btn-sm" onClick={() => editPkg(p)}>Edit</button>
                      <button className="btn btn-danger btn-sm" onClick={() => deletePkg(p.id)}>Delete</button>
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
