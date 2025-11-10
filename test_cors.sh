#!/bin/bash
# CORS Testing Script for ICCT26 Backend
# Tests CORS headers from the API endpoint

API_URL="${1:-https://icct26-backend.onrender.com}"
FRONTEND_URL="https://icct26.netlify.app"

echo "=========================================="
echo "🧪 CORS Testing Script"
echo "=========================================="
echo "Testing: $API_URL"
echo "From: $FRONTEND_URL"
echo "==========================================" 
echo ""

# Test function
test_cors() {
    local method=$1
    local endpoint=$2
    local description=$3
    
    echo "Testing: $method $endpoint"
    echo "Description: $description"
    echo ""
    
    if [ "$method" = "GET" ]; then
        curl -i \
            -X GET \
            -H "Origin: $FRONTEND_URL" \
            -H "Content-Type: application/json" \
            "$API_URL$endpoint" 2>/dev/null | head -20
    elif [ "$method" = "POST" ]; then
        curl -i \
            -X OPTIONS \
            -H "Origin: $FRONTEND_URL" \
            -H "Access-Control-Request-Method: POST" \
            -H "Access-Control-Request-Headers: content-type" \
            "$API_URL$endpoint" 2>/dev/null | head -20
    fi
    
    echo ""
    echo "=================================================="
    echo ""
}

# Test endpoints
test_cors "GET" "/" "API Root"
test_cors "GET" "/health" "Health Check"
test_cors "GET" "/status" "API Status"
test_cors "GET" "/api/teams" "List Teams"
test_cors "POST" "/api/register/team" "Register Team (preflight)"
test_cors "GET" "/admin/teams" "Admin Teams"

echo "✅ CORS test completed"
echo ""
echo "If you see 'Access-Control-Allow-Origin: https://icct26.netlify.app'"
echo "in the response headers, CORS is working correctly!"
