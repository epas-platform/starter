-- Cradle Database Initialization
-- This script runs on first container startup

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    roles JSONB DEFAULT '["user"]'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, email)
);

CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_users_email ON users(email);

-- Audit logs table (immutable)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    actor_id UUID NOT NULL,
    actor_type VARCHAR(50) DEFAULT 'user',
    actor_ip VARCHAR(45),
    action VARCHAR(50) NOT NULL,
    action_detail TEXT,
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(255) NOT NULL,
    tenant_id UUID NOT NULL,
    request_id UUID NOT NULL,
    session_id UUID,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    old_values JSONB,
    new_values JSONB,
    data_classification VARCHAR(20) DEFAULT 'internal'
);

CREATE INDEX idx_audit_tenant_timestamp ON audit_logs(tenant_id, timestamp DESC);
CREATE INDEX idx_audit_actor ON audit_logs(actor_id);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_request ON audit_logs(request_id);

-- Prevent modification of audit logs (production hardening)
CREATE OR REPLACE FUNCTION prevent_audit_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Audit logs cannot be modified or deleted';
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger (comment out for development if needed)
-- CREATE TRIGGER audit_immutable
--     BEFORE UPDATE OR DELETE ON audit_logs
--     FOR EACH ROW
--     EXECUTE FUNCTION prevent_audit_modification();

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Seed development user (password: 'password')
-- bcrypt hash for 'password' with cost factor 12
INSERT INTO users (email, hashed_password, full_name, roles, is_verified)
VALUES (
    'admin@example.com',
    '$2b$12$jELtAOecFSVZP1CI.L0mC.7AYV.WK3KuTpdMfNg39IdBmRWsn.i06',
    'Admin User',
    '["admin", "user"]'::jsonb,
    TRUE
);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO cradle;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO cradle;
