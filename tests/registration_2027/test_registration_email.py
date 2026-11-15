"""Content of the "registration received" email (no database needed)."""

from app.utils.email_reliable import create_registration_email

CAPTAIN = {"name": "John Samuel", "phone": "9876543210", "email": "captain@example.com", "whatsapp": None}
VICE = {"name": "Peter O'Neil", "phone": "9876543211", "email": "vice@example.com", "whatsapp": "9876543212"}
PLAYERS = ["Zed Last", "Aaron First", "Mike Middle"] + [f"Player {chr(65 + i)}lpha" for i in range(10)]


def render(**over):
    args = dict(team_name="Airport Eagles", team_id="ICCT-007", church_name="CSI Church Airport",
                captain=CAPTAIN, vice_captain=VICE, players=PLAYERS)
    args.update(over)
    return create_registration_email(**args)


def test_email_has_team_id_captain_and_vice_details():
    html = render()
    assert "ICCT-007" in html and "Airport Eagles" in html and "CSI Church Airport" in html
    for value in ("John Samuel", "9876543210", "captain@example.com",
                  "Peter O&#x27;Neil", "9876543211", "vice@example.com", "9876543212"):
        assert value in html, value
    assert html.count("WhatsApp") == 1  # captain had none, so only the vice row shows it


def test_players_listed_in_registration_order_with_ids():
    html = render()
    positions = [html.index(f">{name}<") for name in PLAYERS]
    assert positions == sorted(positions)  # not alphabetical: Zed (player 0) comes first
    assert "ICCT-007-P01" in html and "ICCT-007-P13" in html
    assert html.index("ICCT-007-P01") > html.index(">Zed Last<")


def test_user_values_are_escaped():
    html = render(team_name="<b>x</b>", players=["<script>alert(1)</script>"] * 13)
    assert "<script>" not in html and "&lt;script&gt;" in html
    assert "<b>x</b>" not in html


def test_html_email_is_sent_as_html_with_text_fallback(monkeypatch):
    """Regression: <html lang="en"> was not detected and the email arrived as raw code."""
    import asyncio
    from app.utils import email_reliable

    sent = []

    class FakeSMTP:
        def __init__(self, *a, **k): pass
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def starttls(self): pass
        def login(self, *a): pass
        def send_message(self, msg): sent.append(msg)

    monkeypatch.setattr(email_reliable.smtplib, "SMTP", FakeSMTP)
    monkeypatch.setattr(type(email_reliable.settings), "SMTP_ENABLED", property(lambda self: True))

    asyncio.run(email_reliable._send_sync_in_executor("x@example.com", "Subject", render()))

    msg = sent[0]
    assert msg.get_content_type() == "multipart/alternative"
    parts = msg.get_payload()
    assert [p.get_content_type() for p in parts] == ["text/plain", "text/html"]  # HTML last = preferred
    assert parts[1].get_content_charset() == "utf-8"
    plain = parts[0].get_payload(decode=True).decode("utf-8")
    assert "<table" not in plain and "ICCT-007" in plain and "Zed Last" in plain
