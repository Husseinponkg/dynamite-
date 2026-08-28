import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';

import API from '../config';

export default function Home() {
  const [stats, setStats] = useState({
    packages: 0,
    routers: 0,
    vouchers: { active: 0, used: 0, total: 0 },
    sessions: 0,
    income_today: 0,
    balance: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [pkgRes, rtrRes, vchRes, sesRes, incRes] = await Promise.all([
          fetch(`${API}/packages`).catch(() => null),
          fetch(`${API}/routing`).catch(() => null),
          fetch(`${API}/vouchers/stats`).catch(() => null),
          fetch(`${API}/sessions/stats`).catch(() => null),
          fetch(`${API}/income/summary`).catch(() => null),
        ]);

        let packages = 0;
        if (pkgRes?.ok) {
          const d = await pkgRes.json();
          packages = Array.isArray(d) ? d.length : d.packages?.length || 0;
        }
        let routers = 0;
        if (rtrRes?.ok) {
          const d = await rtrRes.json();
          routers = Array.isArray(d) ? d.length : d.routers?.length || 0;
        }
        let vouchers = { active: 0, used: 0, total: 0 };
        if (vchRes?.ok) {
          const d = await vchRes.json();
          vouchers = d.stats || vouchers;
        }
        let sessions = 0;
        if (sesRes?.ok) {
          const d = await sesRes.json();
          sessions = d.stats?.active_now || 0;
        }
        let income_today = 0, balance = 0;
        if (incRes?.ok) {
          const d = await incRes.json();
          income_today = d.income?.today || 0;
          balance = d.income?.available_balance || 0;
        }
        setStats({ packages, routers, vouchers, sessions, income_today, balance });
      } catch (_) {}
      finally { setLoading(false); }
    };
    load();
  }, []);

  const fmt = (n) => `TZS ${Number(n || 0).toLocaleString()}`;

  return (
    <Layout title="Dashboard">
      {loading ? (
        <div className="loading"><div className="spinner" /> Loading dashboard...</div>
      ) : (
        <>
          <div className="stats-grid">
            <div className="stat-card"><div className="label">Today's Income</div><div className="value">{fmt(stats.income_today)}</div></div>
            <div className="stat-card"><div className="label">Available Balance</div><div className="value">{fmt(stats.balance)}</div></div>
            <div className="stat-card"><div className="label">Active Sessions</div><div className="value">{stats.sessions}</div></div>
            <div className="stat-card"><div className="label">Active Vouchers</div><div className="value">{stats.vouchers.active}</div></div>
            <div className="stat-card"><div className="label">Packages</div><div className="value">{stats.packages}</div></div>
            <div className="stat-card"><div className="label">Routers</div><div className="value">{stats.routers}</div></div>
          </div>

          <div className="card">
            <div className="card-header"><h3>Quick Actions</h3></div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
              <a href="#/captive-portal" className="btn btn-primary">📶 Captive Portal</a>
              <a href="#/vouchers" className="btn btn-secondary">🎟️ Generate Vouchers</a>
              <a href="#/packages" className="btn btn-secondary">📦 Packages</a>
              <a href="#/income" className="btn btn-secondary">💰 Income</a>
              <a href="#/withdraws" className="btn btn-secondary">🏦 Withdraw</a>
              <a href="#/sessions" className="btn btn-secondary">🔗 Sessions</a>
              <a href="#/admin" className="btn btn-secondary">👤 Admin</a>
            </div>
          </div>

          <div className="card">
            <div className="card-header"><h3>System Overview</h3></div>
            <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7 }}>
              Full ISP hotspot billing: captive portal for WiFi users, mobile money payments,
              voucher generation &amp; redeem, session tracking, income reports, and owner withdraws.
            </p>
          </div>
        </>
      )}
    </Layout>
  );
}
