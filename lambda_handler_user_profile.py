"""Lambda handler for User Profile API endpoints."""

import json
import os
import sys
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

# Add python directory to path for Lambda environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

from user_profile_models import (
    UpdateProfileRequest,
    ChangePasswordRequest,
    DeleteAccountRequest,
    GetUserPostsRequest,
    GetUserCommentsRequest,
    UserProfileResponse
)
from user_profile_service import UserProfileService

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize user profile service
user_profile_service = UserProfileService()


def create_success_response(message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a success response."""
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-User-ID",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
        },
        "body": json.dumps({
            "success": True,
            "message": message,
            "data": data,
            "error": None
        })
    }


def create_error_response(status_code: int, error_code: str, message: str, additional_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create an error response."""
    error_data = {
        "code": error_code,
        "message": message
    }
    
    if additional_data:
        error_data["additional_data"] = additional_data
    
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-User-ID",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
        },
        "body": json.dumps({
            "success": False,
            "message": None,
            "data": None,
            "error": error_data
        })
    }


def get_user_id_from_event(event: Dict[str, Any]) -> Optional[str]:
    """Extract user ID from event headers."""
    headers = event.get("headers", {})
    
    # Try JWT token first
    auth_header = headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        # For now, use X-User-ID header for testing
        # In production, decode JWT token to get user ID
        pass
    
    # Use X-User-ID header for testing
    return headers.get("X-User-ID")


def parse_request_body(event: Dict[str, Any]) -> Dict[str, Any]:
    """Parse request body from event."""
    body = event.get("body", "{}")
    if isinstance(body, str):
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {}
    return body


# ============================================================================
# USER PROFILE HANDLERS
# ============================================================================

