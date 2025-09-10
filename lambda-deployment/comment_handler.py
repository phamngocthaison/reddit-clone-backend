"""
Comment handlers for API endpoints
"""

import json
from typing import Dict, Any
from comment_service import CommentService
from comment_models import (
    CreateCommentRequest,
    UpdateCommentRequest,
    GetCommentsRequest,
    VoteCommentRequest
)


class CommentHandler:
    """Handler for comment API endpoints"""
    
    def __init__(self):
        self.comment_service = CommentService()
    
    def create_comment_handler(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create comment request"""
        try:
            # Parse request body
            body = json.loads(event.get('body', '{}'))
            request = CreateCommentRequest(**body)
            
            # Get user ID from event
            user_id = self._get_user_id_from_event(event)
            
            # Create comment
            comment = self.comment_service.create_comment(request, user_id)
            
            return {
                'statusCode': 201,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
                },
                'body': json.dumps({
                    'success': True,
                    'message': 'Comment created successfully',
                    'data': {
                        'comment': comment.dict()
                    }
                })
            }
            
        except ValueError as e:
            return self._error_response(400, 'VALIDATION_ERROR', str(e))
        except Exception as e:
            return self._error_response(500, 'INTERNAL_SERVER_ERROR', str(e))
    
    def get_comments_handler(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get comments request"""
        try:
            # Parse query parameters
            query_params = event.get('queryStringParameters') or {}
            
            # Validate required parameters
            post_id = query_params.get('post_id')
            if not post_id:
                return self._error_response(400, 'VALIDATION_ERROR', 'post_id is required')
            
            # Build request
            request = GetCommentsRequest(
                post_id=post_id,
                parent_id=query_params.get('parent_id'),
                sort=query_params.get('sort', 'hot'),
                limit=int(query_params.get('limit', 20)),
                offset=int(query_params.get('offset', 0)),
                include_deleted=query_params.get('include_deleted', 'false').lower() == 'true'
            )
            
            # Get comments
            comments_response = self.comment_service.get_comments(request)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
                },
                'body': json.dumps({
                    'success': True,
                    'message': 'Comments retrieved successfully',
                    'data': comments_response.dict()
                })
            }
            
        except ValueError as e:
            return self._error_response(400, 'VALIDATION_ERROR', str(e))
        except Exception as e:
            return self._error_response(500, 'INTERNAL_SERVER_ERROR', str(e))
    
    def get_comment_by_id_handler(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get comment by ID request"""
        try:
            # Get comment ID from path parameters
            comment_id = event.get('pathParameters', {}).get('comment_id')
            if not comment_id:
                return self._error_response(400, 'VALIDATION_ERROR', 'comment_id is required')
            
            # Get comment
            comment = self.comment_service.get_comment(comment_id)
            if not comment:
                return self._error_response(404, 'COMMENT_NOT_FOUND', 'Comment not found')
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
                },
                'body': json.dumps({
                    'success': True,
                    'message': 'Comment retrieved successfully',
                    'data': {
                        'comment': comment.dict()
                    }
                })
            }
            
        except ValueError as e:
            return self._error_response(400, 'VALIDATION_ERROR', str(e))
        except Exception as e:
            return self._error_response(500, 'INTERNAL_SERVER_ERROR', str(e))
    
    def update_comment_handler(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle update comment request"""
        try:
            # Get comment ID from path parameters
            comment_id = event.get('pathParameters', {}).get('comment_id')
            if not comment_id:
                return self._error_response(400, 'VALIDATION_ERROR', 'comment_id is required')
            
            # Parse request body
            body = json.loads(event.get('body', '{}'))
            request = UpdateCommentRequest(**body)
            
            # Get user ID from event
            user_id = self._get_user_id_from_event(event)
            
            # Update comment
            comment = self.comment_service.update_comment(comment_id, request, user_id)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
                },
                'body': json.dumps({
                    'success': True,
                    'message': 'Comment updated successfully',
                    'data': {
                        'comment': comment.dict()
                    }
                })
            }
            
        except ValueError as e:
            if "Access denied" in str(e):
                return self._error_response(403, 'COMMENT_ACCESS_DENIED', str(e))
            return self._error_response(400, 'VALIDATION_ERROR', str(e))
        except Exception as e:
            return self._error_response(500, 'INTERNAL_SERVER_ERROR', str(e))
    
    def delete_comment_handler(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle delete comment request"""
        try:
            # Get comment ID from path parameters
            comment_id = event.get('pathParameters', {}).get('comment_id')
            if not comment_id:
                return self._error_response(400, 'VALIDATION_ERROR', 'comment_id is required')
            
            # Get user ID from event
            user_id = self._get_user_id_from_event(event)
            
            # Delete comment
            self.comment_service.delete_comment(comment_id, user_id)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
                },
                'body': json.dumps({
                    'success': True,
                    'message': 'Comment deleted successfully'
                })
            }
            
        except ValueError as e:
            if "Access denied" in str(e):
                return self._error_response(403, 'COMMENT_ACCESS_DENIED', str(e))
            return self._error_response(400, 'VALIDATION_ERROR', str(e))
        except Exception as e:
            return self._error_response(500, 'INTERNAL_SERVER_ERROR', str(e))
    
    def vote_comment_handler(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle vote comment request"""
        try:
            # Get comment ID from path parameters
            comment_id = event.get('pathParameters', {}).get('comment_id')
            if not comment_id:
                return self._error_response(400, 'VALIDATION_ERROR', 'comment_id is required')
            
            # Parse request body
            body = json.loads(event.get('body', '{}'))
            request = VoteCommentRequest(**body)
            
            # Get user ID from event
            user_id = self._get_user_id_from_event(event)
            
            # Vote on comment
            vote_response = self.comment_service.vote_comment(comment_id, request, user_id)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
                },
                'body': json.dumps({
                    'success': True,
                    'message': 'Vote processed successfully',
                    'data': vote_response.dict()
                })
            }
            
        except ValueError as e:
            return self._error_response(400, 'VALIDATION_ERROR', str(e))
        except Exception as e:
            return self._error_response(500, 'INTERNAL_SERVER_ERROR', str(e))
    
    def _get_user_id_from_event(self, event: Dict[str, Any]) -> str:
        """Extract user ID from API Gateway event"""
        # For testing purposes, extract from headers
        headers = event.get('headers', {})
        user_id = headers.get('X-User-ID') or headers.get('x-user-id')
        
        # If not in headers, try to get from query parameters for testing
        if not user_id:
            query_params = event.get('queryStringParameters') or {}
            user_id = query_params.get('user_id')
        
        # For testing, use a default user ID if none provided
        if not user_id:
            user_id = "user_1757432106_d66ab80f40704b1"  # Default test user
        
        return user_id
    
    def _error_response(self, status_code: int, error_code: str, message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            'statusCode': status_code,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps({
                'success': False,
                'error': {
                    'code': error_code,
                    'message': message
                }
            })
        }
