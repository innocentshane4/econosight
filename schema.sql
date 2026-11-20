-- =============================================================================
-- EconoSight — Database Schema
-- Run this in Supabase → SQL Editor
-- =============================================================================

-- Economic indicators
CREATE TABLE IF NOT EXISTS indicators (
    id              BIGSERIAL PRIMARY KEY,
    country_code    TEXT NOT NULL,
    country_name    TEXT NOT NULL,
    indicator_code  TEXT NOT NULL,
    indicator_name  TEXT NOT NULL,
    year            INTEGER NOT NULL,
    value           FLOAT,
    fetched_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(country_code, indicator_code, year)
);

-- Currency rates
CREATE TABLE IF NOT EXISTS currency_rates (
    id          BIGSERIAL PRIMARY KEY,
    base        TEXT NOT NULL,
    target      TEXT NOT NULL,
    rate        FLOAT NOT NULL,
    fetched_at  TIMESTAMPTZ DEFAULT NOW()
);

-- User profiles (extends auth.users)
CREATE TABLE IF NOT EXISTS profiles (
    id          UUID REFERENCES auth.users PRIMARY KEY,
    username    TEXT UNIQUE,
    full_name   TEXT,
    plan        TEXT DEFAULT 'free',
    api_key     TEXT UNIQUE,
    api_calls   INTEGER DEFAULT 0,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Saved indicators
CREATE TABLE IF NOT EXISTS saved_indicators (
    id              BIGSERIAL PRIMARY KEY,
    user_id         UUID REFERENCES profiles(id),
    indicator_code  TEXT NOT NULL,
    country_code    TEXT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, indicator_code, country_code)
);

-- API usage log
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
ALTER TABLE indicators       ENABLE ROW LEVEL SECURITY;
ALTER TABLE currency_rates   ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users read own profile"
    ON profiles FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users update own profile"
    ON profiles FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users manage own saved indicators"
    ON saved_indicators FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Public read indicators"
    ON indicators FOR SELECT USING (true);

CREATE POLICY "Public read currency"
    ON currency_rates FOR SELECT USING (true);

-- Service role insert for pipeline
CREATE POLICY "Service insert indicators"
    ON indicators FOR INSERT WITH CHECK (true);

CREATE POLICY "Service insert currency"
    ON currency_rates FOR INSERT WITH CHECK (true);

CREATE POLICY "Service insert profiles"
    ON profiles FOR INSERT WITH CHECK (true);

CREATE POLICY "Service insert api log"
    ON api_usage_log FOR INSERT WITH CHECK (true);
