#!/usr/bin/env python3
"""
Script để test API Lambda functions locally
"""

import json
import asyncio
import os
import sys
import importlib

# Setup environment variables
os.environ["USER_POOL_ID"] = "test-user-pool-id"
os.environ["CLIENT_ID"] = "test-client-id"
os.environ["USERS_TABLE"] = "test-users-table"
os.environ["REGION"] = "us-east-1"
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"

# Add src to path
sys.path.insert(0, 'src')

# Import Lambda handler using importlib to avoid "lambda" keyword issue
lambda_module = importlib.import_module('src.lambda.auth.main')
handler = lambda_module.handler


def create_api_event(method, path, body=None, headers=None):
    """Tạo AWS Lambda event object để test API"""
    event = {
        "httpMethod": method,
        "resource": path,
        "headers": headers or {},
        "pathParameters": None,
        "queryStringParameters": None,
    }
    
    if body:
        event["body"] = json.dumps(body) if isinstance(body, dict) else body
    else:
        event["body"] = None
        
    return event


def test_cors_preflight():
    """Test CORS preflight request"""
    print("🔄 Testing CORS preflight...")
    event = create_api_event("OPTIONS", "/auth/register")
    response = handler(event, None)
    
    print(f"Status Code: {response['statusCode']}")
    print(f"Response: {json.dumps(json.loads(response['body']), indent=2)}")
    print()


def test_register():
    """Test user registration"""
    print("🔄 Testing user registration...")
    event = create_api_event("POST", "/auth/register", {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPass123"
    })
    
    response = handler(event, None)
    print(f"Status Code: {response['statusCode']}")
    print(f"Response: {json.dumps(json.loads(response['body']), indent=2)}")
    print()


def test_login():
    """Test user login"""
    print("🔄 Testing user login...")
    event = create_api_event("POST", "/auth/login", {
        "email": "test@example.com",
        "password": "TestPass123"
    })
    
    response = handler(event, None)
    print(f"Status Code: {response['statusCode']}")
    print(f"Response: {json.dumps(json.loads(response['body']), indent=2)}")
    print()


def test_invalid_endpoint():
    """Test invalid endpoint"""
    print("🔄 Testing invalid endpoint...")
    event = create_api_event("GET", "/invalid/endpoint")
    response = handler(event, None)
    
    print(f"Status Code: {response['statusCode']}")
    print(f"Response: {json.dumps(json.loads(response['body']), indent=2)}")
    print()


def test_invalid_json():
    """Test invalid JSON body"""
    print("🔄 Testing invalid JSON...")
    event = create_api_event("POST", "/auth/register")
    event["body"] = "invalid json"
    
    response = handler(event, None)
    print(f"Status Code: {response['statusCode']}")
    print(f"Response: {json.dumps(json.loads(response['body']), indent=2)}")
    print()


if __name__ == "__main__":
    print("🚀 Testing Reddit Clone Backend API locally...\n")
    
    # Run tests
    test_cors_preflight()
    test_register()
    test_login()
    test_invalid_endpoint()
    test_invalid_json()
    
    print("✅ API testing completed!")
