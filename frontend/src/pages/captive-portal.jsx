import React, { useEffect, useState } from 'react';

import API from '../config';

/** Public captive portal — WiFi users land here to buy or redeem */
export default function CaptivePortal() {
  const [packages, setPackages] = useState([]);
  const [mode, setMode] = useState('packages'); // packages | pay | redeem
  const [selected, setSelected] = useState(null);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [payForm, setPayForm] = useState({
    phone_number: '',
    payment_method: 'mpesa',
    mac_address: '',
  });
  const [redeemCode, setRedeemCode] = useState('');

  useEffect(() => {
    fetch(`${API}/captive/packages`)
      .then((r) => {
        if (!r.ok) throw new Error(`captive packages HTTP ${r.status}`);
        return r.json();
      })
      .then((d) => setPackages(d.packages || []))
      .catch(() =>
        fetch(`${API}/packages`)
          .then((r) => {
            if (!r.ok) throw new Error(`packages HTTP ${r.status}`);
            return r.json();
          })
          .then((d) => setPackages(Array.isArray(d) ? d : d.packages || []))
          .catch(() => {})
      );
  }, []);

  const startPay = (pkg) => {
    setSelected(pkg);
    setMode('pay');
    setMessage('');
    setError('');
  };

  const handlePay = async (e) => {
    e.preventDefault();
    if (!selected) return;
    setLoading(true);
    setMessage('');
    setError('');
    try {
      const res = await fetch(`${API}/captive/checkout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          package_id: selected.id,
          phone_number: payForm.phone_number,
          payment_method: payForm.payment_method,
          mac_address: payForm.mac_address || undefined,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || 'Payment failed');
      setMessage(data.message || 'Payment initiated — check your phone');
    } catch (err) {
      setError(typeof err.message === 'string' ? err.message : 'Payment error');
    } finally {
      setLoading(false);
    }
  };

  const handleRedeem = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    setError('');
    try {
      const res = await fetch(`${API}/captive/redeem`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          voucher_code: redeemCode.trim(),
          mac_address: payForm.mac_address || undefined,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || 'Invalid code');
      setMessage(
        `Connected! Package: ${data.package?.name || 'OK'}${data.session_id ? ` · Session ${data.session_id}` : ''}`
      );
      setRedeemCode('');
    } catch (err) {
      setError(typeof err.message === 'string' ? err.message : 'Redeem failed');
    } finally {
      setLoading(false);
    }
  };

  // Standalone portal look (no admin sidebar) — for WiFi users
  return (
    <div className="auth-page" style={{ alignItems: 'flex-start', paddingTop: '2rem' }}>
      <div style={{ width: '100%', maxWidth: 720 }}>
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <div
            style={{
              width: 56,
              height: 56,
              background: 'linear-gradient(135deg, var(--yellow), #ffaa00)',
              borderRadius: 14,
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 800,
              color: '#000',
              fontSize: '1.4rem',
              marginBottom: 8,
            }}
          >
            DN
          </div>
          <h1 style={{ color: 'var(--yellow)', fontSize: '1.5rem', margin: 0 }}>Dynamite Networks WiFi</h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: 4 }}>Buy internet or redeem a voucher</p>
        </div>

        {message && <div className="alert alert-success">{message}</div>}
        {error && <div className="alert alert-error">{error}</div>}

        <div style={{ display: 'flex', gap: 8, marginBottom: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
          <button className={`btn ${mode === 'packages' || mode === 'pay' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => { setMode('packages'); setSelected(null); }}>
            📦 Packages
          </button>
          <button className={`btn ${mode === 'redeem' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setMode('redeem')}>
            🎟️ Voucher Code
          </button>
        </div>

        {(mode === 'packages' || mode === 'pay') && (
          <>
            {mode === 'packages' && (
              <div className="stats-grid">
                {packages.length === 0 ? (
                  <div className="card" style={{ gridColumn: '1 / -1' }}>
                    <div className="empty-state">No packages available right now</div>
                  </div>
                ) : (
                  packages.map((p) => (
                    <div
                      key={p.id}
                      className="stat-card"
                      style={{ cursor: 'pointer' }}
                      onClick={() => startPay(p)}
                    >
                      <div className="label">{p.package_name}</div>
                      <div className="value">TZS {Number(p.price).toLocaleString()}</div>
                      <div className="sub">
                        {p.validity_days}d{p.validity_hours ? ` ${p.validity_hours}h` : ''} ·{' '}
                        {p.bandwidth_down ? `${p.bandwidth_down} Kbps` : 'Fair use'}
                        {p.data_limit ? ` · ${p.data_limit} MB` : ' · Unlimited'}
                      </div>
                      <button className="btn btn-primary btn-sm" style={{ marginTop: 10, width: '100%' }}>
                        Buy Now
                      </button>
                    </div>
                  ))
                )}
              </div>
            )}

            {mode === 'pay' && selected && (
              <div className="card">
                <div className="card-header">
                  <h3>Pay for {selected.package_name}</h3>
                  <button className="btn btn-ghost btn-sm" onClick={() => { setMode('packages'); setSelected(null); }}>
                    ← Back
                  </button>
                </div>
                <p style={{ color: 'var(--yellow)', fontWeight: 700, fontSize: '1.25rem', marginBottom: 16 }}>
                  TZS {Number(selected.price).toLocaleString()}
                </p>
                <form onSubmit={handlePay}>
                  <div className="form-grid">
                    <div className="form-group">
                      <label>Phone Number *</label>
                      <input
                        required
                        placeholder="2557XXXXXXXX"
                        value={payForm.phone_number}
                        onChange={(e) => setPayForm({ ...payForm, phone_number: e.target.value })}
                      />
                    </div>
                    <div className="form-group">
                      <label>Payment Method</label>
                      <select
                        value={payForm.payment_method}
                        onChange={(e) => setPayForm({ ...payForm, payment_method: e.target.value })}
                      >
                        <option value="mpesa">M-Pesa (Vodacom)</option>
                        <option value="airtel">Airtel Money</option>
                        <option value="tigo">Tigo Pesa</option>
                        <option value="halotel">HaloPesa</option>
                        <option value="yas">Yas</option>
                        <option value="cash">Cash (counter)</option>
                      </select>
                    </div>
                    <div className="form-group">
                      <label>Device MAC (optional)</label>
                      <input
                        placeholder="AA:BB:CC:DD:EE:FF"
                        value={payForm.mac_address}
                        onChange={(e) => setPayForm({ ...payForm, mac_address: e.target.value })}
                      />
                    </div>
                  </div>
                  <button type="submit" className="btn btn-primary" style={{ marginTop: 16, width: '100%' }} disabled={loading}>
                    {loading ? 'Processing...' : `Pay TZS ${Number(selected.price).toLocaleString()}`}
                  </button>
                </form>
              </div>
            )}
          </>
        )}

        {mode === 'redeem' && (
          <div className="card">
            <div className="card-header"><h3>Enter Voucher Code</h3></div>
            <form onSubmit={handleRedeem}>
              <div className="form-group">
                <label>Code</label>
                <input
                  required
                  placeholder="DYN-XXXXXXXX"
                  value={redeemCode}
                  onChange={(e) => setRedeemCode(e.target.value.toUpperCase())}
                  style={{ fontFamily: 'monospace', fontSize: '1.15rem', letterSpacing: '0.1em', textAlign: 'center' }}
                />
              </div>
              <button type="submit" className="btn btn-primary" style={{ marginTop: 12, width: '100%' }} disabled={loading}>
                {loading ? 'Connecting...' : 'Connect to Internet'}
              </button>
            </form>
          </div>
        )}

        <p style={{ textAlign: 'center', marginTop: 24, fontSize: 12, color: 'var(--text-muted)' }}>
          Powered by Dynamite Networks Billing
        </p>
      </div>
    </div>
  );
}
