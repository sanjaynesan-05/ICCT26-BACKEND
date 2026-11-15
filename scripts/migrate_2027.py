"""
ICCT 2027 database reset and schema alignment.

Archives the 2026 registrations into schema archive_2026, empties the live
tables, resets the team counter, and makes the schema match the 2027 backend.
Everything runs in ONE transaction; any failure rolls back everything.

Usage (see scripts/MIGRATE_2027.md; take the pg_dump backup first):
    python scripts/migrate_2027.py --dry-run           # prints SQL + counts, then ROLLBACK
    python scripts/migrate_2027.py --confirm-reset     # really does it

The database URL comes from --database-url, else $DATABASE_URL, else .env.local.

Idempotent: the archive + truncate step runs once and is recorded in
archive_2026.migration_log. Re-running after that only re-applies the schema
steps, so 2027 registrations are never truncated by a second run.
"""

import argparse
import os
import sys
from pathlib import Path
from urllib.parse import urlsplit

import psycopg2

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from config.churches import normalize_church_name  # noqa: E402  (same rule as the API)

ARCHIVE_SCHEMA = "archive_2026"
MARKER = "reset_for_2027"
# Archive order is irrelevant; TRUNCATE lists them together so FKs are satisfied.
TABLES = ["teams", "players", "matches", "idempotency_keys"]
# Legacy tables that have foreign keys into teams (empty in the live DB, but
# TRUNCATE teams fails unless they are truncated too). Included when present.
LEGACY_CHILD_TABLES = ["captains", "vice_captains"]
CHURCH_INDEX = "uq_registered_team_church"


