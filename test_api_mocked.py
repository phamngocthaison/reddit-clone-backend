#!/usr/bin/env python3
"""
Script để test API với mocked AWS services
"""

import json
import os
import sys
import importlib
import boto3
from moto import mock_aws

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


@mock_aws
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
def test_complete_user_flow():
    """Test complete user registration and login flow"""
    print("🚀 Testing complete user flow with mocked AWS services...\n")
    
    # Setup mocked AWS services
    setup_mocked_aws()
    
    # Import handler after setting up mocks
    lambda_module = importlib.import_module('src.lambda.auth.main')
    handler = lambda_module.handler
    
    # Test 1: CORS preflight
    print("🔄 Testing CORS preflight...")
    event = create_api_event("OPTIONS", "/auth/register")
    response = handler(event, None)
    print(f"✅ Status: {response['statusCode']}")
    print(f"Response: {json.loads(response['body'])['message']}\n")
    
    # Test 2: User registration
    print("🔄 Testing user registration...")
    event = create_api_event("POST", "/auth/register", {
        "email": "john@example.com",
        "username": "johndoe",
        "password": "SecurePass123"
    })
    response = handler(event, None)
    print(f"Status: {response['statusCode']}")
    response_data = json.loads(response['body'])
    
    if response['statusCode'] == 200:
        print("✅ Registration successful!")
        print(f"User ID: {response_data['data']['user']['userId']}")
        print(f"Email: {response_data['data']['user']['email']}")
        print(f"Username: {response_data['data']['user']['username']}")
    else:
        print("❌ Registration failed:")
        print(f"Error: {response_data['error']['message']}")
    print()
    
    # Test 3: User login
    print("🔄 Testing user login...")
    event = create_api_event("POST", "/auth/login", {
        "email": "john@example.com",
        "password": "SecurePass123"
    })
    response = handler(event, None)
    print(f"Status: {response['statusCode']}")
    response_data = json.loads(response['body'])
    
    if response['statusCode'] == 200:
        print("✅ Login successful!")
        print(f"Access Token: {response_data['data']['accessToken'][:50]}...")
        print(f"User: {response_data['data']['user']['username']}")
        access_token = response_data['data']['accessToken']
    else:
        print("❌ Login failed:")
        print(f"Error: {response_data['error']['message']}")
        access_token = None
    print()
    
    # Test 4: Forgot password
    print("🔄 Testing forgot password...")
    event = create_api_event("POST", "/auth/forgot-password", {
        "email": "john@example.com"
    })
    response = handler(event, None)
    print(f"Status: {response['statusCode']}")
    response_data = json.loads(response['body'])
    
    if response['statusCode'] == 200:
        print("✅ Password reset email sent!")
    else:
        print("❌ Forgot password failed:")
        print(f"Error: {response_data['error']['message']}")
    print()
    
    # Test 5: Logout (if we have access token)
    if access_token:
        print("🔄 Testing user logout...")
        event = create_api_event("POST", "/auth/logout", {}, {
            "Authorization": f"Bearer {access_token}"
        })
        response = handler(event, None)
        print(f"Status: {response['statusCode']}")
        response_data = json.loads(response['body'])
        
        if response['statusCode'] == 200:
            print("✅ Logout successful!")
        else:
            print("❌ Logout failed:")
            print(f"Error: {response_data['error']['message']}")
        print()
    
    # Test 6: Invalid data validation
    print("🔄 Testing invalid email validation...")
    event = create_api_event("POST", "/auth/register", {
        "email": "invalid-email",
        "username": "testuser",
        "password": "TestPass123"
    })
    response = handler(event, None)
    print(f"Status: {response['statusCode']}")
    response_data = json.loads(response['body'])
    
    if response['statusCode'] == 400:
        print("✅ Email validation working!")
        print(f"Error message: {response_data['error']['message']}")
    else:
        print("❌ Email validation failed")
    print()
    
    print("✅ Complete API testing finished!")


if __name__ == "__main__":
    test_complete_user_flow()
