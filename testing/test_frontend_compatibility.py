"""
Quick Frontend Compatibility Test Script
Run this to verify your frontend can communicate with the backend
"""

import requests
import sys

BACKEND_URL = 'http://localhost:8000'
TEST_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5173',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:5173'
]

print('='*80)
print('🔗 FRONTEND-BACKEND COMPATIBILITY TEST')
print('='*80)
print(f'Backend URL: {BACKEND_URL}')
print('')

tests_passed = 0
tests_failed = 0

def test_result(test_name, passed, details=''):
    global tests_passed, tests_failed
    if passed:
        print(f'✅ {test_name} - PASSED')
        tests_passed += 1
    else:
        print(f'❌ {test_name} - FAILED')
        tests_failed += 1
    if details:
        print(f'   {details}')

# Test 1: Backend Health
print('TEST 1: Backend Health Check')
print('-'*80)
try:
    response = requests.get(f'{BACKEND_URL}/', timeout=5)
    passed = response.status_code == 200
    data = response.json()
    details = f"Status: {response.status_code}, Message: {data.get('message', 'N/A')}"
    test_result('Backend is running', passed, details)
except Exception as e:
    test_result('Backend is running', False, f'Error: {str(e)}')
    print('\n❌ Backend is not running. Start it with: python main.py')
    sys.exit(1)

print('')

# Test 2: CORS Configuration
print('TEST 2: CORS Configuration')
print('-'*80)

for origin in TEST_ORIGINS:
    try:
        response = requests.options(
            f'{BACKEND_URL}/',
            headers={
                'Origin': origin,
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'content-type'
            },
            timeout=5
        )
        cors_origin = response.headers.get('access-control-allow-origin', '')
        passed = cors_origin == origin
        test_result(f'CORS for {origin}', passed)
    except Exception as e:
        test_result(f'CORS for {origin}', False, f'Error: {str(e)}')

print('')

# Test 3: API Documentation
print('TEST 3: API Documentation')
print('-'*80)
try:
    response = requests.get(f'{BACKEND_URL}/docs', timeout=5)
    passed = response.status_code == 200
    test_result('API docs accessible', passed, f'Visit: {BACKEND_URL}/docs')
except Exception as e:
    test_result('API docs accessible', False, f'Error: {str(e)}')

print('')

# Test 4: OpenAPI Spec
print('TEST 4: OpenAPI Specification')
print('-'*80)
try:
    response = requests.get(f'{BACKEND_URL}/openapi.json', timeout=5)
    data = response.json()
    has_paths = 'paths' in data
    registration_endpoint = '/api/register/team' in data.get('paths', {})
    admin_endpoint = '/admin/teams' in data.get('paths', {})
    
    passed = has_paths and registration_endpoint and admin_endpoint
    test_result('OpenAPI spec valid', passed)
    if passed:
        print(f'   Found registration endpoint: /api/register/team')
        print(f'   Found admin endpoint: /admin/teams')
except Exception as e:
    test_result('OpenAPI spec valid', False, f'Error: {str(e)}')

print('')

# Test 5: Admin Endpoints
print('TEST 5: Admin Endpoints')
print('-'*80)
try:
    response = requests.get(f'{BACKEND_URL}/admin/teams', timeout=15)
    if response.status_code == 200:
        data = response.json()
        teams_count = len(data.get('data', []))
        test_result('GET /admin/teams', True, f'Found {teams_count} teams')
    elif response.status_code == 404:
        test_result('GET /admin/teams', True, 'No teams yet (404 is expected)')
    else:
        test_result('GET /admin/teams', False, f'Status: {response.status_code}')
except Exception as e:
    test_result('GET /admin/teams', False, f'Error: {str(e)}')

print('')

# Test 6: Error Handling
print('TEST 6: Error Handling')
print('-'*80)
try:
    response = requests.get(f'{BACKEND_URL}/admin/teams/INVALID999', timeout=15)
    passed = response.status_code == 404
    if passed:
        data = response.json()
        has_error = 'detail' in data
        test_result('404 error handling', passed, f'Error message present: {has_error}')
    else:
        test_result('404 error handling', False, f'Expected 404, got {response.status_code}')
except Exception as e:
    test_result('404 error handling', False, f'Error: {str(e)}')

print('')

# Test 7: Validation Error
print('TEST 7: Validation Error Handling')
print('-'*80)
try:
    response = requests.post(
        f'{BACKEND_URL}/api/register/team',
        json={},
        timeout=5
    )
    passed = response.status_code == 422
    if passed:
        data = response.json()
        has_detail = 'detail' in data
        test_result('Validation errors', passed, f'Validation response format correct: {has_detail}')
    else:
        test_result('Validation errors', False, f'Expected 422, got {response.status_code}')
except Exception as e:
    test_result('Validation errors', False, f'Error: {str(e)}')

print('')

# Summary
print('='*80)
print('📊 TEST SUMMARY')
print('='*80)
print(f'✅ Tests Passed: {tests_passed}')
print(f'❌ Tests Failed: {tests_failed}')
print(f'📈 Total Tests: {tests_passed + tests_failed}')
print('')

if tests_failed == 0:
    print('🎉 ALL COMPATIBILITY TESTS PASSED!')
    print('')
    print('Your frontend is compatible with the backend!')
    print('')
    print('Next steps:')
    print('  1. Update your frontend API_BASE_URL to: http://localhost:8000')
    print('  2. Ensure your frontend origin is in the allowed CORS origins')
    print('  3. Test team registration with actual files')
    print('  4. Check FRONTEND_COMPATIBILITY_GUIDE.md for detailed integration examples')
    print('')
    sys.exit(0)
else:
    print('⚠️  SOME TESTS FAILED')
    print('')
    print('Troubleshooting:')
    print('  1. Make sure backend is running: python main.py')
    print('  2. Check if your frontend origin is in allowed CORS origins')
    print('  3. Review FRONTEND_COMPATIBILITY_GUIDE.md for solutions')
    print('')
    sys.exit(1)
