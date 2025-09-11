"""Lambda handler for Subreddit API endpoints."""

import asyncio
import json
import logging
import sys
import os
from typing import Any, Dict

# Add python directory to path for Lambda environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))
sys.path.insert(0, os.path.dirname(__file__))

from lambda_code.subreddit_models import (
    CreateSubredditRequest,
    UpdateSubredditRequest,
    JoinSubredditRequest,
    GetSubredditsRequest,
    GetSubredditPostsRequest,
    ModeratorRequest,
    BanUserRequest
)
from lambda_code.subreddit_service import SubredditService

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


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
        'body': json.dumps(body)
    }


def create_error_response(status_code: int, error_code: str, message: str) -> Dict[str, Any]:
    """Create error response."""
    return create_response(status_code, {
        "success": False,
        "message": message,
        "error": {
            "code": error_code,
            "message": message
        }
    })


def get_user_id_from_event(event: Dict[str, Any]) -> str:
    """Extract user ID from event headers."""
    headers = event.get('headers', {})
    user_id = headers.get('X-User-ID') or headers.get('x-user-id')
    
    if not user_id:
        raise ValueError("User ID not found in headers")
    
    return user_id


async def handle_create_subreddit(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle POST /subreddits/create"""
    try:
        # Get user ID
        user_id = get_user_id_from_event(event)
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        request = CreateSubredditRequest(**body)
        
        # Create subreddit
        service = SubredditService()
        subreddit = service.create_subreddit(request, user_id)
        
        return create_response(201, {
            "success": True,
            "message": "Subreddit created successfully",
            "data": subreddit.dict()
        })
        
    except ValueError as e:
        return create_error_response(400, "VALIDATION_ERROR", str(e))
    except Exception as e:
        logger.error(f"Error creating subreddit: {str(e)}")
        return create_error_response(500, "INTERNAL_ERROR", "Failed to create subreddit")


async def handle_get_subreddit(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle GET /subreddits/{subreddit_id}"""
    try:
        # Get subreddit ID from path
        path_params = event.get('pathParameters', {}) or {}
        subreddit_id = path_params.get('subreddit_id')
        
        if not subreddit_id:
            return create_error_response(400, "INVALID_PARAMETER", "subreddit_id is required")
        
        # Get user ID (optional)
        user_id = None
        try:
            user_id = get_user_id_from_event(event)
        except:
            pass  # User not authenticated
        
        # Get subreddit
        service = SubredditService()
        subreddit = service.get_subreddit(subreddit_id, user_id)
        
        return create_response(200, {
            "success": True,
            "message": "Subreddit retrieved successfully",
            "data": subreddit.dict()
        })
        
    except ValueError as e:
        return create_error_response(404, "NOT_FOUND", str(e))
    except Exception as e:
        logger.error(f"Error getting subreddit: {str(e)}")
        return create_error_response(500, "INTERNAL_ERROR", "Failed to get subreddit")


async def handle_get_subreddit_by_name(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle GET /subreddits/name/{name}"""
    try:
        # Get subreddit name from path
        path_params = event.get('pathParameters', {}) or {}
        name = path_params.get('name')
        
        if not name:
            return create_error_response(400, "INVALID_PARAMETER", "name is required")
        
        # Get user ID (optional)
        user_id = None
        try:
            user_id = get_user_id_from_event(event)
        except:
            pass  # User not authenticated
        
        # Get subreddit
        service = SubredditService()
        subreddit = service.get_subreddit_by_name(name, user_id)
        
        return create_response(200, {
            "success": True,
            "message": "Subreddit retrieved successfully",
            "data": subreddit.dict()
        })
        
    except ValueError as e:
        return create_error_response(404, "NOT_FOUND", str(e))
    except Exception as e:
        logger.error(f"Error getting subreddit: {str(e)}")
        return create_error_response(500, "INTERNAL_ERROR", "Failed to get subreddit")


async def handle_update_subreddit(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle PUT /subreddits/{subreddit_id}"""
    try:
        # Get user ID
        user_id = get_user_id_from_event(event)
        
        # Get subreddit ID from path
        path_params = event.get('pathParameters', {}) or {}
        subreddit_id = path_params.get('subreddit_id')
        
        if not subreddit_id:
            return create_error_response(400, "INVALID_PARAMETER", "subreddit_id is required")
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        request = UpdateSubredditRequest(**body)
        
        # Update subreddit
        service = SubredditService()
        subreddit = service.update_subreddit(subreddit_id, request, user_id)
        
        return create_response(200, {
            "success": True,
            "message": "Subreddit updated successfully",
            "data": subreddit.dict()
        })
        
    except ValueError as e:
        return create_error_response(400, "VALIDATION_ERROR", str(e))
    except Exception as e:
        logger.error(f"Error updating subreddit: {str(e)}")
        return create_error_response(500, "INTERNAL_ERROR", "Failed to update subreddit")


async def handle_delete_subreddit(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle DELETE /subreddits/{subreddit_id}"""
    try:
        # Get user ID
        user_id = get_user_id_from_event(event)
        
        # Get subreddit ID from path
        path_params = event.get('pathParameters', {}) or {}
        subreddit_id = path_params.get('subreddit_id')
        
        if not subreddit_id:
            return create_error_response(400, "INVALID_PARAMETER", "subreddit_id is required")
        
        # Delete subreddit
        service = SubredditService()
        success = service.delete_subreddit(subreddit_id, user_id)
        
        if success:
            return create_response(200, {
                "success": True,
                "message": "Subreddit deleted successfully"
            })
        else:
            return create_error_response(500, "INTERNAL_ERROR", "Failed to delete subreddit")
        
    except ValueError as e:
        return create_error_response(400, "VALIDATION_ERROR", str(e))
    except Exception as e:
        logger.error(f"Error deleting subreddit: {str(e)}")
        return create_error_response(500, "INTERNAL_ERROR", "Failed to delete subreddit")


async def handle_get_subreddits(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle GET /subreddits"""
    try:
        # Get user ID (optional)
        user_id = None
        try:
            user_id = get_user_id_from_event(event)
        except:
            pass  # User not authenticated
        
        # Parse query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        request = GetSubredditsRequest(**query_params)
        
        # Get subreddits
        service = SubredditService()
        result = service.get_subreddits(request, user_id)
        
        return create_response(200, {
            "success": True,
            "message": "Subreddits retrieved successfully",
            "data": result.dict()
        })
        
    except ValueError as e:
        return create_error_response(400, "VALIDATION_ERROR", str(e))
    except Exception as e:
        logger.error(f"Error getting subreddits: {str(e)}")
        return create_error_response(500, "INTERNAL_ERROR", "Failed to get subreddits")


async def handle_join_subreddit(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle POST /subreddits/{subreddit_id}/join"""
    try:
        # Get user ID
        user_id = get_user_id_from_event(event)
        
        # Get subreddit ID from path
        path_params = event.get('pathParameters', {}) or {}
        subreddit_id = path_params.get('subreddit_id')
        
        if not subreddit_id:
            return create_error_response(400, "INVALID_PARAMETER", "subreddit_id is required")
        
        # Join subreddit
        service = SubredditService()
        subscription = service.join_subreddit(subreddit_id, user_id)
        
        return create_response(200, {
            "success": True,
            "message": "Successfully joined subreddit",
            "data": subscription.dict()
        })
        
    except ValueError as e:
        return create_error_response(400, "VALIDATION_ERROR", str(e))
    except Exception as e:
        logger.error(f"Error joining subreddit: {str(e)}")
        return create_error_response(500, "INTERNAL_ERROR", "Failed to join subreddit")


async def handle_leave_subreddit(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle POST /subreddits/{subreddit_id}/leave"""
    try:
        # Get user ID
        user_id = get_user_id_from_event(event)
        
        # Get subreddit ID from path
        path_params = event.get('pathParameters', {}) or {}
        subreddit_id = path_params.get('subreddit_id')
        
        if not subreddit_id:
            return create_error_response(400, "INVALID_PARAMETER", "subreddit_id is required")
        
        # Leave subreddit
        service = SubredditService()
        success = service.leave_subreddit(subreddit_id, user_id)
        
        if success:
            return create_response(200, {
                "success": True,
                "message": "Successfully left subreddit"
            })
        else:
            return create_error_response(500, "INTERNAL_ERROR", "Failed to leave subreddit")
        
    except ValueError as e:
        return create_error_response(400, "VALIDATION_ERROR", str(e))
    except Exception as e:
        logger.error(f"Error leaving subreddit: {str(e)}")
        return create_error_response(500, "INTERNAL_ERROR", "Failed to leave subreddit")


async def handle_get_subreddit_posts(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle GET /subreddits/{subreddit_id}/posts"""
    try:
        # Get subreddit ID from path
        path_params = event.get('pathParameters', {}) or {}
        subreddit_id = path_params.get('subreddit_id')
        
        if not subreddit_id:
            return create_error_response(400, "INVALID_PARAMETER", "subreddit_id is required")
        
        # Parse query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        request = GetSubredditPostsRequest(**query_params)
        
        # Get posts
        service = SubredditService()
        result = service.get_subreddit_posts(subreddit_id, request)
        
        return create_response(200, {
            "success": True,
            "message": "Subreddit posts retrieved successfully",
            "data": result
        })
        
    except ValueError as e:
        return create_error_response(400, "VALIDATION_ERROR", str(e))
    except Exception as e:
        logger.error(f"Error getting subreddit posts: {str(e)}")
        return create_error_response(500, "INTERNAL_ERROR", "Failed to get subreddit posts")


async def handle_add_moderator(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle POST /subreddits/{subreddit_id}/moderators"""
    try:
        # Get user ID
        user_id = get_user_id_from_event(event)
        
        # Get subreddit ID from path
        path_params = event.get('pathParameters', {}) or {}
        subreddit_id = path_params.get('subreddit_id')
        
        if not subreddit_id:
            return create_error_response(400, "INVALID_PARAMETER", "subreddit_id is required")
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        request = ModeratorRequest(**body)
        
        # Add moderator
        service = SubredditService()
        success = service.add_moderator(subreddit_id, request, user_id)
        
        if success:
            return create_response(200, {
                "success": True,
                "message": "Moderator added successfully"
            })
        else:
            return create_error_response(500, "INTERNAL_ERROR", "Failed to add moderator")
        
    except ValueError as e:
        return create_error_response(400, "VALIDATION_ERROR", str(e))
    except Exception as e:
        logger.error(f"Error adding moderator: {str(e)}")
        return create_error_response(500, "INTERNAL_ERROR", "Failed to add moderator")


async def handle_remove_moderator(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle DELETE /subreddits/{subreddit_id}/moderators/{user_id}"""
    try:
        # Get user ID
        user_id = get_user_id_from_event(event)
        
        # Get subreddit ID and target user ID from path
        path_params = event.get('pathParameters', {}) or {}
        subreddit_id = path_params.get('subreddit_id')
        target_user_id = path_params.get('user_id')
        
        if not subreddit_id or not target_user_id:
            return create_error_response(400, "INVALID_PARAMETER", "subreddit_id and user_id are required")
        
        # Create moderator request
        request = ModeratorRequest(user_id=target_user_id, action='remove')
        
        # Remove moderator
        service = SubredditService()
        success = service.remove_moderator(subreddit_id, request, user_id)
        
        if success:
            return create_response(200, {
                "success": True,
                "message": "Moderator removed successfully"
            })
        else:
            return create_error_response(500, "INTERNAL_ERROR", "Failed to remove moderator")
        
    except ValueError as e:
        return create_error_response(400, "VALIDATION_ERROR", str(e))
    except Exception as e:
        logger.error(f"Error removing moderator: {str(e)}")
        return create_error_response(500, "INTERNAL_ERROR", "Failed to remove moderator")


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler for subreddit endpoints."""
    try:
        # Get HTTP method and resource
        method = event.get('httpMethod', '')
        resource = event.get('resource', '')
        
        # Handle CORS preflight
        if method == 'OPTIONS':
            return create_response(200, {"message": "CORS preflight"})
        
        # Route to appropriate handler
        if resource == '/subreddits/create' and method == 'POST':
            return asyncio.run(handle_create_subreddit(event))
        elif resource == '/subreddits/{subreddit_id}' and method == 'GET':
            return asyncio.run(handle_get_subreddit(event))
        elif resource == '/subreddits/name/{name}' and method == 'GET':
            return asyncio.run(handle_get_subreddit_by_name(event))
        elif resource == '/subreddits/{subreddit_id}' and method == 'PUT':
            return asyncio.run(handle_update_subreddit(event))
        elif resource == '/subreddits/{subreddit_id}' and method == 'DELETE':
            return asyncio.run(handle_delete_subreddit(event))
        elif resource == '/subreddits' and method == 'GET':
            return asyncio.run(handle_get_subreddits(event))
        elif resource == '/subreddits/{subreddit_id}/join' and method == 'POST':
            return asyncio.run(handle_join_subreddit(event))
        elif resource == '/subreddits/{subreddit_id}/leave' and method == 'POST':
            return asyncio.run(handle_leave_subreddit(event))
        elif resource == '/subreddits/{subreddit_id}/posts' and method == 'GET':
            return asyncio.run(handle_get_subreddit_posts(event))
        elif resource == '/subreddits/{subreddit_id}/moderators' and method == 'POST':
            return asyncio.run(handle_add_moderator(event))
        elif resource == '/subreddits/{subreddit_id}/moderators/{user_id}' and method == 'DELETE':
            return asyncio.run(handle_remove_moderator(event))
        else:
            return create_error_response(404, "NOT_FOUND", f"Method {method} not supported for resource {resource}")
            
    except Exception as e:
        logger.error(f"Handler error: {str(e)}")
        return create_error_response(500, "INTERNAL_ERROR", "Internal server error")
