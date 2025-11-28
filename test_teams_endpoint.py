import requests
import json

base_url = 'http://127.0.0.1:8000'

response = requests.get(base_url + '/api/teams')
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
