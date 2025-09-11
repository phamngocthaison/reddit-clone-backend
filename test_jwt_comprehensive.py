#!/usr/bin/env python3
"""
Comprehensive JWT validation test script
"""

import json
import base64
import hmac
import hashlib
import requests
from datetime import datetime, timezone

# API Configuration
API_BASE_URL = "https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod"

def create_test_jwt(user_id: str, username: str) -> str:
    """Create a test JWT token for local testing"""
    # Header
    header = {
        "alg": "HS256",
        "typ": "JWT"
    }
    
    # Payload
    payload = {
        "sub": user_id,
        "username": username,
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "exp": int(datetime.now(timezone.utc).timestamp()) + 3600  # 1 hour
    }
    
    # Encode header and payload
    header_encoded = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
    payload_encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
    
    # Create signature (for testing, we'll use a simple HMAC)
    message = f"{header_encoded}.{payload_encoded}"
    secret = "test_secret_key"
    signature = hmac.new(secret.encode(), message.encode(), hashlib.sha256).digest()
    signature_encoded = base64.urlsafe_b64encode(signature).decode().rstrip('=')
    
    return f"{header_encoded}.{payload_encoded}.{signature_encoded}"

def test_api_endpoint(method: str, endpoint: str, headers: dict = None, data: dict = None, expected_status: int = 200):
    """Test an API endpoint"""
    url = f"{API_BASE_URL}{endpoint}"
    
    if headers is None:
        headers = {"Content-Type": "application/json"}
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        success = response.status_code == expected_status
        status_icon = "✅" if success else "❌"
        
        print(f"{status_icon} {method} {endpoint}")
        print(f"   Status: {response.status_code} (Expected: {expected_status})")
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                print(f"   Response: {response_data.get('message', 'Success')}")
            except:
                print(f"   Response: {response.text[:100]}...")
        else:
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('message', 'Unknown error')}")
            except:
                print(f"   Error: {response.text[:100]}...")
        
        print()
        return success
        
    except Exception as e:
        print(f"❌ {method} {endpoint}")
        print(f"   Exception: {e}")
        print()
        return False

def run_comprehensive_tests():
    """Run comprehensive JWT validation tests"""
    print("🚀 Comprehensive JWT Validation Test Suite")
    print("=" * 60)
    
    # Test data
    test_user_id = "user_1757485758_cde044d0"
    test_username = "testuser789"
    jwt_token = create_test_jwt(test_user_id, test_username)
    
    print(f"🔑 Generated JWT Token: {jwt_token[:50]}...")
    print()
    
    # Test 1: Posts API - No Authentication (Should Fail)
    print("📝 Test 1: Posts API - No Authentication")
    print("-" * 40)
    test_api_endpoint(
        "POST", 
        "/posts/create",
        data={
            "title": "Test Post No Auth",
            "content": "This should fail",
            "subreddit_id": "subreddit_test_123",
            "post_type": "text",
            "is_nsfw": False,
            "is_spoiler": False
        },
        expected_status=401
    )
    
    # Test 2: Posts API - X-User-ID Header (Should Pass)
    print("📝 Test 2: Posts API - X-User-ID Header")
    print("-" * 40)
    test_api_endpoint(
        "POST", 
        "/posts/create",
        headers={
            "Content-Type": "application/json",
            "X-User-ID": test_user_id
        },
        data={
            "title": "Test Post X-User-ID",
            "content": "This should work with X-User-ID",
            "subreddit_id": "subreddit_test_123",
            "post_type": "text",
            "is_nsfw": False,
            "is_spoiler": False
        },
        expected_status=200
    )
    
    # Test 3: Posts API - JWT Token (Should Pass)
    print("📝 Test 3: Posts API - JWT Token")
    print("-" * 40)
    test_api_endpoint(
        "POST", 
        "/posts/create",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {jwt_token}"
        },
        data={
            "title": "Test Post JWT Token",
            "content": "This should work with JWT",
            "subreddit_id": "subreddit_test_123",
            "post_type": "text",
            "is_nsfw": False,
            "is_spoiler": False
        },
        expected_status=200
    )
    
    # Test 4: Comments API - No Authentication (Should Fail)
    print("💬 Test 4: Comments API - No Authentication")
    print("-" * 40)
    test_api_endpoint(
        "POST", 
        "/comments/create",
        data={
            "content": "Test comment no auth",
            "post_id": "post_1757491671_d419fed7",
            "comment_type": "text",
            "is_nsfw": False,
            "is_spoiler": False
        },
        expected_status=401
    )
    
    # Test 5: Comments API - X-User-ID Header (Should Pass)
    print("💬 Test 5: Comments API - X-User-ID Header")
    print("-" * 40)
    test_api_endpoint(
        "POST", 
        "/comments/create",
        headers={
            "Content-Type": "application/json",
            "X-User-ID": test_user_id
        },
        data={
            "content": "Test comment X-User-ID",
            "post_id": "post_1757491671_d419fed7",
            "comment_type": "text",
            "is_nsfw": False,
            "is_spoiler": False
        },
        expected_status=200
    )
    
    # Test 6: Comments API - JWT Token (Should Pass)
    print("💬 Test 6: Comments API - JWT Token")
    print("-" * 40)
    test_api_endpoint(
        "POST", 
        "/comments/create",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {jwt_token}"
        },
        data={
            "content": "Test comment JWT token",
            "post_id": "post_1757491671_d419fed7",
            "comment_type": "text",
            "is_nsfw": False,
            "is_spoiler": False
        },
        expected_status=200
    )
    
    # Test 7: Public Endpoints - No Authentication (Should Pass)
    print("🌐 Test 7: Public Endpoints - No Authentication")
    print("-" * 40)
    test_api_endpoint("GET", "/posts", expected_status=200)
    test_api_endpoint("GET", "/comments", expected_status=200)
    
    # Test 8: Invalid JWT Token (Should Fail)
    print("🔒 Test 8: Invalid JWT Token")
    print("-" * 40)
    test_api_endpoint(
        "POST", 
        "/posts/create",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer invalid.jwt.token"
        },
        data={
            "title": "Test Post Invalid JWT",
            "content": "This should fail",
            "subreddit_id": "subreddit_test_123",
            "post_type": "text",
            "is_nsfw": False,
            "is_spoiler": False
        },
        expected_status=401
    )
    
    print("✅ Comprehensive testing completed!")

if __name__ == "__main__":
    run_comprehensive_tests()
