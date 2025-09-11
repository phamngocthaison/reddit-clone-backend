import json
import asyncio
from typing import Dict, Any
from .posts_service import PostsService
from .models import (
    CreatePostRequest, UpdatePostRequest, GetPostsRequest, VotePostRequest,
    PostResponse, PostListResponse, PostStatsResponse,
    PostNotFoundError, PostAccessDeniedError, PostValidationError
)

def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Create API Gateway response."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
        },
        "body": json.dumps(body, default=str)
    }

def get_user_id_from_event(event: Dict[str, Any]) -> str:
    """Extract user ID from API Gateway event."""
    # This would typically come from JWT token validation
    # For now, we'll extract from the request context or headers
    request_context = event.get('requestContext', {})
    authorizer = request_context.get('authorizer', {})
    
    # If using Cognito authorizer
    if 'claims' in authorizer:
        return authorizer['claims'].get('custom:userId')
    
    # If using custom authorizer
    if 'userId' in authorizer:
        return authorizer['userId']
    
    # For testing purposes, extract from headers
    headers = event.get('headers', {})
    user_id = headers.get('X-User-ID')
    
    if not user_id:
        raise PostAccessDeniedError(message="User ID not found in request")
    
    return user_id

async def handle_create_post(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle POST /posts/create"""
    try:
        # Get user ID
        user_id = get_user_id_from_event(event)
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        request = CreatePostRequest(**body)
        
        # Create post
        posts_service = PostsService()
        post = posts_service.create_post(request, user_id)
        
        return create_response(201, {
            "success": True,
            "message": "Post created successfully",
            "data": {
                "post": post.dict()
            }
        })
        
    except PostValidationError as e:
        return create_response(400, {
            "success": False,
            "message": "Validation error",
            "error": {
                "code": e.error_code,
                "message": e.message,
                "details": e.details
            }
        })
    except PostAccessDeniedError as e:
        return create_response(403, {
            "success": False,
            "message": "Access denied",
            "error": {
                "code": e.error_code,
                "message": e.message,
                "details": e.details
            }
        })
    except Exception as e:
        return create_response(500, {
            "success": False,
            "message": "Internal server error",
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        })

async def handle_get_post(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle GET /posts/{post_id}"""
    try:
        # Get post ID from path parameters
        post_id = event.get('pathParameters', {}).get('post_id')
        if not post_id:
            return create_response(400, {
                "success": False,
                "message": "Post ID is required",
                "error": {
                    "code": "MISSING_POST_ID",
                    "message": "Post ID must be provided in the URL path"
                }
            })
        
        # Get user ID (optional for public posts)
        user_id = None
        try:
            user_id = get_user_id_from_event(event)
        except:
            pass  # User not authenticated, but can still view public posts
        
        # Get post
        posts_service = PostsService()
        post = posts_service.get_post(post_id, user_id)
        
        return create_response(200, {
            "success": True,
            "message": "Post retrieved successfully",
            "data": {
                "post": post.dict()
            }
        })
        
    except PostNotFoundError as e:
        return create_response(404, {
            "success": False,
            "message": "Post not found",
            "error": {
                "code": e.error_code,
                "message": e.message,
                "details": e.details
            }
        })
    except Exception as e:
        return create_response(500, {
            "success": False,
            "message": "Internal server error",
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        })

async def handle_update_post(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle PUT /posts/{post_id}"""
    try:
        # Get post ID from path parameters
        post_id = event.get('pathParameters', {}).get('post_id')
        if not post_id:
            return create_response(400, {
                "success": False,
                "message": "Post ID is required",
                "error": {
                    "code": "MISSING_POST_ID",
                    "message": "Post ID must be provided in the URL path"
                }
            })
        
        # Get user ID
        user_id = get_user_id_from_event(event)
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        request = UpdatePostRequest(**body)
        
        # Update post
        posts_service = PostsService()
        post = posts_service.update_post(post_id, request, user_id)
        
        return create_response(200, {
            "success": True,
            "message": "Post updated successfully",
            "data": {
                "post": post.dict()
            }
        })
        
    except PostNotFoundError as e:
        return create_response(404, {
            "success": False,
            "message": "Post not found",
            "error": {
                "code": e.error_code,
                "message": e.message,
                "details": e.details
            }
        })
    except PostAccessDeniedError as e:
        return create_response(403, {
            "success": False,
            "message": "Access denied",
            "error": {
                "code": e.error_code,
                "message": e.message,
                "details": e.details
            }
        })
    except PostValidationError as e:
        return create_response(400, {
            "success": False,
            "message": "Validation error",
            "error": {
                "code": e.error_code,
                "message": e.message,
                "details": e.details
            }
        })
    except Exception as e:
        return create_response(500, {
            "success": False,
            "message": "Internal server error",
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        })

async def handle_delete_post(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle DELETE /posts/{post_id}"""
    try:
        # Get post ID from path parameters
        post_id = event.get('pathParameters', {}).get('post_id')
        if not post_id:
            return create_response(400, {
                "success": False,
                "message": "Post ID is required",
                "error": {
                    "code": "MISSING_POST_ID",
                    "message": "Post ID must be provided in the URL path"
                }
            })
        
        # Get user ID
        user_id = get_user_id_from_event(event)
        
        # Delete post
        posts_service = PostsService()
        success = posts_service.delete_post(post_id, user_id)
        
        if success:
            return create_response(200, {
                "success": True,
                "message": "Post deleted successfully"
            })
        else:
            return create_response(500, {
                "success": False,
                "message": "Failed to delete post"
            })
        
    except PostNotFoundError as e:
        return create_response(404, {
            "success": False,
            "message": "Post not found",
            "error": {
                "code": e.error_code,
                "message": e.message,
                "details": e.details
            }
        })
    except PostAccessDeniedError as e:
        return create_response(403, {
            "success": False,
            "message": "Access denied",
            "error": {
                "code": e.error_code,
                "message": e.message,
                "details": e.details
            }
        })
    except Exception as e:
        return create_response(500, {
            "success": False,
            "message": "Internal server error",
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        })

async def handle_get_posts(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle GET /posts"""
    try:
        # Get user ID (optional)
        user_id = None
        try:
            user_id = get_user_id_from_event(event)
        except:
            pass  # User not authenticated, but can still view public posts
        
        # Parse query parameters
        query_params = event.get('queryStringParameters') or {}
        
        request = GetPostsRequest(
            subreddit_id=query_params.get('subreddit_id'),
            author_id=query_params.get('author_id'),
            sort=query_params.get('sort', 'hot'),
            time_filter=query_params.get('time_filter', 'day'),
            limit=int(query_params.get('limit', 25)),
            offset=int(query_params.get('offset', 0)),
            post_type=query_params.get('post_type'),
            is_nsfw=query_params.get('is_nsfw')
        )
        
        # Get posts
        posts_service = PostsService()
        result = posts_service.get_posts(request, user_id)
        
        return create_response(200, {
            "success": True,
            "message": "Posts retrieved successfully",
            "data": {
                "posts": [post.dict() for post in result.posts],
                "total_count": result.total_count,
                "has_more": result.has_more,
                "next_offset": result.next_offset
            }
        })
        
    except PostValidationError as e:
        return create_response(400, {
            "success": False,
            "message": "Validation error",
            "error": {
                "code": e.error_code,
                "message": e.message,
                "details": e.details
            }
        })
    except Exception as e:
        return create_response(500, {
            "success": False,
            "message": "Internal server error",
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        })

async def handle_vote_post(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle POST /posts/{post_id}/vote"""
    try:
        # Get post ID from path parameters
        post_id = event.get('pathParameters', {}).get('post_id')
        if not post_id:
            return create_response(400, {
                "success": False,
                "message": "Post ID is required",
                "error": {
                    "code": "MISSING_POST_ID",
                    "message": "Post ID must be provided in the URL path"
                }
            })
        
        # Get user ID
        user_id = get_user_id_from_event(event)
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        request = VotePostRequest(**body)
        
        # Vote on post
        posts_service = PostsService()
        stats = posts_service.vote_post(post_id, request, user_id)
        
        return create_response(200, {
            "success": True,
            "message": "Vote recorded successfully",
            "data": {
                "stats": stats.dict()
            }
        })
        
    except PostNotFoundError as e:
        return create_response(404, {
            "success": False,
            "message": "Post not found",
            "error": {
                "code": e.error_code,
                "message": e.message,
                "details": e.details
            }
        })
    except PostAccessDeniedError as e:
        return create_response(403, {
            "success": False,
            "message": "Access denied",
            "error": {
                "code": e.error_code,
                "message": e.message,
                "details": e.details
            }
        })
    except PostValidationError as e:
        return create_response(400, {
            "success": False,
            "message": "Validation error",
            "error": {
                "code": e.error_code,
                "message": e.message,
                "details": e.details
            }
        })
    except Exception as e:
        return create_response(500, {
            "success": False,
            "message": "Internal server error",
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        })

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler for posts endpoints."""
    try:
        # Get HTTP method and resource
        method = event.get('httpMethod', '')
        resource = event.get('resource', '')
        
        # Route to appropriate handler
        if resource == '/posts/create' and method == 'POST':
            return asyncio.run(handle_create_post(event))
        elif resource == '/posts/{post_id}' and method == 'GET':
            return asyncio.run(handle_get_post(event))
        elif resource == '/posts/{post_id}' and method == 'PUT':
            return asyncio.run(handle_update_post(event))
        elif resource == '/posts/{post_id}' and method == 'DELETE':
            return asyncio.run(handle_delete_post(event))
        elif resource == '/posts' and method == 'GET':
            return asyncio.run(handle_get_posts(event))
        elif resource == '/posts/{post_id}/vote' and method == 'POST':
            return asyncio.run(handle_vote_post(event))
        else:
            return create_response(404, {
                "success": False,
                "message": "Endpoint not found",
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Method {method} not supported for resource {resource}"
                }
            })
            
    except Exception as e:
        return create_response(500, {
            "success": False,
            "message": "Internal server error",
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        })
