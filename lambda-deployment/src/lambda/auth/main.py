"""Main Lambda handler for authentication."""

import asyncio
import json
import logging
from typing import Any, Dict

from ..shared.utils import (
    create_error_response,
    create_success_response,
    parse_request_body,
)
from .auth_service import AuthService

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
