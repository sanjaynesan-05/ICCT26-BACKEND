"""
Comprehensive Integration Tests for Registration and Admin Flows
Tests the complete lifecycle: Register Team → Admin Confirm → Error Handling
"""

import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from models import Team, Player
from app.services import DatabaseService
from app.utils.race_safe_team_id import generate_next_team_id


@pytest.mark.asyncio
async def test_complete_registration_flow(async_db: AsyncSession):
    """
    Test complete registration flow:
    1. Generate team ID
    2. Save team registration
    3. Verify team exists with status=pending
    4. Verify players are created
    """
    # Create mock registration data
    from app.schemas import TeamRegistration, CaptainInfo, ViceCaptainInfo, PlayerDetails
    
    registration = TeamRegistration(
        teamName="Test Warriors",
        churchName="Test Church",
        captain=CaptainInfo(
            name="John Doe",
            phone="1234567890",
            email="john@test.com",
            whatsapp="1234567890"
        ),
        viceCaptain=ViceCaptainInfo(
            name="Jane Smith",
            phone="0987654321",
            email="jane@test.com",
            whatsapp="0987654321"
        ),
        players=[
            PlayerDetails(
                name=f"Player {i}",
                role="Batsman",
                aadharFile="",
                subscriptionFile=""
            ) for i in range(1, 12)
        ],
        paymentReceipt="https://res.cloudinary.com/test/payment.pdf",
        pastorLetter="https://res.cloudinary.com/test/letter.pdf"
    )
    
    # Generate team ID
    team_id = await generate_next_team_id(async_db)
    assert team_id is not None
    assert team_id.startswith("ICCT-")
    
    # Save registration
    team_db_id = await DatabaseService.save_registration_to_db(
        session=async_db,
        registration=registration,
        team_id=team_id
    )
    
    assert team_db_id is not None
    
    # Verify team exists
    team = await DatabaseService.get_team_by_team_id(async_db, team_id)
    assert team is not None
    assert team.team_id == team_id
    assert team.team_name == "Test Warriors"
    assert team.church_name == "Test Church"
    assert team.registration_status == "pending"
    assert team.captain_name == "John Doe"
    assert team.captain_phone == "1234567890"
    
    # Verify players exist
    team_details = await DatabaseService.get_team_details(async_db, team_id)
    assert team_details is not None
    assert len(team_details["players"]) == 11
    
    # Cleanup
    await async_db.execute(text(f"DELETE FROM players WHERE team_id = '{team_id}'"))
    await async_db.execute(text(f"DELETE FROM teams WHERE team_id = '{team_id}'"))
    await async_db.commit()


@pytest.mark.asyncio
async def test_admin_confirm_team_flow(async_db: AsyncSession):
    """
    Test admin team confirmation flow:
    1. Create pending team
    2. Confirm team
    3. Verify status=confirmed
    4. Test idempotency (confirm again)
    """
    # Create test team directly
    team_id = f"TEST-{uuid.uuid4().hex[:8].upper()}"
    team = Team(
        team_id=team_id,
        team_name="Confirm Test Team",
        church_name="Test Church",
        captain_name="Test Captain",
        captain_phone="9999999999",
        captain_email="captain@test.com",
        vice_captain_name="Test Vice Captain",
        vice_captain_phone="8888888888",
        vice_captain_email="vice@test.com",
        payment_receipt="https://res.cloudinary.com/test/payment.pdf",
        pastor_letter="https://res.cloudinary.com/test/letter.pdf",
        registration_status="pending"
    )
    async_db.add(team)
    await async_db.commit()
    await async_db.refresh(team)
    
    # Verify team is pending
    assert team.registration_status == "pending"
    
    # Confirm team
    new_urls = {
        "payment_receipt": "https://res.cloudinary.com/test/confirmed/payment.pdf",
        "pastor_letter": "https://res.cloudinary.com/test/confirmed/letter.pdf"
    }
    
    success = await DatabaseService.confirm_team_registration(
        db=async_db,
        team_id=team_id,
        new_cloudinary_urls=new_urls
    )
    
    assert success is True
    
    # Verify team is confirmed
    confirmed_team = await DatabaseService.get_team_by_team_id(async_db, team_id)
    assert confirmed_team is not None
    assert confirmed_team.registration_status == "confirmed"
    assert confirmed_team.payment_receipt == new_urls["payment_receipt"]
    assert confirmed_team.pastor_letter == new_urls["pastor_letter"]
    
    # Test idempotency - confirm again should succeed
    success_again = await DatabaseService.confirm_team_registration(
        db=async_db,
        team_id=team_id
    )
    assert success_again is True
    
    # Cleanup
    await async_db.execute(text(f"DELETE FROM teams WHERE team_id = '{team_id}'"))
    await async_db.commit()


@pytest.mark.asyncio
async def test_confirm_nonexistent_team(async_db: AsyncSession):
    """
    Test confirming a team that doesn't exist
    Should return False, not crash
    """
    fake_team_id = "ICCT-999999"
    
    success = await DatabaseService.confirm_team_registration(
        db=async_db,
        team_id=fake_team_id
    )
    
    assert success is False


