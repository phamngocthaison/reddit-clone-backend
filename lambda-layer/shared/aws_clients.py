"""AWS clients configuration."""

import os
from typing import Optional

import boto3
from botocore.exceptions import ClientError


class AWSClients:
    """AWS clients singleton."""

    _instance: Optional["AWSClients"] = None
    
    def __new__(cls) -> "AWSClients":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_initialized"):
            return
        
        self.region = os.getenv("AWS_REGION", "ap-southeast-1")
        self.user_pool_id = os.getenv("USER_POOL_ID")
        self.client_id = os.getenv("USER_POOL_CLIENT_ID")
        self.users_table = os.getenv("USERS_TABLE_NAME")

        # Initialize AWS clients
        self.cognito_client = boto3.client("cognito-idp", region_name=self.region)
        self.dynamodb = boto3.resource("dynamodb", region_name=self.region)
        
        if self.users_table:
            self.users_table_resource = self.dynamodb.Table(self.users_table)
        else:
            raise ValueError("USERS_TABLE_NAME environment variable is required")

        self._initialized = True

    def get_cognito_client(self) -> boto3.client:
        """Get Cognito client."""
        return self.cognito_client

    def get_users_table(self) -> boto3.resource:
        """Get DynamoDB users table resource."""
        return self.users_table_resource

    def get_user_pool_id(self) -> str:
        """Get Cognito User Pool ID."""
        if not self.user_pool_id:
            raise ValueError("USER_POOL_ID environment variable is required")
        return self.user_pool_id

    def get_client_id(self) -> str:
        """Get Cognito Client ID."""
        if not self.client_id:
            raise ValueError("CLIENT_ID environment variable is required")
        return self.client_id


# Global instance
aws_clients = AWSClients()
