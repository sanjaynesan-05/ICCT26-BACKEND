"""The team is emailed only after an admin approves it - never at registration."""

import asyncio

from tests.registration_2027.test_registration_2027 import fetch, form, post


async def test_registration_sends_no_email(client, db_conn, cloud):
    res = await post(client, form())
    assert res.status_code == 201, res.text
    assert cloud.emails == []
    assert fetch(db_conn, "SELECT registration_status FROM teams WHERE team_id = 'ICCT-001'") == [("pending",)]


async def test_admin_confirm_sends_one_approval_email(client, db_conn, cloud):
    assert (await post(client, form())).status_code == 201

    res = await client.put("/admin/teams/ICCT-001/confirm")
    assert res.status_code == 200, res.text
    assert res.json()["registration_status"] == "confirmed"
    assert res.json()["email_notification"] == "sent"

    assert len(cloud.emails) == 1
    email = cloud.emails[0]
    assert email["to"] == "captain@example.com"
    assert "ICCT-001" in email["subject"]
    assert "approved and confirmed" in email["body"]
    assert fetch(db_conn, "SELECT registration_status FROM teams WHERE team_id = 'ICCT-001'") == [("confirmed",)]

    # Confirming again does not email the team a second time.
    again = await client.put("/admin/teams/ICCT-001/confirm")
    assert again.status_code == 200
    assert again.json()["data"]["alreadyConfirmed"] is True
    assert len(cloud.emails) == 1


async def test_double_click_approve_emails_once(client, db_conn, cloud):
    assert (await post(client, form())).status_code == 201

    results = await asyncio.gather(
        client.put("/admin/teams/ICCT-001/confirm"),
        client.put("/admin/teams/ICCT-001/confirm"),
    )
    assert all(r.status_code == 200 for r in results), [r.text for r in results]
    assert len(cloud.emails) == 1


async def test_confirm_unknown_team_is_404_and_sends_nothing(client, db_conn, cloud):
    res = await client.put("/admin/teams/ICCT-999/confirm")
    assert res.status_code == 404
    assert cloud.emails == []


def test_approval_email_escapes_team_supplied_html():
    from app.services import EmailService

    body = EmailService.create_admin_approval_email(
        team_name="Eagles <b>XI</b>",
        captain_name="O'Brien & Sons",
        team_id="ICCT-001",
        players=[{"playerId": "ICCT-001-P01", "name": "<script>x</script>"}],
    )
    assert "<b>XI</b>" not in body and "Eagles &lt;b&gt;XI&lt;/b&gt;" in body
    assert "O&#x27;Brien &amp; Sons" in body
    assert "<script>" not in body
