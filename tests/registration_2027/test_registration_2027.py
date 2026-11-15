"""Registration, idempotency and church-availability tests for the 2027 contract."""

import asyncio
import uuid

import pytest

from config.churches import CHURCH_NAMES
from tests.registration_2027.conftest import PNG

CHURCH = "CSI Church Airport"


def form(players=13, church=CHURCH, team_name="Airport Eagles", **overrides):
    data = {
        "team_name": team_name,
        "church_name": church,
        "captain_name": "John Samuel",
        "captain_phone": "9876543210",
        "captain_email": "captain@example.com",
        "captain_whatsapp": "",
        "vice_name": "Peter Paul",
        "vice_phone": "9876543211",
        "vice_email": "vice@example.com",
        "vice_whatsapp": "",
    }
    for i in range(players):
        data[f"player_{i}_name"] = f"Player {chr(65 + i)}lpha"
    data.update(overrides)
    return data


async def post(client, data, key=None, receipt=PNG, filename="receipt.png"):
    key = key or str(uuid.uuid4())
    files = {"payment_receipt": (filename, receipt, "image/png")}
    return await client.post("/api/register/team", data=data, files=files, headers={"Idempotency-Key": key})


def fetch(db_conn, sql, *params):
    with db_conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


# --- happy path ----------------------------------------------------------------

@pytest.mark.parametrize("count", [13, 17])
async def test_registration_succeeds_with_13_and_17_players(client, db_conn, cloud, count):
    res = await post(client, form(players=count))
    assert res.status_code == 201, res.text
    body = res.json()
    assert body == {
        "success": True,
        "data": {"registration_status": "pending", "team_id": "ICCT-001", "team_name": "Airport Eagles"},
        "message": body["message"],
    }
    assert isinstance(body["message"], str) and body["message"]
    players = fetch(db_conn, "SELECT player_id FROM players WHERE team_id = 'ICCT-001' ORDER BY player_id")
    assert [p[0] for p in players] == [f"ICCT-001-P{i:02d}" for i in range(1, count + 1)]
    assert len(cloud.uploads) == 1


async def test_empty_whatsapp_is_stored_as_null(client, db_conn):
    res = await post(client, form())
    assert res.status_code == 201, res.text
    row = fetch(db_conn, "SELECT captain_whatsapp, vice_captain_whatsapp, church_name_normalized FROM teams")[0]
    assert row == (None, None, "csi church airport")


# --- validation ------------------------------------------------------------------

@pytest.mark.parametrize("count", [12, 18])
async def test_wrong_player_count_is_422(client, cloud, count):
    res = await post(client, form(players=count))
    assert res.status_code == 422
    body = res.json()
    assert body["success"] is False and body["error_code"] == "VALIDATION_ERROR"
    assert body["details"]["field"] == "players"
    assert cloud.uploads == []


async def test_gap_in_player_indexes_is_422(client):
    data = form(players=14)
    data["player_20_name"] = data.pop("player_5_name")
    res = await post(client, data)
    assert res.status_code == 422
    assert res.json()["error_code"] == "VALIDATION_ERROR"


async def test_duplicate_player_index_is_422(client):
    data = form(players=13)
    data["player_3_name"] = [data["player_3_name"], "Another Name"]  # field sent twice
    res = await post(client, data)
    assert res.status_code == 422
    assert res.json()["error_code"] == "VALIDATION_ERROR"


async def test_receipt_extension_must_match_content(client, cloud):
    res = await post(client, form(), receipt=PNG, filename="receipt.pdf")
    assert res.status_code == 422
    assert res.json()["details"]["field"] == "payment_receipt"
    assert cloud.uploads == []


async def test_validation_accepts_frontend_edge_values(client):
    data = form(team_name="A1 '-" + "x" * 75, captain_name="Ann O'Neil-Smith", captain_whatsapp="9123456789")
    assert len(data["team_name"]) == 80
    res = await post(client, data)
    assert res.status_code == 201, res.text


# --- church rule -------------------------------------------------------------------

