#!/usr/bin/env python3
"""
Test script for new subreddit APIs:
- GET /subreddits/user/{user_id} - Get user's subscribed subreddits
- GET /subreddits/{subreddit_id}/members/{user_id} - Check user membership
"""

import requests
import json
import sys
from typing import Dict, Any

# Configuration
BASE_URL = "https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod"
JWT_TOKEN = "eyJraWQiOiJwTDliQlM4K2dKVU5OXC9aK3VObGVmcm9VWkdDNFJhNmV5alwvcnN6T3IydW89IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiJmOWJhMTU4Yy1iMDUxLTcwM2UtZGEzZS01ZDNlZDg1MjJiYjUiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuYXAtc291dGhlYXN0LTEuYW1hem9uYXdzLmNvbVwvYXAtc291dGhlYXN0LTFfdGN3SUpTVUZTIiwiY2xpZW50X2lkIjoiMWV0Nm81cWR2ZmdjcmoxOHFxYmdsa3BrbTEiLCJvcmlnaW5fanRpIjoiMzcxMTczYTYtZmMxZC00Mjk1LWFiMmUtY2ExZmE2YTJlMWQyIiwiZXZlbnRfaWQiOiJkMzk5Mzc5ZS0xMmY2LTQxMWEtOTEzZS1lYzU3OWVjYTRlNjAiLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJzY29wZSI6ImF3cy5jb2duaXRvLnNpZ25pbi51c2VyLmFkbWluIiwiYXV0aF90aW1lIjoxNzU3NTc4MjUwLCJleHAiOjE3NTc1ODE4NTAsImlhdCI6MTc1NzU3ODI1MCwianRpIjoiOGNhOWNkZDUtMWQxNS00NDMyLTk3OTktMWY4Yzk3NDBhNjQ3IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEyMyJ9.xNwl8KsN6xpmvTPPEpySKigkGfM0lKaLSZLICBqGZfGukibIuE8kKZCkL0IFGGP9ATRneT2VKE3sbSzTJQ8fzTIs0yuA1EuKUHCLEw5gwWfI2DKyFXdz57QrNRVAJAake3WjVrEmlKsWT1Ge7KYIE-zBU8CEooe7ppQ4jCmEpA735U4KriqoUpYokUcWFfEx5DQoW08uAobk1-YYUwLOWlZwkGJhyhwtIMYdJvEZCNmD8vK790yHX5i1to01D_NFtheXxpUzIgGykpl5oMeQXAoo7INkYl4YroPBqNYvk0Gmm2HdUnmHsSjpewrOJgcKkhS3nyH6H_ytVN40oAUArg"
USER_ID = "user_1757432106_d66ab80f40704b1"
SUBREDDIT_ID = "subreddit_1757556413_5c2c522e"

def make_request(method: str, url: str, headers: Dict[str, str] = None, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Make HTTP request and return response."""
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        print(f"\n{method} {url}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        return {
            "status_code": response.status_code,
            "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        }
    except Exception as e:
        print(f"Error making request: {e}")
        return {"error": str(e)}

def test_get_user_subreddits():
    """Test GET /subreddits/user/{user_id}"""
    print("\n" + "="*60)
    print("TESTING: GET /subreddits/user/{user_id}")
    print("="*60)
    
    url = f"{BASE_URL}/subreddits/user/{USER_ID}"
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "X-User-ID": USER_ID
    }
    
    # Test with default parameters
    result = make_request("GET", url, headers)
    
    # Test with query parameters
    url_with_params = f"{url}?limit=5&offset=0&sort=name"
    print(f"\nTesting with query parameters:")
    result2 = make_request("GET", url_with_params, headers)
    
    return result

def test_check_user_membership():
    """Test GET /subreddits/{subreddit_id}/members/{user_id}"""
    print("\n" + "="*60)
    print("TESTING: GET /subreddits/{subreddit_id}/members/{user_id}")
    print("="*60)
    
    url = f"{BASE_URL}/subreddits/{SUBREDDIT_ID}/members/{USER_ID}"
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "X-User-ID": USER_ID
    }
    
    result = make_request("GET", url, headers)
    return result

def test_invalid_user_id():
    """Test with invalid user ID"""
    print("\n" + "="*60)
    print("TESTING: Invalid user ID")
    print("="*60)
    
    url = f"{BASE_URL}/subreddits/user/invalid_user_id"
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "X-User-ID": USER_ID
    }
    
    result = make_request("GET", url, headers)
    return result

def test_invalid_subreddit_id():
    """Test with invalid subreddit ID"""
    print("\n" + "="*60)
    print("TESTING: Invalid subreddit ID")
    print("="*60)
    
    url = f"{BASE_URL}/subreddits/invalid_subreddit_id/members/{USER_ID}"
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "X-User-ID": USER_ID
    }
    
    result = make_request("GET", url, headers)
    return result

def main():
    """Run all tests."""
    print("Testing New Subreddit APIs")
    print("="*60)
    
    # Test 1: Get user subreddits
    test_get_user_subreddits()
    
    # Test 2: Check user membership
    test_check_user_membership()
    
    # Test 3: Invalid user ID
    test_invalid_user_id()
    
    # Test 4: Invalid subreddit ID
    test_invalid_subreddit_id()
    
    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60)

if __name__ == "__main__":
    main()