class Migration:
    def __init__(self, conn, dry_run: bool):
        self.conn = conn
        self.cur = conn.cursor()
        self.dry_run = dry_run
        self.tables = TABLES + [t for t in LEGACY_CHILD_TABLES if self.exists(f"public.{t}")]

    # -- helpers ------------------------------------------------------------
    def sql(self, statement: str, params=None):
        shown = " ".join(statement.split())
        print(f"  SQL> {shown}" + (f"   -- params={params}" if params else ""))
        self.cur.execute(statement, params)
        return self.cur

    def scalar(self, statement: str, params=None):
        self.cur.execute(statement, params)
        row = self.cur.fetchone()
        return row[0] if row else None

    def exists(self, qualified: str) -> bool:
        return self.scalar("SELECT to_regclass(%s) IS NOT NULL", (qualified,))

    def count(self, qualified: str) -> int:
        return self.scalar(f"SELECT count(*) FROM {qualified}")

    def column_exists(self, table: str, column: str) -> bool:
        return bool(self.scalar(
            """SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = %s AND column_name = %s""",
            (table, column),
        ))

    # -- steps --------------------------------------------------------------
    def preflight(self):
        print("\n== Preflight")
        missing = [t for t in self.tables + ["team_sequence"] if not self.exists(f"public.{t}")]
        if missing:
            raise SystemExit(f"ABORT: missing tables in public schema: {missing}")
        # TRUNCATE without CASCADE fails if another table references these; report it up front.
        self.cur.execute(
            """SELECT conrelid::regclass::text, confrelid::regclass::text, conname
                 FROM pg_constraint
                WHERE contype = 'f'
                  AND confrelid::regclass::text = ANY(%s)
                  AND NOT (conrelid::regclass::text = ANY(%s))""",
            (self.tables, self.tables),
        )
        outside = self.cur.fetchall()
        if outside:
            raise SystemExit(
                "ABORT: these tables reference tables being truncated; handle them first:\n"
                + "\n".join(f"  {src} -> {dst} ({name})" for src, dst, name in outside)
            )
        for t in self.tables:
            print(f"  public.{t}: {self.count('public.' + t)} rows")
        print(f"  team_sequence.last_number = {self.scalar('SELECT last_number FROM public.team_sequence WHERE id = 1')}")

    def already_reset(self) -> bool:
        if not self.exists(f"{ARCHIVE_SCHEMA}.migration_log"):
            return False
        return bool(self.scalar(f"SELECT 1 FROM {ARCHIVE_SCHEMA}.migration_log WHERE step = %s", (MARKER,)))

    def archive_and_reset(self):
        print(f"\n== Archive into {ARCHIVE_SCHEMA}")
        # Block writes for the rest of the transaction so counts can't drift.
        self.sql("SET LOCAL lock_timeout = '10s'")
        locked = ", ".join(f"public.{t}" for t in self.tables + ["team_sequence"])
        self.sql(f"LOCK TABLE {locked} IN ACCESS EXCLUSIVE MODE")
        self.sql(f"CREATE SCHEMA IF NOT EXISTS {ARCHIVE_SCHEMA}")

        mismatches = []
        for t in self.tables:
            archive = f"{ARCHIVE_SCHEMA}.{t}"
            if self.exists(archive):
                print(f"  {archive} already exists - skipping copy")
            else:
                self.sql(f"CREATE TABLE {archive} AS SELECT * FROM public.{t}")
            original, copied = self.count(f"public.{t}"), self.count(archive)
            status = "OK" if original == copied else "MISMATCH"
            print(f"  {t}: public={original} archive={copied} {status}")
            if original != copied:
                mismatches.append(t)
        if mismatches:
            raise SystemExit(f"ABORT: archive row counts differ for {mismatches}; nothing was truncated.")

        print("\n== Reset live tables")
        order = ["players", "matches"] + [t for t in self.tables if t in LEGACY_CHILD_TABLES] + ["teams", "idempotency_keys"]
        self.sql(f"TRUNCATE {', '.join('public.' + t for t in order)} RESTART IDENTITY")
        self.sql("""INSERT INTO public.team_sequence (id, last_number) VALUES (1, 0)
                    ON CONFLICT (id) DO UPDATE SET last_number = 0""")

        self.sql(f"""CREATE TABLE IF NOT EXISTS {ARCHIVE_SCHEMA}.migration_log (
                        step TEXT PRIMARY KEY, done_at TIMESTAMPTZ NOT NULL DEFAULT now())""")
        self.sql(f"INSERT INTO {ARCHIVE_SCHEMA}.migration_log (step) VALUES (%s)", (MARKER,))

    def align_schema(self):
        print("\n== Schema")
        self.sql("ALTER TABLE public.teams ADD COLUMN IF NOT EXISTS church_name_normalized VARCHAR(200)")
        self.sql("ALTER TABLE public.teams ADD COLUMN IF NOT EXISTS "
                 "registration_status VARCHAR(20) NOT NULL DEFAULT 'pending'")

        # Backfill with the exact Python rule the API uses (empty after a reset).
        self.cur.execute("SELECT id, church_name, church_name_normalized FROM public.teams")
        updates = [(normalize_church_name(name), row_id)
                   for row_id, name, current in self.cur.fetchall()
                   if current != normalize_church_name(name)]
        print(f"  church_name_normalized rows to (re)normalize: {len(updates)}")
        for normalized, row_id in updates:
            self.cur.execute("UPDATE public.teams SET church_name_normalized = %s WHERE id = %s", (normalized, row_id))

        dupes = self.scalar("""SELECT count(*) FROM (SELECT church_name_normalized FROM public.teams
                                GROUP BY 1 HAVING count(*) > 1) d""")
        if dupes:
            raise SystemExit(f"ABORT: {dupes} churches have more than one team; cannot add the UNIQUE index.")

        self.sql("ALTER TABLE public.teams ALTER COLUMN church_name_normalized SET NOT NULL")

        # Older startups created a PARTIAL index (excluding rejected teams). Replace it
        # with a plain unique index so it matches the availability count.
        self.cur.execute(
            """SELECT i.indisunique, i.indpred IS NOT NULL,
                      EXISTS (SELECT 1 FROM pg_constraint c WHERE c.conindid = i.indexrelid)
                 FROM pg_index i
                WHERE i.indexrelid = to_regclass(%s)""",
            (f"public.{CHURCH_INDEX}",),
        )
        row = self.cur.fetchone()
        if row is None:
            self.sql(f"CREATE UNIQUE INDEX {CHURCH_INDEX} ON public.teams (church_name_normalized)")
        else:
            is_unique, is_partial, is_constraint = row
            if is_unique and not is_partial:
                print(f"  {CHURCH_INDEX} already a full unique index - ok")
            elif is_constraint:
                raise SystemExit(f"ABORT: {CHURCH_INDEX} is a constraint with an unexpected definition; fix by hand.")
            else:
                print(f"  {CHURCH_INDEX} is {'partial' if is_partial else 'not unique'} - replacing")
                self.sql(f"DROP INDEX public.{CHURCH_INDEX}")
                self.sql(f"CREATE UNIQUE INDEX {CHURCH_INDEX} ON public.teams (church_name_normalized)")

        # Optional / legacy columns: present and nullable.
        for table, column, ddl_type in [
            ("teams", "captain_whatsapp", "VARCHAR(20)"),
            ("teams", "vice_captain_whatsapp", "VARCHAR(20)"),
            ("teams", "pastor_letter", "TEXT"),
            ("teams", "group_photo", "TEXT"),
            ("players", "role", "VARCHAR(20)"),
            ("players", "aadhar_file", "TEXT"),
            ("players", "subscription_file", "TEXT"),
        ]:
            if not self.column_exists(table, column):
                self.sql(f"ALTER TABLE public.{table} ADD COLUMN {column} {ddl_type}")
            self.sql(f"ALTER TABLE public.{table} ALTER COLUMN {column} DROP NOT NULL")

        # Columns the registration route's idempotency logic relies on.
        for column, ddl in [
            ("endpoint", "VARCHAR(100) NOT NULL DEFAULT '/api/register/team'"),
            ("request_fingerprint", "VARCHAR(64)"),
            ("state", "VARCHAR(20) NOT NULL DEFAULT 'processing'"),
            ("team_id", "VARCHAR(50)"),
        ]:
            self.sql(f"ALTER TABLE public.idempotency_keys ADD COLUMN IF NOT EXISTS {column} {ddl}")
        # Keys never expire now; the 2026 schema had expires_at NOT NULL, which makes
        # every registration fail.
        if self.column_exists("idempotency_keys", "expires_at"):
            self.sql("ALTER TABLE public.idempotency_keys ALTER COLUMN expires_at DROP NOT NULL")

        self.sql("""INSERT INTO public.team_sequence (id, last_number) VALUES (1, 0)
                    ON CONFLICT (id) DO NOTHING""")

    def summary(self):
        print("\n== Result (inside the transaction)")
        for t in self.tables:
            archive = f"{ARCHIVE_SCHEMA}.{t}"
            archived = self.count(archive) if self.exists(archive) else "-"
            print(f"  {t}: public={self.count('public.' + t)} archive_2026={archived}")
        print(f"  team_sequence.last_number = {self.scalar('SELECT last_number FROM public.team_sequence WHERE id = 1')}"
              f"  (next team: ICCT-{self.scalar('SELECT last_number FROM public.team_sequence WHERE id = 1') + 1:03d})")


