"""
Live Integration Tests for ICCT26 Backend
Tests actual API endpoints with HTTP requests
"""

import requests
import json
import sys

BASE_URL = 'http://localhost:8000'

print('='*80)
print('🌐 ICCT26 BACKEND - LIVE INTEGRATION TESTS')
print('='*80)
print(f'Target: {BASE_URL}')
print('')

# Track results
tests_passed = 0
tests_failed = 0

def test_result(test_name, passed, details=''):
    global tests_passed, tests_failed
    if passed:
        print(f'✅ {test_name} - PASSED')
        if details:
            print(f'   {details}')
    else:
        print(f'❌ {test_name} - FAILED')
        if details:
            print(f'   {details}')
        tests_failed += 1
        return
    tests_passed += 1

# ============================================================================
# TEST SUITE 1: HEALTH AND CONNECTIVITY
# ============================================================================
print('TEST SUITE 1: Health and Connectivity')
print('-'*80)

try:
    response = requests.get(f'{BASE_URL}/', timeout=5)
    passed = response.status_code == 200
    data = response.json()
    details = f"Status: {response.status_code}, Message: {data.get('message', 'N/A')}"
    test_result('Root endpoint health check', passed, details)
except Exception as e:
    test_result('Root endpoint health check', False, f'Error: {str(e)}')

try:
    response = requests.get(f'{BASE_URL}/docs', timeout=5)
    passed = response.status_code == 200
    details = f'Status: {response.status_code}, Content-Type: {response.headers.get("content-type", "N/A")}'
    test_result('API documentation endpoint', passed, details)
except Exception as e:
    test_result('API documentation endpoint', False, f'Error: {str(e)}')

try:
    response = requests.get(f'{BASE_URL}/openapi.json', timeout=5)
    passed = response.status_code == 200
    data = response.json()
    has_info = 'info' in data
    has_paths = 'paths' in data
    details = f'OpenAPI schema valid: {has_info and has_paths}'
    test_result('OpenAPI specification', passed and has_info and has_paths, details)
except Exception as e:
    test_result('OpenAPI specification', False, f'Error: {str(e)}')

print('')

# ============================================================================
# TEST SUITE 2: CORS HEADERS
# ============================================================================
print('TEST SUITE 2: CORS Configuration')
print('-'*80)

try:
    headers = {
        'Origin': 'http://localhost:3000',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'content-type'
    }
    response = requests.options(f'{BASE_URL}/', headers=headers, timeout=5)
    
    cors_origin = response.headers.get('access-control-allow-origin', '')
    cors_methods = response.headers.get('access-control-allow-methods', '')
    cors_credentials = response.headers.get('access-control-allow-credentials', '')
    
    passed = (
        cors_origin == 'http://localhost:3000' and
        cors_credentials.lower() == 'true'
    )
    
    details = f'Origin: {cors_origin}, Credentials: {cors_credentials}'
    test_result('CORS preflight request', passed, details)
except Exception as e:
    test_result('CORS preflight request', False, f'Error: {str(e)}')

try:
    # Test production origin
    headers = {'Origin': 'https://icct26.netlify.app'}
    response = requests.get(f'{BASE_URL}/', headers=headers, timeout=5)
    
    cors_origin = response.headers.get('access-control-allow-origin', '')
    passed = cors_origin == 'https://icct26.netlify.app'
    
    details = f'Production origin allowed: {passed}'
    test_result('CORS production origin', passed, details)
except Exception as e:
    test_result('CORS production origin', False, f'Error: {str(e)}')

try:
    # Test admin origin
    headers = {'Origin': 'https://icct26-admin.vercel.app'}
    response = requests.get(f'{BASE_URL}/', headers=headers, timeout=5)
    
    cors_origin = response.headers.get('access-control-allow-origin', '')
    passed = cors_origin == 'https://icct26-admin.vercel.app'
    
    details = f'Admin origin allowed: {passed}'
    test_result('CORS admin origin', passed, details)
except Exception as e:
    test_result('CORS admin origin', False, f'Error: {str(e)}')

print('')

# ============================================================================
# TEST SUITE 3: ADMIN ENDPOINTS (GET)
# ============================================================================
print('TEST SUITE 3: Admin GET Endpoints')
print('-'*80)

try:
    response = requests.get(f'{BASE_URL}/admin/teams', timeout=15)  # Increased timeout for DB queries
    passed = response.status_code in [200, 404]  # 200 if data exists, 404 if no teams
    
    if response.status_code == 200:
        data = response.json()
        has_data = 'data' in data
        teams_count = len(data.get('data', [])) if has_data else 0
        details = f'Status: {response.status_code}, Has data field: {has_data}, Teams count: {teams_count}'
    else:
        details = f'Status: {response.status_code} (No teams registered yet)'
    
    test_result('GET /admin/teams', passed, details)
except Exception as e:
    test_result('GET /admin/teams', False, f'Error: {str(e)}')

