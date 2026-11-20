# =============================================================================
# EconoSight — Database Client (Supabase)
# =============================================================================

import httpx
from config import SUPABASE_URL, SUPABASE_SECRET_KEY


HEADERS = {
    "apikey":        SUPABASE_SECRET_KEY,
    "Authorization": f"Bearer {SUPABASE_SECRET_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=representation"
}


def supabase_get(table: str, params: dict = None):
    """Read rows from a Supabase table."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    r = httpx.get(url, headers=HEADERS, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def supabase_post(table: str, data):
    """Insert one or many rows into a Supabase table."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    r = httpx.post(url, headers=HEADERS, json=data, timeout=15)
    r.raise_for_status()
    return r.json()


def supabase_upsert(table: str, data, on_conflict: str = ""):
    """Upsert rows into a Supabase table."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {**HEADERS, "Prefer": f"resolution=merge-duplicates,return=representation"}
    params = {}
    if on_conflict:
        params["on_conflict"] = on_conflict
    r = httpx.post(url, headers=headers, json=data, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def supabase_delete(table: str, params: dict):
    """Delete rows from a Supabase table."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    r = httpx.delete(url, headers=HEADERS, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


# =============================================================================
# SQL Schema — run once to set up tables in Supabase
# Go to Supabase → SQL Editor and paste the contents of schema.sql
# =============================================================================

SCHEMA_SQL = """
-- Economic indicators table
CREATE TABLE IF NOT EXISTS indicators (
    id          BIGSERIAL PRIMARY KEY,
    country_code TEXT NOT NULL,
    country_name TEXT NOT NULL,
    indicator_code TEXT NOT NULL,
    indicator_name TEXT NOT NULL,
    year        INTEGER NOT NULL,
    value       FLOAT,
    fetched_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(country_code, indicator_code, year)
);

-- Currency rates table
CREATE TABLE IF NOT EXISTS currency_rates (
    id          BIGSERIAL PRIMARY KEY,
    base        TEXT NOT NULL,
    target      TEXT NOT NULL,
    rate        FLOAT NOT NULL,
    fetched_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS profiles (
    id          UUID REFERENCES auth.users PRIMARY KEY,
    username    TEXT UNIQUE,
    full_name   TEXT,
    plan        TEXT DEFAULT 'free',
    api_key     TEXT UNIQUE,
    api_calls   INTEGER DEFAULT 0,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Saved indicators per user
CREATE TABLE IF NOT EXISTS saved_indicators (
    id              BIGSERIAL PRIMARY KEY,
    user_id         UUID REFERENCES profiles(id),
    indicator_code  TEXT NOT NULL,
    country_code    TEXT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, indicator_code, country_code)
);

-- API key usage log
CREATE TABLE IF NOT EXISTS api_usage_log (
    id          BIGSERIAL PRIMARY KEY,
    api_key     TEXT,
    endpoint    TEXT,
    ip_address  TEXT,
    called_at   TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE profiles         ENABLE ROW LEVEL SECURITY;
ALTER TABLE saved_indicators ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can read own profile"
    ON profiles FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON profiles FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can manage own saved indicators"
    ON saved_indicators FOR ALL USING (auth.uid() = user_id);

-- Public read on indicators and currency_rates
CREATE POLICY "Public read indicators"
    ON indicators FOR SELECT USING (true);

CREATE POLICY "Public read currency rates"
    ON currency_rates FOR SELECT USING (true);
"""
