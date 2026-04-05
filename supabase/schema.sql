-- =============================================================================
-- NBA Draft Tracker — Supabase Schema
-- =============================================================================
-- Run this entire file in the Supabase SQL Editor (supabase.com → your project
-- → SQL Editor → New Query → paste → Run).
--
-- This replaces:
--   1. backend/data/rosters.json      → participants + rosters tables
--   2. backend/cache.py TTLCache      → standings_cache table
--   3. backend/data/historical/*.json → season_records table (see note below)
--
-- NOTE on historical data:
-- The original design assumed per-team stats existed for every past season.
-- In reality, we only have the *aggregate* W-L per participant per season
-- (i.e. the combined record of their 5 drafted teams). The season_records
-- table stores exactly that — one row per person per season.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- 1. PARTICIPANTS
-- Stores the names of everyone in the draft (e.g. "John", "Nate").
-- This was previously just the keys of rosters.json.
-- -----------------------------------------------------------------------------
CREATE TABLE participants (
    id   SERIAL PRIMARY KEY,     -- auto-incrementing integer, Postgres handles this
    name TEXT   NOT NULL UNIQUE  -- UNIQUE prevents duplicate names
);


-- -----------------------------------------------------------------------------
-- 2. ROSTERS  (current season only)
-- Maps each participant to the NBA team IDs they drafted THIS season.
-- We only track individual team assignments for the current season because
-- we don't have that breakdown for prior seasons.
--
-- REFERENCES creates a foreign key — Postgres will reject a roster row if the
-- participant_id doesn't exist in the participants table.
-- ON DELETE CASCADE means if a participant is deleted, their roster rows go too.
-- -----------------------------------------------------------------------------
CREATE TABLE rosters (
    participant_id INTEGER NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
    team_id        INTEGER NOT NULL,
    PRIMARY KEY (participant_id, team_id)  -- composite PK prevents duplicate drafts
);


-- -----------------------------------------------------------------------------
-- 3. STANDINGS CACHE  (current season live data)
-- One row per NBA team (30 total). Upserted every time someone clicks
-- "Fetch Live Standings". Replaces the in-memory TTLCache in backend/cache.py.
--
-- Survives server restarts so the first page load after a cold start is fast
-- (reads from here, ~100ms) rather than hitting the NBA API (~3-5s).
--
-- TIMESTAMPTZ = timestamp with time zone. Always store in UTC.
-- DEFAULT NOW() sets fetched_at automatically on insert if not provided.
-- -----------------------------------------------------------------------------
CREATE TABLE standings_cache (
    team_id      INTEGER     PRIMARY KEY,
    name         TEXT        NOT NULL,
    abbreviation TEXT        NOT NULL,
    wins         INTEGER     NOT NULL,
    losses       INTEGER     NOT NULL,
    home_record  TEXT        NOT NULL,  -- e.g. "22-11"
    away_record  TEXT        NOT NULL,
    last_10      TEXT        NOT NULL,  -- e.g. "7-3"
    conf_rank    INTEGER     NOT NULL,
    conference   TEXT        NOT NULL,  -- "East" or "West"
    fetched_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- -----------------------------------------------------------------------------
-- 4. SEASON RECORDS  (historical + current season aggregate)
-- One row per participant per season. Stores the combined W-L of all their
-- drafted teams for that season.
--
-- This is the source of truth for the all-time leaderboard. Every completed
-- season gets a row here. The current season's row is NOT stored here while
-- in progress — it's calculated live from standings_cache + rosters and
-- added at season's end.
--
-- Seasons we have data for:
--   2021-22, 2022-23, 2023-24, 2024-25  (completed — seed manually below)
--   2025-26                              (in progress — calculated live)
--
-- UNIQUE (participant_name, season) prevents duplicate entries.
-- We use participant_name as TEXT (not a foreign key to participants) because
-- historical records should survive even if a participant is renamed/removed.
-- -----------------------------------------------------------------------------
CREATE TABLE season_records (
    id               SERIAL  PRIMARY KEY,
    participant_name TEXT    NOT NULL,   -- e.g. 'John'
    season           TEXT    NOT NULL,   -- e.g. '2021-22'
    wins             INTEGER NOT NULL,
    losses           INTEGER NOT NULL,
    UNIQUE (participant_name, season)
);


-- =============================================================================
-- SEEDING YOUR DATA
-- =============================================================================
-- Run these INSERT statements in the Supabase SQL Editor after creating tables.
-- Replace names and values with your actual data.
--
-- STEP 1: Add participants (the people in the draft)
-- -----------------------------------------------------------------------------
--   INSERT INTO participants (name) VALUES
--     ('John'),
--     ('Nate');
--     -- add more as needed
--
-- -----------------------------------------------------------------------------
-- STEP 2: Add current season rosters (from rosters.json)
-- Use the team IDs from the NBA API. Run this to look them up:
--   python -c "from nba_api.stats.static import teams; import json; print(json.dumps(teams.get_teams(), indent=2))"
-- -----------------------------------------------------------------------------
--   INSERT INTO rosters (participant_id, team_id)
--   VALUES
--     ((SELECT id FROM participants WHERE name = 'John'), 1610612745),  -- HOU
--     ((SELECT id FROM participants WHERE name = 'John'), 1610612747),  -- LAL
--     ((SELECT id FROM participants WHERE name = 'Nate'), 1610612738),  -- BOS
--     ((SELECT id FROM participants WHERE name = 'Nate'), 1610612743);  -- DEN
--     -- add all 5 teams per participant
--
-- -----------------------------------------------------------------------------
-- STEP 3: Seed historical aggregate records (2021-22 through 2024-25)
-- Fill in the actual wins/losses you have for each person each season.
-- -----------------------------------------------------------------------------
--   INSERT INTO season_records (participant_name, season, wins, losses)
--   VALUES
--     ('John', '2021-22', 0, 0),   -- TODO: replace 0,0 with real numbers
--     ('John', '2022-23', 0, 0),
--     ('John', '2023-24', 0, 0),
--     ('John', '2024-25', 0, 0),
--     ('Nate', '2021-22', 0, 0),
--     ('Nate', '2022-23', 0, 0),
--     ('Nate', '2023-24', 0, 0),
--     ('Nate', '2024-25', 0, 0);
--     -- add all participants × all seasons
-- =============================================================================
