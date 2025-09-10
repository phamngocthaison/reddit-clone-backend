#!/usr/bin/env python3
"""
JWT Token Generator for Testing
"""

import json
import base64
import hmac
import hashlib
from datetime import datetime, timezone

def create_jwt_token(user_id: str, username: str, expires_hours: int = 1) -> str:
    """Create a JWT token for testing"""
    # Header
    header = {
        "alg": "HS256",
        "typ": "JWT"
    }
    
    # Payload
    now = int(datetime.now(timezone.utc).timestamp())
    payload = {
        "sub": user_id,
        "username": username,
        "iat": now,
        "exp": now + (expires_hours * 3600)
    }
    
    # Encode header and payload
    header_encoded = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
    payload_encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
    
    # Create signature
    message = f"{header_encoded}.{payload_encoded}"
    secret = "test_secret_key"
    signature = hmac.new(secret.encode(), message.encode(), hashlib.sha256).digest()
    signature_encoded = base64.urlsafe_b64encode(signature).decode().rstrip('=')
    
    return f"{header_encoded}.{payload_encoded}.{signature_encoded}"

def generate_test_tokens():
    """Generate test JWT tokens"""
    print("🔑 JWT Token Generator for Testing")
    print("=" * 50)
    
    # Test users
    test_users = [
        {"user_id": "user_1757485758_cde044d0", "username": "testuser789"},
        {"user_id": "user_1234567890_abcdef12", "username": "testuser123"},
        {"user_id": "user_0987654321_fedcba98", "username": "testuser456"}
    ]
    
    print("📋 Generated JWT Tokens:")
    print()
    
    for i, user in enumerate(test_users, 1):
        token = create_jwt_token(user["user_id"], user["username"])
        print(f"{i}. User: {user['username']} ({user['user_id']})")
        print(f"   Token: {token}")
        print(f"   Expires: 1 hour from now")
        print()
    
    # Generate curl commands
    print("📋 Test Commands:")
    print()
    
    for i, user in enumerate(test_users, 1):
        token = create_jwt_token(user["user_id"], user["username"])
        print(f"# Test {i}: {user['username']}")
        print(f"curl -X POST 'https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com/prod/posts/create' \\")
        print("  -H 'Content-Type: application/json' \\")
        print(f"  -H 'Authorization: Bearer {token}' \\")
        print("  -d '{\"title\": \"Test Post\", \"content\": \"Test content\", \"subreddit_id\": \"subreddit_test_123\", \"post_type\": \"text\"}'")
        print()

if __name__ == "__main__":
    generate_test_tokens()