def resolve_url(cli_url):
    url = cli_url or os.getenv("DATABASE_URL")
    if not url:
        env_file = ROOT / ".env.local"
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("DATABASE_URL="):
                    url = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not url:
        raise SystemExit("No database URL: pass --database-url or set DATABASE_URL.")
    url = url.replace("postgresql+asyncpg://", "postgresql://")
    return url.replace("?ssl=require", "?sslmode=require").replace("&ssl=require", "&sslmode=require")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="run everything, print SQL and counts, then ROLLBACK")
    mode.add_argument("--confirm-reset", action="store_true", help="really archive, truncate and COMMIT")
    parser.add_argument("--database-url")
    args = parser.parse_args(argv)

    url = resolve_url(args.database_url)
    parts = urlsplit(url)
    print(f"Target: {parts.hostname}:{parts.port or 5432}{parts.path}   mode: {'DRY RUN' if args.dry_run else 'COMMIT'}")

    conn = psycopg2.connect(url)
    conn.autocommit = False
    migration = Migration(conn, args.dry_run)
    try:
        migration.preflight()
        if migration.already_reset():
            print(f"\n== {ARCHIVE_SCHEMA}.migration_log says the 2027 reset already ran - skipping archive/truncate")
        else:
            migration.archive_and_reset()
        migration.align_schema()
        migration.summary()
        if args.dry_run:
            conn.rollback()
            print("\nDRY RUN: rolled back. Nothing was changed.")
        else:
            conn.commit()
            print("\nCOMMITTED.")
    except BaseException:
        conn.rollback()
        print("\nROLLED BACK because of an error.", file=sys.stderr)
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
