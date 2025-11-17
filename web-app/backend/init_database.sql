-- Voss Taxi Database Initialization Script for Supabase
-- Run this in Supabase SQL Editor to create all required tables

-- Enable UUID extension (optional, for future use)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables (if you want to start fresh)
-- Uncomment these lines if you need to reset the database
-- DROP TABLE IF EXISTS shift_edits CASCADE;
-- DROP TABLE IF EXISTS salary_reports CASCADE;
-- DROP TABLE IF EXISTS shift_reports CASCADE;
-- DROP TABLE IF EXISTS templates CASCADE;
-- DROP TABLE IF EXISTS drivers CASCADE;
-- DROP TABLE IF EXISTS bank_accounts CASCADE;
-- DROP TABLE IF EXISTS companies CASCADE;
-- DROP TABLE IF EXISTS users CASCADE;

-- Users table (for authentication)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR NOT NULL UNIQUE,
    username VARCHAR NOT NULL UNIQUE,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR,
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Companies table
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    org_number VARCHAR,
    address VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bank Accounts table
CREATE TABLE IF NOT EXISTS bank_accounts (
    id SERIAL PRIMARY KEY,
    account_number VARCHAR NOT NULL,
    account_name VARCHAR,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Drivers table
CREATE TABLE IF NOT EXISTS drivers (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    driver_id VARCHAR(4) NOT NULL,
    commission_percentage FLOAT DEFAULT 45.0,
    bank_account_id INTEGER REFERENCES bank_accounts(id),
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_drivers_driver_id ON drivers(driver_id);

-- Templates table
CREATE TABLE IF NOT EXISTS templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    template_type VARCHAR NOT NULL,
    columns JSONB NOT NULL,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Shift Reports table
CREATE TABLE IF NOT EXISTS shift_reports (
    id SERIAL PRIMARY KEY,
    driver_id INTEGER REFERENCES drivers(id),
    file_name VARCHAR NOT NULL,
    report_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data JSONB NOT NULL,
    summary JSONB,
    pdf_path VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_shift_reports_driver ON shift_reports(driver_id);
CREATE INDEX IF NOT EXISTS idx_shift_reports_date ON shift_reports(report_date);

-- Shift Edits table
CREATE TABLE IF NOT EXISTS shift_edits (
    id SERIAL PRIMARY KEY,
    shift_report_id INTEGER REFERENCES shift_reports(id) ON DELETE CASCADE,
    row_index INTEGER NOT NULL,
    column_name VARCHAR NOT NULL,
    old_value VARCHAR,
    new_value VARCHAR NOT NULL,
    note TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_shift_edits_report ON shift_edits(shift_report_id);

-- Salary Reports table
CREATE TABLE IF NOT EXISTS salary_reports (
    id SERIAL PRIMARY KEY,
    driver_id INTEGER REFERENCES drivers(id) NOT NULL,
    report_period VARCHAR,
    file_names JSONB,
    gross_salary FLOAT,
    commission_percentage FLOAT,
    net_salary FLOAT,
    cash_amount FLOAT,
    tips FLOAT,
    data JSONB NOT NULL,
    pdf_path VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_salary_reports_driver ON salary_reports(driver_id);
CREATE INDEX IF NOT EXISTS idx_salary_reports_period ON salary_reports(report_period);

-- Create a function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_companies_updated_at ON companies;
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_bank_accounts_updated_at ON bank_accounts;
CREATE TRIGGER update_bank_accounts_updated_at BEFORE UPDATE ON bank_accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_drivers_updated_at ON drivers;
CREATE TRIGGER update_drivers_updated_at BEFORE UPDATE ON drivers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_templates_updated_at ON templates;
CREATE TRIGGER update_templates_updated_at BEFORE UPDATE ON templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_shift_reports_updated_at ON shift_reports;
CREATE TRIGGER update_shift_reports_updated_at BEFORE UPDATE ON shift_reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_salary_reports_updated_at ON salary_reports;
CREATE TRIGGER update_salary_reports_updated_at BEFORE UPDATE ON salary_reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default company (optional)
INSERT INTO companies (name, org_number, address)
VALUES ('Voss Taxi', '123456789', 'Voss, Norway')
ON CONFLICT DO NOTHING;

-- Verification queries
SELECT 'Database initialized successfully!' as status;
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
