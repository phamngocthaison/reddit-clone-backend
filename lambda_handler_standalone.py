"""Standalone Lambda handler with all dependencies included."""

import asyncio
import json
import logging
import os
import re
import time
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel, EmailStr, Field, ValidationError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ============================================================================
# MODELS
# ============================================================================

class User(BaseModel):
    """User model."""
    user_id: str = Field(..., alias="userId")
    email: EmailStr
    username: str
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    is_active: bool = Field(..., alias="isActive")

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }

class RegisterRequest(BaseModel):
    """User registration request model."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8)

class LoginRequest(BaseModel):
    """User login request model."""
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    """Forgot password request model."""
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    """Reset password request model."""
    email: EmailStr
    confirmation_code: str = Field(..., alias="confirmationCode")
    new_password: str = Field(..., min_length=8, alias="newPassword")

    class Config:
        populate_by_name = True

class AuthResponse(BaseModel):
    """Authentication response model."""
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

class UserResponse(BaseModel):
    """User response model."""
    user_id: str = Field(..., alias="userId")
    email: EmailStr
    username: str
    created_at: datetime = Field(..., alias="createdAt")
    is_active: bool = Field(..., alias="isActive")

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }

class LoginResponse(BaseModel):
    """Login response model."""
    user: UserResponse
    access_token: str = Field(..., alias="accessToken")
    refresh_token: str = Field(..., alias="refreshToken")
    id_token: str = Field(..., alias="idToken")

    class Config:
        populate_by_name = True

# ============================================================================
# UTILITIES
# ============================================================================

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat() + "Z"
        return super().default(obj)

def create_response(status_code: int, body: AuthResponse) -> Dict[str, Any]:
    """Create API Gateway response."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
        "body": json.dumps(body.dict(by_alias=True), cls=DateTimeEncoder),
    }

def create_success_response(data: Optional[Any] = None, message: Optional[str] = None) -> Dict[str, Any]:
    """Create success response."""
    response = AuthResponse(success=True, message=message, data=data)
    return create_response(200, response)

def create_error_response(status_code: int, code: str, message: str) -> Dict[str, Any]:
    """Create error response."""
    response = AuthResponse(success=False, error={"code": code, "message": message})
    return create_response(status_code, response)

def parse_request_body(body: Optional[str]) -> Dict[str, Any]:
    """Parse request body from JSON string."""
    if not body:
        raise ValueError("Request body is required")

    try:
        return json.loads(body)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in request body: {e}")

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
    return re.match(pattern, email) is not None

def validate_password(password: str) -> bool:
    """Validate password strength."""
    if len(password) < 8:
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True

def validate_username(username: str) -> bool:
    """Validate username format."""
    pattern = r"^[a-zA-Z0-9_]{3,20}$"
    return re.match(pattern, username) is not None

def generate_user_id() -> str:
    """Generate a unique user ID."""
    timestamp = int(time.time())
    unique_id = str(uuid.uuid4()).replace("-", "")[:15]
    return f"user_{timestamp}_{unique_id}"

def get_current_timestamp() -> datetime:
    """Get current timestamp as datetime object."""
    return datetime.utcnow()

def get_current_timestamp_str() -> str:
    """Get current timestamp as ISO string."""
    return datetime.utcnow().isoformat() + "Z"

# ============================================================================
# AWS CLIENTS
# ============================================================================

class AWSClientManager:
    """Manages AWS clients."""
    
    def __init__(self):
        self._cognito = None
        self._dynamodb = None
        self._users_table = None
        self._user_pool_id = None
        self._client_id = None
    
    def get_cognito_client(self):
        """Get Cognito client."""
        if not self._cognito:
            self._cognito = boto3.client('cognito-idp', region_name=os.environ.get('REGION', 'ap-southeast-1'))
        return self._cognito
    
    def get_dynamodb(self):
        """Get DynamoDB resource."""
        if not self._dynamodb:
            self._dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('REGION', 'ap-southeast-1'))
        return self._dynamodb
    
    def get_users_table(self):
        """Get users table."""
        if not self._users_table:
            dynamodb = self.get_dynamodb()
            self._users_table = dynamodb.Table(os.environ.get('USERS_TABLE', 'reddit-clone-users'))
        return self._users_table
    
    def get_user_pool_id(self):
        """Get user pool ID."""
        if not self._user_pool_id:
            self._user_pool_id = os.environ.get('USER_POOL_ID')
        return self._user_pool_id
    
    def get_client_id(self):
        """Get client ID."""
        if not self._client_id:
            self._client_id = os.environ.get('CLIENT_ID')
        return self._client_id

