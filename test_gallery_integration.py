#!/usr/bin/env python3
"""
Gallery Backend Integration Test
=================================
Test all gallery endpoints with live backend
"""

import asyncio
import requests
import json
import sys
from typing import Dict, Any
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"
TESTS_PASSED = 0
TESTS_FAILED = 0

def log_test(name: str, status: str, details: str = ""):
    """Log test result"""
    global TESTS_PASSED, TESTS_FAILED
    
    icon = "✅" if status == "PASS" else "❌"
    if status == "PASS":
        TESTS_PASSED += 1
    else:
        TESTS_FAILED += 1
    
    print(f"\n{icon} {name}")
    if details:
        print(f"   {details}")
    return status == "PASS"

def print_header(title: str):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_health_check() -> bool:
    """Test 1: Health Check"""
    print_header("Test 1: Gallery Health Check")
    
    try:
        print(f"GET /api/gallery/health")
        response = requests.get(f"{BASE_URL}/api/gallery/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            is_healthy = data.get("success") and data.get("cloudinary_connected")
            
            details = f"Status: {response.status_code}, Cloudinary: {'Connected' if is_healthy else 'Disconnected'}"
            return log_test("Health Check", "PASS" if is_healthy else "FAIL", details)
        else:
            return log_test("Health Check", "FAIL", f"HTTP {response.status_code}")
    except Exception as e:
        return log_test("Health Check", "FAIL", str(e))

def test_get_images() -> bool:
    """Test 2: Get Gallery Images"""
    print_header("Test 2: Get Gallery Images")
    
    try:
        url = f"{BASE_URL}/api/gallery/ICCT26/Gallery/images"
        print(f"GET {url}?limit=5")
        response = requests.get(url, params={"limit": 5}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            success = data.get("success")
            count = len(data.get("images", []))
            total = data.get("total_count", 0)
            
            details = f"Status: 200, Images: {count}, Total Available: {total}"
            return log_test("Get Images", "PASS" if success else "FAIL", details)
        else:
            return log_test("Get Images", "FAIL", f"HTTP {response.status_code}")
    except Exception as e:
        return log_test("Get Images", "FAIL", str(e))

def test_single_download() -> bool:
    """Test 3: Download Single Image"""
    print_header("Test 3: Download Single Image")
    
    try:
        # First get an image
        url = f"{BASE_URL}/api/gallery/ICCT26/Gallery/images"
        response = requests.get(url, params={"limit": 1}, timeout=10)
        
        if response.status_code != 200:
            return log_test("Download Single", "SKIP", "Cannot fetch images")
        
        images = response.json().get("images", [])
        if not images:
            return log_test("Download Single", "SKIP", "No images in gallery")
        
        public_id = images[0]["public_id"]
        
        # Test download
        print(f"POST /api/gallery/download/single")
        print(f"Payload: {{'public_id': '{public_id}'}}")
        
        response = requests.post(
            f"{BASE_URL}/api/gallery/download/single",
            params={"image_url": public_id},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            has_url = bool(data.get("download_url"))
            details = f"Status: 200, Download URL: {'Generated' if has_url else 'Missing'}"
            return log_test("Download Single", "PASS" if has_url else "FAIL", details)
        else:
            return log_test("Download Single", "FAIL", f"HTTP {response.status_code}")
    except Exception as e:
        return log_test("Download Single", "FAIL", str(e))

def test_bulk_download() -> bool:
    """Test 4: Download Bulk Images"""
    print_header("Test 4: Download Bulk Images")
    
    try:
        # First get images
        url = f"{BASE_URL}/api/gallery/ICCT26/Gallery/images"
        response = requests.get(url, params={"limit": 3}, timeout=10)
        
        if response.status_code != 200:
            return log_test("Download Bulk", "SKIP", "Cannot fetch images")
        
        images = response.json().get("images", [])
        if not images:
            return log_test("Download Bulk", "SKIP", "No images in gallery")
        
        public_ids = [img["public_id"] for img in images[:min(2, len(images))]]
        
        # Test bulk download
        print(f"POST /api/gallery/download/bulk")
        print(f"Payload: {len(public_ids)} image(s)")
        
        response = requests.post(
            f"{BASE_URL}/api/gallery/download/bulk",
            params={"image_urls": public_ids},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            success = data.get("success")
            count = len(data.get("individual_urls", []))
            details = f"Status: 200, URLs Generated: {count}"
            return log_test("Download Bulk", "PASS" if success else "FAIL", details)
        else:
            return log_test("Download Bulk", "FAIL", f"HTTP {response.status_code}")
    except Exception as e:
        return log_test("Download Bulk", "FAIL", str(e))

def test_pagination() -> bool:
    """Test 5: Pagination Support"""
    print_header("Test 5: Pagination (limit and skip)")
    
    try:
        url = f"{BASE_URL}/api/gallery/ICCT26/Gallery/images"
        
        # Test limit
        print(f"GET {url}?limit=2")
        response = requests.get(url, params={"limit": 2}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            returned = len(data.get("images", []))
            limit_ok = returned <= 2
            
            details = f"Requested: 2, Returned: {returned}"
            return log_test("Pagination", "PASS" if limit_ok else "FAIL", details)
        else:
            return log_test("Pagination", "FAIL", f"HTTP {response.status_code}")
    except Exception as e:
        return log_test("Pagination", "FAIL", str(e))

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 12 + "GALLERY BACKEND INTEGRATION TEST" + " " * 25 + "║")
    print("╚" + "=" * 68 + "╝")
    print(f"\n📍 Base URL: {BASE_URL}")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nℹ️  Make sure the backend is running: python -m uvicorn main:app --host 127.0.0.1 --port 8000")
    
    # Run tests
    test_health_check()
    test_get_images()
    test_single_download()
    test_bulk_download()
    test_pagination()
    
    # Summary
    print_header("Test Summary")
    total = TESTS_PASSED + TESTS_FAILED
    
    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {TESTS_PASSED}")
    print(f"❌ Failed: {TESTS_FAILED}")
    
    if total > 0:
        percentage = (TESTS_PASSED / total) * 100
        print(f"\nSuccess Rate: {percentage:.1f}%")
    
    if TESTS_FAILED == 0 and TESTS_PASSED > 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {TESTS_FAILED} test(s) failed or skipped")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