async def test_same_church_with_other_case_or_spacing_is_409_without_upload(client, db_conn, cloud):
    assert (await post(client, form())).status_code == 201
    uploads_before = len(cloud.uploads)

    res = await post(client, form(church="  csi   CHURCH   airport ", team_name="Second Team"))
    assert res.status_code == 409
    body = res.json()
    assert body["error_code"] == "CHURCH_ALREADY_REGISTERED"
    assert body["message"] == "CSI Church Airport already has its one allowed entry."
    assert len(cloud.uploads) == uploads_before  # rejected before uploading
    assert fetch(db_conn, "SELECT count(*) FROM teams")[0][0] == 1


async def test_unique_index_race_maps_to_409_and_deletes_upload(client, db_conn, cloud):
    async def competitor_wins(key):
        # Another registration for the same church commits while we upload.
        with db_conn.cursor() as cur:
            cur.execute("""INSERT INTO teams (team_id, team_name, church_name, church_name_normalized,
                               captain_name, captain_phone, captain_email,
                               vice_captain_name, vice_captain_phone, vice_captain_email)
                           VALUES ('ICCT-900', 'Rival', 'CSI Church Airport', 'csi church airport',
                                   'A B C', '9000000000', 'a@b.co', 'D E F', '9000000001', 'd@e.co')""")
    cloud.before_return = competitor_wins

    key = str(uuid.uuid4())
    res = await post(client, form(), key=key)
    assert res.status_code == 409
    assert res.json()["error_code"] == "CHURCH_ALREADY_REGISTERED"
    assert cloud.deletes == [key]
    assert fetch(db_conn, "SELECT state FROM idempotency_keys WHERE key = %s", key)[0][0] == "failed"


async def test_reused_captain_email_is_422_not_500(client, cloud):
    assert (await post(client, form())).status_code == 201
    res = await post(client, form(church="CSI Perur Pastorate", team_name="Perur Team", captain_phone="9123456780"))
    assert res.status_code == 422, res.text
    assert res.json()["error_code"] == "VALIDATION_ERROR"
    assert res.json()["details"]["field"] == "captain_email"
    assert len(cloud.deletes) == 1  # the second upload was cleaned up


async def test_unknown_church_is_422(client):
    res = await post(client, form(church="Some Other Church"))
    assert res.status_code == 422
    assert res.json()["details"]["field"] == "church_name"


# --- idempotency -------------------------------------------------------------------

async def test_replay_after_success_returns_identical_201(client, db_conn, cloud):
    key = str(uuid.uuid4())
    first = await post(client, form(), key=key)
    second = await post(client, form(), key=key)
    assert first.status_code == second.status_code == 201
    assert first.json() == second.json()
    assert len(cloud.uploads) == 1
    assert fetch(db_conn, "SELECT count(*) FROM teams")[0][0] == 1


async def test_same_key_while_processing_is_409_in_progress(client, cloud):
    started, release = asyncio.Event(), asyncio.Event()

    async def slow(key):
        started.set()
        await release.wait()
    cloud.before_return = slow

    key = str(uuid.uuid4())
    first = asyncio.create_task(post(client, form(), key=key))
    await asyncio.wait_for(started.wait(), 10)

    second = await post(client, form(), key=key)
    assert second.status_code == 409
    assert second.json()["error_code"] == "REQUEST_IN_PROGRESS"
    assert second.headers["Retry-After"] == "5"

    release.set()
    assert (await first).status_code == 201
    third = await post(client, form(), key=key)
    assert third.status_code == 201 and third.json() == (await first).json()


