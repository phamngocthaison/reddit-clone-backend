"""Integration tests for Lambda handler."""

import json
import pytest
from unittest.mock import patch
import importlib
# Use importlib to import from directory named 'lambda' (reserved keyword)
lambda_module = importlib.import_module('src.lambda.auth.main')
handler = lambda_module.handler


class TestLambdaHandler:
    """Test cases for Lambda handler."""

    def test_options_request(self):
        """Test OPTIONS request for CORS."""
        event = {
            "httpMethod": "OPTIONS",
            "resource": "/auth/register",
            "headers": {},
            "body": None,
        }
        
        response = handler(event, None)
        
        assert response["statusCode"] == 200
        assert "Access-Control-Allow-Origin" in response["headers"]
        
        body = json.loads(response["body"])
        assert body["success"] is True
        assert body["message"] == "CORS preflight"

    def test_invalid_endpoint(self):
        """Test request to invalid endpoint."""
        event = {
            "httpMethod": "POST",
            "resource": "/invalid/endpoint",
            "headers": {},
            "body": json.dumps({}),
        }
        
        response = handler(event, None)
        
        assert response["statusCode"] == 404
        body = json.loads(response["body"])
        assert body["success"] is False
        assert body["error"]["code"] == "NOT_FOUND"

    def test_register_missing_body(self):
        """Test register request with missing body."""
        event = {
            "httpMethod": "POST",
            "resource": "/auth/register",
            "headers": {},
            "body": None,
        }
        
        response = handler(event, None)
        
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert body["success"] is False
        assert body["error"]["code"] == "REGISTRATION_ERROR"

    def test_register_invalid_json(self):
        """Test register request with invalid JSON."""
        event = {
            "httpMethod": "POST",
            "resource": "/auth/register",
            "headers": {},
            "body": "invalid json",
        }
        
        response = handler(event, None)
        
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert body["success"] is False
        assert body["error"]["code"] == "REGISTRATION_ERROR"

    @patch("src.lambda.auth.main.auth_service")
    def test_register_success(self, mock_auth_service):
        """Test successful registration."""
        # Mock the auth service
        mock_auth_service.register.return_value = {
            "user": {
                "userId": "test-user-id",
                "email": "test@example.com",
                "username": "testuser",
                "createdAt": "2023-01-01T00:00:00.000Z",
                "isActive": True,
            }
        }
        
        event = {
            "httpMethod": "POST",
            "resource": "/auth/register",
            "headers": {},
            "body": json.dumps({
                "email": "test@example.com",
                "username": "testuser",
                "password": "TestPass123",
            }),
        }
        
        response = handler(event, None)
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["success"] is True
        assert body["message"] == "User registered successfully"
        assert "user" in body["data"]

    @patch("src.lambda.auth.main.auth_service")
    def test_login_success(self, mock_auth_service):
        """Test successful login."""
        # Mock the auth service
        mock_auth_service.login.return_value = {
            "user": {
                "userId": "test-user-id",
                "email": "test@example.com",
                "username": "testuser",
                "createdAt": "2023-01-01T00:00:00.000Z",
                "isActive": True,
            },
            "accessToken": "access-token",
            "refreshToken": "refresh-token",
            "idToken": "id-token",
        }
        
        event = {
            "httpMethod": "POST",
            "resource": "/auth/login",
            "headers": {},
            "body": json.dumps({
                "email": "test@example.com",
                "password": "TestPass123",
            }),
        }
        
        response = handler(event, None)
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["success"] is True
        assert body["message"] == "Login successful"
        assert "user" in body["data"]
        assert "accessToken" in body["data"]

    def test_logout_missing_auth_header(self):
        """Test logout request without authorization header."""
        event = {
            "httpMethod": "POST",
            "resource": "/auth/logout",
            "headers": {},
            "body": json.dumps({}),
        }
        
        response = handler(event, None)
        
        assert response["statusCode"] == 401
        body = json.loads(response["body"])
        assert body["success"] is False
        assert body["error"]["code"] == "UNAUTHORIZED"

    @patch("src.lambda.auth.main.auth_service")
    def test_logout_success(self, mock_auth_service):
        """Test successful logout."""
        # Mock the auth service
        mock_auth_service.logout.return_value = None
        
        event = {
            "httpMethod": "POST",
            "resource": "/auth/logout",
            "headers": {
                "Authorization": "Bearer access-token"
            },
            "body": json.dumps({}),
        }
        
        response = handler(event, None)
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["success"] is True
        assert body["message"] == "Logout successful"

    @patch("src.lambda.auth.main.auth_service")
    def test_forgot_password_success(self, mock_auth_service):
        """Test successful forgot password request."""
        # Mock the auth service
        mock_auth_service.forgot_password.return_value = None
        
        event = {
            "httpMethod": "POST",
            "resource": "/auth/forgot-password",
            "headers": {},
            "body": json.dumps({
                "email": "test@example.com"
            }),
        }
        
        response = handler(event, None)
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["success"] is True
        assert body["message"] == "Password reset code sent to email"

    @patch("src.lambda.auth.main.auth_service")
    def test_reset_password_success(self, mock_auth_service):
        """Test successful password reset."""
        # Mock the auth service
        mock_auth_service.reset_password.return_value = None
        
        event = {
            "httpMethod": "POST",
            "resource": "/auth/reset-password",
            "headers": {},
            "body": json.dumps({
                "email": "test@example.com",
                "confirmationCode": "123456",
                "newPassword": "NewPass123",
            }),
        }
        
        response = handler(event, None)
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["success"] is True
        assert body["message"] == "Password reset successfully"

    def test_internal_error_handling(self):
        """Test internal error handling."""
        # Create a malformed event that will cause an exception
        event = {
            # Missing required fields
        }
        
        response = handler(event, None)
        
        assert response["statusCode"] == 500
        body = json.loads(response["body"])
        assert body["success"] is False
        assert body["error"]["code"] == "INTERNAL_ERROR"
