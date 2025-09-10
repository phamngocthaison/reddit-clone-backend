"""
Lambda handler for Authentication + Posts functionality
"""

import json
import logging
import os
import boto3
import asyncio
import base64
import hmac
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
cognito = boto3.client("cognito-idp")
dynamodb = boto3.resource("dynamodb")

# Environment variables
USER_POOL_ID = os.environ.get("USER_POOL_ID")
CLIENT_ID = os.environ.get("CLIENT_ID")
USERS_TABLE = os.environ.get("USERS_TABLE")
POSTS_TABLE = os.environ.get("POSTS_TABLE")
SUBREDDITS_TABLE = os.environ.get("SUBREDDITS_TABLE")

# DynamoDB tables
users_table = dynamodb.Table(USERS_TABLE) if USERS_TABLE else None
posts_table = dynamodb.Table(POSTS_TABLE) if POSTS_TABLE else None
subreddits_table = dynamodb.Table(SUBREDDITS_TABLE) if SUBREDDITS_TABLE else None

# Authentication configuration
AUTH_MODE = os.environ.get('AUTH_MODE', 'hybrid')  # 'jwt', 'x-user-id', 'hybrid'

# ============================================================================
# AUTHENTICATION MODELS
# ============================================================================

from pydantic import BaseModel, EmailStr, validator, Field, root_validator, ValidationError
from typing import Optional, List
from enum import Enum
import uuid

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class LoginRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str
    
    @root_validator
    def validate_username_or_email(cls, values):
        # At least one of username or email must be provided
        username = values.get('username')
        email = values.get('email')
        if not username and not email:
            raise ValueError('Either username or email must be provided')
        return values

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str
    new_password: str

    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

# ============================================================================
# POSTS MODELS
# ============================================================================

class PostType(str, Enum):
    TEXT = "text"
    LINK = "link"
    IMAGE = "image"
    VIDEO = "video"
    POLL = "poll"

class PostBase(BaseModel):
    title: str = Field(..., min_length=1, description="Post title cannot be empty")
    content: Optional[str] = None
    subreddit_id: str = Field(..., min_length=1, description="Subreddit ID cannot be empty")
    post_type: PostType = PostType.TEXT
    url: Optional[str] = None
    media_urls: Optional[List[str]] = []
    is_nsfw: bool = False
    is_spoiler: bool = False
    flair: Optional[str] = None
    tags: Optional[List[str]] = []

class CreatePostRequest(PostBase):
    pass

class UpdatePostRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_nsfw: Optional[bool] = None
    is_spoiler: Optional[bool] = None
    flair: Optional[str] = None
    tags: Optional[List[str]] = None

class GetPostsRequest(BaseModel):
    subreddit_id: Optional[str] = None
    author_id: Optional[str] = None
    post_type: Optional[PostType] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"
    limit: int = 20
    offset: Optional[str] = None

class PostResponse(BaseModel):
    post_id: str
    title: str
    content: str
    author_id: str
    author_username: str
    subreddit_id: str
    post_type: str
    url: Optional[str]
    media_urls: List[str]
    score: int
    upvotes: int
    downvotes: int
    comment_count: int
    view_count: int
    created_at: str
    updated_at: str
    is_deleted: bool
    is_locked: bool
    is_sticky: bool
    is_nsfw: bool
    is_spoiler: bool
    flair: Optional[str]
    tags: List[str]
    awards: List[str]

class PostsResponse(BaseModel):
    posts: List[PostResponse]
    total_count: int
    has_more: bool
    next_offset: Optional[str]

class VoteType(str, Enum):
    UPVOTE = "upvote"
    DOWNVOTE = "downvote"
    REMOVE = "remove"

class VoteRequest(BaseModel):
    vote_type: VoteType

class VoteResponse(BaseModel):
    post_id: str
    user_id: str
    vote_type: str
    new_score: int
    new_upvotes: int
    new_downvotes: int

# ============================================================================
# JWT VALIDATION FUNCTIONS
# ============================================================================

