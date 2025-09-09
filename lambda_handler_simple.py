"""
Simple Lambda handler without Pydantic dependencies.
"""

import json
import os
import re
from datetime import datetime
from typing import Any, Dict, Optional

import boto3
from botocore.exceptions import ClientError


# AWS Clients
cognito_client = boto3.client('cognito-idp', region_name=os.environ.get('REGION', 'ap-southeast-1'))
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('REGION', 'ap-southeast-1'))

# Environment variables
USER_POOL_ID = os.environ.get('USER_POOL_ID')
CLIENT_ID = os.environ.get('CLIENT_ID')
USERS_TABLE = os.environ.get('USERS_TABLE')

# Get DynamoDB table
users_table = dynamodb.Table(USERS_TABLE) if USERS_TABLE else None


def validate_email(email: str) -> bool:
    """Simple email validation."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> bool:
    """Simple password validation."""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True


def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Create API Gateway response."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(body, default=str)
    }


def register_user(event: Dict[str, Any]) -> Dict[str, Any]:
    """Register a new user."""
    try:
        body = json.loads(event.get('body', '{}'))
        email = body.get('email', '').strip()
        username = body.get('username', '').strip()
        password = body.get('password', '')

        # Validation
        if not email or not username or not password:
            return create_response(400, {'message': 'Email, username, and password are required'})

        if not validate_email(email):
            return create_response(400, {'message': 'Invalid email format'})

        if not validate_password(password):
            return create_response(400, {'message': 'Password must be at least 8 characters with uppercase, lowercase, and number'})

        if len(username) < 3:
            return create_response(400, {'message': 'Username must be at least 3 characters'})

        # Check if user already exists
        try:
            cognito_client.admin_get_user(
                UserPoolId=USER_POOL_ID,
                Username=email
            )
            return create_response(400, {'message': 'User already exists'})
        except ClientError as e:
            if e.response['Error']['Code'] != 'UserNotFoundException':
                raise

        # Create user in Cognito
        try:
            cognito_client.admin_create_user(
                UserPoolId=USER_POOL_ID,
                Username=email,
                UserAttributes=[
                    {'Name': 'email', 'Value': email},
                    {'Name': 'preferred_username', 'Value': username},
                    {'Name': 'email_verified', 'Value': 'true'}
                ],
                TemporaryPassword=password,
                MessageAction='SUPPRESS'
            )

            # Set permanent password
            cognito_client.admin_set_user_password(
                UserPoolId=USER_POOL_ID,
                Username=email,
                Password=password,
                Permanent=True
            )

            # Create user profile in DynamoDB
            if users_table:
                user_id = f"user_{email.replace('@', '_').replace('.', '_')}"
                users_table.put_item(
                    Item={
                        'userId': user_id,
                        'email': email,
                        'username': username,
                        'createdAt': datetime.utcnow().isoformat(),
                        'updatedAt': datetime.utcnow().isoformat()
                    }
                )

            return create_response(201, {
                'message': 'User registered successfully',
                'userId': user_id if users_table else 'N/A'
            })

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'UsernameExistsException':
                return create_response(400, {'message': 'User already exists'})
            else:
                return create_response(500, {'message': f'Registration failed: {str(e)}'})

    except json.JSONDecodeError:
        return create_response(400, {'message': 'Invalid JSON in request body'})
    except Exception as e:
        return create_response(500, {'message': f'Internal server error: {str(e)}'})


def login_user(event: Dict[str, Any]) -> Dict[str, Any]:
    """Login user."""
    try:
        body = json.loads(event.get('body', '{}'))
        email = body.get('email', '').strip()
        password = body.get('password', '')

        if not email or not password:
            return create_response(400, {'message': 'Email and password are required'})

        try:
            # Authenticate with Cognito
            response = cognito_client.admin_initiate_auth(
                UserPoolId=USER_POOL_ID,
                ClientId=CLIENT_ID,
                AuthFlow='ADMIN_NO_SRP_AUTH',
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password
                }
            )

            if 'AuthenticationResult' in response:
                return create_response(200, {
                    'message': 'Login successful',
                    'accessToken': response['AuthenticationResult']['AccessToken'],
                    'refreshToken': response['AuthenticationResult']['RefreshToken'],
                    'idToken': response['AuthenticationResult']['IdToken']
                })
            else:
                return create_response(401, {'message': 'Invalid credentials'})

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['NotAuthorizedException', 'UserNotFoundException']:
                return create_response(401, {'message': 'Invalid credentials'})
            else:
                return create_response(500, {'message': f'Login failed: {str(e)}'})

    except json.JSONDecodeError:
        return create_response(400, {'message': 'Invalid JSON in request body'})
    except Exception as e:
        return create_response(500, {'message': f'Internal server error: {str(e)}'})


def logout_user(event: Dict[str, Any]) -> Dict[str, Any]:
    """Logout user."""
    try:
        body = json.loads(event.get('body', '{}'))
        access_token = body.get('accessToken', '')

        if not access_token:
            return create_response(400, {'message': 'Access token is required'})

        try:
            cognito_client.global_sign_out(AccessToken=access_token)
            return create_response(200, {'message': 'Logout successful'})
        except ClientError as e:
            return create_response(500, {'message': f'Logout failed: {str(e)}'})

    except json.JSONDecodeError:
        return create_response(400, {'message': 'Invalid JSON in request body'})
    except Exception as e:
        return create_response(500, {'message': f'Internal server error: {str(e)}'})


def forgot_password(event: Dict[str, Any]) -> Dict[str, Any]:
    """Initiate forgot password flow."""
    try:
        body = json.loads(event.get('body', '{}'))
        email = body.get('email', '').strip()

        if not email:
            return create_response(400, {'message': 'Email is required'})

        try:
            cognito_client.forgot_password(
                ClientId=CLIENT_ID,
                Username=email
            )
            return create_response(200, {'message': 'Password reset code sent to email'})
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'UserNotFoundException':
                return create_response(404, {'message': 'User not found'})
            else:
                return create_response(500, {'message': f'Failed to send reset code: {str(e)}'})

    except json.JSONDecodeError:
        return create_response(400, {'message': 'Invalid JSON in request body'})
    except Exception as e:
        return create_response(500, {'message': f'Internal server error: {str(e)}'})


def reset_password(event: Dict[str, Any]) -> Dict[str, Any]:
    """Reset password with code."""
    try:
        body = json.loads(event.get('body', '{}'))
        email = body.get('email', '').strip()
        code = body.get('code', '').strip()
        new_password = body.get('newPassword', '')

        if not email or not code or not new_password:
            return create_response(400, {'message': 'Email, code, and new password are required'})

        if not validate_password(new_password):
            return create_response(400, {'message': 'Password must be at least 8 characters with uppercase, lowercase, and number'})

        try:
            cognito_client.confirm_forgot_password(
                ClientId=CLIENT_ID,
                Username=email,
                ConfirmationCode=code,
                Password=new_password
            )
            return create_response(200, {'message': 'Password reset successful'})
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'CodeMismatchException':
                return create_response(400, {'message': 'Invalid reset code'})
            elif error_code == 'ExpiredCodeException':
                return create_response(400, {'message': 'Reset code has expired'})
            else:
                return create_response(500, {'message': f'Password reset failed: {str(e)}'})

    except json.JSONDecodeError:
        return create_response(400, {'message': 'Invalid JSON in request body'})
    except Exception as e:
        return create_response(500, {'message': f'Internal server error: {str(e)}'})


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler."""
    try:
        # Get the HTTP method and path
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')

        # Route the request
        if http_method == 'POST':
            if path.endswith('/register'):
                return register_user(event)
            elif path.endswith('/login'):
                return login_user(event)
            elif path.endswith('/logout'):
                return logout_user(event)
            elif path.endswith('/forgot-password'):
                return forgot_password(event)
            elif path.endswith('/reset-password'):
                return reset_password(event)
            else:
                return create_response(404, {'message': 'Endpoint not found'})
        else:
            return create_response(405, {'message': 'Method not allowed'})

    except Exception as e:
        return create_response(500, {'message': f'Internal server error: {str(e)}'})
