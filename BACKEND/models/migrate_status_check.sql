-- Run this if your database already exists and is missing 'verified' in the status check constraint
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_status_check;
ALTER TABLE users ADD CONSTRAINT users_status_check CHECK (status IN ('active', 'inactive', 'verified'));
