#!/bin/bash
# Quick API Testing Script for ICCT26 Backend
# Usage: bash test_quick.sh

BASE_URL="https://icct26-backend.onrender.com"

echo "========================================"
echo "ICCT26 Backend - Quick API Test"
echo "URL: $BASE_URL"
echo "========================================"
echo ""

# Test 1: Health Check
echo "Test 1: Health Check"
echo "GET $BASE_URL/health"
curl -s "$BASE_URL/health" | python -m json.tool 2>/dev/null || echo "❌ Failed to connect"
echo ""

# Test 2: Get Home
echo "Test 2: Home Endpoint"
echo "GET $BASE_URL/"
curl -s "$BASE_URL/" | head -5
echo ""

# Test 3: Get All Teams
echo "Test 3: Get All Teams"
echo "GET $BASE_URL/admin/teams"
curl -s "$BASE_URL/admin/teams" | python -m json.tool 2>/dev/null | head -30
echo ""

# Test 4: Status
echo "Test 4: Server Status"
echo "GET $BASE_URL/status"
curl -s "$BASE_URL/status" | python -m json.tool 2>/dev/null
echo ""

echo "========================================"
echo "Quick tests completed"
echo "========================================"
