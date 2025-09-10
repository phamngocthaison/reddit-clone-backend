#!/usr/bin/env python3
"""
Quick JWT validation test script
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
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": user_id,
        "username": username,
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "exp": int(datetime.now(timezone.utc).timestamp()) + 3600
    }
    
    header_encoded = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
    payload_encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
    
    message = f"{header_encoded}.{payload_encoded}"
    secret = "test_secret_key"
    signature = hmac.new(secret.encode(), message.encode(), hashlib.sha256).digest()
    signature_encoded = base64.urlsafe_b64encode(signature).decode().rstrip('=')
    
    return f"{header_encoded}.{payload_encoded}.{signature_encoded}"

def quick_test():
    """Quick test of JWT validation"""
    print("🚀 Quick JWT Validation Test")
    print("=" * 40)
    
    # Generate JWT token
    jwt_token = create_test_jwt("user_1757485758_cde044d0", "testuser789")
    print(f"🔑 JWT Token: {jwt_token[:50]}...")
    print()
    
    # Test 1: No Auth (Should Fail)
    print("❌ Test 1: No Authentication")
    response = requests.post(f"{API_BASE_URL}/posts/create", json={
        "title": "Test No Auth",
        "content": "Should fail",
        "subreddit_id": "subreddit_test_123",
        "post_type": "text"
    })
    print(f"   Status: {response.status_code} - {'✅ PASS' if response.status_code == 401 else '❌ FAIL'}")
    print()
    
    # Test 2: X-User-ID (Should Pass)
    print("✅ Test 2: X-User-ID Header")
    response = requests.post(f"{API_BASE_URL}/posts/create", 
        headers={"X-User-ID": "user_1757485758_cde044d0"},
        json={
            "title": "Test X-User-ID",
            "content": "Should work",
            "subreddit_id": "subreddit_test_123",
            "post_type": "text"
        })
    print(f"   Status: {response.status_code} - {'✅ PASS' if response.status_code == 200 else '❌ FAIL'}")
    print()
    
    # Test 3: JWT Token (Should Pass)
    print("🔐 Test 3: JWT Token")
    response = requests.post(f"{API_BASE_URL}/posts/create", 
        headers={"Authorization": f"Bearer {jwt_token}"},
        json={
            "title": "Test JWT Token",
            "content": "Should work",
            "subreddit_id": "subreddit_test_123",
            "post_type": "text"
        })
    print(f"   Status: {response.status_code} - {'✅ PASS' if response.status_code == 200 else '❌ FAIL'}")
    print()
    
    # Test 4: Comments with JWT
    print("💬 Test 4: Comments with JWT")
    response = requests.post(f"{API_BASE_URL}/comments/create", 
        headers={"Authorization": f"Bearer {jwt_token}"},
        json={
            "content": "Test comment with JWT",
            "post_id": "post_1757491671_d419fed7",
            "comment_type": "text"
        })
    print(f"   Status: {response.status_code} - {'✅ PASS' if response.status_code == 200 else '❌ FAIL'}")
    print()
    
    print("🎉 Quick test completed!")

if __name__ == "__main__":
    quick_test()