# Global AWS clients manager
aws_clients = AWSClientManager()

# ============================================================================
# AUTH SERVICE
# ============================================================================

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
                    "updatedAt": get_current_timestamp_str(),
                }
            )
        except Exception as e:
            logger.warning(f"Failed to update user timestamp: {e}")
            # Don't raise error as this is not critical

# ============================================================================
# LAMBDA HANDLER
# ============================================================================

# Initialize auth service
auth_service = AuthService()

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for authentication endpoints."""
    logger.info(f"Event: {json.dumps(event)}")

    try:
        # Get path and method
        resource = event.get("resource", "")
        method = event.get("httpMethod", "")

        # Handle preflight OPTIONS requests
        if method == "OPTIONS":
            return create_success_response(message="CORS preflight")

        # Route to appropriate handler based on path
        if resource == "/auth/register" and method == "POST":
            return asyncio.run(handle_register(event))
        elif resource == "/auth/login" and method == "POST":
            return asyncio.run(handle_login(event))
        elif resource == "/auth/logout" and method == "POST":
            return asyncio.run(handle_logout(event))
        elif resource == "/auth/forgot-password" and method == "POST":
            return asyncio.run(handle_forgot_password(event))
        elif resource == "/auth/reset-password" and method == "POST":
            return asyncio.run(handle_reset_password(event))
        else:
            return create_error_response(404, "NOT_FOUND", "Endpoint not found")

    except Exception as e:
        logger.error(f"Lambda handler error: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Internal server error")

async def handle_register(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle user registration."""
    try:
        body = parse_request_body(event.get("body"))
        result = await auth_service.register(body)
        return create_success_response(result, "User registered successfully")
    except ValueError as e:
        logger.error(f"Register error: {e}")
        return create_error_response(400, "REGISTRATION_ERROR", str(e))
    except Exception as e:
        logger.error(f"Register error: {e}")
        return create_error_response(500, "REGISTRATION_ERROR", "Registration failed")

async def handle_login(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle user login."""
    try:
        body = parse_request_body(event.get("body"))
        result = await auth_service.login(body)
        return create_success_response(result, "Login successful")
    except ValueError as e:
        logger.error(f"Login error: {e}")
        return create_error_response(400, "LOGIN_ERROR", str(e))
    except Exception as e:
        logger.error(f"Login error: {e}")
        return create_error_response(500, "LOGIN_ERROR", "Login failed")

async def handle_logout(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle user logout."""
    try:
        headers = event.get("headers", {})
        auth_header = headers.get("Authorization") or headers.get("authorization")
        
        if not auth_header:
            return create_error_response(401, "UNAUTHORIZED", "Authorization header required")
        
        token = auth_header.replace("Bearer ", "")
        await auth_service.logout(token)
        return create_success_response(message="Logout successful")
    except ValueError as e:
        logger.error(f"Logout error: {e}")
        return create_error_response(400, "LOGOUT_ERROR", str(e))
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return create_error_response(500, "LOGOUT_ERROR", "Logout failed")

async def handle_forgot_password(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle forgot password request."""
    try:
        body = parse_request_body(event.get("body"))
        await auth_service.forgot_password(body)
        return create_success_response(message="Password reset code sent to email")
    except ValueError as e:
        logger.error(f"Forgot password error: {e}")
        return create_error_response(400, "FORGOT_PASSWORD_ERROR", str(e))
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        return create_error_response(500, "FORGOT_PASSWORD_ERROR", "Failed to send password reset code")

async def handle_reset_password(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle password reset."""
    try:
        body = parse_request_body(event.get("body"))
        await auth_service.reset_password(body)
        return create_success_response(message="Password reset successfully")
    except ValueError as e:
        logger.error(f"Reset password error: {e}")
        return create_error_response(400, "RESET_PASSWORD_ERROR", str(e))
    except Exception as e:
        logger.error(f"Reset password error: {e}")
        return create_error_response(500, "RESET_PASSWORD_ERROR", "Failed to reset password")
