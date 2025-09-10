import json
import logging
import os
import boto3
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Simple Lambda handler for testing."""
    try:
        # Get HTTP method and path
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        
        logger.info(f"Received {http_method} request to {path}")
        
        # Simple routing
        if path == '/comments/create' and http_method == 'POST':
            return create_comment_simple(event)
        elif path == '/comments' and http_method == 'GET':
            return get_comments_simple(event)
        else:
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-User-ID',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
                },
                'body': json.dumps({
                    'message': 'Simple handler working',
                    'path': path,
                    'method': http_method,
                    'event': event
                })
            }
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-User-ID',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }

def create_comment_simple(event: Dict[str, Any]) -> Dict[str, Any]:
    """Simple create comment function."""
    try:
        # Get request body
        body = json.loads(event.get('body', '{}'))
        
        # Get user ID from headers
        headers = event.get('headers', {})
        user_id = headers.get('X-User-ID') or headers.get('x-user-id')
        
        if not user_id:
            user_id = "user_1757432106_d66ab80f40704b1"  # Default test user
        
        # Create comment ID
        comment_id = f"comment_{int(datetime.now().timestamp())}_{hash(body.get('content', '')) % 10000:04d}"
        
        # Simple response
        response = {
            'commentId': comment_id,
            'postId': body.get('post_id'),
            'content': body.get('content'),
            'authorId': user_id,
            'parentId': body.get('parent_id'),
            'commentType': body.get('comment_type', 'comment'),
            'isNsfw': body.get('is_nsfw', False),
            'isSpoiler': body.get('is_spoiler', False),
            'flair': body.get('flair'),
            'tags': body.get('tags', []),
            'score': 0,
            'upvotes': 0,
            'downvotes': 0,
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat(),
            'isDeleted': False,
            'editCount': 0,
            'lastEditedAt': None
        }
        
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-User-ID',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps({
                'message': 'Comment created successfully',
                'comment': response
            })
        }
        
    except Exception as e:
        logger.error(f"Error creating comment: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-User-ID',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }

def get_comments_simple(event: Dict[str, Any]) -> Dict[str, Any]:
    """Simple get comments function."""
    try:
        # Get query parameters
        query_params = event.get('queryStringParameters') or {}
        post_id = query_params.get('post_id')
        
        # Simple response
        comments = [
            {
                'commentId': 'comment_1757482000_0001',
                'postId': post_id,
                'content': 'This is a test comment',
                'authorId': 'user_1757432106_d66ab80f40704b1',
                'parentId': None,
                'commentType': 'comment',
                'isNsfw': False,
                'isSpoiler': False,
                'flair': 'Discussion',
                'tags': ['test'],
                'score': 1,
                'upvotes': 1,
                'downvotes': 0,
                'createdAt': datetime.now().isoformat(),
                'updatedAt': datetime.now().isoformat(),
                'isDeleted': False,
                'editCount': 0,
                'lastEditedAt': None
            }
        ]
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-User-ID',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps({
                'message': 'Comments retrieved successfully',
                'comments': comments,
                'total': len(comments),
                'page': 1,
                'limit': 20
            })
        }
        
    except Exception as e:
        logger.error(f"Error getting comments: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-User-ID',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }