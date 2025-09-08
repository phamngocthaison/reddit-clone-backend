"""Integration tests for Lambda handler."""

import json
import pytest
from unittest.mock import patch
from src.lambda.auth.main import handler


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
        \"\"\"Test register request with invalid JSON.\"\"\"\n        event = {\n            \"httpMethod\": \"POST\",\n            \"resource\": \"/auth/register\",\n            \"headers\": {},\n            \"body\": \"invalid json\",\n        }\n        \n        response = handler(event, None)\n        \n        assert response[\"statusCode\"] == 400\n        body = json.loads(response[\"body\"])\n        assert body[\"success\"] is False\n        assert body[\"error\"][\"code\"] == \"REGISTRATION_ERROR\"\n\n    @patch(\"src.lambda.auth.main.auth_service\")\n    def test_register_success(self, mock_auth_service):\n        \"\"\"Test successful registration.\"\"\"\n        # Mock the auth service\n        mock_auth_service.register.return_value = {\n            \"user\": {\n                \"userId\": \"test-user-id\",\n                \"email\": \"test@example.com\",\n                \"username\": \"testuser\",\n                \"createdAt\": \"2023-01-01T00:00:00.000Z\",\n                \"isActive\": True,\n            }\n        }\n        \n        event = {\n            \"httpMethod\": \"POST\",\n            \"resource\": \"/auth/register\",\n            \"headers\": {},\n            \"body\": json.dumps({\n                \"email\": \"test@example.com\",\n                \"username\": \"testuser\",\n                \"password\": \"TestPass123\",\n            }),\n        }\n        \n        response = handler(event, None)\n        \n        assert response[\"statusCode\"] == 200\n        body = json.loads(response[\"body\"])\n        assert body[\"success\"] is True\n        assert body[\"message\"] == \"User registered successfully\"\n        assert \"user\" in body[\"data\"]\n\n    @patch(\"src.lambda.auth.main.auth_service\")\n    def test_login_success(self, mock_auth_service):\n        \"\"\"Test successful login.\"\"\"\n        # Mock the auth service\n        mock_auth_service.login.return_value = {\n            \"user\": {\n                \"userId\": \"test-user-id\",\n                \"email\": \"test@example.com\",\n                \"username\": \"testuser\",\n                \"createdAt\": \"2023-01-01T00:00:00.000Z\",\n                \"isActive\": True,\n            },\n            \"accessToken\": \"access-token\",\n            \"refreshToken\": \"refresh-token\",\n            \"idToken\": \"id-token\",\n        }\n        \n        event = {\n            \"httpMethod\": \"POST\",\n            \"resource\": \"/auth/login\",\n            \"headers\": {},\n            \"body\": json.dumps({\n                \"email\": \"test@example.com\",\n                \"password\": \"TestPass123\",\n            }),\n        }\n        \n        response = handler(event, None)\n        \n        assert response[\"statusCode\"] == 200\n        body = json.loads(response[\"body\"])\n        assert body[\"success\"] is True\n        assert body[\"message\"] == \"Login successful\"\n        assert \"user\" in body[\"data\"]\n        assert \"accessToken\" in body[\"data\"]\n\n    def test_logout_missing_auth_header(self):\n        \"\"\"Test logout request without authorization header.\"\"\"\n        event = {\n            \"httpMethod\": \"POST\",\n            \"resource\": \"/auth/logout\",\n            \"headers\": {},\n            \"body\": json.dumps({}),\n        }\n        \n        response = handler(event, None)\n        \n        assert response[\"statusCode\"] == 401\n        body = json.loads(response[\"body\"])\n        assert body[\"success\"] is False\n        assert body[\"error\"][\"code\"] == \"UNAUTHORIZED\"\n\n    @patch(\"src.lambda.auth.main.auth_service\")\n    def test_logout_success(self, mock_auth_service):\n        \"\"\"Test successful logout.\"\"\"\n        # Mock the auth service\n        mock_auth_service.logout.return_value = None\n        \n        event = {\n            \"httpMethod\": \"POST\",\n            \"resource\": \"/auth/logout\",\n            \"headers\": {\n                \"Authorization\": \"Bearer access-token\"\n            },\n            \"body\": json.dumps({}),\n        }\n        \n        response = handler(event, None)\n        \n        assert response[\"statusCode\"] == 200\n        body = json.loads(response[\"body\"])\n        assert body[\"success\"] is True\n        assert body[\"message\"] == \"Logout successful\"\n\n    @patch(\"src.lambda.auth.main.auth_service\")\n    def test_forgot_password_success(self, mock_auth_service):\n        \"\"\"Test successful forgot password request.\"\"\"\n        # Mock the auth service\n        mock_auth_service.forgot_password.return_value = None\n        \n        event = {\n            \"httpMethod\": \"POST\",\n            \"resource\": \"/auth/forgot-password\",\n            \"headers\": {},\n            \"body\": json.dumps({\n                \"email\": \"test@example.com\"\n            }),\n        }\n        \n        response = handler(event, None)\n        \n        assert response[\"statusCode\"] == 200\n        body = json.loads(response[\"body\"])\n        assert body[\"success\"] is True\n        assert body[\"message\"] == \"Password reset code sent to email\"\n\n    @patch(\"src.lambda.auth.main.auth_service\")\n    def test_reset_password_success(self, mock_auth_service):\n        \"\"\"Test successful password reset.\"\"\"\n        # Mock the auth service\n        mock_auth_service.reset_password.return_value = None\n        \n        event = {\n            \"httpMethod\": \"POST\",\n            \"resource\": \"/auth/reset-password\",\n            \"headers\": {},\n            \"body\": json.dumps({\n                \"email\": \"test@example.com\",\n                \"confirmationCode\": \"123456\",\n                \"newPassword\": \"NewPass123\",\n            }),\n        }\n        \n        response = handler(event, None)\n        \n        assert response[\"statusCode\"] == 200\n        body = json.loads(response[\"body\"])\n        assert body[\"success\"] is True\n        assert body[\"message\"] == \"Password reset successfully\"\n\n    def test_internal_error_handling(self):\n        \"\"\"Test internal error handling.\"\"\"\n        # Create a malformed event that will cause an exception\n        event = {\n            # Missing required fields\n        }\n        \n        response = handler(event, None)\n        \n        assert response[\"statusCode\"] == 500\n        body = json.loads(response[\"body\"])\n        assert body[\"success\"] is False\n        assert body[\"error\"][\"code\"] == \"INTERNAL_ERROR\"","line_range_start":1,"line_range_end":213}}
</function_results>

<function_calls>
<invoke name="mark_todo_as_done">
<parameter name="todo_ids">["f81ac9ed-7248-4742-b28d-39cf6fb65f28"]
