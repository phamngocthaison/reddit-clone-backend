#!/usr/bin/env python3
"""
Simple Quick Test Script for Reddit Clone Backend
Tests only the most critical endpoints for deployment verification.
"""

import requests
import json
import time
import sys

BASE_URL = "https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod"

def test_endpoint(method, endpoint, data=None, headers=None, expected_status=200):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        else:
            return False, f"Unsupported method: {method}"
        
        success = response.status_code == expected_status
        return success, f"Status: {response.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    """Run simple quick tests"""
    print("🚀 Reddit Clone Backend - Quick Test")
    print("=" * 40)
    
    tests = [
        ("GET", "/posts?limit=1", None, None, "Get Posts"),
        ("GET", "/subreddits?limit=1", None, None, "Get Subreddits"),
        ("GET", f"/subreddits/subreddit_1757518063_01b8625d/posts?limit=1", None, None, "Get Subreddit Posts"),
        ("GET", f"/users/user_1757951120_a341a0c0/posts?limit=1", None, None, "Get User Posts"),
        ("GET", f"/posts/post_1757508287_f8e2cbd7", None, None, "Get Post by ID"),
        ("GET", f"/comments/comment_1757509982_351caa27", None, None, "Get Comment by ID"),
    ]
    
    passed = 0
    total = len(tests)
    
    for method, endpoint, data, headers, name in tests:
        success, message = test_endpoint(method, endpoint, data, headers)
        status = "✅" if success else "❌"
        print(f"{status} {name}")
        if not success:
            print(f"   {message}")
        else:
            passed += 1
    
    print("=" * 40)
    print(f"Results: {passed}/{total} tests passed")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
