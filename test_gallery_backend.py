"""
Gallery Backend Testing Script
================================
Comprehensive tests for gallery API endpoints
"""

import requests
import json
import sys
from typing import Dict, Any
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
GALLERY_PREFIX = "/api/gallery"

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "errors": []
}


def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_test(test_name: str, status: str, details: str = ""):
    """Print test result"""
    status_symbol = "✅" if status == "PASS" else "❌"
    print(f"\n{status_symbol} {test_name}")
    if details:
        print(f"   {details}")


def test_health_check():
    """Test Gallery Health Check Endpoint"""
    print_header("Test 1: Gallery Health Check")
    
    try:
        url = f"{BASE_URL}{GALLERY_PREFIX}/health"
        print(f"Endpoint: GET {url}")
        
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if data.get("success") and data.get("cloudinary_api") == "connected":
                print_test("Health Check", "PASS", "Cloudinary API is connected")
                test_results["passed"] += 1
                return True
            else:
                print_test("Health Check", "FAIL", "Cloudinary connection status unknown")
                test_results["failed"] += 1
                test_results["errors"].append("Health check returned success=false")
                return False
        else:
            print_test("Health Check", "FAIL", f"HTTP {response.status_code}")
            test_results["failed"] += 1
            test_results["errors"].append(f"Health check returned HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print_test("Health Check", "FAIL", "Cannot connect to backend")
        test_results["failed"] += 1
        test_results["errors"].append(f"Connection error: {str(e)}")
        return False
    except Exception as e:
        print_test("Health Check", "FAIL", str(e))
        test_results["failed"] += 1
        test_results["errors"].append(f"Health check error: {str(e)}")
        return False


def test_get_gallery_images():
    """Test Get Gallery Images Endpoint"""
    print_header("Test 2: Get Gallery Images")
    
    try:
        url = f"{BASE_URL}{GALLERY_PREFIX}/ICCT26/Gallery/images"
        print(f"Endpoint: GET {url}")
        print(f"Query Params: limit=5, skip=0")
        
        params = {"limit": 5, "skip": 0}
        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Keys: {list(data.keys())}")
            
            # Validate response structure
            if "success" in data and "images" in data:
                image_count = len(data.get("images", []))
                total_count = data.get("total_count", 0)
                print(f"Images Retrieved: {image_count}")
                print(f"Total Available: {total_count}")
                
                if image_count > 0:
                    first_image = data["images"][0]
                    print(f"\nFirst Image:")
                    print(f"  public_id: {first_image.get('public_id')}")
                    print(f"  width: {first_image.get('width')}")
                    print(f"  height: {first_image.get('height')}")
                    print(f"  format: {first_image.get('format')}")
                    print_test("Get Gallery Images", "PASS", f"{image_count} images retrieved")
                    test_results["passed"] += 1
                    return True
                else:
                    print_test("Get Gallery Images", "PASS", "No images in gallery (expected if empty)")
                    test_results["passed"] += 1
                    return True
            else:
                print_test("Get Gallery Images", "FAIL", "Invalid response structure")
                test_results["failed"] += 1
                test_results["errors"].append("Response missing 'success' or 'images' field")
                return False
        else:
            print_test("Get Gallery Images", "FAIL", f"HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}")
            test_results["failed"] += 1
            test_results["errors"].append(f"Get images returned HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_test("Get Gallery Images", "FAIL", str(e))
        test_results["failed"] += 1
        test_results["errors"].append(f"Get images error: {str(e)}")
        return False


def test_download_single_image():
    """Test Download Single Image Endpoint"""
    print_header("Test 3: Download Single Image")
    
    try:
        # First get available images
        url = f"{BASE_URL}{GALLERY_PREFIX}/ICCT26/Gallery/images"
        response = requests.get(url, params={"limit": 1}, timeout=10)
        
        if response.status_code != 200:
            print_test("Download Single Image", "FAIL", "Cannot fetch gallery images")
            test_results["failed"] += 1
            return False
        
        data = response.json()
        images = data.get("images", [])
        
        if not images:
            print_test("Download Single Image", "SKIP", "No images in gallery to test")
            return None
        
        # Test download with first image
        image_public_id = images[0]["public_id"]
        print(f"Testing with image: {image_public_id}")
        
        download_url = f"{BASE_URL}{GALLERY_PREFIX}/download/single"
        print(f"Endpoint: POST {download_url}")
        
        payload = {"public_id": image_public_id}
        print(f"Payload: {json.dumps(payload)}")
        
        response = requests.post(download_url, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if data.get("success") and data.get("download_url"):
                print_test("Download Single Image", "PASS", "Download URL generated")
                test_results["passed"] += 1
                return True
            else:
                print_test("Download Single Image", "FAIL", "Invalid response structure")
                test_results["failed"] += 1
                test_results["errors"].append("Download response missing required fields")
                return False
        else:
            print_test("Download Single Image", "FAIL", f"HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}")
            test_results["failed"] += 1
            test_results["errors"].append(f"Download single returned HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_test("Download Single Image", "FAIL", str(e))
        test_results["failed"] += 1
        test_results["errors"].append(f"Download single error: {str(e)}")
        return False


def test_download_bulk_images():
    """Test Download Bulk Images Endpoint"""
    print_header("Test 4: Download Bulk Images")
    
    try:
        # First get available images
        url = f"{BASE_URL}{GALLERY_PREFIX}/ICCT26/Gallery/images"
        response = requests.get(url, params={"limit": 3}, timeout=10)
        
        if response.status_code != 200:
            print_test("Download Bulk Images", "FAIL", "Cannot fetch gallery images")
            test_results["failed"] += 1
            return False
        
        data = response.json()
        images = data.get("images", [])
        
        if len(images) < 1:
            print_test("Download Bulk Images", "SKIP", "Not enough images for bulk test")
            return None
        
        # Test with available images
        public_ids = [img["public_id"] for img in images[:min(2, len(images))]]
        print(f"Testing with {len(public_ids)} images")
        
        download_url = f"{BASE_URL}{GALLERY_PREFIX}/download/bulk"
        print(f"Endpoint: POST {download_url}")
        
        payload = {"public_ids": public_ids}
        print(f"Payload: {len(public_ids)} public_ids")
        
        response = requests.post(download_url, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Keys: {list(data.keys())}")
            
            if data.get("success"):
                count = data.get("count", 0)
                urls_count = len(data.get("download_urls", []))
                print(f"Download URLs Generated: {urls_count}")
                print_test("Download Bulk Images", "PASS", f"{urls_count} download URLs prepared")
                test_results["passed"] += 1
                return True
            else:
                print_test("Download Bulk Images", "FAIL", "Response success=false")
                test_results["failed"] += 1
                test_results["errors"].append("Bulk download returned success=false")
                return False
        else:
            print_test("Download Bulk Images", "FAIL", f"HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}")
            test_results["failed"] += 1
            test_results["errors"].append(f"Download bulk returned HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_test("Download Bulk Images", "FAIL", str(e))
        test_results["failed"] += 1
        test_results["errors"].append(f"Download bulk error: {str(e)}")
        return False


def test_pagination():
    """Test Pagination Parameters"""
    print_header("Test 5: Pagination (limit and skip)")
    
    try:
        url = f"{BASE_URL}{GALLERY_PREFIX}/ICCT26/Gallery/images"
        print(f"Endpoint: GET {url}")
        
        # Test limit parameter
        print("\nTest 5a: Limit Parameter")
        response = requests.get(url, params={"limit": 2}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            returned_count = len(data.get("images", []))
            print(f"Requested limit: 2, Received: {returned_count}")
            
            if returned_count <= 2:
                print_test("Limit Parameter", "PASS", f"Correctly limited to {returned_count} images")
                test_results["passed"] += 1
            else:
                print_test("Limit Parameter", "FAIL", f"Returned {returned_count} instead of 2")
                test_results["failed"] += 1
        else:
            print_test("Limit Parameter", "FAIL", f"HTTP {response.status_code}")
            test_results["failed"] += 1
        
        # Test skip parameter
        print("\nTest 5b: Skip Parameter")
        response = requests.get(url, params={"limit": 100, "skip": 10}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            skip_value = data.get("skip", 0)
            print(f"Requested skip: 10, Returned skip: {skip_value}")
            
            if skip_value == 10:
                print_test("Skip Parameter", "PASS", "Skip parameter working correctly")
                test_results["passed"] += 1
                return True
            else:
                print_test("Skip Parameter", "FAIL", f"Skip value mismatch")
                test_results["failed"] += 1
                return False
        else:
            print_test("Skip Parameter", "FAIL", f"HTTP {response.status_code}")
            test_results["failed"] += 1
            return False
            
    except Exception as e:
        print_test("Pagination", "FAIL", str(e))
        test_results["failed"] += 1
        test_results["errors"].append(f"Pagination error: {str(e)}")
        return False


def print_summary():
    """Print test summary"""
    print_header("Test Summary")
    
    total = test_results["passed"] + test_results["failed"]
    passed = test_results["passed"]
    failed = test_results["failed"]
    
    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if test_results["errors"]:
        print("\n⚠️  Error Details:")
        for i, error in enumerate(test_results["errors"], 1):
            print(f"   {i}. {error}")
    
    print(f"\nSuccess Rate: {(passed/total*100):.1f}%" if total > 0 else "No tests run")
    
    if failed == 0 and total > 0:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return False


def main():
    """Run all gallery tests"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "GALLERY BACKEND TEST SUITE" + " " * 27 + "║")
    print("╚" + "=" * 68 + "╝")
    print(f"\n📍 Base URL: {BASE_URL}")
    print(f"🎯 Gallery Prefix: {GALLERY_PREFIX}")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    test_health_check()
    test_get_gallery_images()
    test_download_single_image()
    test_download_bulk_images()
    test_pagination()
    
    # Print summary
    success = print_summary()
    
    print("\n")
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
