#!/usr/bin/env python3
"""
Flask server để test Reddit Clone API locally
"""

import json
import os
import sys
import importlib
from flask import Flask, request, jsonify
from flask_cors import CORS
from moto import mock_cognitoidp, mock_dynamodb
import boto3

# Setup environment variables
os.environ["USER_POOL_ID"] = "test-user-pool-id"
os.environ["CLIENT_ID"] = "test-client-id"
os.environ["USERS_TABLE"] = "test-users-table"
os.environ["REGION"] = "us-east-1"
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"

# Add src to path
sys.path.insert(0, 'src')

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize mocked AWS services
mock_cognito = mock_cognitoidp()
mock_ddb = mock_dynamodb()

mock_cognito.start()
mock_ddb.start()

# Setup mocked AWS resources
def setup_aws_resources():
    # Setup Cognito
    cognito_client = boto3.client("cognito-idp", region_name="us-east-1")
    
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
        ],
    )
    
    user_pool_id = user_pool_response["UserPool"]["Id"]
    os.environ["USER_POOL_ID"] = user_pool_id
    
    client_response = cognito_client.create_user_pool_client(
        UserPoolId=user_pool_id,
        ClientName="test-client",
        ExplicitAuthFlows=["ADMIN_NO_SRP_AUTH", "USER_PASSWORD_AUTH"],
    )
    
    client_id = client_response["UserPoolClient"]["ClientId"]
    os.environ["CLIENT_ID"] = client_id
    
    # Setup DynamoDB
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    dynamodb.create_table(
        TableName="test-users-table",
        KeySchema=[{"AttributeName": "userId", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "userId", "AttributeType": "S"},
            {"AttributeName": "email", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "EmailIndex",
                "KeySchema": [{"AttributeName": "email", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5,
                },
            }
        ],
        BillingMode="PROVISIONED",
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )

# Setup AWS resources
setup_aws_resources()

# Import Lambda handler
lambda_module = importlib.import_module('src.lambda.auth.main')
handler = lambda_module.handler


def create_lambda_event(method, resource, body=None, headers=None):
    """Convert Flask request to Lambda event format"""
    event = {
        "httpMethod": method,
        "resource": resource,
        "headers": headers or {},
        "pathParameters": None,
        "queryStringParameters": None,
        "body": body
    }
    return event


def lambda_response_to_flask(lambda_response):
    """Convert Lambda response to Flask response"""
    status_code = lambda_response.get("statusCode", 200)
    body = lambda_response.get("body", "{}")
    headers = lambda_response.get("headers", {})
    
    return json.loads(body), status_code, headers


# API Routes
@app.route('/auth/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        event = create_lambda_event('OPTIONS', '/auth/register')
        lambda_response = handler(event, None)
        return lambda_response_to_flask(lambda_response)
    
    body = json.dumps(request.json) if request.json else None
    event = create_lambda_event('POST', '/auth/register', body, dict(request.headers))
    lambda_response = handler(event, None)
    return lambda_response_to_flask(lambda_response)


@app.route('/auth/login', methods=['POST'])
def login():
    body = json.dumps(request.json) if request.json else None
    event = create_lambda_event('POST', '/auth/login', body, dict(request.headers))
    lambda_response = handler(event, None)
    return lambda_response_to_flask(lambda_response)


@app.route('/auth/logout', methods=['POST'])
def logout():
    body = json.dumps(request.json) if request.json else None
    event = create_lambda_event('POST', '/auth/logout', body, dict(request.headers))
    lambda_response = handler(event, None)
    return lambda_response_to_flask(lambda_response)


@app.route('/auth/forgot-password', methods=['POST'])
def forgot_password():
    body = json.dumps(request.json) if request.json else None
    event = create_lambda_event('POST', '/auth/forgot-password', body, dict(request.headers))
    lambda_response = handler(event, None)
    return lambda_response_to_flask(lambda_response)


@app.route('/auth/reset-password', methods=['POST'])
def reset_password():
    body = json.dumps(request.json) if request.json else None
    event = create_lambda_event('POST', '/auth/reset-password', body, dict(request.headers))
    lambda_response = handler(event, None)
    return lambda_response_to_flask(lambda_response)


@app.route('/health', methods=['GET'])
def health():
    return {"status": "healthy", "message": "Reddit Clone API is running!"}, 200


@app.route('/')
def home():
    return {
        "message": "🚀 Reddit Clone Backend API",
        "endpoints": {
            "POST /auth/register": "Register new user",
            "POST /auth/login": "Login user", 
            "POST /auth/logout": "Logout user",
            "POST /auth/forgot-password": "Request password reset",
            "POST /auth/reset-password": "Reset password",
            "GET /health": "Health check"
        }
    }


if __name__ == '__main__':
    print("🚀 Starting Reddit Clone Backend API server...")
    print("📍 Server: http://localhost:5000")
    print("📍 Health check: http://localhost:5000/health")
    print("📍 API endpoints: http://localhost:5000")
    print()
    
    try:
        app.run(debug=True, port=5000, host='0.0.0.0')
    finally:
        # Cleanup
        mock_cognito.stop()
        mock_ddb.stop()
