#!/usr/bin/env python3
"""
Quick test script for basic API functionality
"""

import requests
import json
import time
import random
import string

BASE_URL = "https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod"

def test_basic_endpoints():
    """Test basic API endpoints quickly"""
    print("🚀 Quick API Test")
    print("=" * 40)
    
    # Generate test data
    timestamp = str(int(time.time()))
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    test_user = {
        "email": f"quick_test_{timestamp}_{random_suffix}@example.com",
        "username": f"quickuser_{timestamp}_{random_suffix}",
        "password": "QuickTest123"
    }
    
    test_user_id = f"user_{timestamp}_{random_suffix}"
    test_subreddit_id = f"subreddit_{timestamp}_{random_suffix}"
    
    results = []
    
    # Test 1: User Registration
    print("1. Testing User Registration...")
    try:
        response = requests.post(f"{BASE_URL}/auth/register", 
                               headers={"Content-Type": "application/json"}, 
                               json=test_user, timeout=10)
        success = response.status_code == 200
        results.append(("User Registration", success, response.status_code))
        print(f"   {'✅' if success else '❌'} Status: {response.status_code}")
    except Exception as e:
        results.append(("User Registration", False, str(e)))
        print(f"   ❌ Error: {e}")
    
    # Test 2: User Login
    print("2. Testing User Login...")
    try:
        login_data = {"email": test_user["email"], "password": test_user["password"]}
        response = requests.post(f"{BASE_URL}/auth/login", 
                               headers={"Content-Type": "application/json"}, 
                               json=login_data, timeout=10)
        success = response.status_code == 200
        results.append(("User Login", success, response.status_code))
        print(f"   {'✅' if success else '❌'} Status: {response.status_code}")
    except Exception as e:
        results.append(("User Login", False, str(e)))
        print(f"   ❌ Error: {e}")
    
    # Test 3: Create Post
    print("3. Testing Create Post...")
    try:
        post_data = {
            "title": "Quick Test Post",
            "content": "This is a quick test post",
            "subreddit_id": test_subreddit_id,
            "post_type": "text"
        }
        headers = {
            "Content-Type": "application/json",
            "X-User-ID": test_user_id
        }
        response = requests.post(f"{BASE_URL}/posts/create", 
                               headers=headers, 
                               json=post_data, timeout=10)
        success = response.status_code == 201
        results.append(("Create Post", success, response.status_code))
        print(f"   {'✅' if success else '❌'} Status: {response.status_code}")
    except Exception as e:
        results.append(("Create Post", False, str(e)))
        print(f"   ❌ Error: {e}")
    
    # Test 4: Get Posts
    print("4. Testing Get Posts...")
    try:
        headers = {"X-User-ID": test_user_id}
        response = requests.get(f"{BASE_URL}/posts", 
                              headers=headers, timeout=10)
        success = response.status_code == 200
        results.append(("Get Posts", success, response.status_code))
        print(f"   {'✅' if success else '❌'} Status: {response.status_code}")
    except Exception as e:
        results.append(("Get Posts", False, str(e)))
        print(f"   ❌ Error: {e}")
    
    # Test 5: Create Comment
    print("5. Testing Create Comment...")
    try:
        comment_data = {
            "post_id": f"post_{timestamp}_test",
            "content": "Quick test comment",
            "comment_type": "comment"
        }
        headers = {
            "Content-Type": "application/json",
            "X-User-ID": test_user_id
        }
        response = requests.post(f"{BASE_URL}/comments/create", 
                               headers=headers, 
                               json=comment_data, timeout=10)
        success = response.status_code == 201
        results.append(("Create Comment", success, response.status_code))
        print(f"   {'✅' if success else '❌'} Status: {response.status_code}")
    except Exception as e:
        results.append(("Create Comment", False, str(e)))
        print(f"   ❌ Error: {e}")
    
    # Test 6: Get Feeds
    print("6. Testing Get Feeds...")
    try:
        headers = {"X-User-ID": test_user_id}
        response = requests.get(f"{BASE_URL}/feeds", 
                              headers=headers, timeout=10)
        success = response.status_code == 200
        results.append(("Get Feeds", success, response.status_code))
        print(f"   {'✅' if success else '❌'} Status: {response.status_code}")
    except Exception as e:
        results.append(("Get Feeds", False, str(e)))
        print(f"   ❌ Error: {e}")
    
    # Print Summary
    print("\n" + "=" * 40)
    print("📊 Quick Test Summary")
    print("=" * 40)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print()
    
    for test_name, success, status in results:
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {test_name}: {status}")
    
    print()
    if passed == total:
        print("🎉 All quick tests passed!")
    else:
        print("⚠️  Some quick tests failed")
    
    return passed == total

if __name__ == "__main__":
    success = test_basic_endpoints()
    exit(0 if success else 1)
