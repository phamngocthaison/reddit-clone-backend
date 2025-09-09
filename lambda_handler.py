"""Main Lambda handler for authentication - Fixed for AWS deployment."""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Now import the modules using importlib to handle dots in module names
import importlib.util

# Import shared utils
utils_spec = importlib.util.spec_from_file_location(
    "shared_utils", 
    os.path.join(os.path.dirname(__file__), 'src', 'lambda', 'shared', 'utils.py')
)
shared_utils = importlib.util.module_from_spec(utils_spec)
utils_spec.loader.exec_module(shared_utils)

# Import auth service
auth_service_spec = importlib.util.spec_from_file_location(
    "auth_service", 
    os.path.join(os.path.dirname(__file__), 'src', 'lambda', 'auth', 'auth_service.py')
)
auth_service_module = importlib.util.module_from_spec(auth_service_spec)
auth_service_spec.loader.exec_module(auth_service_module)

# Get the functions and classes we need
create_error_response = shared_utils.create_error_response
create_success_response = shared_utils.create_success_response
parse_request_body = shared_utils.parse_request_body
AuthService = auth_service_module.AuthService

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
