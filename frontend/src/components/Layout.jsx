import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

const navItems = [
  {
    section: 'Overview',
    items: [
      { path: '/home', label: 'Dashboard', icon: '📊' },
      { path: '/income', label: 'Income', icon: '💰' },
    ],
  },
  {
    section: 'Network',
    items: [
      { path: '/routers', label: 'Routers', icon: '📡' },
      { path: '/sessions', label: 'Sessions', icon: '🔗' },
      { path: '/branches', label: 'Branches', icon: '🏢' },
    ],
  },
  {
    section: 'Billing',
    items: [
      { path: '/packages', label: 'Packages', icon: '📦' },
      { path: '/vouchers', label: 'Vouchers', icon: '🎟️' },
      { path: '/payments', label: 'Payments', icon: '💳' },
      { path: '/captive-portal', label: 'Captive Portal', icon: '📶' },
      { path: '/withdraws', label: 'Withdraws', icon: '🏦' },
    ],
  },
  {
    section: 'System',
    items: [
      { path: '/admin', label: 'Admin', icon: '👤' },
      { path: '/settings', label: 'Settings', icon: '⚙️' },
    ],
  },
];

export default function Layout({ title, children }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  const logout = () => {
    localStorage.removeItem('token');
    navigate('/');
  };

  return (
    <div className="app-layout">
      <aside className={`sidebar ${open ? 'open' : ''}`}>
        <div className="sidebar-brand">
          <div className="logo-icon">DN</div>
          <div>
            <h1>Dynamite</h1>
            <span>Networks Billing</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((sec) => (
            <div key={sec.section} className="nav-section">
              <div className="nav-section-title">{sec.section}</div>
              {sec.items.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
                  onClick={() => setOpen(false)}
                >
                  <span className="icon">{item.icon}</span>
                  {item.label}
                </Link>
              ))}
            </div>
          ))}
        </nav>

        <div className="sidebar-footer">
          <button className="nav-link" onClick={logout} style={{ color: 'var(--danger)' }}>
            <span className="icon">🚪</span> Logout
          </button>
        </div>
      </aside>

      <div className="main-content">
        <header className="topbar">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <button className="menu-toggle" onClick={() => setOpen(!open)}>☰</button>
            <h2>{title}</h2>
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Admin Panel</div>
        </header>
        <div className="page-body">{children}</div>
      </div>
    </div>
  );
}
