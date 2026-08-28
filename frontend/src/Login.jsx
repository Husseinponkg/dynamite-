import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import API from './config';

export default function Login() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setFormData({ ...formData, [e.target.id]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    try {
      const response = await fetch(`${API}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      const result = await response.json();
      if (response.ok && result.success) {
        localStorage.setItem('token', result.access_token);
        setMessage('Login successful! Redirecting...');
        setTimeout(() => navigate('/home'), 800);
      } else {
        setMessage(result.message || 'Invalid email or password.');
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
          <h1>Dynamite Networks</h1>
          <p className="subtitle">Sign in to your billing panel</p>
        </div>
        {message && (
          <div className={`alert ${message.includes('successful') ? 'alert-success' : 'alert-error'}`}>
            {message}
          </div>
        )}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input type="email" id="email" placeholder="admin@dynamite.tz" onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input type="password" id="password" placeholder="••••••••" onChange={handleChange} required />
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        <div className="auth-footer">
          <p>New user? <Link to="/register">Register</Link></p>
          <p style={{ marginTop: 6 }}>Need OTP? <Link to="/verify-otp">Verify OTP</Link></p>
        </div>
      </div>
    </div>
  );
}
