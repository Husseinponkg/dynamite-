-- Extra tables for modern billing: withdraws, wallet balance tracking
-- Run: psql -d dynamite -f models/migrate_add_billing_tables.sql

CREATE TABLE IF NOT EXISTS withdraws (
    id SERIAL PRIMARY KEY,
    admin_id INT,
    amount DECIMAL(12, 2) NOT NULL CHECK (amount > 0),
    method VARCHAR(30) NOT NULL DEFAULT 'mpesa'
        CHECK (method IN ('mpesa', 'airtel', 'tigo', 'halotel', 'bank_transfer', 'cash')),
    account_number VARCHAR(50) NOT NULL,
    account_name VARCHAR(150),
    status VARCHAR(20) DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'completed', 'rejected', 'cancelled')),
    notes TEXT,
    processed_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (admin_id) REFERENCES admin(id) ON DELETE SET NULL,
    FOREIGN KEY (processed_by) REFERENCES admin(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_withdraws_status ON withdraws(status);
CREATE INDEX IF NOT EXISTS idx_withdraws_created ON withdraws(created_at);

-- Wallet / ledger summary view helper: completed payments minus completed withdraws
-- (computed in API, not a physical table)

-- Branches table
CREATE TABLE IF NOT EXISTS branches (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(200),
    manager_name VARCHAR(150),
    phone VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Link routers to branches (optional column if not exists)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'routers' AND column_name = 'branch_id'
    ) THEN
        ALTER TABLE routers ADD COLUMN branch_id INT REFERENCES branches(id) ON DELETE SET NULL;
    END IF;
END $$;

-- Allow captive portal payments without registered user
ALTER TABLE payments ALTER COLUMN user_id DROP NOT NULL;
ALTER TABLE payments ALTER COLUMN package_id DROP NOT NULL;
ALTER TABLE payments ALTER COLUMN router_id DROP NOT NULL;
