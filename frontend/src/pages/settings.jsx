import React, { useState } from 'react';
import Layout from '../components/Layout';

export default function Settings() {
  const [msg, setMsg] = useState('');
  const [form, setForm] = useState({
    company: 'Dynamite Networks',
    currency: 'TZS',
    timezone: 'Africa/Dar_es_Salaam',
    sms_enabled: false,
  });

  const save = (e) => {
    e.preventDefault();
    setMsg('Settings saved locally (connect backend to persist).');
  };

  return (
    <Layout title="Settings">
      {msg && <div className="alert alert-success">{msg}</div>}
      <div className="card">
        <div className="card-header"><h3>General Settings</h3></div>
        <form onSubmit={save}>
          <div className="form-grid">
            <div className="form-group">
              <label>Company Name</label>
              <input value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Currency</label>
              <select value={form.currency} onChange={(e) => setForm({ ...form, currency: e.target.value })}>
                <option value="TZS">TZS — Tanzanian Shilling</option>
                <option value="USD">USD</option>
                <option value="KES">KES</option>
              </select>
            </div>
            <div className="form-group">
              <label>Timezone</label>
              <input value={form.timezone} onChange={(e) => setForm({ ...form, timezone: e.target.value })} />
            </div>
          </div>
          <div style={{ marginTop: '1rem' }}>
            <button type="submit" className="btn btn-primary">Save Settings</button>
          </div>
        </form>
      </div>
      <div className="card">
        <div className="card-header"><h3>Theme</h3></div>
        <p style={{ color: 'var(--text-secondary)' }}>
          Current theme: <strong style={{ color: 'var(--yellow)' }}>Black & Yellow</strong> — optimized for modern ISP billing dashboards.
        </p>
      </div>
    </Layout>
  );
}
