#!/usr/bin/env python
"""Quick Gallery Backend Tests"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

print("\n" + "="*70)
print("  GALLERY BACKEND QUICK TEST")
print("="*70 + "\n")

# Test 1: Health Check
print("Test 1: Gallery Health Check")
print("-" * 50)
try:
    resp = requests.get(f"{BASE_URL}/api/gallery/health", timeout=5)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        print("✅ PASS\n")
    else:
        print(f"Response: {resp.text[:100]}")
        print("❌ FAIL\n")
except Exception as e:
    print(f"❌ ERROR: {e}\n")

# Test 2: Get Images
print("Test 2: Get Gallery Images")
print("-" * 50)
try:
    resp = requests.get(f"{BASE_URL}/api/gallery/ICCT26/Gallery/images", 
                       params={"limit": 5}, timeout=5)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Images Found: {len(data.get('images', []))}")
        print(f"Total Available: {data.get('total_count', 0)}")
        if data.get('images'):
            print(f"First Image: {data['images'][0].get('public_id')}")
        print("✅ PASS\n")
    else:
        print(f"Response: {resp.text[:100]}")
        print("❌ FAIL\n")
except Exception as e:
    print(f"❌ ERROR: {e}\n")

# Test 3: Download Single
print("Test 3: Download Single Image")
print("-" * 50)
try:
    resp = requests.get(f"{BASE_URL}/api/gallery/ICCT26/Gallery/images", 
                       params={"limit": 1}, timeout=5)
    if resp.status_code == 200 and resp.json().get('images'):
        public_id = resp.json()['images'][0]['public_id']
        
        dl_resp = requests.post(f"{BASE_URL}/api/gallery/download/single",
                               json={"public_id": public_id}, timeout=5)
        print(f"Status: {dl_resp.status_code}")
        if dl_resp.status_code == 200:
            data = dl_resp.json()
            print(f"Download URL Generated: {bool(data.get('download_url'))}")
            print("✅ PASS\n")
        else:
            print(f"Response: {dl_resp.text[:100]}")
            print("❌ FAIL\n")
    else:
        print("⚠️  SKIP: No images in gallery\n")
except Exception as e:
    print(f"❌ ERROR: {e}\n")

# Test 4: Download Bulk
print("Test 4: Download Bulk Images")
print("-" * 50)
try:
    resp = requests.get(f"{BASE_URL}/api/gallery/ICCT26/Gallery/images", 
                       params={"limit": 3}, timeout=5)
    if resp.status_code == 200 and resp.json().get('images'):
        public_ids = [img['public_id'] for img in resp.json()['images'][:2]]
        
        dl_resp = requests.post(f"{BASE_URL}/api/gallery/download/bulk",
                               json={"public_ids": public_ids}, timeout=5)
        print(f"Status: {dl_resp.status_code}")
        if dl_resp.status_code == 200:
            data = dl_resp.json()
            print(f"Download URLs Generated: {len(data.get('download_urls', []))}")
            print("✅ PASS\n")
        else:
            print(f"Response: {dl_resp.text[:100]}")
            print("❌ FAIL\n")
    else:
        print("⚠️  SKIP: No images in gallery\n")
except Exception as e:
    print(f"❌ ERROR: {e}\n")

print("="*70)
print("  TEST SUMMARY COMPLETE")
print("="*70 + "\n")
