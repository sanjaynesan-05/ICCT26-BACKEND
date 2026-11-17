# 2027 database reset

`scripts/migrate_2027.py` archives the 2026 data and prepares the database for 2027
registrations. It runs in a single transaction.

## 1. Full backup first (required)

Use a `pg_dump` whose major version is at least the server's (Neon: check with
`SELECT version();`). Use the plain `postgresql://` URL with `sslmode=require`,
not the `postgresql+asyncpg://` form.

```bash
pg_dump "postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require" \
  --format=custom --no-owner --no-privileges \
  --file="icct26_full_backup_$(date +%Y%m%d_%H%M%S).dump"

# Check the dump is readable and contains the tables:
pg_restore --list icct26_full_backup_*.dump | grep -E "TABLE DATA public (teams|players|matches|idempotency_keys|team_sequence)"
```

Restore (into an empty database) if you ever need it:

```bash
pg_restore --no-owner --no-privileges --dbname "postgresql://...target..." icct26_full_backup_XXXX.dump
```

## 2. Dry run

```bash
python scripts/migrate_2027.py --dry-run --database-url "postgresql://...?sslmode=require"
```

This prints every SQL statement, the original and archived row counts for `teams`,
`players`, `matches` and `idempotency_keys`, and the final state, then **rolls back**.
Check that every archive line says `OK`.

## 3. Real run

Stop the backend (or put it in maintenance) so nobody registers mid-migration, then:

```bash
python scripts/migrate_2027.py --confirm-reset --database-url "postgresql://...?sslmode=require"
```

## What it does

1. Preflight: the tables exist and nothing outside them has a foreign key into them.
2. `LOCK` the tables, `CREATE SCHEMA IF NOT EXISTS archive_2026`, then
   `CREATE TABLE archive_2026.<t> AS SELECT * FROM public.<t>` for each table (skipped
   if that archive table already exists). Aborts unless every archived row count equals
   the original.
   The legacy `captains` and `vice_captains` tables (empty, but with foreign keys into
   `teams`) are archived and truncated too when they exist.
3. `TRUNCATE public.players, public.matches, [captains, vice_captains,] public.teams, public.idempotency_keys RESTART IDENTITY`,
   then sets `team_sequence.last_number = 0` (creating row `id = 1` if it's missing).
   The next team is `ICCT-001` (players `ICCT-001-P01` …).
4. Records the reset in `archive_2026.migration_log`. **Re-running never truncates again**:
   it only re-applies step 5, so 2027 data is safe.
5. Schema: `teams.church_name_normalized` is backfilled with the API's
   `normalize_church_name()` (`" ".join(s.split()).casefold()`), made `NOT NULL`, and
   covered by a full (non-partial) `UNIQUE` index `uq_registered_team_church`. A partial
   index left by older startups is replaced. The WhatsApp columns and the legacy
   `pastor_letter`, `group_photo`, `role`, `aadhar_file`, `subscription_file` columns are
   made nullable (added if missing). The `idempotency_keys` columns the route needs are added if missing, and
   `expires_at` is made nullable (keys never expire now; NOT NULL there made every registration fail).

The app no longer creates the church column or index at startup; this script does.

## Run log

- 2026-11-15: run on Neon with `--confirm-reset`. Archived 22 teams, 312 players, 1 key.
  No pg_dump was available, so a CSV export of every table was taken first
  (`D:\ICCT26_backups\neon_before_2027_20261115_232158`).
