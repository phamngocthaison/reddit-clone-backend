import json
import os
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from enum import Enum

import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel, EmailStr, validator, Field

# Configure logging
logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

# AWS Clients
dynamodb = boto3.resource("dynamodb")
cognito = boto3.client("cognito-idp")

# Environment variables
USERS_TABLE = os.environ.get("USERS_TABLE", "reddit-clone-users")
COMMENTS_TABLE = os.environ.get("COMMENTS_TABLE", "reddit-clone-comments")
POSTS_TABLE = os.environ.get("POSTS_TABLE", "reddit-clone-posts")

# DynamoDB Tables
users_table = dynamodb.Table(USERS_TABLE)
comments_table = dynamodb.Table(COMMENTS_TABLE)
posts_table = dynamodb.Table(POSTS_TABLE)

# ==================== MODELS ====================

class CommentType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    LINK = "link"

class CommentBase(BaseModel):
    content: str
    post_id: str
    parent_comment_id: Optional[str] = None
    comment_type: CommentType = CommentType.TEXT
    media_urls: Optional[List[str]] = []
    is_nsfw: bool = False
    is_spoiler: bool = False
    flair: Optional[str] = None
    tags: Optional[List[str]] = []

class CreateCommentRequest(CommentBase):
    pass

class UpdateCommentRequest(BaseModel):
    content: Optional[str] = None
    comment_type: Optional[CommentType] = None
    media_urls: Optional[List[str]] = None
    is_nsfw: Optional[bool] = None
    is_spoiler: Optional[bool] = None
    flair: Optional[str] = None
    tags: Optional[List[str]] = None

class CommentResponse(BaseModel):
    comment_id: str
    content: str
    author_id: str
    author_username: str
    post_id: str
    parent_comment_id: Optional[str]
    comment_type: str
    media_urls: List[str]
    score: int
    upvotes: int
    downvotes: int
    reply_count: int
    created_at: str
    updated_at: str
    is_deleted: bool
    is_edited: bool
    is_nsfw: bool
    is_spoiler: bool
    flair: Optional[str]
    tags: List[str]
    awards: List[dict]

class GetCommentsRequest(BaseModel):
    post_id: Optional[str] = None
    parent_comment_id: Optional[str] = None
    author_id: Optional[str] = None
    limit: int = 20
    offset: Optional[str] = None
    sort_by: str = "created_at"  # created_at, score
    sort_order: str = "desc"  # asc, desc

class VoteCommentRequest(BaseModel):
    vote_type: str  # upvote, downvote, remove

# ==================== UTILITY FUNCTIONS ====================

def create_success_response(data: Any = None, message: str = "Success") -> Dict[str, Any]:
    """Create a successful API response."""
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

def create_error_response(status_code: int, error_code: str, message: str) -> Dict[str, Any]:
    """Create an error API response."""
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
            "message": message,
            "data": None,
            "error": {
                "code": error_code,
                "message": message
            }
        })
    }

def get_user_id_from_event(event: Dict[str, Any]) -> str:
    """Extract user ID from the API Gateway event."""
    headers = event.get("headers", {})
    query_params = event.get("queryStringParameters", {}) or {}
    
    # Check headers (case-insensitive)
    user_id = headers.get("X-User-ID") or headers.get("x-user-id")
    
    # Check query parameters
    if not user_id:
        user_id = query_params.get("user_id")
    
    # For testing purposes, return a default user ID if not found
    if not user_id:
        user_id = "user_test_123"
        logger.warning("User ID not found in request, using default test user")
    
    return user_id

# ==================== COMMENT HANDLERS ====================

