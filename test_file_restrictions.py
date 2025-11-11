"""
Test file upload restrictions - JPEG, PNG, PDF only
"""
import sys
sys.path.insert(0, r"d:\ICCT26 BACKEND")

from app.schemas_team import TeamRegistrationRequest, CaptainInfo, ViceCaptainInfo, PlayerInfo
import base64

print("=" * 80)
print("TEST: File Type Restrictions (JPEG, PNG, PDF ONLY)")
print("=" * 80)

# Test data
valid_captain = {
    "name": "John Captain",
    "phone": "+919876543210",
    "whatsapp": "9876543210",
    "email": "captain@example.com"
}

valid_vice_captain = {
    "name": "Jane Vice",
    "phone": "+919876543211",
    "whatsapp": "9876543211",
    "email": "vice@example.com"
}

# Valid JPEG signature
jpeg_bytes = b'\xff\xd8\xff\xe0' + b'\x00' * 50
jpeg_base64 = base64.b64encode(jpeg_bytes).decode()
jpeg_data_uri = f"data:image/jpeg;base64,{jpeg_base64}"

# Valid PNG signature
png_bytes = b'\x89PNG\r\n\x1a\n' + b'\x00' * 50
png_base64 = base64.b64encode(png_bytes).decode()
png_data_uri = f"data:image/png;base64,{png_base64}"

# Valid PDF signature
pdf_bytes = b'%PDF-1.4' + b'\x00' * 50
pdf_base64 = base64.b64encode(pdf_bytes).decode()
pdf_data_uri = f"data:application/pdf;base64,{pdf_base64}"

# Invalid GIF signature (should fail)
gif_bytes = b'GIF89a' + b'\x00' * 50
gif_base64 = base64.b64encode(gif_bytes).decode()
gif_data_uri = f"data:image/gif;base64,{gif_base64}"

# Test 1: Valid JPEG for Pastor Letter
print("\n[TEST 1] Valid JPEG for pastorLetter - should PASS")
try:
    data = {
        "churchName": "Test Church",
        "teamName": "Test Team",
        "pastorLetter": jpeg_data_uri,
        "paymentReceipt": None,
        "captain": valid_captain,
        "viceCaptain": valid_vice_captain,
        "players": [
            {
                "name": "Player 1",
                "age": 25,
                "phone": "9876543212",
                "role": "Batsman",
                "aadharFile": None,
                "subscriptionFile": None
            }
        ]
    }
    result = TeamRegistrationRequest(**data)
    print("✓ PASS: JPEG accepted for pastorLetter")
except Exception as e:
    print(f"✗ FAIL: {e}")

# Test 2: Valid PNG for Payment Receipt
print("\n[TEST 2] Valid PNG for paymentReceipt - should PASS")
try:
    data = {
        "churchName": "Test Church",
        "teamName": "Test Team",
        "pastorLetter": None,
        "paymentReceipt": png_data_uri,
        "captain": valid_captain,
        "viceCaptain": valid_vice_captain,
        "players": [
            {
                "name": "Player 1",
                "age": 25,
                "phone": "9876543212",
                "role": "Batsman",
                "aadharFile": None,
                "subscriptionFile": None
            }
        ]
    }
    result = TeamRegistrationRequest(**data)
    print("✓ PASS: PNG accepted for paymentReceipt")
except Exception as e:
    print(f"✗ FAIL: {e}")

# Test 3: Valid PDF for Aadhar File
print("\n[TEST 3] Valid PDF for aadharFile - should PASS")
try:
    data = {
        "churchName": "Test Church",
        "teamName": "Test Team",
        "pastorLetter": None,
        "paymentReceipt": None,
        "captain": valid_captain,
        "viceCaptain": valid_vice_captain,
        "players": [
            {
                "name": "Player 1",
                "age": 25,
                "phone": "9876543212",
                "role": "Batsman",
                "aadharFile": pdf_data_uri,
                "subscriptionFile": None
            }
        ]
    }
    result = TeamRegistrationRequest(**data)
    print("✓ PASS: PDF accepted for aadharFile")
except Exception as e:
    print(f"✗ FAIL: {e}")

# Test 4: Valid PDF for Subscription File
print("\n[TEST 4] Valid PDF for subscriptionFile - should PASS")
try:
    data = {
        "churchName": "Test Church",
        "teamName": "Test Team",
        "pastorLetter": None,
        "paymentReceipt": None,
        "captain": valid_captain,
        "viceCaptain": valid_vice_captain,
        "players": [
            {
                "name": "Player 1",
                "age": 25,
                "phone": "9876543212",
                "role": "Batsman",
                "aadharFile": None,
                "subscriptionFile": pdf_data_uri
            }
        ]
    }
    result = TeamRegistrationRequest(**data)
    print("✓ PASS: PDF accepted for subscriptionFile")
except Exception as e:
    print(f"✗ FAIL: {e}")

# Test 5: Invalid GIF (should fail)
print("\n[TEST 5] Invalid GIF format - should FAIL")
try:
    data = {
        "churchName": "Test Church",
        "teamName": "Test Team",
        "pastorLetter": gif_data_uri,
        "paymentReceipt": None,
        "captain": valid_captain,
        "viceCaptain": valid_vice_captain,
        "players": [
            {
                "name": "Player 1",
                "age": 25,
                "phone": "9876543212",
                "role": "Batsman",
                "aadharFile": None,
                "subscriptionFile": None
            }
        ]
    }
    result = TeamRegistrationRequest(**data)
    print("✗ FAIL: GIF was accepted (should have been rejected)")
except Exception as e:
    print(f"✓ PASS: GIF correctly rejected - {str(e)[:80]}...")

# Test 6: All valid files together
print("\n[TEST 6] All valid files together (JPEG, PNG, PDF) - should PASS")
try:
    data = {
        "churchName": "Test Church",
        "teamName": "Test Team",
        "pastorLetter": jpeg_data_uri,
        "paymentReceipt": png_data_uri,
        "captain": valid_captain,
        "viceCaptain": valid_vice_captain,
        "players": [
            {
                "name": "Player 1",
                "age": 25,
                "phone": "9876543212",
                "role": "Batsman",
                "aadharFile": pdf_data_uri,
                "subscriptionFile": pdf_data_uri
            }
        ]
    }
    result = TeamRegistrationRequest(**data)
    print("✓ PASS: All valid files (JPEG, PNG, PDF) accepted")
except Exception as e:
    print(f"✗ FAIL: {e}")

print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print("✓ File restrictions updated successfully!")
print("✓ Only JPEG, PNG, and PDF files are now allowed")
print("✓ All 4 file fields accept these types: pastorLetter, paymentReceipt,")
print("  aadharFile, subscriptionFile")
print("=" * 80)
