"""
Simple Team Registration Test with Dummy URLs and Extended Timeout
==================================================================
Tests team registration with dummy file URLs (no actual cloud uploads).
Focus: Team ID generation and database storage.
"""

import asyncio
import httpx
import logging
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# 11 Players
PLAYERS = [
    ("John Michael", "Batsman"),
    ("David Thomas", "Bowler"),
    ("Matthew Joseph", "All-Rounder"),
    ("Samuel Peter", "Wicket-Keeper"),
    ("James Abraham", "Batsman"),
    ("Andrew Isaac", "Bowler"),
    ("Philip Jacob", "All-Rounder"),
    ("Thomas Daniel", "Batsman"),
    ("Simon Paul", "Bowler"),
    ("Stephen Mark", "All-Rounder"),
    ("Luke George", "Batsman"),
]


def create_dummy_pdf():
    """Create minimal valid PDF content"""
    return b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
trailer
<< /Size 4 /Root 1 0 R >>
startxref
213
%%EOF
"""


def create_dummy_png():
    """Create minimal valid PNG"""
    return bytes.fromhex(
        '89504e470d0a1a0a0000000d494844520000000100000001'
        '08060000001f15c4890000000a49444154789c630001000005'
        '0001028d05390f0e0000000049454e44ae426082'
    )


async def test():
    """Test team registration with dummy URLs"""
    logger.info("")
    logger.info("=" * 70)
    logger.info("🏏 TEAM REGISTRATION TEST (DUMMY URLs, EXTENDED TIMEOUT)")
    logger.info("=" * 70)
    logger.info("")
    
    pdf = create_dummy_pdf()
    png = create_dummy_png()
    
    # Build file list
    files = [
        ("pastor_letter", ("pastor_letter.pdf", pdf, "application/pdf")),
        ("payment_receipt", ("payment_receipt.pdf", pdf, "application/pdf")),
        ("group_photo", ("group_photo.png", png, "image/png")),
    ]
    
    # Add player files
    for idx in range(11):
        files.append((f"player_{idx}_aadhar_file", (f"aadhar_{idx}.pdf", pdf, "application/pdf")))
        files.append((f"player_{idx}_subscription_file", (f"subs_{idx}.pdf", pdf, "application/pdf")))
    
    # Form data
    form_data = {
        "team_name": "St Thomas Cricket Club",
        "church_name": "St Thomas Orthodox Church",
        "captain_name": "John Michael",
        "captain_phone": "9876543210",
        "captain_email": "john@example.com",
        "captain_whatsapp": "9876543210",
        "vice_name": "David Thomas",
        "vice_phone": "9876543211",
        "vice_email": "david@example.com",
        "vice_whatsapp": "9876543211",
    }
    
    # Add players
    for idx, (name, role) in enumerate(PLAYERS):
        form_data[f"player_{idx}_name"] = name
        form_data[f"player_{idx}_role"] = role
    
    logger.info(f"📋 Team: {form_data['team_name']}")
    logger.info(f"👤 Captain: {form_data['captain_name']}")
    logger.info(f"👥 Players: 11")
    logger.info(f"📄 Files: {len(files)}")
    logger.info("")
    logger.info("🚀 Submitting registration (timeout: 120 seconds)...")
    logger.info("")
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "http://localhost:8000/api/register/team",
                data=form_data,
                files=files,
            )
            
            logger.info(f"Response Status: {response.status_code}")
            logger.info("")
            
            if response.status_code in [200, 201]:
                data = response.json()
                logger.info("✅ REGISTRATION SUCCESSFUL!")
                logger.info("")
                logger.info(json.dumps(data, indent=2))
                return True
            else:
                logger.info(f"Response: {response.text[:500]}")
                return False
            
    except Exception as e:
        logger.error(f"Error: {type(e).__name__}: {e}")
        return False


if __name__ == "__main__":
    import sys
    success = asyncio.run(test())
    logger.info("")
    logger.info("=" * 70)
    if success:
        logger.info("✅ TEST PASSED!")
    else:
        logger.info("❌ TEST FAILED")
    logger.info("=" * 70)
    sys.exit(0 if success else 1)
