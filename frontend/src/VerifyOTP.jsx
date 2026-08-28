import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import API from './config';

export default function VerifyOTP() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);

  const startCooldown = (seconds = 30) => {
    setResendCooldown(seconds);
    const interval = setInterval(() => {
      setResendCooldown((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const handleResend = async () => {
    if (!email || resendCooldown > 0) return;
    setResendLoading(true);
    setMessage('');
    try {
      const res = await fetch(`${API}/auth/resend-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      const data = await res.json();
      if (res.ok) {
        setMessage(data.message || 'New OTP sent!');
        startCooldown();
      } else {
        setMessage(data.message || data.detail || 'Failed to resend OTP');
      }
    } catch {
      setMessage('Could not connect to server.');
    } finally {
      setResendLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    try {
      const res = await fetch(`${API}/auth/verify-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, otp }),
      });
      const data = await res.json();
      if (res.ok) {
        setMessage(data.message || 'Verified!');
        setTimeout(() => navigate('/'), 1000);
      } else {
        setMessage(data.message || data.detail || 'Invalid OTP');
      }
    } catch {
      setMessage('Could not connect to server.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="brand">
          <div className="logo">DN</div>
          <h1>Verify OTP</h1>
          <p className="subtitle">Enter the code sent to your email</p>
        </div>
        {message && (
          <div className={`alert ${message.includes('Verified') ? 'alert-success' : 'alert-error'}`}>{message}</div>
        )}
        <form onSubmit={handleSubmit}>
          <div className="form-group"><label>Email</label><input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></div>
          <div className="form-group"><label>OTP Code</label><input value={otp} onChange={(e) => setOtp(e.target.value)} required placeholder="6-digit code" /></div>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Verifying...' : 'Verify'}
          </button>
          <button type="button" className="btn btn-secondary" onClick={handleResend} disabled={resendLoading || resendCooldown > 0 || !email} style={{ marginTop: 10 }}>
            {resendLoading ? 'Sending...' : resendCooldown > 0 ? `Resend OTP (${resendCooldown}s)` : 'Resend OTP'}
          </button>
        </form>
        <div className="auth-footer"><p><Link to="/">Back to Login</Link></p></div>
      </div>
    </div>
  );
}