def validate_jwt_token(event: Dict[str, Any]) -> Optional[str]:
    """
    Validate JWT token and return user_id if valid
    """
    try:
        # Get Authorization header
        headers = event.get('headers', {})
        auth_header = headers.get('Authorization') or headers.get('authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header[7:]  # Remove 'Bearer '
        
        # For now, we'll use a simple validation approach
        # In production, you should validate the JWT signature with Cognito
        try:
            # Decode JWT header and payload (without signature validation for now)
            parts = token.split('.')
            if len(parts) != 3:
                return None
            
            # Decode payload
            payload = parts[1]
            # Add padding if needed
            payload += '=' * (4 - len(payload) % 4)
            decoded_payload = base64.urlsafe_b64decode(payload)
            payload_data = json.loads(decoded_payload)
            
            # Check if token is expired
            exp = payload_data.get('exp')
            if exp and datetime.now(timezone.utc).timestamp() > exp:
                logger.warning("JWT token expired")
                return None
            
            # Extract user_id from token
            user_id = payload_data.get('sub') or payload_data.get('cognito:username')
            if not user_id:
                logger.warning("No user_id found in JWT token")
                return None
            
            logger.info(f"JWT validation successful for user: {user_id}")
            return user_id
            
        except Exception as e:
            logger.error(f"JWT token validation error: {e}")
            return None
            
    except Exception as e:
        logger.error(f"JWT validation error: {e}")
        return None

def get_user_id_from_event(event: Dict[str, Any]) -> Optional[str]:
    """
    Get user_id from JWT token or X-User-ID header based on AUTH_MODE
    """
    if AUTH_MODE == 'jwt':
        # JWT only mode
        return validate_jwt_token(event)
    
    elif AUTH_MODE == 'x-user-id':
        # X-User-ID only mode (for testing)
        headers = event.get('headers', {})
        return headers.get('X-User-ID') or headers.get('x-user-id')
    
    else:  # hybrid mode
        # Try JWT first, fallback to X-User-ID
        user_id = validate_jwt_token(event)
        if user_id:
            return user_id
        
        # Fallback to X-User-ID for testing
        headers = event.get('headers', {})
        return headers.get('X-User-ID') or headers.get('x-user-id')

def require_authentication(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Check if request requires authentication and validate it
    Returns error response if authentication fails, None if successful
    """
    user_id = get_user_id_from_event(event)
    if not user_id:
        return create_error_response(
            401, 
            "UNAUTHORIZED", 
            "Authentication required. Please provide valid JWT token or X-User-ID header."
        )
    return None

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_success_response(data: Any = None, message: str = "Success") -> Dict[str, Any]:
    """Create a success response."""
    response = {
        "success": True,
        "message": message,
        "data": data,
        "error": None
    }
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-User-ID",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
        },
        "body": json.dumps(response)
    }

def create_error_response(status_code: int, error_code: str, message: str, additional_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create an error response."""
    error_info = {
        "code": error_code,
        "message": message
    }
    
    if additional_data:
        error_info.update(additional_data)
    
    response = {
        "success": False,
        "message": message,
        "data": None,
        "error": error_info
    }
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-User-ID",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
        },
        "body": json.dumps(response)
    }


# ============================================================================
# AUTHENTICATION HANDLERS
# ============================================================================

