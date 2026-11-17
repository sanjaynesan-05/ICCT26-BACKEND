"""
Fixtures for the 2027 registration tests.

These tests need a disposable LOCAL PostgreSQL. They refuse to run against any
non-local host so they can never touch the real (Neon) database.

    docker run -d --rm --name icct-test-pg -e POSTGRES_PASSWORD=test \
        -e POSTGRES_DB=icct_test -p 55432:5432 postgres:16-alpine
    venv/Scripts/python -m pytest tests/registration_2027 -v
"""

import os
from urllib.parse import urlsplit

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL", "postgresql://postgres:test@localhost:55432/icct_test"
)
if urlsplit(TEST_DATABASE_URL).hostname not in {"localhost", "127.0.0.1"}:
    raise RuntimeError(f"Refusing to run tests against non-local database: {TEST_DATABASE_URL}")

# Must be set before `database` / `config.settings` are imported (env beats .env.local).
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["CLOUDINARY_PREFIX"] = "icct27"
os.environ.pop("CHURCH_LIST", None)

# python-magic's libmagic hangs on import in the Windows dev venv. Block it so
# app.utils.validation uses its built-in magic-byte signature check (which is
# authoritative anyway). Remove this if libmagic works in your environment.
import sys  # noqa: E402
if sys.platform == "win32":
    sys.modules.setdefault("magic", None)

import struct  # noqa: E402
import zlib  # noqa: E402

import httpx  # noqa: E402
import psycopg2  # noqa: E402
import pytest  # noqa: E402
from fastapi import FastAPI  # noqa: E402


def _png_bytes() -> bytes:
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    raw = b"\x00\xff\xff\xff"
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


PNG = _png_bytes()


def reset_database():
    """Drop everything and recreate the schema from the models (fresh 2027 state)."""
    from database import Base, sync_engine
    import models  # noqa: F401  (registers tables)

    conn = psycopg2.connect(TEST_DATABASE_URL)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("DROP SCHEMA IF EXISTS archive_2026 CASCADE")
        cur.execute("DROP SCHEMA public CASCADE")
        cur.execute("CREATE SCHEMA public")
    conn.close()
    sync_engine.dispose()
    Base.metadata.create_all(sync_engine)
    conn = psycopg2.connect(TEST_DATABASE_URL)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("INSERT INTO team_sequence (id, last_number) VALUES (1, 0)")
        # Unique indexes that exist in the live database but not in models.py.
        cur.execute("CREATE UNIQUE INDEX ix_teams_captain_email ON teams (captain_email)")
        cur.execute("CREATE UNIQUE INDEX ix_teams_captain_phone ON teams (captain_phone)")
    conn.close()


@pytest.fixture
def db_conn():
    reset_database()
    conn = psycopg2.connect(TEST_DATABASE_URL)
    conn.autocommit = True
    yield conn
    conn.close()


class FakeCloudinary:
    """Records uploads/deletes; behaviour can be swapped per test."""

    def __init__(self):
        self.uploads = []
        self.deletes = []
        self.before_return = None  # optional async hook(key)
        self.fail = False

    async def upload(self, receipt, key):
        self.uploads.append(key)
        if self.before_return:
            await self.before_return(key)
        if self.fail:
            from app.utils.cloudinary_reliable import CloudinaryUploadError
            raise CloudinaryUploadError("simulated outage")
        return f"https://res.cloudinary.com/test/image/upload/icct27/pending/{key}/payment_receipt.png"

    async def delete(self, key):
        self.deletes.append(key)


@pytest.fixture
def cloud(monkeypatch):
    from app.routes import registration_production as route

    fake = FakeCloudinary()
    monkeypatch.setattr(route, "_upload_receipt", fake.upload)
    monkeypatch.setattr(route, "_delete_receipt", fake.delete)

    # Record every email instead of sending it. Registration must send none;
    # only admin approval may email the team.
    fake.emails = []

    async def record_email(to_email, subject, body, **kwargs):
        fake.emails.append({"to": to_email, "subject": subject, "body": body})
        return True
    from app.utils import email_reliable
    monkeypatch.setattr(email_reliable, "send_email_with_retry", record_email)

    # Admin confirm moves files pending -> confirmed; don't hit Cloudinary.
    from app.utils.cloudinary_upload import cloudinary_uploader

    async def fake_move(team_id, file_field_name):
        return f"https://res.cloudinary.com/test/image/upload/icct27/confirmed/{team_id}/{file_field_name}.png"
    monkeypatch.setattr(cloudinary_uploader, "move_to_confirmed", fake_move)
    return fake


@pytest.fixture
async def client(db_conn, cloud):
    from app.routes.churches import router as churches_router
    from app.routes.registration_production import router as registration_router
    from app.routes.admin import router as admin_router

    app = FastAPI()
    app.include_router(registration_router, prefix="/api")
    app.include_router(admin_router, prefix="/admin")
    app.include_router(churches_router)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
        yield c
