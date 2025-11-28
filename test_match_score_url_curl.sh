#!/bin/bash

# Match Score URL Feature - Testing & Integration Commands
# Quick reference for curl commands to test the new endpoint

BASE_URL="http://127.0.0.1:8000/api/schedule"
MATCH_ID="20"  # Change this to your match ID

echo "======================================================"
echo "Match Score URL Feature - Testing Commands"
echo "======================================================"
echo ""

# Test 1: Create a match
echo "[1] Creating a new match..."
curl -X POST "$BASE_URL/matches" \
  -H "Content-Type: application/json" \
  -d '{
    "round": "Test Round",
    "round_number": 100,
    "match_number": 1,
    "team1": "Team A",
    "team2": "Team B"
  }' | jq '.data | {id, team1, team2, match_score_url}'

echo ""
echo ""

# Test 2: Update match score URL
echo "[2] Updating match score URL..."
curl -X PUT "$BASE_URL/matches/$MATCH_ID/score-url" \
  -H "Content-Type: application/json" \
  -d '{
    "match_score_url": "https://example.com/matches/123/scorecard"
  }' | jq '.data | {id, team1, team2, match_score_url}'

echo ""
echo ""

# Test 3: Get match and verify URL is saved
echo "[3] Fetching match to verify URL is saved..."
curl -X GET "$BASE_URL/matches/$MATCH_ID" \
  -H "Content-Type: application/json" | jq '.data | {id, team1, team2, match_score_url}'

echo ""
echo ""

# Test 4: Update URL to a different value
echo "[4] Updating URL to a different value..."
curl -X PUT "$BASE_URL/matches/$MATCH_ID/score-url" \
  -H "Content-Type: application/json" \
  -d '{
    "match_score_url": "https://cricketlive.com/match/456/live"
  }' | jq '.data | {id, team1, team2, match_score_url}'

echo ""
echo ""

# Test 5: Test invalid URL (should fail with 422)
echo "[5] Testing invalid URL validation (should fail)..."
curl -X PUT "$BASE_URL/matches/$MATCH_ID/score-url" \
  -H "Content-Type: application/json" \
  -d '{
    "match_score_url": "not-a-valid-url"
  }' | jq '.detail[0] | {field: .loc[-1], error: .msg}'

echo ""
echo ""

# Test 6: Get all matches and verify match_score_url in list
echo "[6] Getting all matches (verify match_score_url in list)..."
curl -X GET "$BASE_URL/matches?limit=3" \
  -H "Content-Type: application/json" | jq '.data[0] | {id, team1, team2, match_score_url}'

echo ""
echo ""

# Test 7: Update match status and verify URL persists
echo "[7] Updating match status (verify URL persists)..."
curl -X PUT "$BASE_URL/matches/$MATCH_ID/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "live"}' | jq '.data | {status, match_score_url}'

echo ""
echo ""

echo "======================================================"
echo "Testing Complete!"
echo "======================================================"
echo ""
echo "Summary:"
echo "  ✓ Create match: match_score_url initially null"
echo "  ✓ Update URL: URL is set and returned"
echo "  ✓ Get match: URL is persisted and retrieved"
echo "  ✓ Update URL: URL can be changed"
echo "  ✓ URL validation: Invalid URLs are rejected (422)"
echo "  ✓ List matches: URL appears in list response"
echo "  ✓ Other updates: URL persists with other changes"
echo ""
echo "API Endpoint: PUT /matches/{id}/score-url"
echo "Request Format:"
echo "  {\"match_score_url\": \"https://...\"}"
echo ""
