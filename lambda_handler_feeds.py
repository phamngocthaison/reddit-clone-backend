"""
Lambda handler for News Feed System.
Handles all feed-related API endpoints.
"""

import json
import os
from typing import Dict, Any
from feed_models import (
    GetFeedRequest, GetFeedResponse, RefreshFeedRequest, RefreshFeedResponse,
    GetFeedStatsResponse, ErrorResponse, SortType
)
from feed_service import FeedService


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for feed operations.
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    try:
        # Parse HTTP method and path
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        
        # Get user ID from headers (case insensitive)
        headers = event.get('headers', {})
        user_id = headers.get('X-User-ID') or headers.get('x-user-id') or headers.get('X-user-id') or headers.get('x-User-ID', '')
        if not user_id:
            return _create_error_response(400, f"Missing X-User-ID header. Available headers: {list(headers.keys())}")
        
        # Initialize feed service
        feed_service = FeedService()
        
        # Route to appropriate handler
        if http_method == 'GET' and path == '/feeds':
            return _handle_get_feed(event, feed_service, user_id)
        elif http_method == 'POST' and path == '/feeds/refresh':
            return _handle_refresh_feed(event, feed_service, user_id)
        elif http_method == 'GET' and path == '/feeds/stats':
            return _handle_get_feed_stats(event, feed_service, user_id)
        else:
            return _create_error_response(404, f"Endpoint not found: {http_method} {path}")
            
    except Exception as e:
        print(f"Error in feed handler: {str(e)}")
        return _create_error_response(500, f"Internal server error: {str(e)}")


def _handle_get_feed(event: Dict[str, Any], feed_service: FeedService, user_id: str) -> Dict[str, Any]:
    """Handle GET /feeds endpoint."""
    try:
        # Parse query parameters
        query_params = event.get('queryStringParameters') or {}
        
        # Create request object
        request = GetFeedRequest(
            limit=int(query_params.get('limit', 20)),
            offset=int(query_params.get('offset', 0)),
            sort=SortType(query_params.get('sort', 'new')),
            includeNSFW=query_params.get('includeNSFW', 'false').lower() == 'true',
            includeSpoilers=query_params.get('includeSpoilers', 'false').lower() == 'true',
            subredditId=query_params.get('subredditId'),
            authorId=query_params.get('authorId')
        )
        
        # Get feed
        response = feed_service.get_user_feed(user_id, request)
        
        if response.success:
            return _create_success_response(200, response.data, response.message)
        else:
            return _create_error_response(400, response.message)
            
    except ValueError as e:
        return _create_error_response(400, f"Invalid request parameters: {str(e)}")
    except Exception as e:
        return _create_error_response(500, f"Error getting feed: {str(e)}")


def _handle_refresh_feed(event: Dict[str, Any], feed_service: FeedService, user_id: str) -> Dict[str, Any]:
    """Handle POST /feeds/refresh endpoint."""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Create request object
        request = RefreshFeedRequest(
            reason=body.get('reason', 'manual'),
            subredditId=body.get('subredditId'),
            userId=body.get('userId')
        )
        
        # Refresh feed
        response = feed_service.refresh_user_feed(user_id, request)
        
        if response.success:
            return _create_success_response(200, response.data, response.message)
        else:
            return _create_error_response(400, response.message)
            
    except json.JSONDecodeError:
        return _create_error_response(400, "Invalid JSON in request body")
    except Exception as e:
        return _create_error_response(500, f"Error refreshing feed: {str(e)}")


def _handle_get_feed_stats(event: Dict[str, Any], feed_service: FeedService, user_id: str) -> Dict[str, Any]:
    """Handle GET /feeds/stats endpoint."""
    try:
        # Get feed stats
        response = feed_service.get_feed_stats(user_id)
        
        if response.success:
            return _create_success_response(200, response.data.dict(), response.message)
        else:
            return _create_error_response(400, response.message)
            
    except Exception as e:
        return _create_error_response(500, f"Error getting feed stats: {str(e)}")


def _create_success_response(status_code: int, data: Dict[str, Any], message: str = None) -> Dict[str, Any]:
    """Create a successful API Gateway response."""
    response_body = {
        "success": True,
        "data": data
    }
    
    if message:
        response_body["message"] = message
    
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-User-ID',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(response_body)
    }


def _create_error_response(status_code: int, message: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create an error API Gateway response."""
    error_response = ErrorResponse(
        success=False,
        error=message,
        details=details,
        timestamp=json.dumps({"timestamp": "2025-09-10T10:00:00Z"})
    )
    
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-User-ID',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(error_response.dict())
    }
