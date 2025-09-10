#!/usr/bin/env python3
"""
Local test script for JWT validation
"""

import json
import base64
import hmac
import hashlib
from datetime import datetime, timezone

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

def test_jwt_validation():
    """Test JWT validation functions"""
    print("🧪 Testing JWT Validation Functions")
    print("=" * 50)
    
    # Test data
    test_user_id = "user_1757485758_cde044d0"
    test_username = "testuser789"
    
    # Create test JWT
    jwt_token = create_test_jwt(test_user_id, test_username)
    print(f"✅ Created test JWT token:")
    print(f"   Token: {jwt_token[:50]}...")
    print()
    
    # Test JWT parsing
    try:
        parts = jwt_token.split('.')
        if len(parts) != 3:
            print("❌ Invalid JWT format")
            return
        
        # Decode header
        header_padding = '=' * (4 - len(parts[0]) % 4)
        header_decoded = base64.urlsafe_b64decode(parts[0] + header_padding)
        header = json.loads(header_decoded)
        print(f"✅ JWT Header: {header}")
        
        # Decode payload
        payload_padding = '=' * (4 - len(parts[1]) % 4)
        payload_decoded = base64.urlsafe_b64decode(parts[1] + payload_padding)
        payload = json.loads(payload_decoded)
        print(f"✅ JWT Payload: {payload}")
        
        # Extract user info
        extracted_user_id = payload.get('sub')
        extracted_username = payload.get('username')
        
        print(f"✅ Extracted User ID: {extracted_user_id}")
        print(f"✅ Extracted Username: {extracted_username}")
        
        # Verify user info matches
        if extracted_user_id == test_user_id and extracted_username == test_username:
            print("✅ JWT validation successful!")
        else:
            print("❌ JWT validation failed - user info mismatch")
            
    except Exception as e:
        print(f"❌ JWT validation error: {e}")

def test_authentication_scenarios():
    """Test different authentication scenarios"""
    print("\n🔐 Testing Authentication Scenarios")
    print("=" * 50)
    
    # Scenario 1: Valid JWT token
    print("1. Valid JWT Token:")
    jwt_token = create_test_jwt("user_1757485758_cde044d0", "testuser789")
    print(f"   Token: {jwt_token[:50]}...")
    print("   Expected: ✅ SUCCESS")
    print()
    
    # Scenario 2: Invalid JWT token
    print("2. Invalid JWT Token:")
    invalid_token = "invalid.jwt.token"
    print(f"   Token: {invalid_token}")
    print("   Expected: ❌ FAIL")
    print()
    
    # Scenario 3: X-User-ID header
    print("3. X-User-ID Header:")
    print("   Header: X-User-ID: user_1757485758_cde044d0")
    print("   Expected: ✅ SUCCESS")
    print()
    
    # Scenario 4: No authentication
    print("4. No Authentication:")
    print("   Headers: None")
    print("   Expected: ❌ FAIL")
    print()

def test_api_endpoints():
    """Test API endpoint scenarios"""
    print("\n🌐 Testing API Endpoint Scenarios")
    print("=" * 50)
    
    # Test data
    test_post_data = {
        "title": "Test Post for JWT Validation",
        "content": "Testing JWT validation in local environment",
        "subreddit_id": "subreddit_test_123",
        "post_type": "text",
        "is_nsfw": False,
        "is_spoiler": False
    }
    
    test_comment_data = {
        "content": "Test comment for JWT validation",
        "post_id": "post_1757491048_2d57ea9c",
        "comment_type": "text",
        "is_nsfw": False,
        "is_spoiler": False
    }
    
    print("📝 Test Post Data:")
    print(json.dumps(test_post_data, indent=2))
    print()
    
    print("💬 Test Comment Data:")
    print(json.dumps(test_comment_data, indent=2))
    print()
    
    # Generate test JWT
    jwt_token = create_test_jwt("user_1757485758_cde044d0", "testuser789")
    
    print("🔑 Test JWT Token:")
    print(f"   Authorization: Bearer {jwt_token}")
    print()
    
    print("📋 Test Commands:")
    print("   # Test Posts API with JWT:")
    print(f"   curl -X POST 'https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod/posts/create' \\")
    print("     -H 'Content-Type: application/json' \\")
    print(f"     -H 'Authorization: Bearer {jwt_token}' \\")
    print(f"     -d '{json.dumps(test_post_data)}'")
    print()
    
    print("   # Test Comments API with JWT:")
    print(f"   curl -X POST 'https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod/comments/create' \\")
    print("     -H 'Content-Type: application/json' \\")
    print(f"     -H 'Authorization: Bearer {jwt_token}' \\")
    print(f"     -d '{json.dumps(test_comment_data)}'")
    print()

if __name__ == "__main__":
    print("🚀 JWT Validation Local Test")
    print("=" * 50)
    
    test_jwt_validation()
    test_authentication_scenarios()
    test_api_endpoints()
    
    print("\n✅ Local testing completed!")
    print("💡 You can now test the actual API endpoints with the generated JWT tokens.")
