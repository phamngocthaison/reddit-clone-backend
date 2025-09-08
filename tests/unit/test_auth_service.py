"""Unit tests for authentication service."""

import pytest
from unittest.mock import patch, MagicMock
from src.lambda.auth.auth_service import AuthService


class TestAuthService:
    """Test cases for AuthService."""

    @pytest.mark.asyncio
    async def test_register_validation_success(self, sample_user_data):
        """Test successful registration validation."""
        with patch("src.lambda.auth.auth_service.aws_clients") as mock_clients:
            # Setup mocks
            mock_cognito = MagicMock()
            mock_table = MagicMock()
            mock_clients.get_cognito_client.return_value = mock_cognito
            mock_clients.get_users_table.return_value = mock_table
            mock_clients.get_user_pool_id.return_value = "test-pool-id"
            mock_clients.get_client_id.return_value = "test-client-id"
            
            # Mock DynamoDB query (no existing user)
            mock_table.query.return_value = {"Items": []}
            
            # Mock Cognito responses
            mock_cognito.admin_create_user.return_value = {}
            mock_cognito.admin_set_user_password.return_value = {}
            
            # Mock DynamoDB put_item
            mock_table.put_item.return_value = {}
            
            auth_service = AuthService()
            result = await auth_service.register(sample_user_data)
            
            # Assertions
            assert "user" in result
            assert result["user"]["email"] == sample_user_data["email"]
            assert result["user"]["username"] == sample_user_data["username"]
            assert result["user"]["isActive"] is True

    @pytest.mark.asyncio
    async def test_register_invalid_email(self):
        """Test registration with invalid email."""
        with patch("src.lambda.auth.auth_service.aws_clients"):
            auth_service = AuthService()
            
            invalid_data = {
                "email": "invalid-email",
                "username": "testuser",
                "password": "TestPass123"
            }
            
            with pytest.raises(ValueError, match="Invalid email format"):
                await auth_service.register(invalid_data)

    @pytest.mark.asyncio
    async def test_register_weak_password(self):
        """Test registration with weak password."""
        with patch("src.lambda.auth.auth_service.aws_clients"):
            auth_service = AuthService()
            
            invalid_data = {
                "email": "test@example.com",
                "username": "testuser",
                "password": "weak"
            }
            
            with pytest.raises(ValueError, match="Password must be at least 8 characters"):
                await auth_service.register(invalid_data)

    @pytest.mark.asyncio
    async def test_register_invalid_username(self):
        """Test registration with invalid username."""
        with patch("src.lambda.auth.auth_service.aws_clients"):
            auth_service = AuthService()
            
            invalid_data = {
                "email": "test@example.com",
                "username": "a",  # Too short
                "password": "TestPass123"
            }
            
            with pytest.raises(ValueError, match="Username must be 3-20 characters"):
                await auth_service.register(invalid_data)

    @pytest.mark.asyncio
    async def test_register_user_already_exists(self, sample_user_data):
        """Test registration when user already exists."""
        with patch("src.lambda.auth.auth_service.aws_clients") as mock_clients:
            # Setup mocks
            mock_table = MagicMock()
            mock_clients.get_users_table.return_value = mock_table
            
            # Mock existing user
            mock_table.query.return_value = {
                "Items": [{"userId": "existing-user", "email": sample_user_data["email"]}]
            }
            
            auth_service = AuthService()
            
            with pytest.raises(ValueError, match="User with this email already exists"):
                await auth_service.register(sample_user_data)

    @pytest.mark.asyncio
    async def test_login_success(self, sample_user_data):
        """Test successful login."""
        with patch("src.lambda.auth.auth_service.aws_clients") as mock_clients:
            # Setup mocks
            mock_cognito = MagicMock()
            mock_table = MagicMock()
            mock_clients.get_cognito_client.return_value = mock_cognito
            mock_clients.get_users_table.return_value = mock_table
            mock_clients.get_user_pool_id.return_value = "test-pool-id"
            mock_clients.get_client_id.return_value = "test-client-id"
            
            # Mock Cognito auth response
            mock_cognito.admin_initiate_auth.return_value = {
                "AuthenticationResult": {
                    "AccessToken": "access-token",
                    "RefreshToken": "refresh-token",
                    "IdToken": "id-token",
                }
            }
            
            # Mock DynamoDB user lookup
            mock_table.query.return_value = {
                "Items": [{
                    "userId": "test-user-id",
                    "email": sample_user_data["email"],
                    "username": sample_user_data["username"],
                    "createdAt": "2023-01-01T00:00:00.000Z",
                    "isActive": True,
                }]
            }
            
            auth_service = AuthService()
            login_data = {
                "email": sample_user_data["email"],
                "password": sample_user_data["password"],
            }
            
            result = await auth_service.login(login_data)
            
            # Assertions
            assert "user" in result
            assert "accessToken" in result
            assert "refreshToken" in result
            assert "idToken" in result
            assert result["user"]["email"] == sample_user_data["email"]

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, sample_user_data):
        """Test login with invalid credentials."""
        with patch("src.lambda.auth.auth_service.aws_clients") as mock_clients:
            # Setup mocks
            mock_cognito = MagicMock()
            mock_clients.get_cognito_client.return_value = mock_cognito
            mock_clients.get_user_pool_id.return_value = "test-pool-id"
            mock_clients.get_client_id.return_value = "test-client-id"
            
            # Mock Cognito auth failure
            from botocore.exceptions import ClientError
            mock_cognito.admin_initiate_auth.side_effect = ClientError(
                error_response={"Error": {"Code": "NotAuthorizedException"}},
                operation_name="AdminInitiateAuth"
            )
            
            auth_service = AuthService()
            login_data = {
                "email": sample_user_data["email"],
                "password": "wrong-password",
            }
            
            with pytest.raises(ValueError, match="Invalid credentials"):
                await auth_service.login(login_data)

    @pytest.mark.asyncio
    async def test_forgot_password_success(self):
        """Test successful forgot password request."""
        with patch("src.lambda.auth.auth_service.aws_clients") as mock_clients:
            # Setup mocks
            mock_cognito = MagicMock()
            mock_clients.get_cognito_client.return_value = mock_cognito
            mock_clients.get_client_id.return_value = "test-client-id"
            
            mock_cognito.forgot_password.return_value = {}
            
            auth_service = AuthService()
            request_data = {"email": "test@example.com"}
            
            # Should not raise any exception
            await auth_service.forgot_password(request_data)
            
            # Verify Cognito was called
            mock_cognito.forgot_password.assert_called_once()

    @pytest.mark.asyncio
    async def test_reset_password_success(self):
        """Test successful password reset."""
        with patch("src.lambda.auth.auth_service.aws_clients") as mock_clients:
            # Setup mocks
            mock_cognito = MagicMock()
            mock_table = MagicMock()
            mock_clients.get_cognito_client.return_value = mock_cognito
            mock_clients.get_users_table.return_value = mock_table
            mock_clients.get_client_id.return_value = "test-client-id"
            
            mock_cognito.confirm_forgot_password.return_value = {}
            
            # Mock user lookup for timestamp update
            mock_table.query.return_value = {
                "Items": [{
                    "userId": "test-user-id",
                    "email": "test@example.com",
                    "username": "testuser",
                    "createdAt": "2023-01-01T00:00:00.000Z",
                    "updatedAt": "2023-01-01T00:00:00.000Z",
                    "isActive": True,
                }]
            }
            mock_table.put_item.return_value = {}
            
            auth_service = AuthService()
            request_data = {
                "email": "test@example.com",
                "confirmationCode": "123456",
                "newPassword": "NewPass123",
            }
            
            # Should not raise any exception
            await auth_service.reset_password(request_data)
            
            # Verify Cognito was called
            mock_cognito.confirm_forgot_password.assert_called_once()

    @pytest.mark.asyncio
    async def test_logout_success(self):
        """Test successful logout."""
        with patch("src.lambda.auth.auth_service.aws_clients") as mock_clients:
            # Setup mocks
            mock_cognito = MagicMock()
            mock_clients.get_cognito_client.return_value = mock_cognito
            
            mock_cognito.global_sign_out.return_value = {}
            
            auth_service = AuthService()
            
            # Should not raise any exception
            await auth_service.logout("access-token")
            
            # Verify Cognito was called
            mock_cognito.global_sign_out.assert_called_once_with(AccessToken="access-token")
