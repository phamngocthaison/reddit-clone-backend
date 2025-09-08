"""Shared utilities for the Reddit Clone Backend."""

import json
import re
import time
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from .models import AuthResponse


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
        "body": json.dumps(body.dict(by_alias=True)),
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
    # At least 8 characters, 1 uppercase, 1 lowercase, 1 number
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
    # 3-20 characters, alphanumeric and underscores only
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
