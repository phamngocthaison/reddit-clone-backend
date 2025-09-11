"""Authentication service for Reddit Clone Backend."""

import logging
from datetime import datetime
from typing import Dict, Any

from botocore.exceptions import ClientError
from pydantic import ValidationError

from ..shared.aws_clients import aws_clients
from ..shared.models import (
    User,
    RegisterRequest,
    LoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserResponse,
    LoginResponse,
)
from ..shared.utils import (
    generate_user_id,
    get_current_timestamp,
    get_current_timestamp_str,
    validate_email,
    validate_password,
    validate_username,
)

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service."""

    def __init__(self) -> None:
        self.cognito = aws_clients.get_cognito_client()
        self.users_table = aws_clients.get_users_table()
        self.user_pool_id = aws_clients.get_user_pool_id()
        self.client_id = aws_clients.get_client_id()

    async def register(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new user."""
        try:
            # Validate request
            request = RegisterRequest(**request_data)
        except ValidationError as e:
            raise ValueError(f"Invalid request data: {e}")

        # Additional validation
        if not validate_email(request.email):
            raise ValueError("Invalid email format")
        
        if not validate_username(request.username):
            raise ValueError("Username must be 3-20 characters, alphanumeric and underscores only")
        
        if not validate_password(request.password):
            raise ValueError("Password must be at least 8 characters with uppercase, lowercase, and numbers")

        try:
            # Check if user already exists
            await self._check_user_exists(request.email, request.username)

            # Generate user ID
            user_id = generate_user_id()
            current_time = get_current_timestamp()
            current_time_str = get_current_timestamp_str()

            # Create user in Cognito
            self.cognito.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=request.email,
                UserAttributes=[
                    {"Name": "email", "Value": request.email},
                    {"Name": "email_verified", "Value": "true"},
                    {"Name": "preferred_username", "Value": request.username},
                    {"Name": "custom:userId", "Value": user_id},
                ],
                MessageAction="SUPPRESS",  # Don't send welcome email
                TemporaryPassword="TempPass123!",  # Temporary password
            )

            # Set permanent password
            self.cognito.admin_set_user_password(
                UserPoolId=self.user_pool_id,
                Username=request.email,
                Password=request.password,
                Permanent=True,
            )

            # Create user record in DynamoDB
            user_data = {
                "userId": user_id,
                "email": request.email,
                "username": request.username,
                "createdAt": current_time_str,
                "updatedAt": current_time_str,
                "isActive": True,
            }

            self.users_table.put_item(
                Item=user_data,
                ConditionExpression="attribute_not_exists(userId)",
            )

            # Return user data
            user_response = UserResponse(
                userId=user_id,
                email=request.email,
                username=request.username,
                createdAt=current_time,
                isActive=True,
            )

            return {"user": user_response.dict(by_alias=True)}

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "UsernameExistsException":
                raise ValueError("User with this email already exists")
            logger.error(f"Cognito error: {e}")
            raise ValueError(f"Registration failed: {e}")
        except Exception as e:
            logger.error(f"Registration error: {e}")
            raise ValueError(f"Registration failed: {e}")

    async def login(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Login user."""
        try:
            # Validate request
            request = LoginRequest(**request_data)
        except ValidationError as e:
            raise ValueError(f"Invalid request data: {e}")

        if not validate_email(request.email):
            raise ValueError("Invalid email format")

        try:
            # Authenticate with Cognito
            auth_response = self.cognito.admin_initiate_auth(
                UserPoolId=self.user_pool_id,
                ClientId=self.client_id,
                AuthFlow="ADMIN_NO_SRP_AUTH",
                AuthParameters={
                    "USERNAME": request.email,
                    "PASSWORD": request.password,
                },
            )

            if "AuthenticationResult" not in auth_response:
                raise ValueError("Authentication failed")

            auth_result = auth_response["AuthenticationResult"]

            # Get user from DynamoDB
            user_record = await self._get_user_by_email(request.email)

            # Create response
            user_response = UserResponse(
                userId=user_record["userId"],
                email=user_record["email"],
                username=user_record["username"],
                createdAt=datetime.fromisoformat(user_record["createdAt"].replace("Z", "+00:00")),
                isActive=user_record["isActive"],
            )

            login_response = LoginResponse(
                user=user_response,
                accessToken=auth_result["AccessToken"],
                refreshToken=auth_result["RefreshToken"],
                idToken=auth_result["IdToken"],
            )

            return login_response.dict(by_alias=True)

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "NotAuthorizedException":
                raise ValueError("Invalid credentials")
            elif error_code == "UserNotFoundException":
                raise ValueError("User not found")
            logger.error(f"Cognito error: {e}")
            raise ValueError(f"Login failed: {e}")
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise ValueError(f"Login failed: {e}")

    async def logout(self, access_token: str) -> None:
        """Logout user."""
        try:
            self.cognito.global_sign_out(AccessToken=access_token)
        except ClientError as e:
            logger.error(f"Logout error: {e}")
            raise ValueError("Logout failed")

    async def forgot_password(self, request_data: Dict[str, Any]) -> None:
        """Send forgot password code."""
        try:
            # Validate request
            request = ForgotPasswordRequest(**request_data)
        except ValidationError as e:
            raise ValueError(f"Invalid request data: {e}")

        if not validate_email(request.email):
            raise ValueError("Invalid email format")

        try:
            self.cognito.forgot_password(
                ClientId=self.client_id,
                Username=request.email,
            )
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "UserNotFoundException":
                raise ValueError("User not found")
            logger.error(f"Forgot password error: {e}")
            raise ValueError("Failed to send password reset code")

    async def reset_password(self, request_data: Dict[str, Any]) -> None:
        """Reset user password."""
        try:
            # Validate request
            request = ResetPasswordRequest(**request_data)
        except ValidationError as e:
            raise ValueError(f"Invalid request data: {e}")

        if not validate_password(request.new_password):
            raise ValueError("Password must be at least 8 characters with uppercase, lowercase, and numbers")

        try:
            self.cognito.confirm_forgot_password(
                ClientId=self.client_id,
                Username=request.email,
                ConfirmationCode=request.confirmation_code,
                Password=request.new_password,
            )

            # Update user record in DynamoDB
            await self._update_user_timestamp(request.email)

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "CodeMismatchException":
                raise ValueError("Invalid confirmation code")
            elif error_code == "ExpiredCodeException":
                raise ValueError("Confirmation code has expired")
            logger.error(f"Reset password error: {e}")
            raise ValueError("Failed to reset password")

    async def _check_user_exists(self, email: str, username: str) -> None:
        """Check if user already exists."""
        try:
            response = self.users_table.query(
                IndexName="EmailIndex",
                KeyConditionExpression="email = :email",
                ExpressionAttributeValues={":email": email},
            )

            if response.get("Items"):
                raise ValueError("User with this email already exists")

        except ClientError as e:
            if "already exists" in str(e):
                raise
            logger.warning(f"Error checking user existence: {e}")

    async def _get_user_by_email(self, email: str) -> Dict[str, Any]:
        """Get user by email."""
        try:
            response = self.users_table.query(
                IndexName="EmailIndex",
                KeyConditionExpression="email = :email",
                ExpressionAttributeValues={":email": email},
            )

            items = response.get("Items", [])
            if not items:
                raise ValueError("User not found")

            return items[0]

        except ClientError as e:
            logger.error(f"Get user by email error: {e}")
            raise ValueError("Failed to retrieve user")

    async def _update_user_timestamp(self, email: str) -> None:
        """Update user timestamp."""
        try:
            user = await self._get_user_by_email(email)
            
            self.users_table.put_item(
                Item={
                    **user,
                    "updatedAt": get_current_timestamp().isoformat() + "Z",
                }
            )
        except Exception as e:
            logger.warning(f"Failed to update user timestamp: {e}")
            # Don't raise error as this is not critical
