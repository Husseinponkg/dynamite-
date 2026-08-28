import React from 'react';
import { HashRouter, Routes, Route } from 'react-router-dom';
import ErrorBoundary from './ErrorBoundary.jsx';
import Register from './register.jsx';
import Login from './Login.jsx';
import VerifyOTP from './VerifyOTP.jsx';
import Home from './pages/Home.jsx';
import Router from './pages/routers.jsx';
import Packages from './pages/packages.jsx';
import Vouchers from './pages/vouchers.jsx';
import CaptivePortal from './pages/captive-portal.jsx';
import Sessions from './pages/sessions.jsx';
import Income from './pages/income.jsx';
import Payments from './pages/payments.jsx';
import Settings from './pages/settings.jsx';
import Withdraws from './pages/withdraws.jsx';
import Branches from './pages/branches.jsx';
import AdminPage from './pages/admin.jsx';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/verify-otp" element={<VerifyOTP />} />
      <Route path="/home" element={<Home />} />
      <Route path="/routers" element={<Router />} />
      <Route path="/packages" element={<Packages />} />
      <Route path="/vouchers" element={<Vouchers />} />
      <Route path="/captive-portal" element={<CaptivePortal />} />
      <Route path="/sessions" element={<Sessions />} />
      <Route path="/income" element={<Income />} />
      <Route path="/payments" element={<Payments />} />
      <Route path="/settings" element={<Settings />} />
      <Route path="/withdraws" element={<Withdraws />} />
      <Route path="/branches" element={<Branches />} />
      <Route path="/admin" element={<AdminPage />} />
    </Routes>
  );
}

function Root() {
  return (
    <ErrorBoundary>
      <HashRouter>
        <App />
      </HashRouter>
    </ErrorBoundary>
  );
}

export default Root;