async def handle_create_comment(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle creating a new comment."""
    try:
        # Parse request body
        body = json.loads(event.get("body", "{}"))
        request = CreateCommentRequest(**body)
        
        # Get user ID
        user_id = get_user_id_from_event(event)
        
        # Generate comment ID
        import uuid
        comment_id = f"comment_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
        
        # Create comment data
        comment_data = {
            "commentId": comment_id,
            "content": request.content,
            "authorId": user_id,
            "postId": request.post_id,
            "parentCommentId": request.parent_comment_id,
            "commentType": request.comment_type.value,
            "mediaUrls": request.media_urls or [],
            "score": 0,
            "upvotes": 0,
            "downvotes": 0,
            "replyCount": 0,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "updatedAt": datetime.now(timezone.utc).isoformat(),
            "isDeleted": False,
            "isEdited": False,
            "isNsfw": request.is_nsfw,
            "isSpoiler": request.is_spoiler,
            "flair": request.flair,
            "tags": request.tags or [],
            "awards": []
        }
        
        # Store in DynamoDB
        comments_table.put_item(Item=comment_data)
        
        # Update post comment count
        try:
            posts_table.update_item(
                Key={"postId": request.post_id},
                UpdateExpression="ADD commentCount :inc",
                ExpressionAttributeValues={":inc": 1}
            )
        except Exception as e:
            logger.warning(f"Failed to update post comment count: {e}")
        
        # Update parent comment reply count if it's a reply
        if request.parent_comment_id:
            try:
                comments_table.update_item(
                    Key={"commentId": request.parent_comment_id},
                    UpdateExpression="ADD replyCount :inc",
                    ExpressionAttributeValues={":inc": 1}
                )
            except Exception as e:
                logger.warning(f"Failed to update parent comment reply count: {e}")
        
        # Get author username
        try:
            user_response = users_table.get_item(Key={"userId": user_id})
            author_username = user_response.get("Item", {}).get("username", "Unknown")
        except:
            author_username = "Unknown"
        
        # Create response
        comment_response = CommentResponse(
            comment_id=comment_id,
            content=request.content,
            author_id=user_id,
            author_username=author_username,
            post_id=request.post_id,
            parent_comment_id=request.parent_comment_id,
            comment_type=request.comment_type.value,
            media_urls=request.media_urls or [],
            score=0,
            upvotes=0,
            downvotes=0,
            reply_count=0,
            created_at=comment_data["createdAt"],
            updated_at=comment_data["updatedAt"],
            is_deleted=False,
            is_edited=False,
            is_nsfw=request.is_nsfw,
            is_spoiler=request.is_spoiler,
            flair=request.flair,
            tags=request.tags or [],
            awards=[]
        )
        
        return create_success_response(
            data={"comment": comment_response.dict()},
            message="Comment created successfully"
        )
        
    except Exception as e:
        logger.error(f"Create comment error: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Create comment failed")

async def handle_get_comments(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle getting comments."""
    try:
        # Parse query parameters
        query_params = event.get("queryStringParameters", {}) or {}
        request = GetCommentsRequest(**query_params)
        
        # Build filter expression
        filter_expressions = []
        expression_values = {}
        
        if request.post_id:
            filter_expressions.append("postId = :post_id")
            expression_values[":post_id"] = request.post_id
        
        if request.parent_comment_id:
            filter_expressions.append("parentCommentId = :parent_comment_id")
            expression_values[":parent_comment_id"] = request.parent_comment_id
        elif request.post_id:  # Only get top-level comments if post_id is specified
            filter_expressions.append("attribute_not_exists(parentCommentId)")
        
        if request.author_id:
            filter_expressions.append("authorId = :author_id")
            expression_values[":author_id"] = request.author_id
        
        # Add filter for non-deleted comments
        filter_expressions.append("isDeleted = :is_deleted")
        expression_values[":is_deleted"] = False
        
        # Query comments
        if filter_expressions:
            response = comments_table.scan(
                FilterExpression=" AND ".join(filter_expressions),
                ExpressionAttributeValues=expression_values,
                Limit=request.limit
            )
        else:
            response = comments_table.scan(Limit=request.limit)
        
        comments = response.get("Items", [])
        
        # Sort comments
        if request.sort_by == "created_at":
            comments.sort(key=lambda x: x.get("createdAt", ""), reverse=(request.sort_order == "desc"))
        elif request.sort_by == "score":
            comments.sort(key=lambda x: x.get("score", 0), reverse=(request.sort_order == "desc"))
        
        # Get author usernames
        for comment in comments:
            try:
                user_response = users_table.get_item(Key={"userId": comment["authorId"]})
                comment["authorUsername"] = user_response.get("Item", {}).get("username", "Unknown")
            except:
                comment["authorUsername"] = "Unknown"
        
        # Create response
        comment_responses = []
        for comment in comments:
            comment_responses.append(CommentResponse(
                comment_id=comment["commentId"],
                content=comment["content"],
                author_id=comment["authorId"],
                author_username=comment["authorUsername"],
                post_id=comment["postId"],
                parent_comment_id=comment.get("parentCommentId"),
                comment_type=comment["commentType"],
                media_urls=comment.get("mediaUrls", []),
                score=comment["score"],
                upvotes=comment["upvotes"],
                downvotes=comment["downvotes"],
                reply_count=comment["replyCount"],
                created_at=comment["createdAt"],
                updated_at=comment["updatedAt"],
                is_deleted=comment.get("isDeleted", False),
                is_edited=comment.get("isEdited", False),
                is_nsfw=comment.get("isNsfw", False),
                is_spoiler=comment.get("isSpoiler", False),
                flair=comment.get("flair"),
                tags=comment.get("tags", []),
                awards=comment.get("awards", [])
            ).dict())
        
        return create_success_response(
            data={
                "comments": comment_responses,
                "total_count": len(comment_responses),
                "has_more": False,
                "next_offset": None
            },
            message="Comments retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Get comments error: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Get comments failed")

async def handle_get_comment_by_id(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle getting a comment by ID."""
    try:
        # Get comment ID from path parameters
        path_params = event.get("pathParameters", {}) or {}
        comment_id = path_params.get("comment_id")
        
        if not comment_id:
            return create_error_response(400, "BAD_REQUEST", "Comment ID is required")
        
        # Get comment from DynamoDB
        response = comments_table.get_item(Key={"commentId": comment_id})
        
        if "Item" not in response:
            return create_error_response(404, "NOT_FOUND", "Comment not found")
        
        comment = response["Item"]
        
        # Get author username
        try:
            user_response = users_table.get_item(Key={"userId": comment["authorId"]})
            comment["authorUsername"] = user_response.get("Item", {}).get("username", "Unknown")
        except:
            comment["authorUsername"] = "Unknown"
        
        # Create response
        comment_response = CommentResponse(
            comment_id=comment["commentId"],
            content=comment["content"],
            author_id=comment["authorId"],
            author_username=comment["authorUsername"],
            post_id=comment["postId"],
            parent_comment_id=comment.get("parentCommentId"),
            comment_type=comment["commentType"],
            media_urls=comment.get("mediaUrls", []),
            score=comment["score"],
            upvotes=comment["upvotes"],
            downvotes=comment["downvotes"],
            reply_count=comment["replyCount"],
            created_at=comment["createdAt"],
            updated_at=comment["updatedAt"],
            is_deleted=comment.get("isDeleted", False),
            is_edited=comment.get("isEdited", False),
            is_nsfw=comment.get("isNsfw", False),
            is_spoiler=comment.get("isSpoiler", False),
            flair=comment.get("flair"),
            tags=comment.get("tags", []),
            awards=comment.get("awards", [])
        )
        
        return create_success_response(
            data={"comment": comment_response.dict()},
            message="Comment retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Get comment by ID error: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Get comment failed")

async def handle_update_comment(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle updating a comment."""
    try:
        # Get comment ID from path parameters
        path_params = event.get("pathParameters", {}) or {}
        comment_id = path_params.get("comment_id")
        
        if not comment_id:
            return create_error_response(400, "BAD_REQUEST", "Comment ID is required")
        
        # Parse request body
        body = json.loads(event.get("body", "{}"))
        request = UpdateCommentRequest(**body)
        
        # Get user ID
        user_id = get_user_id_from_event(event)
        
        # Check if comment exists and user owns it
        response = comments_table.get_item(Key={"commentId": comment_id})
        
        if "Item" not in response:
            return create_error_response(404, "NOT_FOUND", "Comment not found")
        
        comment = response["Item"]
        
        if comment["authorId"] != user_id:
            return create_error_response(403, "FORBIDDEN", "You can only update your own comments")
        
        # Build update expression
        update_expressions = []
        expression_values = {}
        
        if request.content is not None:
            update_expressions.append("content = :content")
            expression_values[":content"] = request.content
        
        if request.comment_type is not None:
            update_expressions.append("commentType = :comment_type")
            expression_values[":comment_type"] = request.comment_type.value
        
        if request.media_urls is not None:
            update_expressions.append("mediaUrls = :media_urls")
            expression_values[":media_urls"] = request.media_urls
        
        if request.is_nsfw is not None:
            update_expressions.append("isNsfw = :is_nsfw")
            expression_values[":is_nsfw"] = request.is_nsfw
        
        if request.is_spoiler is not None:
            update_expressions.append("isSpoiler = :is_spoiler")
            expression_values[":is_spoiler"] = request.is_spoiler
        
        if request.flair is not None:
            update_expressions.append("flair = :flair")
            expression_values[":flair"] = request.flair
        
        if request.tags is not None:
            update_expressions.append("tags = :tags")
            expression_values[":tags"] = request.tags
        
        # Always update the updated_at timestamp and mark as edited
        update_expressions.append("updatedAt = :updated_at")
        expression_values[":updated_at"] = datetime.now(timezone.utc).isoformat()
        
        update_expressions.append("isEdited = :is_edited")
        expression_values[":is_edited"] = True
        
        if not update_expressions:
            return create_error_response(400, "BAD_REQUEST", "No fields to update")
        
        # Update comment
        comments_table.update_item(
            Key={"commentId": comment_id},
            UpdateExpression="SET " + ", ".join(update_expressions),
            ExpressionAttributeValues=expression_values
        )
        
        # Get updated comment
        updated_response = comments_table.get_item(Key={"commentId": comment_id})
        updated_comment = updated_response["Item"]
        
        # Get author username
        try:
            user_response = users_table.get_item(Key={"userId": updated_comment["authorId"]})
            updated_comment["authorUsername"] = user_response.get("Item", {}).get("username", "Unknown")
        except:
            updated_comment["authorUsername"] = "Unknown"
        
        # Create response
        comment_response = CommentResponse(
            comment_id=updated_comment["commentId"],
            content=updated_comment["content"],
            author_id=updated_comment["authorId"],
            author_username=updated_comment["authorUsername"],
            post_id=updated_comment["postId"],
            parent_comment_id=updated_comment.get("parentCommentId"),
            comment_type=updated_comment["commentType"],
            media_urls=updated_comment.get("mediaUrls", []),
            score=updated_comment["score"],
            upvotes=updated_comment["upvotes"],
            downvotes=updated_comment["downvotes"],
            reply_count=updated_comment["replyCount"],
            created_at=updated_comment["createdAt"],
            updated_at=updated_comment["updatedAt"],
            is_deleted=updated_comment.get("isDeleted", False),
            is_edited=updated_comment.get("isEdited", False),
            is_nsfw=updated_comment.get("isNsfw", False),
            is_spoiler=updated_comment.get("isSpoiler", False),
            flair=updated_comment.get("flair"),
            tags=updated_comment.get("tags", []),
            awards=updated_comment.get("awards", [])
        )
        
        return create_success_response(
            data={"comment": comment_response.dict()},
            message="Comment updated successfully"
        )
        
    except Exception as e:
        logger.error(f"Update comment error: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Update comment failed")

async def handle_delete_comment(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle deleting a comment."""
    try:
        # Get comment ID from path parameters
        path_params = event.get("pathParameters", {}) or {}
        comment_id = path_params.get("comment_id")
        
        if not comment_id:
            return create_error_response(400, "BAD_REQUEST", "Comment ID is required")
        
        # Get user ID
        user_id = get_user_id_from_event(event)
        
        # Check if comment exists and user owns it
        response = comments_table.get_item(Key={"commentId": comment_id})
        
        if "Item" not in response:
            return create_error_response(404, "NOT_FOUND", "Comment not found")
        
        comment = response["Item"]
        
        if comment["authorId"] != user_id:
            return create_error_response(403, "FORBIDDEN", "You can only delete your own comments")
        
        # Soft delete comment
        comments_table.update_item(
            Key={"commentId": comment_id},
            UpdateExpression="SET isDeleted = :is_deleted, updatedAt = :updated_at",
            ExpressionAttributeValues={
                ":is_deleted": True,
                ":updated_at": datetime.now(timezone.utc).isoformat()
            }
        )
        
        # Update post comment count
        try:
            posts_table.update_item(
                Key={"postId": comment["postId"]},
                UpdateExpression="ADD commentCount :dec",
                ExpressionAttributeValues={":dec": -1}
            )
        except Exception as e:
            logger.warning(f"Failed to update post comment count: {e}")
        
        # Update parent comment reply count if it's a reply
        if comment.get("parentCommentId"):
            try:
                comments_table.update_item(
                    Key={"commentId": comment["parentCommentId"]},
                    UpdateExpression="ADD replyCount :dec",
                    ExpressionAttributeValues={":dec": -1}
                )
            except Exception as e:
                logger.warning(f"Failed to update parent comment reply count: {e}")
        
        return create_success_response(
            data={"comment_id": comment_id},
            message="Comment deleted successfully"
        )
        
    except Exception as e:
        logger.error(f"Delete comment error: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Delete comment failed")

async def handle_vote_comment(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle voting on a comment."""
    try:
        # Get comment ID from path parameters
        path_params = event.get("pathParameters", {}) or {}
        comment_id = path_params.get("comment_id")
        
        if not comment_id:
            return create_error_response(400, "BAD_REQUEST", "Comment ID is required")
        
        # Parse request body
        body = json.loads(event.get("body", "{}"))
        request = VoteCommentRequest(**body)
        
        # Get user ID
        user_id = get_user_id_from_event(event)
        
        # Check if comment exists
        response = comments_table.get_item(Key={"commentId": comment_id})
        
        if "Item" not in response:
            return create_error_response(404, "NOT_FOUND", "Comment not found")
        
        comment = response["Item"]
        
        # For now, just update the vote counts (simplified implementation)
        if request.vote_type == "upvote":
            comments_table.update_item(
                Key={"commentId": comment_id},
                UpdateExpression="ADD upvotes :inc, score :inc",
                ExpressionAttributeValues={":inc": 1}
            )
        elif request.vote_type == "downvote":
            comments_table.update_item(
                Key={"commentId": comment_id},
                UpdateExpression="ADD downvotes :inc, score :dec",
                ExpressionAttributeValues={":inc": 1, ":dec": -1}
            )
        elif request.vote_type == "remove":
            # Remove vote (simplified - just decrement)
            comments_table.update_item(
                Key={"commentId": comment_id},
                UpdateExpression="ADD upvotes :dec, score :dec",
                ExpressionAttributeValues={":dec": -1}
            )
        else:
            return create_error_response(400, "BAD_REQUEST", "Invalid vote type")
        
        return create_success_response(
            data={"comment_id": comment_id, "vote_type": request.vote_type},
            message="Vote recorded successfully"
        )
        
    except Exception as e:
        logger.error(f"Vote comment error: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Vote comment failed")

# ==================== MAIN HANDLER ====================

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for comment endpoints."""
    logger.info(f"Event: {json.dumps(event)}")

    try:
        # Get path and method
        resource = event.get("resource", "")
        method = event.get("httpMethod", "")

        # Handle preflight OPTIONS requests
        if method == "OPTIONS":
            return create_success_response(message="CORS preflight")

        # Route to appropriate handler based on path
        if resource == "/comments/create" and method == "POST":
            return asyncio.run(handle_create_comment(event))
        elif resource == "/comments" and method == "GET":
            return asyncio.run(handle_get_comments(event))
        elif resource == "/comments/{comment_id}" and method == "GET":
            return asyncio.run(handle_get_comment_by_id(event))
        elif resource == "/comments/{comment_id}" and method == "PUT":
            return asyncio.run(handle_update_comment(event))
        elif resource == "/comments/{comment_id}" and method == "DELETE":
            return asyncio.run(handle_delete_comment(event))
        elif resource == "/comments/{comment_id}/vote" and method == "POST":
            return asyncio.run(handle_vote_comment(event))
        else:
            return create_error_response(404, "NOT_FOUND", "Endpoint not found")

    except Exception as e:
        logger.error(f"Lambda handler error: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Internal server error")