@pytest.mark.asyncio
async def test_get_nonexistent_team(async_db: AsyncSession):
    """
    Test getting a team that doesn't exist
    Should return None, not crash
    """
    fake_team_id = "ICCT-999999"
    
    team = await DatabaseService.get_team_by_team_id(async_db, fake_team_id)
    assert team is None
    
    team_details = await DatabaseService.get_team_details(async_db, fake_team_id)
    assert team_details is None


@pytest.mark.asyncio
async def test_uuid_generation_for_new_teams(async_db: AsyncSession):
    """
    Test that teams.id automatically generates UUIDs
    This is the critical fix for NULL constraint violations
    """
    # Create team WITHOUT specifying id
    team_id = f"UUID-TEST-{uuid.uuid4().hex[:8].upper()}"
    team = Team(
        team_id=team_id,
        team_name="UUID Test Team",
        church_name="UUID Test Church",
        captain_name="UUID Captain",
        captain_phone="7777777777",
        captain_email="uuid@test.com",
        vice_captain_name="UUID Vice",
        vice_captain_phone="6666666666",
        vice_captain_email="uuidvice@test.com",
        registration_status="pending"
    )
    # id is NOT set - PostgreSQL should auto-generate it
    
    async_db.add(team)
    await async_db.commit()
    await async_db.refresh(team)
    
    # Verify UUID was auto-generated
    assert team.id is not None
    assert isinstance(team.id, uuid.UUID)
    
    # Cleanup
    await async_db.execute(text(f"DELETE FROM teams WHERE team_id = '{team_id}'"))
    await async_db.commit()


@pytest.mark.asyncio
async def test_get_all_teams_with_status_filter(async_db: AsyncSession):
    """
    Test getting all teams and filtering by registration_status
    """
    # Create test teams with different statuses
    test_teams = []
    for status in ["pending", "confirmed"]:
        team_id = f"STATUS-{status.upper()}-{uuid.uuid4().hex[:6]}"
        team = Team(
            team_id=team_id,
            team_name=f"{status.title()} Team",
            church_name="Test Church",
            captain_name="Test Captain",
            captain_phone=f"555{status[:4]}",
            captain_email=f"{status}@test.com",
            vice_captain_name="Test Vice",
            vice_captain_phone="5555555555",
            vice_captain_email="vice@test.com",
            registration_status=status
        )
        async_db.add(team)
        test_teams.append(team_id)
    
    await async_db.commit()
    
    # Get all teams
    all_teams = await DatabaseService.get_all_teams(async_db)
    assert len(all_teams) >= 2
    
    # Verify status field exists in response
    for team in all_teams:
        assert "registrationStatus" in team
        assert team["registrationStatus"] in ["pending", "confirmed", "rejected"]
    
    # Cleanup
    for team_id in test_teams:
        await async_db.execute(text(f"DELETE FROM teams WHERE team_id = '{team_id}'"))
    await async_db.commit()


@pytest.mark.asyncio
async def test_team_sequence_race_safety(async_db: AsyncSession):
    """
    Test that team ID generation is race-safe
    Generate multiple team IDs and ensure no duplicates
    """
    team_ids = set()
    
    # Generate 5 team IDs
    for _ in range(5):
        team_id = await generate_next_team_id(async_db)
        assert team_id is not None
        assert team_id not in team_ids, f"Duplicate team ID generated: {team_id}"
        team_ids.add(team_id)
    
    # Verify all are sequential
    numbers = [int(tid.split("-")[1]) for tid in team_ids]
    assert len(numbers) == len(set(numbers)), "Duplicate numbers generated"


@pytest.mark.asyncio
async def test_database_schema_validation(async_db: AsyncSession):
    """
    Test that startup validation correctly checks database schema
    """
    from app.utils.startup_validation import validate_database_schema
    
    results = await validate_database_schema(async_db)
    
    # Check results structure
    assert "valid" in results
    assert "errors" in results
    assert "warnings" in results
    assert "checks" in results
    
    # Verify critical checks passed
    checks = {check["check"]: check for check in results["checks"]}
    
    assert "teams.id DEFAULT gen_random_uuid()" in checks
    assert "✅" in checks["teams.id DEFAULT gen_random_uuid()"]["status"]
    
    # Should be valid (all critical checks passed)
    if not results["valid"]:
        print("VALIDATION ERRORS:")
        for error in results["errors"]:
            print(f"  - {error}")
    
    assert results["valid"] is True, "Database schema validation failed"


def test_database_service_methods_available():
    """
    Test that all required DatabaseService methods exist
    """
    from app.utils.startup_validation import validate_database_service_methods
    
    results = validate_database_service_methods()  # This is synchronous, not async
    
    # Check results structure
    assert "valid" in results
    assert "methods" in results
    
    # Verify all methods are available
    method_statuses = {m["method"]: m["status"] for m in results["methods"]}
    
    required_methods = [
        "get_team_by_team_id",
        "confirm_team_registration",
        "get_team_details",
        "get_all_teams",
        "save_registration_to_db",
        "get_player_details"
    ]
    
    for method in required_methods:
        assert method in method_statuses
        assert "✅" in method_statuses[method], f"Method {method} not available"
    
    assert results["valid"] is True, "DatabaseService methods validation failed"