try:
    response = requests.get(f'{BASE_URL}/admin/players', timeout=5)
    passed = response.status_code in [200, 404]
    data = response.json() if response.status_code == 200 else {}
    
    if response.status_code == 200:
        is_list = isinstance(data, list)
        details = f'Status: {response.status_code}, Returns list: {is_list}, Count: {len(data) if is_list else 0}'
    else:
        details = f'Status: {response.status_code} (No players registered yet)'
    
    test_result('GET /admin/players', passed, details)
except Exception as e:
    test_result('GET /admin/players', False, f'Error: {str(e)}')

try:
    response = requests.get(f'{BASE_URL}/admin/payments', timeout=5)
    passed = response.status_code in [200, 404]
    
    if response.status_code == 200:
        data = response.json()
        is_list = isinstance(data, list)
        details = f'Status: {response.status_code}, Returns list: {is_list}, Count: {len(data) if is_list else 0}'
    else:
        details = f'Status: {response.status_code} (No payments recorded yet)'
    
    test_result('GET /admin/payments', passed, details)
except Exception as e:
    test_result('GET /admin/payments', False, f'Error: {str(e)}')

print('')

# ============================================================================
# TEST SUITE 4: ERROR HANDLING
# ============================================================================
print('TEST SUITE 4: Error Handling')
print('-'*80)

try:
    # Test non-existent endpoint
    response = requests.get(f'{BASE_URL}/api/nonexistent', timeout=5)
    passed = response.status_code == 404
    details = f'Status: {response.status_code} (Expected 404)'
    test_result('404 Not Found error', passed, details)
except Exception as e:
    test_result('404 Not Found error', False, f'Error: {str(e)}')

try:
    # Test invalid team ID lookup
    response = requests.get(f'{BASE_URL}/admin/teams/INVALID999', timeout=15)  # Increased for DB queries
    passed = response.status_code == 404
    
    if response.status_code == 404:
        data = response.json()
        has_error_format = 'detail' in data or 'message' in data
        details = f'Status: {response.status_code}, Has error message: {has_error_format}'
    else:
        details = f'Status: {response.status_code}'
    
    test_result('Invalid team ID (404)', passed, details)
except Exception as e:
    test_result('Invalid team ID (404)', False, f'Error: {str(e)}')

try:
    # Test POST without required fields (should fail validation)
    response = requests.post(
        f'{BASE_URL}/api/register/team',
        json={},  # Empty payload
        timeout=5
    )
    passed = response.status_code == 422  # Validation error
    details = f'Status: {response.status_code} (Expected 422 validation error)'
    test_result('Missing required fields validation', passed, details)
except Exception as e:
    test_result('Missing required fields validation', False, f'Error: {str(e)}')

print('')

# ============================================================================
# TEST SUITE 5: RESPONSE FORMAT VALIDATION
# ============================================================================
print('TEST SUITE 5: Response Format Validation')
print('-'*80)

try:
    response = requests.get(f'{BASE_URL}/', timeout=5)
    data = response.json()
    
    has_message = 'message' in data
    has_status = 'status' in data or 'success' in data
    
    passed = has_message
    details = f'Has message field: {has_message}, Has status field: {has_status}'
    test_result('Root endpoint response format', passed, details)
except Exception as e:
    test_result('Root endpoint response format', False, f'Error: {str(e)}')

try:
    response = requests.get(f'{BASE_URL}/admin/teams', timeout=15)  # Increased for DB queries
    
    if response.status_code == 200:
        data = response.json()
        has_success = 'success' in data
        has_data = 'data' in data
        is_data_list = isinstance(data.get('data', None), list) if has_data else False
        
        passed = has_success and has_data and is_data_list
        details = f'Success field: {has_success}, Data field: {has_data}, Data is array: {is_data_list}'
    else:
        # If 404, check error response format
        data = response.json()
        has_detail = 'detail' in data
        passed = has_detail
        details = f'Error response has detail: {has_detail}'
    
    test_result('Admin teams response format', passed, details)
except Exception as e:
    test_result('Admin teams response format', False, f'Error: {str(e)}')

print('')

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print('='*80)
print('📊 INTEGRATION TEST RESULTS')
print('='*80)
print(f'✅ Tests Passed: {tests_passed}')
print(f'❌ Tests Failed: {tests_failed}')
print(f'📈 Total Tests: {tests_passed + tests_failed}')
print('')

if tests_failed == 0:
    print('🎉 ALL INTEGRATION TESTS PASSED!')
    print('')
    print('✅ Server is healthy and responding correctly')
    print('✅ CORS is configured properly for all origins')
    print('✅ Admin endpoints are accessible')
    print('✅ Error handling works as expected')
    print('✅ Response formats are consistent')
    print('')
    print('Backend is production-ready! ✨')
    sys.exit(0)
else:
    print('⚠️  SOME INTEGRATION TESTS FAILED')
    print('Please review failed tests above.')
    sys.exit(1)
