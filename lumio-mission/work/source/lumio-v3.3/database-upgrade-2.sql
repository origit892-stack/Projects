-- Lumio 4.0 — additive migration (ADDITIVE ONLY).
-- Run in the Supabase SQL editor AFTER database.sql and database-upgrade.sql.
-- BACK UP YOUR DATA FIRST. Safe to re-run.
-- Adds: provenance columns on tasks/school_items (retrieval_method,
-- verification_state, synced_at, created_at), the four connection-fact
-- booleans + feed_url/feed_stamp on connections, and the apps_script_key for
-- the student-owned daily Classroom sync.
-- No new tables. RLS is unchanged — the existing table-level owner policies
-- already cover the new columns.

alter table public.tasks add column if not exists retrieval_method text not null default 'user_entry' check (retrieval_method in ('official_api','public_school_feed','local_sync','user_import','user_entry'));
alter table public.tasks add column if not exists verification_state text not null default 'user_imported_unverified' check (verification_state in ('live_verified','sandbox_verified','fixture_only','user_imported_unverified'));
alter table public.tasks add column if not exists synced_at timestamptz;
alter table public.tasks add column if not exists created_at timestamptz not null default now();

alter table public.school_items add column if not exists retrieval_method text not null default 'user_entry' check (retrieval_method in ('official_api','public_school_feed','local_sync','user_import','user_entry'));
alter table public.school_items add column if not exists verification_state text not null default 'user_imported_unverified' check (verification_state in ('live_verified','sandbox_verified','fixture_only','user_imported_unverified'));
alter table public.school_items add column if not exists synced_at timestamptz;
alter table public.school_items add column if not exists created_at timestamptz not null default now();

alter table public.connections add column if not exists identity_authenticated boolean not null default false;
alter table public.connections add column if not exists permission_granted boolean not null default false;
alter table public.connections add column if not exists data_readable boolean not null default false;
alter table public.connections add column if not exists sync_working boolean not null default false;
alter table public.connections add column if not exists feed_url text;
alter table public.connections add column if not exists feed_stamp text;
alter table public.connections add column if not exists apps_script_key text;
create unique index if not exists connections_apps_script_key_unique on public.connections(apps_script_key);

-- database.sql only allowed the v3 states. Widen the check to the Lumio 4.0
-- states, keeping the legacy values so existing rows stay valid.
-- (The auto-generated name from database.sql is connections_state_check.)
alter table public.connections drop constraint if exists connections_state_check;
alter table public.connections add constraint connections_state_check check (state in ('not_connected','login_only','awaiting_consent','requires_admin','connected_unverified','syncing','synced','needs_reauth','manual_import_only','unavailable','error','imported','api_connected'));

-- rollback (manual, only if needed):
-- alter table public.tasks drop column if exists retrieval_method;
-- alter table public.tasks drop column if exists verification_state;
-- alter table public.tasks drop column if exists synced_at;
-- alter table public.tasks drop column if exists created_at;
-- alter table public.school_items drop column if exists retrieval_method;
-- alter table public.school_items drop column if exists verification_state;
-- alter table public.school_items drop column if exists synced_at;
-- alter table public.school_items drop column if exists created_at;
-- alter table public.connections drop column if exists identity_authenticated;
-- alter table public.connections drop column if exists permission_granted;
-- alter table public.connections drop column if exists data_readable;
-- alter table public.connections drop column if exists sync_working;
-- alter table public.connections drop column if exists feed_url;
-- alter table public.connections drop column if exists feed_stamp;
-- alter table public.connections drop column if exists apps_script_key;
-- drop index if exists public.connections_apps_script_key_unique;
-- alter table public.connections drop constraint if exists connections_state_check;
-- alter table public.connections add constraint connections_state_check check (state in ('not_connected','imported','api_connected'));
