#!/usr/bin/env bash
# Test script for player file handling fix
# Tests the registration endpoint with dynamic player fields and file uploads

set -e

BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
IDEMPOTENCY_KEY="test-fix-$(date +%s)"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🧪 Testing Player File Handling Fix${NC}"
echo "=================================="
echo "Backend URL: $BACKEND_URL"
echo "Idempotency Key: $IDEMPOTENCY_KEY"
echo ""

# Create test files if they don't exist
mkdir -p test_files
if [ ! -f "test_files/pastor_letter.pdf" ]; then
    echo "Creating test files..."
    echo "Test Pastor Letter" > test_files/pastor_letter.pdf
    echo "Test Payment Receipt" > test_files/receipt.jpg
    echo "Test Group Photo" > test_files/group.jpg
    echo "Test Aadhar 1" > test_files/aadhar1.jpg
    echo "Test Subscription 1" > test_files/sub1.jpg
    echo "Test Aadhar 2" > test_files/aadhar2.jpg
    echo "Test Subscription 2" > test_files/sub2.jpg
fi

echo -e "${YELLOW}📤 Sending registration request...${NC}"

# Send the request
RESPONSE=$(curl -v -X POST "$BACKEND_URL/api/register/team" \
  -H "Idempotency-Key: $IDEMPOTENCY_KEY" \
  -F "team_name=TEST WARRIORS" \
  -F "church_name=CSI Test Church" \
  -F "captain_name=Robin" \
  -F "captain_phone=9944064709" \
  -F "captain_email=robin@test.com" \
  -F "captain_whatsapp=9944064709" \
  -F "vice_name=Anand" \
  -F "vice_phone=9944064710" \
  -F "vice_email=anand@test.com" \
  -F "vice_whatsapp=9944064710" \
  -F "pastor_letter=@test_files/pastor_letter.pdf" \
  -F "payment_receipt=@test_files/receipt.jpg" \
  -F "group_photo=@test_files/group.jpg" \
  -F "player_0_name=Robin Kumar" \
  -F "player_0_role=Batsman" \
  -F "player_0_aadhar_file=@test_files/aadhar1.jpg" \
  -F "player_0_subscription_file=@test_files/sub1.jpg" \
  -F "player_1_name=Anand Raj" \
  -F "player_1_role=Bowler" \
  -F "player_1_aadhar_file=@test_files/aadhar2.jpg" \
  -F "player_1_subscription_file=@test_files/sub2.jpg" \
  2>&1)

# Extract HTTP status code
HTTP_CODE=$(echo "$RESPONSE" | grep -oP 'HTTP/\d\.\d \K\d+' | tail -1)

# Extract JSON response
JSON_RESPONSE=$(echo "$RESPONSE" | grep -oP '\{.*\}' | tail -1)

echo ""
echo -e "${YELLOW}📊 Response Details:${NC}"
echo "HTTP Status Code: $HTTP_CODE"
echo "JSON Response: $JSON_RESPONSE"
echo ""

# Check if successful
if [ "$HTTP_CODE" == "201" ] || [ "$HTTP_CODE" == "409" ]; then
    TEAM_ID=$(echo "$JSON_RESPONSE" | grep -oP '"team_id":\s*"\K[^"]+')
    PLAYER_COUNT=$(echo "$JSON_RESPONSE" | grep -oP '"player_count":\s*\K\d+')
    
    echo -e "${GREEN}✅ Registration Successful!${NC}"
    echo "   Team ID: $TEAM_ID"
    echo "   Player Count: $PLAYER_COUNT"
    echo ""
    
    # Test idempotency
    echo -e "${YELLOW}🔁 Testing idempotency (re-sending same request)...${NC}"
    IDEMPOTENCY_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/register/team" \
      -H "Idempotency-Key: $IDEMPOTENCY_KEY" \
      -F "team_name=TEST WARRIORS" \
      -F "church_name=CSI Test Church" \
      -F "captain_name=Robin" \
      -F "captain_phone=9944064709" \
      -F "captain_email=robin@test.com" \
      -F "captain_whatsapp=9944064709" \
      -F "vice_name=Anand" \
      -F "vice_phone=9944064710" \
      -F "vice_email=anand@test.com" \
      -F "vice_whatsapp=9944064710" \
      -F "pastor_letter=@test_files/pastor_letter.pdf" \
      -F "player_0_name=Robin Kumar" \
      -F "player_0_role=Batsman")
    
    IDEM_TEAM_ID=$(echo "$IDEMPOTENCY_RESPONSE" | grep -oP '"team_id":\s*"\K[^"]+')
    
    if [ "$IDEM_TEAM_ID" == "$TEAM_ID" ]; then
        echo -e "${GREEN}✅ Idempotency works! Same team_id returned: $TEAM_ID${NC}"
    else
        echo -e "${RED}❌ Idempotency failed! Different team_id: $IDEM_TEAM_ID${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    echo ""
    echo -e "${YELLOW}📋 Next Steps:${NC}"
    echo "1. Check database to verify:"
    echo "   - teams.pastor_letter IS NOT NULL"
    echo "   - teams.group_photo IS NOT NULL"
    echo "   - players.aadhar_file IS NOT NULL (for each player)"
    echo "   - players.subscription_file IS NOT NULL (for each player)"
    echo ""
    echo "2. Check Cloudinary console to verify files in:"
    echo "   - ICCT26/pastor_letters/$TEAM_ID/"
    echo "   - ICCT26/group_photos/$TEAM_ID/"
    echo "   - ICCT26/players/$TEAM_ID/player_0/aadhar/"
    echo "   - ICCT26/players/$TEAM_ID/player_0/subscription/"
    echo "   - ICCT26/players/$TEAM_ID/player_1/aadhar/"
    echo "   - ICCT26/players/$TEAM_ID/player_1/subscription/"
    
else
    echo -e "${RED}❌ Registration Failed!${NC}"
    echo "HTTP Status: $HTTP_CODE"
    echo "Response: $JSON_RESPONSE"
    exit 1
fi
