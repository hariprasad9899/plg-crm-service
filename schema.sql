CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TYPE tenant_type_enum AS ENUM (
    'personal',
    'organization'
);

CREATE TYPE subscription_plan_enum AS ENUM (
    'free',
    'starter',
    'pro',
    'enterprise'
);

CREATE TYPE membership_role_enum AS ENUM (
    'owner',
    'admin',
    'member'
);

CREATE TYPE auth_provider_enum AS ENUM (
    'password',
    'google',
    'microsoft'
);

CREATE TYPE user_status_enum AS ENUM (
    'active',
    'invited',
    'suspended',
    'deleted'
);

CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL CHECK (slug ~ '^[a-z0-9-]+$'),
    tenant_type tenant_type_enum NOT NULL DEFAULT 'personal',
    claimed_domain VARCHAR(255),
    is_domain_verified BOOLEAN NOT NULL DEFAULT FALSE,
    subscription_plan subscription_plan_enum NOT NULL DEFAULT 'free',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    settings JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE UNIQUE INDEX idx_tenant_slug ON tenants(slug);
CREATE INDEX idx_tenants_domain ON tenants(claimed_domain);
CREATE UNIQUE INDEX idx_unique_claimed_domain ON tenants(LOWER(claimed_domain)) WHERE claimed_domain IS NOT NULL;

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(255),
    primary_email VARCHAR(320) NOT NULL,
    avatar_url TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    last_login_at TIMESTAMPTZ,
    status user_status_enum NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE UNIQUE INDEX idx_user_email ON users(LOWER(primary_email));

CREATE TABLE auth_identities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider auth_provider_enum NOT NULL,
    provider_user_id TEXT,
    provider_email TEXT NOT NULL,
    password_hash TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK ((provider = 'password' AND password_hash IS NOT NULL) OR (provider != 'password'))
);

CREATE INDEX idx_auth_user ON auth_identities(user_id);
CREATE UNIQUE INDEX idx_provider_identity ON auth_identities(provider, provider_user_id) 
WHERE provider_user_id IS NOT NULL;
CREATE UNIQUE INDEX idx_password_email ON auth_identities(LOWER(provider_email))
WHERE provider = 'password';

CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id)ON DELETE CASCADE,
    token_hash TEXT NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_refresh_user ON refresh_tokens(user_id);

CREATE TABLE tenant_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role membership_role_enum NOT NULL DEFAULT 'member',
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    invited_by UUID REFERENCES users(id),
    UNIQUE(tenant_id, user_id)
);

CREATE INDEX idx_membership_user ON tenant_memberships(user_id);
CREATE INDEX idx_membership_tenant ON tenant_memberships(tenant_id);
CREATE INDEX idx_membership_role ON tenant_memberships(role);

CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_workspace_tenant ON workspaces(tenant_id);

CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    refresh_token_hash TEXT NOT NULL,
    ip_address INET,
    user_agent TEXT,
    device_name TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sessions_user ON sessions(user_id);
CREATE INDEX idx_sessions_tenant ON sessions(tenant_id);
CREATE INDEX idx_sessions_revoked ON sessions(revoked_at);