"""Test configuration and fixtures."""

import os
import pytest
from moto import mock_cognito_idp, mock_dynamodb
import boto3


@pytest.fixture(autouse=True)
def setup_environment():
    """Set up environment variables for testing."""
    os.environ["USER_POOL_ID"] = "test-user-pool-id"
    os.environ["CLIENT_ID"] = "test-client-id"
    os.environ["USERS_TABLE"] = "test-users-table"
    os.environ["REGION"] = "us-east-1"
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture
def mock_cognito():
    """Mock Cognito service."""
    with mock_cognito_idp():
        yield boto3.client("cognito-idp", region_name="us-east-1")


@pytest.fixture
def mock_dynamodb_resource():
    """Mock DynamoDB resource."""
    with mock_dynamodb():
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
        
        yield dynamodb


@pytest.fixture
def cognito_user_pool(mock_cognito):
    """Create a test Cognito user pool."""
    response = mock_cognito.create_user_pool(
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
        UsernameConfiguration={"CaseSensitive": False},
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
    
    user_pool_id = response["UserPool"]["Id"]
    os.environ["USER_POOL_ID"] = user_pool_id
    
    # Create user pool client
    client_response = mock_cognito.create_user_pool_client(
        UserPoolId=user_pool_id,
        ClientName="test-client",
        ExplicitAuthFlows=[
            "ADMIN_NO_SRP_AUTH",
            "USER_PASSWORD_AUTH",
        ],
    )
    
    client_id = client_response["UserPoolClient"]["ClientId"]
    os.environ["CLIENT_ID"] = client_id
    
    return user_pool_id, client_id


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPass123",
    }


@pytest.fixture
def invalid_user_data():
    """Invalid user data for testing."""
    return [
        {"email": "", "username": "testuser", "password": "TestPass123"},
        {"email": "invalid-email", "username": "testuser", "password": "TestPass123"},
        {"email": "test@example.com", "username": "a", "password": "TestPass123"},
        {"email": "test@example.com", "username": "testuser", "password": "weak"},
    ]
