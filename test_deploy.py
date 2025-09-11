#!/usr/bin/env python3
"""
Simple test script to run after each deployment
"""

import requests
import json
import time
import random
import string

BASE_URL = "https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod"

def test_endpoint(method, endpoint, data=None, headers=None, expected_status=200):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=10)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            return False, f"Unsupported method: {method}"
        
        success = response.status_code == expected_status
        return success, f"{response.status_code} - {response.text[:100]}"
    
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    """Run basic deployment tests"""
    print("🚀 Reddit Clone Backend - Deployment Test")
    print("=" * 50)
    
    # Generate test data
    timestamp = str(int(time.time()))
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    test_user = {
        "email": f"deploy_test_{timestamp}_{random_suffix}@example.com",
        "username": f"deployuser_{timestamp}_{random_suffix}",
        "password": "DeployTest123"
    }
    
    test_user_id = f"user_{timestamp}_{random_suffix}"
    test_subreddit_id = f"subreddit_{timestamp}_{random_suffix}"
    
    headers = {"Content-Type": "application/json"}
    user_headers = {
        "Content-Type": "application/json",
        "X-User-ID": test_user_id
    }
    
    tests = [
        # Authentication tests
        ("POST", "/auth/register", test_user, headers, 200),
        ("POST", "/auth/login", {"email": test_user["email"], "password": test_user["password"]}, headers, 200),
        
        # Posts tests
        ("POST", "/posts/create", {
            "title": "Deploy Test Post",
            "content": "Testing after deployment",
            "subreddit_id": test_subreddit_id,
            "post_type": "text"
        }, user_headers, 200),
        ("GET", "/posts", None, user_headers, 200),
        
        # Comments tests
        ("POST", "/comments/create", {
            "post_id": f"post_{timestamp}_test",
            "content": "Deploy test comment",
            "comment_type": "comment"
        }, user_headers, 200),
        ("GET", "/comments", None, user_headers, 200),
        
        # Subreddits tests
        ("POST", "/subreddits/create", {
            "name": f"deploytest_{timestamp}",
            "display_name": "Deploy Test Subreddit",
            "description": "Testing subreddit creation"
        }, user_headers, 201),
        ("GET", "/subreddits", None, user_headers, 200),
        
        # Feeds tests
        ("GET", "/feeds", None, user_headers, 200),
        ("POST", "/feeds/refresh", {"reason": "deploy_test"}, user_headers, 200),
        ("GET", "/feeds/stats", None, user_headers, 200),
    ]
    
    results = []
    
    for i, (method, endpoint, data, headers, expected_status) in enumerate(tests, 1):
        print(f"{i:2d}. {method} {endpoint}...", end=" ")
        
        success, message = test_endpoint(method, endpoint, data, headers, expected_status)
        
        if success:
            print("✅")
        else:
            print("❌")
            print(f"    {message}")
        
        results.append((f"{method} {endpoint}", success))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Deployment Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All deployment tests passed!")
        print("✅ Your Reddit Clone Backend is working correctly!")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed!")
        print("🔧 Please check the failed endpoints above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
