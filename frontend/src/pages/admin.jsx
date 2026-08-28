import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';

import API from '../config';

export default function AdminPage() {
  const [tab, setTab] = useState('admins'); // admins | users | branches
  const [admins, setAdmins] = useState([]);
  const [users, setUsers] = useState([]);
  const [branches, setBranches] = useState([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const [adminForm, setAdminForm] = useState({
    username: '', email: '', password: '', full_name: '', role: 'admin',
  });
  const [branchForm, setBranchForm] = useState({
    name: '', location: '', manager_name: '', phone: '',
  });

  const load = async () => {
    try {
      const [a, u, b] = await Promise.all([
        fetch(`${API}/admin/admins`),
        fetch(`${API}/admin/users`),
        fetch(`${API}/admin/branches`),
      ]);
      if (a.ok) setAdmins((await a.json()).admins || []);
      if (u.ok) setUsers((await u.json()).users || []);
      if (b.ok) setBranches((await b.json()).branches || []);
    } catch (_) {}
  };

  useEffect(() => { load(); }, []);

  const createAdmin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    setError('');
    try {
      const res = await fetch(`${API}/admin/admins`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(adminForm),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || 'Failed');
      setMessage(data.message || 'Admin created');
      setAdminForm({ username: '', email: '', password: '', full_name: '', role: 'admin' });
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteAdmin = async (id) => {
    if (!confirm('Delete this admin?')) return;
    try {
      const res = await fetch(`${API}/admin/admins/${id}`, { method: 'DELETE' });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed');
      setMessage('Admin deleted');
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  const createBranch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    setError('');
    try {
      const res = await fetch(`${API}/admin/branches`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(branchForm),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || 'Failed');
      setMessage('Branch created');
      setBranchForm({ name: '', location: '', manager_name: '', phone: '' });
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout title="Admin & System">
      {message && <div className="alert alert-success">{message}</div>}
      {error && <div className="alert alert-error">{error}</div>}

      <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
        <button className={`btn ${tab === 'admins' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTab('admins')}>Admins</button>
        <button className={`btn ${tab === 'users' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTab('users')}>Customers</button>
        <button className={`btn ${tab === 'branches' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTab('branches')}>Branches</button>
      </div>

      {tab === 'admins' && (
        <>
          <div className="card">
            <div className="card-header"><h3>Create Admin</h3></div>
            <form onSubmit={createAdmin}>
              <div className="form-grid">
                <div className="form-group"><label>Username *</label><input required value={adminForm.username} onChange={(e) => setAdminForm({ ...adminForm, username: e.target.value })} /></div>
                <div className="form-group"><label>Email *</label><input type="email" required value={adminForm.email} onChange={(e) => setAdminForm({ ...adminForm, email: e.target.value })} /></div>
                <div className="form-group"><label>Password *</label><input type="password" required minLength={6} value={adminForm.password} onChange={(e) => setAdminForm({ ...adminForm, password: e.target.value })} /></div>
                <div className="form-group"><label>Full Name</label><input value={adminForm.full_name} onChange={(e) => setAdminForm({ ...adminForm, full_name: e.target.value })} /></div>
                <div className="form-group"><label>Role</label>
                  <select value={adminForm.role} onChange={(e) => setAdminForm({ ...adminForm, role: e.target.value })}>
                    <option value="super_admin">Super Admin</option>
                    <option value="admin">Admin</option>
                    <option value="support">Support</option>
                  </select>
                </div>
              </div>
              <button type="submit" className="btn btn-primary" style={{ marginTop: 12 }} disabled={loading}>
                {loading ? 'Saving...' : 'Create Admin'}
              </button>
            </form>
          </div>
          <div className="card">
            <div className="card-header"><h3>Administrators</h3></div>
            {admins.length === 0 ? (
              <div className="empty-state">No admins found</div>
            ) : (
              <div className="table-wrap">
                <table>
                  <thead><tr><th>Username</th><th>Email</th><th>Name</th><th>Role</th><th>Status</th><th>Actions</th></tr></thead>
                  <tbody>
                    {admins.map((a) => (
                      <tr key={a.id}>
                        <td style={{ fontWeight: 600 }}>{a.username}</td>
                        <td>{a.email}</td>
                        <td>{a.full_name || '—'}</td>
                        <td><span className="badge badge-active">{a.role}</span></td>
                        <td><span className={`badge badge-${a.status}`}>{a.status}</span></td>
                        <td>
                          <button className="btn btn-danger btn-sm" onClick={() => deleteAdmin(a.id)}>Delete</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}

      {tab === 'users' && (
        <div className="card">
          <div className="card-header"><h3>Registered Customers</h3></div>
          {users.length === 0 ? (
            <div className="empty-state">No customers yet</div>
          ) : (
            <div className="table-wrap">
              <table>
                <thead><tr><th>Username</th><th>Email</th><th>Phone</th><th>Name</th><th>Status</th><th>Joined</th></tr></thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.id}>
                      <td style={{ fontWeight: 600 }}>{u.username}</td>
                      <td>{u.email}</td>
                      <td>{u.phone || '—'}</td>
                      <td>{u.full_name || '—'}</td>
                      <td><span className={`badge badge-${u.status}`}>{u.status}</span></td>
                      <td>{u.created_at?.slice(0, 10)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {tab === 'branches' && (
        <>
          <div className="card">
            <div className="card-header"><h3>Add Branch</h3></div>
            <form onSubmit={createBranch}>
              <div className="form-grid">
                <div className="form-group"><label>Name *</label><input required value={branchForm.name} onChange={(e) => setBranchForm({ ...branchForm, name: e.target.value })} /></div>
                <div className="form-group"><label>Location</label><input value={branchForm.location} onChange={(e) => setBranchForm({ ...branchForm, location: e.target.value })} /></div>
                <div className="form-group"><label>Manager</label><input value={branchForm.manager_name} onChange={(e) => setBranchForm({ ...branchForm, manager_name: e.target.value })} /></div>
                <div className="form-group"><label>Phone</label><input value={branchForm.phone} onChange={(e) => setBranchForm({ ...branchForm, phone: e.target.value })} /></div>
              </div>
              <button type="submit" className="btn btn-primary" style={{ marginTop: 12 }} disabled={loading}>Add Branch</button>
            </form>
          </div>
          <div className="card">
            <div className="card-header"><h3>All Branches</h3></div>
            {branches.length === 0 ? (
              <div className="empty-state">No branches</div>
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
        </>
      )}
    </Layout>
  );
}
