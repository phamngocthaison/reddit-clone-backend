#!/usr/bin/env python3
"""
Demo script để test tạo user và đăng nhập
"""

import json
import os
import sys
import importlib
import boto3
from moto import mock_aws
from datetime import datetime

# Setup environment variables
os.environ["USER_POOL_ID"] = "test-user-pool-id"
os.environ["CLIENT_ID"] = "test-client-id"
os.environ["USERS_TABLE"] = "test-users-table"
os.environ["REGION"] = "us-east-1"
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"

# Add src to path
sys.path.insert(0, 'src')


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


def setup_mocked_aws():
    """Setup mocked AWS services"""
    # Setup Cognito
    cognito_client = boto3.client("cognito-idp", region_name="us-east-1")
    
    # Create user pool
    user_pool_response = cognito_client.create_user_pool(
        PoolName="test-user-pool",
        Policies={
            "PasswordPolicy": {
                "MinimumLength": 8,
                "RequireUppercase": True,
                "RequireLowercase": True,
                "RequireNumbers": True,
                "RequireSymbols": False,
            }
        },
        Schema=[
            {
                "Name": "email",
                "AttributeDataType": "String",
                "Required": True,
                "Mutable": True,
            },
            {
                "Name": "preferred_username",
                "AttributeDataType": "String",
                "Required": False,
                "Mutable": True,
            },
        ],
    )
    
    user_pool_id = user_pool_response["UserPool"]["Id"]
    os.environ["USER_POOL_ID"] = user_pool_id
    
    # Create user pool client
    client_response = cognito_client.create_user_pool_client(
        UserPoolId=user_pool_id,
        ClientName="test-client",
        ExplicitAuthFlows=[
            "ADMIN_NO_SRP_AUTH",
            "USER_PASSWORD_AUTH",
        ],
    )
    
    client_id = client_response["UserPoolClient"]["ClientId"]
    os.environ["CLIENT_ID"] = client_id
    
    # Setup DynamoDB
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    
    # Create users table
    table = dynamodb.create_table(
        TableName="test-users-table",
        KeySchema=[
            {"AttributeName": "userId", "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "userId", "AttributeType": "S"},
            {"AttributeName": "email", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "EmailIndex",
                "KeySchema": [
                    {"AttributeName": "email", "KeyType": "HASH"},
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5,
                },
            }
        ],
        BillingMode="PROVISIONED",
        ProvisionedThroughput={
            "ReadCapacityUnits": 5,
            "WriteCapacityUnits": 5,
        },
    )
    
    return cognito_client, dynamodb


@mock_aws
def test_user_registration_and_login():
    """Test user registration and login functionality"""
    print("🚀 Demo: Test tạo user và đăng nhập")
    print("=" * 50)
    
    # Setup mocked AWS services
    setup_mocked_aws()
    
    # Import handler after setting up mocks
    lambda_module = importlib.import_module('src.lambda.auth.main')
    handler = lambda_module.handler
    
    # Test 1: User registration
    print("\n📝 Bước 1: Đăng ký user mới")
    print("-" * 30)
    
    registration_data = {
        "email": "demo@example.com",
        "username": "demouser",
        "password": "DemoPass123"
    }
    
    print(f"📧 Email: {registration_data['email']}")
    print(f"👤 Username: {registration_data['username']}")
    print(f"🔒 Password: {registration_data['password']}")
    
    event = create_api_event("POST", "/auth/register", registration_data)
    response = handler(event, None)
    response_data = json.loads(response['body'])
    
    print(f"\n📊 Kết quả đăng ký:")
    print(f"   Status Code: {response['statusCode']}")
    
    if response['statusCode'] == 200:
        print("   ✅ Đăng ký thành công!")
        user_data = response_data['data']['user']
        print(f"   🆔 User ID: {user_data['userId']}")
        print(f"   📧 Email: {user_data['email']}")
        print(f"   👤 Username: {user_data['username']}")
        print(f"   📅 Created: {user_data['createdAt']}")
        print(f"   ✅ Active: {user_data['isActive']}")
    else:
        print("   ❌ Đăng ký thất bại:")
        print(f"   Error: {response_data['error']['message']}")
        return
    
    # Test 2: User login
    print("\n🔐 Bước 2: Đăng nhập")
    print("-" * 30)
    
    login_data = {
        "email": "demo@example.com",
        "password": "DemoPass123"
    }
    
    print(f"📧 Email: {login_data['email']}")
    print(f"🔒 Password: {login_data['password']}")
    
    event = create_api_event("POST", "/auth/login", login_data)
    response = handler(event, None)
    response_data = json.loads(response['body'])
    
    print(f"\n📊 Kết quả đăng nhập:")
    print(f"   Status Code: {response['statusCode']}")
    
    if response['statusCode'] == 200:
        print("   ✅ Đăng nhập thành công!")
        login_result = response_data['data']
        user_info = login_result['user']
        print(f"   🆔 User ID: {user_info['userId']}")
        print(f"   👤 Username: {user_info['username']}")
        print(f"   🔑 Access Token: {login_result['accessToken'][:50]}...")
        print(f"   🔄 Refresh Token: {login_result['refreshToken'][:50]}...")
        print(f"   🆔 ID Token: {login_result['idToken'][:50]}...")
    else:
        print("   ❌ Đăng nhập thất bại:")
        print(f"   Error: {response_data['error']['message']}")
    
    # Test 3: Validation errors
    print("\n⚠️  Bước 3: Test validation errors")
    print("-" * 30)
    
    # Test invalid email
    print("📧 Test invalid email:")
    invalid_email_data = {
        "email": "invalid-email",
        "username": "testuser",
        "password": "TestPass123"
    }
    
    event = create_api_event("POST", "/auth/register", invalid_email_data)
    response = handler(event, None)
    response_data = json.loads(response['body'])
    
    if response['statusCode'] == 400:
        print("   ✅ Email validation working!")
        print(f"   Error: {response_data['error']['message']}")
    else:
        print("   ❌ Email validation failed")
    
    # Test weak password
    print("\n🔒 Test weak password:")
    weak_password_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "weak"
    }
    
    event = create_api_event("POST", "/auth/register", weak_password_data)
    response = handler(event, None)
    response_data = json.loads(response['body'])
    
    if response['statusCode'] == 400:
        print("   ✅ Password validation working!")
        print(f"   Error: {response_data['error']['message']}")
    else:
        print("   ❌ Password validation failed")
    
    print("\n🎉 Demo hoàn thành!")
    print("=" * 50)


if __name__ == "__main__":
    test_user_registration_and_login()
