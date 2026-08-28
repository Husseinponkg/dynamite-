-- Create and use the database
CREATE DATABASE dynamite;

-- Connect to the database
\c dynamite;

-- Users table (customers)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL, -- Store hashed passwords
    otp VARCHAR(10),
    otp_expires_at TIMESTAMP NULL,
    phone VARCHAR(20),
    full_name VARCHAR(150),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'verified', 'active', 'inactive', 'suspended'))
);

-- Create indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- Admin table
CREATE TABLE admin (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL, -- Store hashed passwords
    full_name VARCHAR(150),
    role VARCHAR(20) DEFAULT 'admin' CHECK (role IN ('super_admin', 'admin', 'support')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive'))
);

-- Package/Plan table
CREATE TABLE package (
    id SERIAL PRIMARY KEY,
    package_name VARCHAR(100) NOT NULL,
    package_desc TEXT,
    price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    validity_days INT NOT NULL, -- e.g., 7, 15, 30 days
    validity_hours INT DEFAULT 0, -- For hourly packages
    bandwidth_up INT DEFAULT 0, -- Upload speed in Kbps
    bandwidth_down INT DEFAULT 0, -- Download speed in Kbps
    data_limit INT DEFAULT 0, -- Data limit in MB (0 = unlimited)
    concurrent_logins INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive'))
);

-- Create indexes
CREATE INDEX idx_package_name ON package(package_name);
CREATE INDEX idx_package_price ON package(price);

-- Routers table
CREATE TABLE routers (
    id SERIAL PRIMARY KEY,
    router_name VARCHAR(100) NOT NULL,
    router_ip VARCHAR(45) NOT NULL, -- Supports IPv4 and IPv6
    router_port INT DEFAULT 8728, -- API port (8728 for old API, 443 for REST API)
    username VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    api_type VARCHAR(20) DEFAULT 'mikrotik' CHECK (api_type IN ('mikrotik', 'rest_api')),
    location VARCHAR(100),
    max_users INT DEFAULT 500,
    status VARCHAR(20) DEFAULT 'online' CHECK (status IN ('online', 'offline', 'maintenance')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_checked TIMESTAMP NULL
);

-- Create indexes
CREATE INDEX idx_routers_name ON routers(router_name);
CREATE INDEX idx_routers_status ON routers(status);

-- Vouchers table
CREATE TABLE vouchers (
    id SERIAL PRIMARY KEY,
    voucher_code VARCHAR(50) UNIQUE NOT NULL, -- Use VARCHAR for flexible codes
    package_id INT NOT NULL,
    router_id INT NOT NULL,
    created_by INT, -- Admin ID who created the voucher
    used_by INT NULL, -- User ID who redeemed it
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'used', 'expired', 'cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expire_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP NULL,
    FOREIGN KEY (package_id) REFERENCES package(id) ON DELETE CASCADE,
    FOREIGN KEY (router_id) REFERENCES routers(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES admin(id) ON DELETE SET NULL,
    FOREIGN KEY (used_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Create indexes
CREATE INDEX idx_vouchers_code ON vouchers(voucher_code);
CREATE INDEX idx_vouchers_status ON vouchers(status);
CREATE INDEX idx_vouchers_expire_at ON vouchers(expire_at);

-- Payments table
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    package_id INT NOT NULL,
    router_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(20) NOT NULL CHECK (payment_method IN ('airtel', 'vodacom', 'tigo', 'tigopesa', 'halotel', 'yas', 'cash', 'bank_transfer')),
    transaction_id VARCHAR(100) UNIQUE,
    phone_number VARCHAR(20),
    reference_number VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    expiry_date TIMESTAMP NULL, -- When the service expires
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (package_id) REFERENCES package(id) ON DELETE CASCADE,
    FOREIGN KEY (router_id) REFERENCES routers(id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_transaction_id ON payments(transaction_id);
CREATE INDEX idx_payments_created_at ON payments(created_at);

-- Active Sessions table (to track connected users)
CREATE TABLE active_sessions (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    router_id INT NOT NULL,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(45),
    mac_address VARCHAR(17),
    bandwidth_up_used BIGINT DEFAULT 0, -- In bytes
    bandwidth_down_used BIGINT DEFAULT 0, -- In bytes
    total_usage BIGINT DEFAULT 0, -- Total bytes used
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'terminated')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (router_id) REFERENCES routers(id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX idx_sessions_session_id ON active_sessions(session_id);
CREATE INDEX idx_sessions_user_id ON active_sessions(user_id);
CREATE INDEX idx_sessions_status ON active_sessions(status);

-- System logs table
CREATE TABLE system_logs (
    id SERIAL PRIMARY KEY,
    admin_id INT NULL,
    user_id INT NULL,
    action VARCHAR(100) NOT NULL,
    description TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES admin(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Create indexes
CREATE INDEX idx_logs_action ON system_logs(action);
CREATE INDEX idx_logs_created_at ON system_logs(created_at);

-- Router credentials history (for audit)
CREATE TABLE router_credentials_history (
    id SERIAL PRIMARY KEY,
    router_id INT NOT NULL,
    old_username VARCHAR(100),
    new_username VARCHAR(100),
    old_password VARCHAR(255),
    new_password VARCHAR(255),
    changed_by INT, -- Admin ID
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (router_id) REFERENCES routers(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES admin(id) ON DELETE SET NULL
);

-- Package assignment history
CREATE TABLE package_history (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    package_id INT NOT NULL,
    router_id INT NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    deactivated_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (package_id) REFERENCES package(id) ON DELETE CASCADE,
    FOREIGN KEY (router_id) REFERENCES routers(id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX idx_package_history_user_id ON package_history(user_id);
CREATE INDEX idx_package_history_expires_at ON package_history(expires_at);

-- ============================================
-- 🚀 HELPER FUNCTIONS AND TRIGGERS
-- ============================================

-- Function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for users table
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for payments table
CREATE TRIGGER update_payments_updated_at 
    BEFORE UPDATE ON payments 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for active_sessions table
CREATE TRIGGER update_sessions_last_update 
    BEFORE UPDATE ON active_sessions 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 💡 SAMPLE INSERT DATA
-- ============================================





-- ============================================
-- 🔍 USEFUL QUERIES
-- ============================================

-- Get active users with their current package
SELECT 
    u.id,
    u.username,
    u.full_name,
    u.email,
    u.phone,
    p.package_name,
    p.price,
    ph.expires_at,
    CASE 
        WHEN ph.expires_at > CURRENT_TIMESTAMP THEN 'Active'
        ELSE 'Expired'
    END as subscription_status
FROM users u
LEFT JOIN package_history ph ON u.id = ph.user_id AND ph.deactivated_at IS NULL
LEFT JOIN package p ON ph.package_id = p.id
WHERE u.status = 'active';

-- Get router status and connection info
SELECT 
    r.id,
    r.router_name,
    r.router_ip,
    r.status,
    COUNT(as_sessions.id) as active_connections,
    r.max_users,
    ROUND(COUNT(as_sessions.id)::decimal / r.max_users * 100, 2) as utilization_percentage
FROM routers r
LEFT JOIN active_sessions as_sessions ON r.id = as_sessions.router_id AND as_sessions.status = 'active'
GROUP BY r.id, r.router_name, r.router_ip, r.status, r.max_users;

-- Voucher redemption report
SELECT 
    v.voucher_code,
    p.package_name,
    v.created_at,
    v.used_at,
    u.username as used_by_user,
    a.username as created_by_admin,
    v.status
FROM vouchers v
LEFT JOIN package p ON v.package_id = p.id
LEFT JOIN users u ON v.used_by = u.id
LEFT JOIN admin a ON v.created_by = a.id
ORDER BY v.created_at DESC;

-- Payment summary by method
SELECT 
    payment_method,
    COUNT(*) as total_payments,
    SUM(amount) as total_amount,
    AVG(amount) as average_amount,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_payments
FROM payments
GROUP BY payment_method
ORDER BY total_amount DESC;

-- User session usage summary
SELECT 
    u.id,
    u.username,
    u.full_name,
    COUNT(as_sessions.id) as total_sessions,
    COALESCE(SUM(as_sessions.total_usage), 0) as total_usage_bytes,
    COALESCE(SUM(as_sessions.total_usage) / 1024 / 1024, 0) as total_usage_mb,
    MAX(as_sessions.start_time) as last_session_start
FROM users u
LEFT JOIN active_sessions as_sessions ON u.id = as_sessions.user_id
GROUP BY u.id, u.username, u.full_name
HAVING COUNT(as_sessions.id) > 0
ORDER BY total_usage_bytes DESC;