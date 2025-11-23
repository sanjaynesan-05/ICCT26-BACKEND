@echo off
REM Gallery Backend Testing Script
REM Tests all gallery endpoints using curl

setlocal enabledelayedexpansion
set BASE_URL=http://127.0.0.1:8000
set PASSED=0
set FAILED=0

echo.
echo ======================================================================
echo   GALLERY BACKEND TEST SUITE
echo ======================================================================
echo.
echo Base URL: %BASE_URL%
echo Timestamp: %date% %time%
echo.

REM Test 1: Health Check
echo Test 1: Gallery Health Check
echo ======================================================================
curl -s -X GET "%BASE_URL%/api/gallery/health" -w "\nStatus Code: %%{http_code}\n" -H "Content-Type: application/json"
echo.

REM Test 2: Get Gallery Images
echo Test 2: Get Gallery Images (limit=5)
echo ======================================================================
curl -s -X GET "%BASE_URL%/api/gallery/ICCT26/Gallery/images?limit=5&skip=0" -w "\nStatus Code: %%{http_code}\n" -H "Content-Type: application/json"
echo.

REM Test 3: Download Single (with sample public_id)
echo Test 3: Download Single Image
echo ======================================================================
curl -s -X POST "%BASE_URL%/api/gallery/download/single" ^
  -H "Content-Type: application/json" ^
  -d "{\"public_id\": \"ICCT26/Gallery/test\"}" ^
  -w "\nStatus Code: %%{http_code}\n"
echo.

REM Test 4: Download Bulk (with sample public_ids)
echo Test 4: Download Bulk Images
echo ======================================================================
curl -s -X POST "%BASE_URL%/api/gallery/download/bulk" ^
  -H "Content-Type: application/json" ^
  -d "{\"public_ids\": [\"ICCT26/Gallery/test1\", \"ICCT26/Gallery/test2\"]}" ^
  -w "\nStatus Code: %%{http_code}\n"
echo.

echo ======================================================================
echo   TEST COMPLETE
echo ======================================================================
echo.
