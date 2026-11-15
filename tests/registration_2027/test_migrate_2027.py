"""scripts/migrate_2027.py against a seeded 2026-style local database."""

import re
import subprocess
import sys
from pathlib import Path

from tests.registration_2027.conftest import TEST_DATABASE_URL

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "migrate_2027.py"
TABLES = ["teams", "players", "matches", "idempotency_keys"]


def seed_2026(conn):
    """Recreate the legacy shape: nullable column, lower(trim()) values, partial index."""
    with conn.cursor() as cur:
        # 2026 quirks seen in the live database:
        cur.execute("UPDATE idempotency_keys SET expires_at = now()")
        cur.execute("ALTER TABLE idempotency_keys ALTER COLUMN expires_at SET NOT NULL")
        for legacy in ("captains", "vice_captains"):
            cur.execute(f"""CREATE TABLE {legacy} (id SERIAL PRIMARY KEY,
                            team_id VARCHAR(50) REFERENCES teams(team_id), name VARCHAR(100))""")
        cur.execute("DROP INDEX uq_registered_team_church")
        cur.execute("ALTER TABLE teams ALTER COLUMN church_name_normalized DROP NOT NULL")
        cur.execute("""CREATE UNIQUE INDEX uq_registered_team_church ON teams(church_name_normalized)
                       WHERE registration_status IS NULL OR registration_status <> 'rejected'""")
        for n, church in enumerate(["CSI Perur Pastorate", "CSI  Annur   Pastorate", "CSI Pollachi Pastorate"], 1):
            team_id = f"ICCT-{n:03d}"
            cur.execute("""INSERT INTO teams (team_id, team_name, church_name, church_name_normalized,
                               captain_name, captain_phone, captain_email,
                               vice_captain_name, vice_captain_phone, vice_captain_email)
                           VALUES (%s, %s, %s, lower(trim(%s)), 'A B C', %s, 'a@b.co', 'D E F', '9000000001', 'd@e.co')""",
                        (team_id, f"Team {n}", church, church, f"90000000{n:02d}"))
            for p in range(1, 14):
                cur.execute("INSERT INTO players (player_id, team_id, name) VALUES (%s, %s, 'Some Player')",
                            (f"{team_id}-P{p:02d}", team_id))
        cur.execute("""INSERT INTO matches (round, round_number, match_number, team1_id, team2_id, status)
                       SELECT 'Round 1', 1, 1, a.id, b.id, 'completed'
                         FROM teams a, teams b WHERE a.team_id = 'ICCT-001' AND b.team_id = 'ICCT-002'""")
        cur.execute("INSERT INTO idempotency_keys (key, state, created_at, endpoint, expires_at) "
                    "VALUES ('k1', 'completed', now(), 'x', now()), ('k2', 'failed', now(), 'x', now())")
        cur.execute("UPDATE team_sequence SET last_number = 3")


def counts(conn, schema="public"):
    with conn.cursor() as cur:
        result = {}
        for t in TABLES:
            cur.execute(f"SELECT count(*) FROM {schema}.{t}")
            result[t] = cur.fetchone()[0]
        return result


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--database-url", TEST_DATABASE_URL, *args],
        cwd=ROOT, capture_output=True, text=True, timeout=120,
    )


def test_dry_run_archive_counts_match_and_nothing_changes(db_conn):
    seed_2026(db_conn)
    before = counts(db_conn)
    assert before == {"teams": 3, "players": 39, "matches": 1, "idempotency_keys": 2}

    result = run("--dry-run")
    assert result.returncode == 0, result.stdout + result.stderr
    out = result.stdout
    for t, n in before.items():
        assert re.search(rf"{t}: public={n} archive={n} OK", out), out
    assert ("TRUNCATE public.players, public.matches, public.captains, public.vice_captains, "
            "public.teams, public.idempotency_keys RESTART IDENTITY") in out
    assert "DRY RUN: rolled back" in out

    assert counts(db_conn) == before  # rolled back
    with db_conn.cursor() as cur:
        cur.execute("SELECT to_regnamespace('archive_2026')")
        assert cur.fetchone()[0] is None


def test_real_run_then_rerun_is_idempotent(db_conn):
    seed_2026(db_conn)
    before = counts(db_conn)

    first = run("--confirm-reset")
    assert first.returncode == 0, first.stdout + first.stderr
    assert counts(db_conn) == {t: 0 for t in TABLES}
    assert counts(db_conn, "archive_2026") == before
    with db_conn.cursor() as cur:
        cur.execute("SELECT last_number FROM team_sequence WHERE id = 1")
        assert cur.fetchone()[0] == 0
        cur.execute("SELECT indisunique, indpred IS NULL FROM pg_index "
                    "WHERE indexrelid = 'public.uq_registered_team_church'::regclass")
        assert cur.fetchone() == (True, True)  # full, not partial
        cur.execute("SELECT is_nullable FROM information_schema.columns "
                    "WHERE table_name = 'teams' AND column_name = 'church_name_normalized'")
        assert cur.fetchone()[0] == "NO"
        # The route inserts keys without expires_at; that must work after the migration.
        cur.execute("INSERT INTO idempotency_keys (key, state, endpoint, created_at) VALUES ('new', 'processing', 'x', now())")
        # A 2027 registration arrives...
        cur.execute("""INSERT INTO teams (team_id, team_name, church_name, church_name_normalized,
                           captain_name, captain_phone, captain_email,
                           vice_captain_name, vice_captain_phone, vice_captain_email)
                       VALUES ('ICCT-001', 'New', 'CSI Perur Pastorate', 'csi perur pastorate',
                               'A B C', '9000000000', 'a@b.co', 'D E F', '9000000001', 'd@e.co')""")

    second = run("--confirm-reset")
    assert second.returncode == 0, second.stdout + second.stderr
    assert "already ran - skipping archive/truncate" in second.stdout
    assert counts(db_conn)["teams"] == 1  # 2027 data survives a re-run
    assert counts(db_conn, "archive_2026") == before