async def handle_get_my_profile(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle GET /auth/me - Get current user profile."""
    try:
        user_id = get_user_id_from_event(event)
        if not user_id:
            return create_error_response(401, "UNAUTHORIZED", "User ID not provided")
        
        user_profile = await user_profile_service.get_user_profile(user_id)
        
        # Use Pydantic's json() method which handles datetime serialization
        import json
        user_data = json.loads(user_profile.json())
        
        return create_success_response(
            "User profile retrieved successfully",
            {"user": user_data}
        )
        
    except ValueError as e:
        return create_error_response(404, "USER_NOT_FOUND", str(e))
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Failed to retrieve user profile")


async def handle_update_my_profile(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle PUT /auth/me - Update current user profile."""
    try:
        user_id = get_user_id_from_event(event)
        if not user_id:
            return create_error_response(401, "UNAUTHORIZED", "User ID not provided")
        
        body = parse_request_body(event)
        request = UpdateProfileRequest(**body)
        
        updated_profile = await user_profile_service.update_user_profile(user_id, request)
        
        # Use Pydantic's json() method which handles datetime serialization
        import json
        user_data = json.loads(updated_profile.json())
        
        return create_success_response(
            "User profile updated successfully",
            {"user": user_data}
        )
        
    except ValueError as e:
        return create_error_response(400, "VALIDATION_ERROR", str(e))
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Failed to update user profile")


async def handle_get_user_profile(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle GET /users/{user_id} - Get public user profile."""
    try:
        user_id = event.get("pathParameters", {}).get("user_id")
        if not user_id:
            return create_error_response(400, "MISSING_USER_ID", "User ID is required")
        
        public_profile = await user_profile_service.get_public_user_profile(user_id)
        
        # Use Pydantic's json() method which handles datetime serialization
        import json
        user_data = json.loads(public_profile.json())
        
        return create_success_response(
            "User profile retrieved successfully",
            {"user": user_data}
        )
        
    except ValueError as e:
        if "not found" in str(e).lower():
            return create_error_response(404, "USER_NOT_FOUND", str(e))
        elif "private" in str(e).lower():
            return create_error_response(403, "PROFILE_PRIVATE", str(e))
        else:
            return create_error_response(400, "VALIDATION_ERROR", str(e))
    except Exception as e:
        logger.error(f"Error getting public user profile: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Failed to retrieve user profile")


def handle_change_password(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle PUT /auth/change-password - Change user password."""
    try:
        user_id = get_user_id_from_event(event)
        if not user_id:
            return create_error_response(401, "UNAUTHORIZED", "User ID not provided")
        
        body = parse_request_body(event)
        request = ChangePasswordRequest(**body)
        
        user_profile_service.change_password(user_id, request)
        
        return create_success_response("Password changed successfully")
        
    except ValueError as e:
        return create_error_response(400, "VALIDATION_ERROR", str(e))
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Failed to change password")


def handle_delete_account(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle DELETE /auth/me - Delete user account."""
    try:
        user_id = get_user_id_from_event(event)
        if not user_id:
            return create_error_response(401, "UNAUTHORIZED", "User ID not provided")
        
        body = parse_request_body(event)
        request = DeleteAccountRequest(**body)
        
        user_profile_service.delete_user_account(user_id, request.password)
        
        return create_success_response("Account deleted successfully")
        
    except ValueError as e:
        return create_error_response(400, "VALIDATION_ERROR", str(e))
    except Exception as e:
        logger.error(f"Error deleting account: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Failed to delete account")


async def handle_get_user_posts(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle GET /users/{user_id}/posts - Get user posts."""
    try:
        user_id = event.get("pathParameters", {}).get("user_id")
        if not user_id:
            return create_error_response(400, "MISSING_USER_ID", "User ID is required")
        
        # Parse query parameters
        query_params = event.get("queryStringParameters") or {}
        request = GetUserPostsRequest(
            limit=int(query_params.get("limit", 20)),
            offset=int(query_params.get("offset", 0)),
            sort=query_params.get("sort", "new"),
            post_type=query_params.get("post_type"),
            is_nsfw=query_params.get("is_nsfw")
        )
        
        posts_response = await user_profile_service.get_user_posts(user_id, request)
        
        return create_success_response(
            "User posts retrieved successfully",
            posts_response.dict()
        )
        
    except ValueError as e:
        return create_error_response(400, "VALIDATION_ERROR", str(e))
    except Exception as e:
        logger.error(f"Error getting user posts: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Failed to retrieve user posts")


async def handle_get_user_comments(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle GET /users/{user_id}/comments - Get user comments."""
    try:
        user_id = event.get("pathParameters", {}).get("user_id")
        if not user_id:
            return create_error_response(400, "MISSING_USER_ID", "User ID is required")
        
        # Parse query parameters
        query_params = event.get("queryStringParameters") or {}
        request = GetUserCommentsRequest(
            limit=int(query_params.get("limit", 20)),
            offset=int(query_params.get("offset", 0)),
            sort=query_params.get("sort", "new"),
            comment_type=query_params.get("comment_type")
        )
        
        comments_response = await user_profile_service.get_user_comments(user_id, request)
        
        return create_success_response(
            "User comments retrieved successfully",
            comments_response.dict()
        )
        
    except ValueError as e:
        return create_error_response(400, "VALIDATION_ERROR", str(e))
    except Exception as e:
        logger.error(f"Error getting user comments: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Failed to retrieve user comments")


# ============================================================================
# MAIN HANDLER
# ============================================================================

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for user profile endpoints."""
    import asyncio
    
    async def async_handler():
        logger.info(f"Event: {json.dumps(event)}")
        
        try:
            # Get path and method
            resource = event.get("resource", "")
            method = event.get("httpMethod", "")
            
            # Handle preflight OPTIONS requests
            if method == "OPTIONS":
                return create_success_response("CORS preflight")
            
            # Route to appropriate handler based on path
            if resource == "/auth/me" and method == "GET":
                return await handle_get_my_profile(event)
            elif resource == "/auth/me" and method == "PUT":
                return await handle_update_my_profile(event)
            elif resource == "/auth/me" and method == "DELETE":
                return handle_delete_account(event)
            elif resource == "/auth/change-password" and method == "PUT":
                return handle_change_password(event)
            elif resource == "/users/{user_id}" and method == "GET":
                return await handle_get_user_profile(event)
            elif resource == "/users/{user_id}/posts" and method == "GET":
                return await handle_get_user_posts(event)
            elif resource == "/users/{user_id}/comments" and method == "GET":
                return await handle_get_user_comments(event)
            else:
                return create_error_response(404, "NOT_FOUND", "Endpoint not found")
        
        except Exception as e:
            logger.error(f"Lambda handler error: {e}")
            return create_error_response(500, "INTERNAL_ERROR", "Internal server error")
    
    return asyncio.run(async_handler())
