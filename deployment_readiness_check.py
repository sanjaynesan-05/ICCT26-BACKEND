"""
Backend Deployment Readiness Check
"""
import requests
import json

print('=' * 70)
print('BACKEND DEPLOYMENT READINESS CHECK')
print('=' * 70)

# Test 1: Server Health
print('\n1️⃣  SERVER HEALTH CHECK')
try:
    response = requests.get('http://127.0.0.1:8000/api/schedule/matches')
    if response.status_code == 200:
        print('   ✅ Server is running and responding')
        data = response.json()
        print(f'   ✅ Database accessible - {len(data.get("data", []))} matches found')
    else:
        print(f'   ❌ Server returned {response.status_code}')
except Exception as e:
    print(f'   ❌ Server not responding: {e}')

# Test 2: Check critical endpoints
print('\n2️⃣  CRITICAL ENDPOINTS')
endpoints = [
    ('GET', '/api/schedule/matches', 'List all matches'),
    ('GET', '/api/admin/teams', 'List all teams'),
]

for method, endpoint, description in endpoints:
    try:
        if method == 'GET':
            response = requests.get(f'http://127.0.0.1:8000{endpoint}')
        status = '✅' if response.status_code == 200 else '❌'
        print(f'   {status} {method:4} {endpoint:30} ({description})')
    except Exception as e:
        print(f'   ❌ {method:4} {endpoint:30} - {str(e)[:40]}')

# Test 3: Check response format
print('\n3️⃣  RESPONSE FORMAT VALIDATION')
try:
    response = requests.get('http://127.0.0.1:8000/api/schedule/matches')
    if response.status_code == 200:
        data = response.json()
        if 'success' in data and 'data' in data:
            print('   ✅ Response has correct structure (success, data)')
        if data['data'] and len(data['data']) > 0:
            match = data['data'][0]
            required_fields = ['id', 'round', 'team1', 'team2', 'status', 'result']
            all_present = all(field in match for field in required_fields)
            if all_present:
                print('   ✅ All required match fields present')
            else:
                missing = [f for f in required_fields if f not in match]
                print(f'   ⚠️  Missing fields: {missing}')
except Exception as e:
    print(f'   ❌ Error checking response: {e}')

# Test 4: Check runs and wickets fields
print('\n4️⃣  RUNS & WICKETS FIELDS')
try:
    response = requests.get('http://127.0.0.1:8000/api/schedule/matches')
    if response.status_code == 200:
        data = response.json()
        if data['data']:
            match = data['data'][0]
            wickets_fields = ['team1_first_innings_runs', 'team1_first_innings_wickets', 
                            'team2_first_innings_runs', 'team2_first_innings_wickets']
            all_present = all(field in match for field in wickets_fields)
            if all_present:
                print('   ✅ All runs & wickets fields present in response')
                if match.get('team1_first_innings_runs') is not None:
                    print(f'   ✅ Data populated: T1({match["team1_first_innings_runs"]}-{match["team1_first_innings_wickets"]}), T2({match["team2_first_innings_runs"]}-{match["team2_first_innings_wickets"]})')
            else:
                print('   ❌ Some runs/wickets fields missing')
except Exception as e:
    print(f'   ❌ Error: {e}')

# Test 5: Match result format
print('\n5️⃣  MATCH RESULT FORMAT (CAMELCASE)')
try:
    response = requests.get('http://127.0.0.1:8000/api/schedule/matches')
    if response.status_code == 200:
        data = response.json()
        done_matches = [m for m in data['data'] if m.get('status') == 'done']
        if done_matches:
            match = done_matches[0]
            if match.get('result'):
                result = match['result']
                required = ['winner', 'margin', 'marginType', 'wonByBattingFirst']
                all_present = all(field in result for field in required)
                if all_present:
                    print('   ✅ Result format correct (marginType, wonByBattingFirst in camelCase)')
                    print(f'   ✅ Sample: {result["winner"]} won by {result["margin"]} {result["marginType"]}')
                else:
                    print(f'   ❌ Missing result fields: {[f for f in required if f not in result]}')
        else:
            print('   ℹ️  No completed matches to validate result format')
except Exception as e:
    print(f'   ❌ Error: {e}')

# Test 6: Database integrity
print('\n6️⃣  DATABASE INTEGRITY')
try:
    response = requests.get('http://127.0.0.1:8000/api/schedule/matches')
    if response.status_code == 200:
        data = response.json()
        matches = data.get('data', [])
        print(f'   ✅ Total matches in database: {len(matches)}')
        
        statuses = {}
        for match in matches:
            status = match.get('status', 'unknown')
            statuses[status] = statuses.get(status, 0) + 1
        
        for status, count in sorted(statuses.items()):
            print(f'   ℹ️  {status.capitalize()}: {count} matches')
except Exception as e:
    print(f'   ❌ Error: {e}')

print('\n' + '=' * 70)
print('DEPLOYMENT READINESS: CHECKING...')
print('=' * 70)
