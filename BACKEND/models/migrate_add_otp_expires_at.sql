-- Run this if your database already exists and is missing the OTP expiry column
ALTER TABLE users ADD COLUMN IF NOT EXISTS otp_expires_at TIMESTAMP NULL;
CREATE INDEX IF NOT EXISTS idx_otp_expires_at ON users(otp_expires_at);
