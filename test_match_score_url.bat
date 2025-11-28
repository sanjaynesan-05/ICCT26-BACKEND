@echo off
REM Match Score URL Feature - Testing Commands for Windows
REM Quick reference for curl commands to test the new endpoint

setlocal enabledelayedexpansion

set BASE_URL=http://127.0.0.1:8000/api/schedule
set MATCH_ID=20

echo ======================================================
echo Match Score URL Feature - Windows Testing Commands
echo ======================================================
echo.

REM Test 1: Create a match
echo [1] Creating a new match...
curl -X POST "%BASE_URL%/matches" ^
  -H "Content-Type: application/json" ^
  -d "{\"round\": \"Test Round\", \"round_number\": 100, \"match_number\": 1, \"team1\": \"Team A\", \"team2\": \"Team B\"}" ^
  | findstr /R "match_score_url.*team1.*team2"

echo.
echo.

REM Test 2: Update match score URL
echo [2] Updating match score URL...
curl -X PUT "%BASE_URL%/matches/%MATCH_ID%/score-url" ^
  -H "Content-Type: application/json" ^
  -d "{\"match_score_url\": \"https://example.com/matches/123/scorecard\"}"

echo.
echo.

REM Test 3: Get match and verify URL is saved
echo [3] Fetching match to verify URL is saved...
curl -X GET "%BASE_URL%/matches/%MATCH_ID%" ^
  -H "Content-Type: application/json"

echo.
echo.

REM Test 4: Update URL to a different value
echo [4] Updating URL to a different value...
curl -X PUT "%BASE_URL%/matches/%MATCH_ID%/score-url" ^
  -H "Content-Type: application/json" ^
  -d "{\"match_score_url\": \"https://cricketlive.com/match/456/live\"}"

echo.
echo.

REM Test 5: Test invalid URL (should fail with 422)
echo [5] Testing invalid URL validation ^(should fail with 422^)...
curl -X PUT "%BASE_URL%/matches/%MATCH_ID%/score-url" ^
  -H "Content-Type: application/json" ^
  -d "{\"match_score_url\": \"not-a-valid-url\"}"

echo.
echo.

REM Test 6: Get all matches
echo [6] Getting all matches...
curl -X GET "%BASE_URL%/matches?limit=3" ^
  -H "Content-Type: application/json"

echo.
echo.

echo ======================================================
echo Testing Complete!
echo ======================================================
echo.
echo API Endpoint: PUT /matches/{id}/score-url
echo Request Format:
echo   {"match_score_url": "https://..."}
echo.
echo Base URL: %BASE_URL%
echo Match ID: %MATCH_ID%
echo.
pause