async def test_two_simultaneous_retries_of_failed_key_only_one_proceeds(client, db_conn, cloud):
    key = str(uuid.uuid4())
    cloud.fail = True
    failed = await post(client, form(), key=key)
    assert failed.status_code == 503
    assert failed.json()["error_code"] == "FILE_UPLOAD_FAILED"
    assert fetch(db_conn, "SELECT state FROM idempotency_keys WHERE key = %s", key)[0][0] == "failed"

    cloud.fail = False
    cloud.uploads.clear()

    async def slow(_key):
        await asyncio.sleep(0.5)
    cloud.before_return = slow

    a, b = await asyncio.gather(post(client, form(), key=key), post(client, form(), key=key))
    statuses = sorted([a.status_code, b.status_code])
    assert statuses == [201, 409], (a.text, b.text)
    loser = a if a.status_code == 409 else b
    assert loser.json()["error_code"] == "REQUEST_IN_PROGRESS"
    assert loser.headers["Retry-After"] == "5"
    assert len(cloud.uploads) == 1
    assert fetch(db_conn, "SELECT count(*) FROM teams")[0][0] == 1


async def test_stale_processing_key_is_taken_over(client, db_conn, cloud):
    key = str(uuid.uuid4())
    cloud.fail = True
    await post(client, form(), key=key)
    with db_conn.cursor() as cur:
        cur.execute("UPDATE idempotency_keys SET state = 'processing', created_at = now() - interval '16 minutes' "
                    "WHERE key = %s", (key,))
    cloud.fail = False
    res = await post(client, form(), key=key)
    assert res.status_code == 201, res.text


async def test_same_key_different_body_is_409_duplicate(client):
    key = str(uuid.uuid4())
    assert (await post(client, form(), key=key)).status_code == 201
    res = await post(client, form(team_name="Different Name"), key=key)
    assert res.status_code == 409
    assert res.json()["error_code"] == "DUPLICATE_SUBMISSION"


async def test_missing_or_bad_idempotency_key_is_422(client):
    res = await client.post("/api/register/team", data=form(), files={"payment_receipt": ("r.png", PNG, "image/png")})
    assert res.status_code == 422
    res = await post(client, form(), key="not-a-uuid")
    assert res.status_code == 422


async def test_error_bodies_always_have_details(client):
    res = await post(client, form(players=12))
    assert set(res.json()) == {"success", "error_code", "message", "details"}


# --- availability -------------------------------------------------------------------

async def test_availability_lists_every_configured_church(client, db_conn):
    assert (await post(client, form(church="csi church AIRPORT"))).status_code == 201
    with db_conn.cursor() as cur:  # a legacy row stored with odd spacing/casing
        cur.execute("""INSERT INTO teams (team_id, team_name, church_name, church_name_normalized,
                           captain_name, captain_phone, captain_email,
                           vice_captain_name, vice_captain_phone, vice_captain_email)
                       VALUES ('ICCT-050', 'Ooty Team', '  csi  WESLEY church ooty', 'csi wesley church ooty',
                               'A B C', '9000000000', 'a@b.co', 'D E F', '9000000001', 'd@e.co')""")

    res = await client.get("/api/churches/availability")
    assert res.status_code == 200
    body = res.json()
    names = [c["church_name"] for c in body["churches"]]
    assert names == CHURCH_NAMES  # every name, exact spelling
    by_name = {c["church_name"]: c for c in body["churches"]}
    assert by_name["CSI Church Airport"] == {"church_name": "CSI Church Airport", "team_count": 1, "locked": True}
    assert by_name["CSI Wesley Church Ooty"]["team_count"] == 1 and by_name["CSI Wesley Church Ooty"]["locked"]
    assert by_name["CSI Perur Pastorate"] == {"church_name": "CSI Perur Pastorate", "team_count": 0, "locked": False}
    assert body["summary"] == {
        "total_churches": len(CHURCH_NAMES), "locked_churches": 2, "available_churches": len(CHURCH_NAMES) - 2,
    }


# --- CORS ------------------------------------------------------------------------------

async def test_cors_exposes_retry_after():
    import httpx
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    from app.middleware.production_middleware import setup_middleware

    app = FastAPI()
    setup_middleware(app)

    @app.get("/x")
    async def x():
        return JSONResponse({}, status_code=409, headers={"Retry-After": "5"})

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
        res = await c.get("/x", headers={"Origin": "https://icct27.netlify.app"})
    assert "retry-after" in res.headers.get("access-control-expose-headers", "").lower()
