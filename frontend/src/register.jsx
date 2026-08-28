import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import API from './config';

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: '', email: '', password: '', phone: '', full_name: '', address: '',
  });
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    try {
      const res = await fetch(`${API}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (res.ok) {
        setMessage(data.message || 'Registered! Check email for OTP.');
        setTimeout(() => navigate('/verify-otp'), 1200);
      } else {
        setMessage(data.message || data.detail || 'Registration failed');
      }
    } catch {
      setMessage('Could not connect to server.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card" style={{ maxWidth: 480 }}>
        <div className="brand">
          <div className="logo">DN</div>
          <h1>Create Account</h1>
          <p className="subtitle">Join Dynamite Networks</p>
        </div>
        {message && (
          <div className={`alert ${message.includes('Registered') || message.includes('OTP') ? 'alert-success' : 'alert-error'}`}>
            {message}
          </div>
        )}
        <form onSubmit={handleSubmit}>
          <div className="form-group"><label>Full Name</label><input name="full_name" required onChange={handleChange} /></div>
          <div className="form-group"><label>Username</label><input name="username" required onChange={handleChange} /></div>
          <div className="form-group"><label>Email</label><input name="email" type="email" required onChange={handleChange} /></div>
          <div className="form-group"><label>Phone</label><input name="phone" required onChange={handleChange} /></div>
          <div className="form-group"><label>Address</label><input name="address" onChange={handleChange} /></div>
          <div className="form-group"><label>Password</label><input name="password" type="password" required onChange={handleChange} /></div>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Creating...' : 'Register'}
          </button>
        </form>
        <div className="auth-footer">
          <p>Already have an account? <Link to="/">Sign In</Link></p>
        </div>
      </div>
    </div>
  );
}