async def handle_register(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle user registration."""
    try:
        body = json.loads(event.get("body", "{}"))
        request = RegisterRequest(**body)
        
        # Generate user ID
        user_id = f"user_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
        
        # Create user in Cognito
        try:
            cognito.admin_create_user(
                UserPoolId=USER_POOL_ID,
                Username=request.username,
                UserAttributes=[
                    {"Name": "email", "Value": request.email},
                    {"Name": "email_verified", "Value": "true"},
                    {"Name": "preferred_username", "Value": request.username},
                    {"Name": "custom:userId", "Value": user_id},
                ],
                MessageAction="SUPPRESS",
                TemporaryPassword="TempPass123!",
            )
            
            # Set permanent password
            cognito.admin_set_user_password(
                UserPoolId=USER_POOL_ID,
                Username=request.username,
                Password=request.password,
                Permanent=True,
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'UsernameExistsException':
                return create_error_response(400, "USER_EXISTS", "Username already exists")
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                return create_error_response(400, "INVALID_PARAMETER", str(e))
            else:
                raise e
        
        # Store user in DynamoDB
        user_data = {
            "userId": user_id,
            "email": request.email,
            "username": request.username,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "isActive": True
        }
        
        users_table.put_item(Item=user_data)
        
        return create_success_response(
            data={"user": user_data},
            message="User registered successfully"
        )
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Registration failed")

async def handle_login(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle user login."""
    try:
        body = json.loads(event.get("body", "{}"))
        request = LoginRequest(**body)
        
        # Authenticate with Cognito
        try:
            # Use email if provided, otherwise use username
            login_username = request.email or request.username
            
            response = cognito.admin_initiate_auth(
                UserPoolId=USER_POOL_ID,
                ClientId=CLIENT_ID,
                AuthFlow="ADMIN_NO_SRP_AUTH",
                AuthParameters={
                    "USERNAME": login_username,
                    "PASSWORD": request.password,
                },
            )
            
            # Get user details
            user_response = cognito.admin_get_user(
                UserPoolId=USER_POOL_ID,
                Username=login_username
            )
            
            # Extract user ID from custom attributes
            user_id = None
            for attr in user_response.get("UserAttributes", []):
                if attr["Name"] == "custom:userId":
                    user_id = attr["Value"]
                    break
            
            if not user_id:
                return create_error_response(500, "USER_ID_NOT_FOUND", "User ID not found")
            
            return create_success_response(
                data={
                    "access_token": response["AuthenticationResult"]["AccessToken"],
                    "refresh_token": response["AuthenticationResult"]["RefreshToken"],
                    "id_token": response["AuthenticationResult"]["IdToken"],
                    "user_id": user_id,
                    "username": request.username
                },
                message="Login successful"
            )
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NotAuthorizedException':
                return create_error_response(401, "INVALID_CREDENTIALS", "Invalid username or password")
            else:
                raise e
                
    except ValidationError as e:
        logger.error(f"Login validation error: {e}")
        error_details = []
        for error in e.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            error_details.append(f"{field}: {message}")
        
        return create_error_response(
            400,
            "VALIDATION_ERROR",
            "Validation failed",
            {"validation_errors": error_details}
        )
    except Exception as e:
        logger.error(f"Login error: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Login failed")

async def handle_logout(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle user logout."""
    try:
        # Check authentication
        auth_error = require_authentication(event)
        if auth_error:
            return auth_error
        
        # For now, just return success
        # In a real implementation, you would invalidate the token
        return create_success_response(message="Logout successful")
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Logout failed")

async def handle_forgot_password(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle forgot password request."""
    try:
        body = json.loads(event.get("body", "{}"))
        request = ForgotPasswordRequest(**body)
        
        # Send forgot password code
        cognito.forgot_password(
            ClientId=CLIENT_ID,
            Username=request.email
        )
        
        return create_success_response(message="Password reset code sent")
        
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Forgot password failed")

async def handle_reset_password(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle password reset."""
    try:
        body = json.loads(event.get("body", "{}"))
        request = ResetPasswordRequest(**body)
        
        # Reset password
        cognito.confirm_forgot_password(
            ClientId=CLIENT_ID,
            Username=request.email,
            ConfirmationCode=request.code,
            Password=request.new_password
        )
        
        return create_success_response(message="Password reset successful")
        
    except Exception as e:
        logger.error(f"Reset password error: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Password reset failed")

# ============================================================================
# POSTS HANDLERS
# ============================================================================

async def handle_create_post(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle create post request."""
    try:
        # Check authentication
        auth_error = require_authentication(event)
        if auth_error:
            return auth_error
        
        body = json.loads(event.get("body", "{}"))
        request = CreatePostRequest(**body)
        user_id = get_user_id_from_event(event)
        
        # Generate post ID
        post_id = f"post_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
        
        # Create post data
        post_data = {
            "postId": post_id,
            "title": request.title,
            "content": request.content or "",
            "authorId": user_id,
            "subredditId": request.subreddit_id,
            "postType": request.post_type.value,
            "url": request.url,
            "mediaUrls": request.media_urls or [],
            "score": 0,
            "upvotes": 0,
            "downvotes": 0,
            "commentCount": 0,
            "viewCount": 0,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "updatedAt": datetime.now(timezone.utc).isoformat(),
            "isDeleted": False,
            "isLocked": False,
            "isSticky": False,
            "isNsfw": request.is_nsfw,
            "isSpoiler": request.is_spoiler,
            "flair": request.flair,
            "tags": request.tags or [],
            "awards": []
        }
        
        # Store in DynamoDB
        posts_table.put_item(Item=post_data)
        
        # Get author username
        try:
            user_response = users_table.get_item(Key={"userId": user_id})
            author_username = user_response.get("Item", {}).get("username", "Unknown")
        except:
            author_username = "Unknown"
        
        # Create response
        post_response = PostResponse(
            post_id=post_data["postId"],
            title=post_data["title"],
            content=post_data["content"],
            author_id=post_data["authorId"],
            author_username=author_username,
            subreddit_id=post_data["subredditId"],
            post_type=post_data["postType"],
            url=post_data["url"],
            media_urls=post_data["mediaUrls"],
            score=post_data["score"],
            upvotes=post_data["upvotes"],
            downvotes=post_data["downvotes"],
            comment_count=post_data["commentCount"],
            view_count=post_data["viewCount"],
            created_at=post_data["createdAt"],
            updated_at=post_data["updatedAt"],
            is_deleted=post_data["isDeleted"],
            is_locked=post_data["isLocked"],
            is_sticky=post_data["isSticky"],
            is_nsfw=post_data["isNsfw"],
            is_spoiler=post_data["isSpoiler"],
            flair=post_data["flair"],
            tags=post_data["tags"],
            awards=post_data["awards"]
        )
        
        return create_success_response(
            data={"post": post_response.dict()},
            message="Post created successfully"
        )
        
    except ValidationError as e:
        logger.error(f"Create post validation error: {e}")
        # Extract validation error details
        error_details = []
        for error in e.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            error_details.append(f"{field}: {message}")
        
        return create_error_response(
            400, 
            "VALIDATION_ERROR", 
            "Validation failed", 
            {"validation_errors": error_details}
        )
    except Exception as e:
        logger.error(f"Create post error: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Create post failed")

async def handle_get_posts(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get posts request."""
    try:
        query_params = event.get("queryStringParameters") or {}
        
        # Build query parameters
        query_params_dynamo = {}
        
        if query_params.get("subreddit_id"):
            query_params_dynamo["subredditId"] = query_params["subreddit_id"]
        
        if query_params.get("author_id"):
            query_params_dynamo["authorId"] = query_params["author_id"]
        
        if query_params.get("post_type"):
            query_params_dynamo["postType"] = query_params["post_type"]
        
        # Query posts
        if query_params_dynamo:
            response = posts_table.scan(
                FilterExpression=" AND ".join([f"{k} = :{k}" for k in query_params_dynamo.keys()]),
                ExpressionAttributeValues={f":{k}": v for k, v in query_params_dynamo.items()},
                Limit=int(query_params.get("limit", 20))
            )
        else:
            response = posts_table.scan(Limit=int(query_params.get("limit", 20)))
        
        posts = response.get("Items", [])
        
        # Sort posts
        sort_by = query_params.get("sort_by", "created_at")
        sort_order = query_params.get("sort_order", "desc")
        
        if sort_by == "created_at":
            posts.sort(key=lambda x: x.get("createdAt", ""), reverse=(sort_order == "desc"))
        elif sort_by == "score":
            posts.sort(key=lambda x: x.get("score", 0), reverse=(sort_order == "desc"))
        
        # Get author usernames
        for post in posts:
            try:
                user_response = users_table.get_item(Key={"userId": post["authorId"]})
                post["authorUsername"] = user_response.get("Item", {}).get("username", "Unknown")
            except:
                post["authorUsername"] = "Unknown"
        
        # Create response
        post_responses = []
        for post in posts:
            post_responses.append(PostResponse(
                post_id=post["postId"],
                title=post["title"],
                content=post["content"],
                author_id=post["authorId"],
                author_username=post["authorUsername"],
                subreddit_id=post["subredditId"],
                post_type=post["postType"],
                url=post["url"],
                media_urls=post["mediaUrls"],
                score=post["score"],
                upvotes=post["upvotes"],
                downvotes=post["downvotes"],
                comment_count=post["commentCount"],
                view_count=post["viewCount"],
                created_at=post["createdAt"],
                updated_at=post["updatedAt"],
                is_deleted=post.get("isDeleted", False),
                is_locked=post.get("isLocked", False),
                is_sticky=post.get("isSticky", False),
                is_nsfw=post.get("isNsfw", False),
                is_spoiler=post.get("isSpoiler", False),
                flair=post["flair"],
                tags=post["tags"],
                awards=post["awards"]
            ).dict())
        
        return create_success_response(
            data={
                "posts": post_responses,
                "total_count": len(post_responses),
                "has_more": False,
                "next_offset": None
            },
            message="Posts retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Get posts error: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Get posts failed")


async def handle_get_posts(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get posts request."""
    try:
        query_params = event.get("queryStringParameters") or {}
        request = GetPostsRequest(**query_params)
        
        # Build query parameters
        query_params_dynamo = {}
        
        if request.subreddit_id:
            query_params_dynamo["subredditId"] = request.subreddit_id
        
        if request.author_id:
            query_params_dynamo["authorId"] = request.author_id
        
        if request.post_type:
            query_params_dynamo["postType"] = request.post_type.value
        
        # Query posts
        if query_params_dynamo:
            response = posts_table.scan(
                FilterExpression=" AND ".join([f"{k} = :{k}" for k in query_params_dynamo.keys()]),
                ExpressionAttributeValues={f":{k}": v for k, v in query_params_dynamo.items()},
                Limit=request.limit
            )
        else:
            response = posts_table.scan(Limit=request.limit)
        
        posts = response.get("Items", [])
        
        # Sort posts
        if request.sort_by == "created_at":
            posts.sort(key=lambda x: x.get("createdAt", ""), reverse=(request.sort_order == "desc"))
        elif request.sort_by == "score":
            posts.sort(key=lambda x: x.get("score", 0), reverse=(request.sort_order == "desc"))
        
        # Get author usernames
        for post in posts:
            try:
                user_response = users_table.get_item(Key={"userId": post["authorId"]})
                post["authorUsername"] = user_response.get("Item", {}).get("username", "Unknown")
            except:
                post["authorUsername"] = "Unknown"
        
        # Create response
        post_responses = []
        for post in posts:
            post_responses.append(PostResponse(
                post_id=post["postId"],
                title=post["title"],
                content=post["content"],
                author_id=post["authorId"],
                author_username=post["authorUsername"],
                subreddit_id=post["subredditId"],
                post_type=post["postType"],
                url=post["url"],
                media_urls=post["mediaUrls"],
                score=post["score"],
                upvotes=post["upvotes"],
                downvotes=post["downvotes"],
                comment_count=post["commentCount"],
                view_count=post["viewCount"],
                created_at=post["createdAt"],
                updated_at=post["updatedAt"],
                is_deleted=post.get("isDeleted", False),
                is_locked=post.get("isLocked", False),
                is_sticky=post.get("isSticky", False),
                is_nsfw=post.get("isNsfw", False),
                is_spoiler=post.get("isSpoiler", False),
                flair=post["flair"],
                tags=post["tags"],
                awards=post["awards"]
            ).dict())
        
        return create_success_response(
            data={
                "posts": post_responses,
                "total_count": len(post_responses),
                "has_more": False,
                "next_offset": None
            },
            message="Posts retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Get posts error: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Get posts failed")

async def handle_get_post_by_id(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get post by ID request."""
    try:
        # Extract post ID from path
        path = event.get("path", "")
        post_id = path.split("/")[-1]
        
        if not post_id or post_id == "posts":
            return create_error_response(400, "INVALID_POST_ID", "Post ID is required")
        
        # Get post from DynamoDB
        response = posts_table.get_item(Key={"postId": post_id})
        
        if "Item" not in response:
            return create_error_response(404, "POST_NOT_FOUND", "Post not found")
        
        post = response["Item"]
        
        # Get author username
        try:
            user_response = users_table.get_item(Key={"userId": post["authorId"]})
            author_username = user_response.get("Item", {}).get("username", "Unknown")
        except:
            author_username = "Unknown"
        
        # Create response
        post_response = PostResponse(
            post_id=post["postId"],
            title=post["title"],
            content=post["content"],
            author_id=post["authorId"],
            author_username=author_username,
            subreddit_id=post["subredditId"],
            post_type=post["postType"],
            url=post["url"],
            media_urls=post["mediaUrls"],
            score=post["score"],
            upvotes=post["upvotes"],
            downvotes=post["downvotes"],
            comment_count=post["commentCount"],
            view_count=post["viewCount"],
            created_at=post["createdAt"],
            updated_at=post["updatedAt"],
            is_deleted=post.get("isDeleted", False),
            is_locked=post.get("isLocked", False),
            is_sticky=post.get("isSticky", False),
            is_nsfw=post.get("isNsfw", False),
            is_spoiler=post.get("isSpoiler", False),
            flair=post["flair"],
            tags=post["tags"],
            awards=post["awards"]
        )
        
        return create_success_response(
            data={"post": post_response.dict()},
            message="Post retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Get post by ID error: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Get post failed")

async def handle_update_post(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle update post request."""
    try:
        # Check authentication
        auth_error = require_authentication(event)
        if auth_error:
            return auth_error
        
        # Extract post ID from path
        path = event.get("path", "")
        post_id = path.split("/")[-1]
        
        if not post_id or post_id == "posts":
            return create_error_response(400, "INVALID_POST_ID", "Post ID is required")
        
        body = json.loads(event.get("body", "{}"))
        request = UpdatePostRequest(**body)
        user_id = get_user_id_from_event(event)
        
        # Get existing post
        response = posts_table.get_item(Key={"postId": post_id})
        
        if "Item" not in response:
            return create_error_response(404, "POST_NOT_FOUND", "Post not found")
        
        post = response["Item"]
        
        # Check if user is the author
        if post["authorId"] != user_id:
            return create_error_response(403, "ACCESS_DENIED", "Only the author can update this post")
        
        # Update post data
        update_expression = "SET updatedAt = :updatedAt"
        expression_values = {":updatedAt": datetime.now(timezone.utc).isoformat()}
        
        if request.title is not None:
            update_expression += ", title = :title"
            expression_values[":title"] = request.title
        
        if request.content is not None:
            update_expression += ", content = :content"
            expression_values[":content"] = request.content
        
        if request.is_nsfw is not None:
            update_expression += ", isNsfw = :isNsfw"
            expression_values[":isNsfw"] = request.is_nsfw
        
        if request.is_spoiler is not None:
            update_expression += ", isSpoiler = :isSpoiler"
            expression_values[":isSpoiler"] = request.is_spoiler
        
        if request.flair is not None:
            update_expression += ", flair = :flair"
            expression_values[":flair"] = request.flair
        
        if request.tags is not None:
            update_expression += ", tags = :tags"
            expression_values[":tags"] = request.tags
        
        # Update post in DynamoDB
        posts_table.update_item(
            Key={"postId": post_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values
        )
        
        # Get updated post
        updated_response = posts_table.get_item(Key={"postId": post_id})
        updated_post = updated_response["Item"]
        
        # Get author username
        try:
            user_response = users_table.get_item(Key={"userId": updated_post["authorId"]})
            author_username = user_response.get("Item", {}).get("username", "Unknown")
        except:
            author_username = "Unknown"
        
        # Create response
        post_response = PostResponse(
            post_id=updated_post["postId"],
            title=updated_post["title"],
            content=updated_post["content"],
            author_id=updated_post["authorId"],
            author_username=author_username,
            subreddit_id=updated_post["subredditId"],
            post_type=updated_post["postType"],
            url=updated_post["url"],
            media_urls=updated_post["mediaUrls"],
            score=updated_post["score"],
            upvotes=updated_post["upvotes"],
            downvotes=updated_post["downvotes"],
            comment_count=updated_post["commentCount"],
            view_count=updated_post["viewCount"],
            created_at=updated_post["createdAt"],
            updated_at=updated_post["updatedAt"],
            is_deleted=updated_post.get("isDeleted", False),
            is_locked=updated_post.get("isLocked", False),
            is_sticky=updated_post.get("isSticky", False),
            is_nsfw=updated_post.get("isNsfw", False),
            is_spoiler=updated_post.get("isSpoiler", False),
            flair=updated_post["flair"],
            tags=updated_post["tags"],
            awards=updated_post["awards"]
        )
        
        return create_success_response(
            data={"post": post_response.dict()},
            message="Post updated successfully"
        )
        
    except ValidationError as e:
        logger.error(f"Update post validation error: {e}")
        error_details = []
        for error in e.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            error_details.append(f"{field}: {message}")
        
        return create_error_response(
            400, 
            "VALIDATION_ERROR", 
            "Validation failed", 
            {"validation_errors": error_details}
        )
    except Exception as e:
        logger.error(f"Update post error: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Update post failed")

async def handle_delete_post(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle delete post request."""
    try:
        # Check authentication
        auth_error = require_authentication(event)
        if auth_error:
            return auth_error
        
        # Extract post ID from path
        path = event.get("path", "")
        post_id = path.split("/")[-1]
        
        if not post_id or post_id == "posts":
            return create_error_response(400, "INVALID_POST_ID", "Post ID is required")
        
        user_id = get_user_id_from_event(event)
        
        # Get existing post
        response = posts_table.get_item(Key={"postId": post_id})
        
        if "Item" not in response:
            return create_error_response(404, "POST_NOT_FOUND", "Post not found")
        
        post = response["Item"]
        
        # Check if user is the author
        if post["authorId"] != user_id:
            return create_error_response(403, "ACCESS_DENIED", "Only the author can delete this post")
        
        # Soft delete post
        posts_table.update_item(
            Key={"postId": post_id},
            UpdateExpression="SET isDeleted = :isDeleted, updatedAt = :updatedAt",
            ExpressionAttributeValues={
                ":isDeleted": True,
                ":updatedAt": datetime.now(timezone.utc).isoformat()
            }
        )
        
        return create_success_response(message="Post deleted successfully")
        
    except Exception as e:
        logger.error(f"Delete post error: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Delete post failed")

async def handle_vote_post(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle vote post request."""
    try:
        # Check authentication
        auth_error = require_authentication(event)
        if auth_error:
            return auth_error
        
        # Extract post ID from path
        path = event.get("path", "")
        post_id = path.split("/")[-2]  # /posts/{post_id}/vote
        
        if not post_id or post_id == "posts":
            return create_error_response(400, "INVALID_POST_ID", "Post ID is required")
        
        body = json.loads(event.get("body", "{}"))
        request = VoteRequest(**body)
        user_id = get_user_id_from_event(event)
        
        # Get existing post
        response = posts_table.get_item(Key={"postId": post_id})
        
        if "Item" not in response:
            return create_error_response(404, "POST_NOT_FOUND", "Post not found")
        
        post = response["Item"]
        
        # For now, just update the vote counts (simplified implementation)
        # In a real implementation, you would track individual user votes
        current_upvotes = post.get("upvotes", 0)
        current_downvotes = post.get("downvotes", 0)
        
        if request.vote_type == VoteType.UPVOTE:
            new_upvotes = current_upvotes + 1
            new_downvotes = current_downvotes
        elif request.vote_type == VoteType.DOWNVOTE:
            new_upvotes = current_upvotes
            new_downvotes = current_downvotes + 1
        else:  # REMOVE
            new_upvotes = max(0, current_upvotes - 1)
            new_downvotes = max(0, current_downvotes - 1)
        
        new_score = new_upvotes - new_downvotes
        
        # Update post vote counts
        posts_table.update_item(
            Key={"postId": post_id},
            UpdateExpression="SET upvotes = :upvotes, downvotes = :downvotes, score = :score, updatedAt = :updatedAt",
            ExpressionAttributeValues={
                ":upvotes": new_upvotes,
                ":downvotes": new_downvotes,
                ":score": new_score,
                ":updatedAt": datetime.now(timezone.utc).isoformat()
            }
        )
        
        return create_success_response(
            data={
                "stats": {
                    "post_id": post_id,
                    "score": new_score,
                    "upvotes": new_upvotes,
                    "downvotes": new_downvotes,
                    "comment_count": post.get("commentCount", 0),
                    "view_count": post.get("viewCount", 0)
                }
            },
            message="Vote recorded successfully"
        )
        
    except ValidationError as e:
        logger.error(f"Vote post validation error: {e}")
        error_details = []
        for error in e.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            error_details.append(f"{field}: {message}")
        
        return create_error_response(
            400, 
            "VALIDATION_ERROR", 
            "Validation failed", 
            {"validation_errors": error_details}
        )
    except Exception as e:
        logger.error(f"Vote post error: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Vote post failed")

# ============================================================================
# MAIN HANDLER
# ============================================================================

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for authentication and posts endpoints."""
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
        elif resource == "/posts/create" and method == "POST":
            return asyncio.run(handle_create_post(event))
        elif resource == "/posts" and method == "GET":
            return asyncio.run(handle_get_posts(event))
        elif resource.startswith("/posts/") and method == "GET":
            return asyncio.run(handle_get_post_by_id(event))
        elif resource.startswith("/posts/") and method == "PUT":
            return asyncio.run(handle_update_post(event))
        elif resource.startswith("/posts/") and method == "DELETE":
            return asyncio.run(handle_delete_post(event))
        elif resource.endswith("/vote") and method == "POST":
            return asyncio.run(handle_vote_post(event))
        else:
            return create_error_response(404, "NOT_FOUND", "Endpoint not found")

    except Exception as e:
        logger.error(f"Lambda handler error: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Internal server error")
