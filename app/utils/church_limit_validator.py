"""
Church availability (one team per church).

The one-team-per-church rule itself is enforced in the registration route
(pre-upload SELECT) and by the UNIQUE index uq_registered_team_church on
teams.church_name_normalized. This module only reports availability.
"""

import logging
from typing import Dict, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from config.churches import normalize_church_name, parse_church_list
from config.settings import settings
from models import Team

logger = logging.getLogger(__name__)

MAX_TEAMS_PER_CHURCH = 1


def configured_churches() -> List[str]:
    """Church names from settings.CHURCH_LIST, spelled exactly as configured."""
    return parse_church_list(settings.CHURCH_LIST)


async def get_church_availability(db: AsyncSession) -> List[Dict]:
    """
    One row per name in settings.CHURCH_LIST (including churches with no team).

    Teams are counted by church_name_normalized, so a team stored with
    different casing or spacing still counts against its configured church.
    church_name is returned exactly as spelled in CHURCH_LIST.
    """
    result = await db.execute(
        select(Team.church_name_normalized, func.count(Team.id)).group_by(Team.church_name_normalized)
    )
    counts = {normalized: int(count) for normalized, count in result.all() if normalized}

    names = configured_churches()
    if not names:
        # No configured list: fall back to the churches that have registrations.
        rows = await db.execute(select(Team.church_name, Team.church_name_normalized))
        names = sorted({church for church, _ in rows.all()})

    churches = []
    for name in names:
        team_count = counts.get(normalize_church_name(name), 0)
        churches.append({
            "church_name": name,
            "team_count": team_count,
            "locked": team_count >= MAX_TEAMS_PER_CHURCH,
        })
    return churches
