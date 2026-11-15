"""
Church list and church-name normalization for ICCT registrations.

CHURCH_NAMES mirrors `const CHURCH_NAMES` in the frontend
(ICCT26/src/pages/Registration.tsx). The frontend matches availability rows by
exact string equality, so spellings here must stay identical to that list.

normalize_church_name() is the single normalization rule used by the
registration route, the availability endpoint and scripts/migrate_2027.py.
This module deliberately has no database or framework imports so the
migration script can use it standalone.
"""

from typing import Iterable, List


def normalize_church_name(name: str) -> str:
    """Collapse all whitespace runs to one space, trim, and casefold."""
    return " ".join((name or "").split()).casefold()


def parse_church_list(raw: str) -> List[str]:
    """Split a comma-separated CHURCH_LIST into display names (whitespace collapsed)."""
    return [" ".join(part.split()) for part in (raw or "").split(",") if part.strip()]


def build_church_lookup(names: Iterable[str]) -> dict:
    """Map normalized name -> configured display spelling."""
    return {normalize_church_name(name): name for name in names}


CHURCH_NAMES: List[str] = [
    "CSI St Peters Church Rathinapuri",
    "CSI Immanuel Church Coimbatore",
    "CSI Christ Church Trichy Road",
    "CSI Christ Church Gandhipuram",
    "CSI All Souls Church Race Course",
    "CSI Ramanathapuram Pastorate",
    "CSI Christ Church NGGO Colony",
    "CSI Christ Church TVS Nagar",
    "CSI Christ Church Madukkarai",
    "CSI Christ Church Police Quarters",
    "CSI Christ Church Sundarapuram",
    "CSI Christ Church Kovaipudur",
    "CSI Singanallur Pastorate",
    "CSI Ondipudur Pastorate",
    "CSI Sowripalayam Pastorate",
    "CSI Varadarajapuram Pastorate",
    "CSI Good Shepherd Church Cheran Ma Nagar",
    "CSI Union Church Podanur",
    "CSI Addis Pastorate",
    "CSI Kavundampalayam Pastorate",
    "CSI Holy Redeemers Church SB Colony",
    "CSI Pollachi Pastorate",
    "CSI Perur Pastorate",
    "CSI Vadavalli Pastorate",
    "CSI Christ Church Mathuvarayapuram",
    "CSI Malumichampatti Pastorate",
    "CSI Visuvasapuram Pastorate",
    "CSI Church Airport",
    "CSI Saint Marks Church Podanur",
    "CSI Church Irugur",
    "CSI Chettipalayam Pastorate",
    "CSI New Mullai Nagar Pastorate",
    "CSI Pattanam Pastorate",
    "CSI Wals Memorial Church Thadagam",
    "CSI Saint Pauls Church Tirupur",
    "CSI Saint Lukes Church Tirupur",
    "CSI Tirupur Rural Pastorate",
    "CSI Pitchampalayam Pastorate",
    "CSI Church Peruntholuvu",
    "CSI Church Nallur",
    "CSI Christ Church Press Colony",
    "CSI Sirumugai Pastorate",
    "CSI Mettupalayam Pastorate",
    "CSI Karamadai Pastorate",
    "CSI Christ Church Somanur",
    "CSI Sulur Pastorate",
    "CSI Annur Pastorate",
    "CSI Avinashi Pastorate",
    "CSI Kaniyur Mooperipalayam Pastorate",
    "CSI Church Nambiyur Kedarai",
    "CSI Perumanallur Kunnathur Pastorate",
    "CSI Saint Johns Church Palladam",
    "CSI Annur Rural Pastorate",
    "CSI Iduvai Divine Nagar Pastorate",
    "CSI Church Chinniampalayam",
    "CSI Gudalur Pastorate",
    "CSI Devarshola Pastorate",
    "CSI Pandalur Pastorate",
    "CSI Masinagudi Pastorate",
    "CSI Naduvattam Pastorate",
    "CSI Holy Trinity Church Ooty",
    "CSI Lovedale Pastorate",
    "CSI Saint Stephens Church Ooty",
    "CSI Wesley Church Ooty",
    "CSI Wesley Church Ketti",
    "CSI Saint Georges Church Wellington",
    "CSI Aruvankadu Pastorate",
    "CSI Selas Pastorate",
    "CSI Kundha Pastorate",
    "CSI Hulical Pastorate",
    "CSI Nonsuch Pastorate",
    "CSI Wesley Church Coonoor",
    "CSI Saint Johns Church Coonoor",
    "CSI All Saints Church Coonoor",
    "CSI Kullakamby Pastorate",
    "CSI Adderley Pastorate",
    "CSI Saint Lukes Church Kotagiri",
    "CSI Wesley Church Kotagiri",
    "CSI Masakkal And Thanthanadu",
    "CSI Burnside Pastorate",
    "CSI Kil Kotagiri Pastorate",
    "CSI Milidhane Pastorate",
]
