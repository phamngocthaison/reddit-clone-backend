"""Phase 2 Lambda handler with authentication and posts functionality."""

import asyncio
import json
import logging
import os
import re
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel, EmailStr, Field, ValidationError
from enum import Enum

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Force rebuild - Phase 2.3 with Posts and Comments functionality

# Import Comment handlers
try:
    from comment_handler import (
        create_comment_handler,
        get_comments_handler,
        get_comment_by_id_handler,
        update_comment_handler,
        delete_comment_handler,
        vote_comment_handler
    )
except ImportError:
    # Fallback - define simple handlers
    def create_comment_handler(event):
        return {"statusCode": 501, "body": "Comment handler not available"}
    def get_comments_handler(event):
        return {"statusCode": 501, "body": "Comment handler not available"}
    def get_comment_by_id_handler(event):
        return {"statusCode": 501, "body": "Comment handler not available"}
    def update_comment_handler(event):
        return {"statusCode": 501, "body": "Comment handler not available"}
    def delete_comment_handler(event):
        return {"statusCode": 501, "body": "Comment handler not available"}
    def vote_comment_handler(event):
        return {"statusCode": 501, "body": "Comment handler not available"}

# ============================================================================
# MODELS
# ============================================================================

class User(BaseModel):
    """User model."""
    user_id: str = Field(..., alias="userId")
    email: EmailStr
    username: str
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    is_active: bool = Field(..., alias="isActive")

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }

class RegisterRequest(BaseModel):
    """User registration request model."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8)

class LoginRequest(BaseModel):
    """User login request model."""
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    """Forgot password request model."""
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    """Reset password request model."""
    email: EmailStr
    code: str
    new_password: str = Field(..., min_length=8)

class LogoutRequest(BaseModel):
    """Logout request model."""
    access_token: str

# Posts Models
class PostType(str, Enum):
    TEXT = "text"
    LINK = "link"
    IMAGE = "image"
    VIDEO = "video"
    POLL = "poll"

class PostSort(str, Enum):
    HOT = "hot"
    NEW = "new"
    TOP = "top"
    RISING = "rising"
    CONTROVERSIAL = "controversial"

class PostTimeFilter(str, Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    ALL = "all"

class CreatePostRequest(BaseModel):
    """Create post request model."""
    title: str = Field(..., min_length=1, max_length=300)
    content: Optional[str] = Field(None, max_length=40000)
    subreddit_id: str = Field(..., description="Subreddit ID")
    post_type: PostType = Field(PostType.TEXT)
    url: Optional[str] = Field(None)
    media_urls: Optional[list] = Field(None)
    is_nsfw: bool = Field(False)
    is_spoiler: bool = Field(False)
    flair: Optional[str] = Field(None, max_length=100)
    tags: Optional[list] = Field(None)

class UpdatePostRequest(BaseModel):
    """Update post request model."""
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    content: Optional[str] = Field(None, max_length=40000)
    is_nsfw: Optional[bool] = Field(None)
    is_spoiler: Optional[bool] = Field(None)
    flair: Optional[str] = Field(None, max_length=100)
    tags: Optional[list] = Field(None)

class GetPostsRequest(BaseModel):
    """Get posts request model."""
    subreddit_id: Optional[str] = Field(None)
    author_id: Optional[str] = Field(None)
    sort: PostSort = Field(PostSort.HOT)
    time_filter: PostTimeFilter = Field(PostTimeFilter.DAY)
    limit: int = Field(25, ge=1, le=100)
    offset: int = Field(0, ge=0)
    post_type: Optional[PostType] = Field(None)
    is_nsfw: Optional[bool] = Field(None)

class VotePostRequest(BaseModel):
    """Vote post request model."""
    vote_type: str = Field(..., regex="^(upvote|downvote|remove)$")

# ============================================================================
# SERVICES
# ============================================================================

class AuthService:
    """Authentication service."""
    
    def __init__(self):
        self.cognito = boto3.client('cognito-idp', region_name=os.getenv('REGION', 'ap-southeast-1'))
        self.dynamodb = boto3.resource('dynamodb', region_name=os.getenv('REGION', 'ap-southeast-1'))
        self.user_pool_id = os.getenv('USER_POOL_ID')
        self.client_id = os.getenv('CLIENT_ID')
        self.users_table = self.dynamodb.Table(os.getenv('USERS_TABLE', 'reddit-clone-users'))
    
    def register(self, request: RegisterRequest) -> User:
        """Register a new user."""
        try:
            # Check if user already exists
            existing_user = self._get_user_by_email(request.email)
            if existing_user:
                raise ValueError("User with this email already exists")
            
            # Generate user ID
            user_id = f"user_{int(time.time())}_{str(uuid.uuid4())[:8]}"
            
            # Create user in Cognito
            self.cognito.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=request.username,  # Use username instead of email
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
            self.cognito.admin_set_user_password(
                UserPoolId=self.user_pool_id,
                Username=request.username,  # Use username instead of email
                Password=request.password,
                Permanent=True,
            )
            
            # Store user in DynamoDB
            current_time = datetime.now(timezone.utc).isoformat()
            user_data = {
                "userId": user_id,
                "email": request.email,
                "username": request.username,
                "createdAt": current_time,
                "updatedAt": current_time,
                "isActive": True,
            }
            
            self.users_table.put_item(Item=user_data)
            
            return User(**user_data)
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'UsernameExistsException':
                raise ValueError("Username already exists")
            elif error_code == 'InvalidParameterException':
                raise ValueError("Invalid parameters provided")
            else:
                raise ValueError(f"Registration failed: {e.response['Error']['Message']}")
    
    def login(self, request: LoginRequest) -> Dict[str, Any]:
        """Login user."""
        try:
            # Authenticate with Cognito
            response = self.cognito.admin_initiate_auth(
                UserPoolId=self.user_pool_id,
                ClientId=self.client_id,
                AuthFlow="ADMIN_NO_SRP_AUTH",
                AuthParameters={
                    "USERNAME": request.email,  # Use email for login
                    "PASSWORD": request.password,
                },
            )
            
            # Get user info
            user_info = self.cognito.admin_get_user(
                UserPoolId=self.user_pool_id,
                Username=request.email
            )
            
            # Extract user ID from custom attributes
            user_id = None
            for attr in user_info.get('UserAttributes', []):
                if attr['Name'] == 'custom:userId':
                    user_id = attr['Value']
                    break
            
            if not user_id:
                raise ValueError("User ID not found")
            
            # Get user from DynamoDB
            user = self._get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found in database")
            
            return {
                "user": user,
                "access_token": response['AuthenticationResult']['AccessToken'],
                "refresh_token": response['AuthenticationResult']['RefreshToken'],
                "id_token": response['AuthenticationResult']['IdToken'],
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NotAuthorizedException':
                raise ValueError("Invalid credentials")
            elif error_code == 'UserNotFoundException':
                raise ValueError("User not found")
            else:
                raise ValueError(f"Login failed: {e.response['Error']['Message']}")
    
    def logout(self, request: LogoutRequest) -> bool:
        """Logout user."""
        try:
            # Global sign out
            self.cognito.global_sign_out(
                AccessToken=request.access_token
            )
            return True
        except ClientError as e:
            logger.error(f"Logout failed: {e}")
            return False
    
    def forgot_password(self, request: ForgotPasswordRequest) -> bool:
        """Initiate forgot password flow."""
        try:
            self.cognito.forgot_password(
                ClientId=self.client_id,
                Username=request.email
            )
            return True
        except ClientError as e:
            logger.error(f"Forgot password failed: {e}")
            return False
    
    def reset_password(self, request: ResetPasswordRequest) -> bool:
        """Reset password with confirmation code."""
        try:
            self.cognito.confirm_forgot_password(
                ClientId=self.client_id,
                Username=request.email,
                ConfirmationCode=request.code,
                Password=request.new_password
            )
            return True
        except ClientError as e:
            logger.error(f"Reset password failed: {e}")
            return False
    
    def _get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            response = self.users_table.query(
                IndexName="EmailIndex",
                KeyConditionExpression="email = :email",
                ExpressionAttributeValues={":email": email}
            )
            
            if response['Items']:
                return User(**response['Items'][0])
            return None
        except ClientError:
            return None
    
    def _get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        try:
            response = self.users_table.get_item(Key={"userId": user_id})
            if 'Item' in response:
                return User(**response['Item'])
            return None
        except ClientError:
            return None

class PostsService:
    """Posts service."""
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=os.getenv('REGION', 'ap-southeast-1'))
        self.posts_table = self.dynamodb.Table(os.getenv('POSTS_TABLE', 'reddit-clone-posts'))
        self.users_table = self.dynamodb.Table(os.getenv('USERS_TABLE', 'reddit-clone-users'))
        self.subreddits_table = self.dynamodb.Table(os.getenv('SUBREDDITS_TABLE', 'reddit-clone-subreddits'))
    
    def create_post(self, request: CreatePostRequest, author_id: str) -> Dict[str, Any]:
        """Create a new post."""
        try:
            # Generate post ID
            post_id = f"post_{int(time.time())}_{str(uuid.uuid4())[:8]}"
            current_time = datetime.now(timezone.utc).isoformat()
            
            # Get author info
            author = self._get_user(author_id)
            if not author:
                raise ValueError("Author not found")
            
            # Create post data
            post_data = {
                "postId": post_id,
                "title": request.title,
                "content": request.content,
                "authorId": author_id,
                "subredditId": request.subreddit_id,
                "postType": request.post_type.value,
                "url": request.url,
                "mediaUrls": request.media_urls or [],
                "score": 0,
                "upvotes": 0,
                "downvotes": 0,
                "commentCount": 0,
                "viewCount": 0,
                "createdAt": current_time,
                "updatedAt": current_time,
                "isDeleted": False,
                "isLocked": False,
                "isSticky": False,
                "isNSFW": request.is_nsfw,
                "isSpoiler": request.is_spoiler,
                "flair": request.flair,
                "tags": request.tags or [],
                "awards": []
            }
            
            # Save to DynamoDB
            self.posts_table.put_item(Item=post_data)
            
            # Return response
            return {
                "post_id": post_id,
                "title": request.title,
                "content": request.content,
                "author_id": author_id,
                "author_username": author.get('username', 'Unknown'),
                "subreddit_id": request.subreddit_id,
                "post_type": request.post_type.value,
                "url": request.url,
                "media_urls": request.media_urls,
                "score": 0,
                "upvotes": 0,
                "downvotes": 0,
                "comment_count": 0,
                "view_count": 0,
                "created_at": current_time,
                "updated_at": current_time,
                "is_deleted": False,
                "is_locked": False,
                "is_sticky": False,
                "is_nsfw": request.is_nsfw,
                "is_spoiler": request.is_spoiler,
                "flair": request.flair,
                "tags": request.tags,
                "awards": None
            }
            
        except ClientError as e:
            raise ValueError(f"Database error: {str(e)}")
    
    def get_post(self, post_id: str) -> Dict[str, Any]:
        """Get a single post by ID."""
        try:
            response = self.posts_table.get_item(Key={"postId": post_id})
            
            if 'Item' not in response:
                raise ValueError("Post not found")
            
            post_data = response['Item']
            
            # Check if post is deleted
            if post_data.get('isDeleted', False):
                raise ValueError("Post not found")
            
            # Get author info
            author = self._get_user(post_data['authorId'])
            
            return {
                "post_id": post_data['postId'],
                "title": post_data['title'],
                "content": post_data.get('content'),
                "author_id": post_data['authorId'],
                "author_username": author.get('username', 'Unknown') if author else 'Unknown',
                "subreddit_id": post_data['subredditId'],
                "post_type": post_data['postType'],
                "url": post_data.get('url'),
                "media_urls": post_data.get('mediaUrls', []),
                "score": post_data.get('score', 0),
                "upvotes": post_data.get('upvotes', 0),
                "downvotes": post_data.get('downvotes', 0),
                "comment_count": post_data.get('commentCount', 0),
                "view_count": post_data.get('viewCount', 0),
                "created_at": post_data['createdAt'],
                "updated_at": post_data['updatedAt'],
                "is_deleted": post_data.get('isDeleted', False),
                "is_locked": post_data.get('isLocked', False),
                "is_sticky": post_data.get('isSticky', False),
                "is_nsfw": post_data.get('isNSFW', False),
                "is_spoiler": post_data.get('isSpoiler', False),
                "flair": post_data.get('flair'),
                "tags": post_data.get('tags', []),
                "awards": post_data.get('awards', [])
            }
            
        except ClientError as e:
            raise ValueError(f"Database error: {str(e)}")
    
    def get_posts(self, request: GetPostsRequest) -> Dict[str, Any]:
        """Get posts with filtering and sorting."""
        try:
            posts = []
            
            # For now, simple scan with basic filtering
            scan_params = {
                "Limit": request.limit + request.offset
            }
            
            # Add filters
            filter_expressions = []
            expression_values = {}
            
            if request.subreddit_id:
                filter_expressions.append("subredditId = :subreddit_id")
                expression_values[":subreddit_id"] = request.subreddit_id
            
            if request.author_id:
                filter_expressions.append("authorId = :author_id")
                expression_values[":author_id"] = request.author_id
            
            if request.post_type:
                filter_expressions.append("postType = :post_type")
                expression_values[":post_type"] = request.post_type.value
            
            if request.is_nsfw is not None:
                filter_expressions.append("isNSFW = :is_nsfw")
                expression_values[":is_nsfw"] = request.is_nsfw
            
            if filter_expressions:
                scan_params["FilterExpression"] = " AND ".join(filter_expressions)
                scan_params["ExpressionAttributeValues"] = expression_values
            
            response = self.posts_table.scan(**scan_params)
            
            # Process results
            for item in response.get('Items', []):
                if item.get('isDeleted', False):
                    continue
                
                # Get author info
                author = self._get_user(item['authorId'])
                
                post = {
                    "post_id": item['postId'],
                    "title": item['title'],
                    "content": item.get('content'),
                    "author_id": item['authorId'],
                    "author_username": author.get('username', 'Unknown') if author else 'Unknown',
                    "subreddit_id": item['subredditId'],
                    "post_type": item['postType'],
                    "url": item.get('url'),
                    "media_urls": item.get('mediaUrls', []),
                    "score": item.get('score', 0),
                    "upvotes": item.get('upvotes', 0),
                    "downvotes": item.get('downvotes', 0),
                    "comment_count": item.get('commentCount', 0),
                    "view_count": item.get('viewCount', 0),
                    "created_at": item['createdAt'],
                    "updated_at": item['updatedAt'],
                    "is_deleted": item.get('isDeleted', False),
                    "is_locked": item.get('isLocked', False),
                    "is_sticky": item.get('isSticky', False),
                    "is_nsfw": item.get('isNSFW', False),
                    "is_spoiler": item.get('isSpoiler', False),
                    "flair": item.get('flair'),
                    "tags": item.get('tags', []),
                    "awards": item.get('awards', [])
                }
                posts.append(post)
            
            # Apply pagination
            start_idx = request.offset
            end_idx = start_idx + request.limit
            paginated_posts = posts[start_idx:end_idx]
            
            return {
                "posts": paginated_posts,
                "total_count": len(posts),
                "has_more": end_idx < len(posts),
                "next_offset": end_idx if end_idx < len(posts) else None
            }
            
        except ClientError as e:
            raise ValueError(f"Database error: {str(e)}")
    
    def _get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information."""
        try:
            response = self.users_table.get_item(Key={"userId": user_id})
            return response.get('Item')
        except ClientError:
            return None

# ============================================================================
# HANDLERS
# ============================================================================

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

async def handle_register(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle user registration."""
    try:
        body = json.loads(event.get('body', '{}'))
        request = RegisterRequest(**body)
        
        auth_service = AuthService()
        user = auth_service.register(request)
        
        return create_response(201, {
            "success": True,
            "message": "User registered successfully",
            "data": {"user": user.dict()}
        })
    except ValidationError as e:
        return create_response(400, {
            "success": False,
            "message": "Validation error",
            "error": {"details": e.errors()}
        })
    except ValueError as e:
        return create_response(400, {
            "success": False,
            "message": str(e)
        })
    except Exception as e:
        return create_response(500, {
            "success": False,
            "message": "Internal server error",
            "error": {"details": str(e)}
        })

async def handle_login(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle user login."""
    try:
        body = json.loads(event.get('body', '{}'))
        request = LoginRequest(**body)
        
        auth_service = AuthService()
        result = auth_service.login(request)
        
        return create_response(200, {
            "success": True,
            "message": "Login successful",
            "data": result
        })
    except ValidationError as e:
        return create_response(400, {
            "success": False,
            "message": "Validation error",
            "error": {"details": e.errors()}
        })
    except ValueError as e:
        return create_response(401, {
            "success": False,
            "message": str(e)
        })
    except Exception as e:
        return create_response(500, {
            "success": False,
            "message": "Internal server error",
            "error": {"details": str(e)}
        })

async def handle_logout(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle user logout."""
    try:
        body = json.loads(event.get('body', '{}'))
        request = LogoutRequest(**body)
        
        auth_service = AuthService()
        success = auth_service.logout(request)
        
        if success:
            return create_response(200, {
                "success": True,
                "message": "Logout successful"
            })
        else:
            return create_response(400, {
                "success": False,
                "message": "Logout failed"
            })
    except ValidationError as e:
        return create_response(400, {
            "success": False,
            "message": "Validation error",
            "error": {"details": e.errors()}
        })
    except Exception as e:
        return create_response(500, {
            "success": False,
            "message": "Internal server error",
            "error": {"details": str(e)}
        })

async def handle_forgot_password(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle forgot password."""
    try:
        body = json.loads(event.get('body', '{}'))
        request = ForgotPasswordRequest(**body)
        
        auth_service = AuthService()
        success = auth_service.forgot_password(request)
        
        if success:
            return create_response(200, {
                "success": True,
                "message": "Password reset email sent"
            })
        else:
            return create_response(400, {
                "success": False,
                "message": "Failed to send password reset email"
            })
    except ValidationError as e:
        return create_response(400, {
            "success": False,
            "message": "Validation error",
            "error": {"details": e.errors()}
        })
    except Exception as e:
        return create_response(500, {
            "success": False,
            "message": "Internal server error",
            "error": {"details": str(e)}
        })

async def handle_reset_password(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle reset password."""
    try:
        body = json.loads(event.get('body', '{}'))
        request = ResetPasswordRequest(**body)
        
        auth_service = AuthService()
        success = auth_service.reset_password(request)
        
        if success:
            return create_response(200, {
                "success": True,
                "message": "Password reset successfully"
            })
        else:
            return create_response(400, {
                "success": False,
                "message": "Failed to reset password"
            })
    except ValidationError as e:
        return create_response(400, {
            "success": False,
            "message": "Validation error",
            "error": {"details": e.errors()}
        })
    except Exception as e:
        return create_response(500, {
            "success": False,
            "message": "Internal server error",
            "error": {"details": str(e)}
        })

# Posts handlers
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
            "data": {"post": post}
        })
        
    except ValidationError as e:
        return create_response(400, {
            "success": False,
            "message": "Validation error",
            "error": {"details": e.errors()}
        })
    except ValueError as e:
        return create_response(400, {
            "success": False,
            "message": str(e)
        })
    except Exception as e:
        return create_response(500, {
            "success": False,
            "message": "Internal server error",
            "error": {"details": str(e)}
        })

async def handle_get_post(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle GET /posts/{post_id}"""
    try:
        # Get post ID from path parameters
        post_id = event.get('pathParameters', {}).get('post_id')
        if not post_id:
            return create_response(400, {
                "success": False,
                "message": "Post ID is required"
            })
        
        # Get post
        posts_service = PostsService()
        post = posts_service.get_post(post_id)
        
        return create_response(200, {
            "success": True,
            "message": "Post retrieved successfully",
            "data": {"post": post}
        })
        
    except ValueError as e:
        return create_response(404, {
            "success": False,
            "message": str(e)
        })
    except Exception as e:
        return create_response(500, {
            "success": False,
            "message": "Internal server error",
            "error": {"details": str(e)}
        })

async def handle_get_posts(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle GET /posts"""
    try:
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
        result = posts_service.get_posts(request)
        
        return create_response(200, {
            "success": True,
            "message": "Posts retrieved successfully",
            "data": result
        })
        
    except ValidationError as e:
        return create_response(400, {
            "success": False,
            "message": "Validation error",
            "error": {"details": e.errors()}
        })
    except Exception as e:
        return create_response(500, {
            "success": False,
            "message": "Internal server error",
            "error": {"details": str(e)}
        })

# ============================================================================
# MAIN HANDLER
# ============================================================================

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler."""
    try:
        # Get HTTP method and resource
        method = event.get('httpMethod', '')
        resource = event.get('resource', '')
        
        # Route to appropriate handler
        if resource == '/auth/register' and method == 'POST':
            return asyncio.run(handle_register(event))
        elif resource == '/auth/login' and method == 'POST':
            return asyncio.run(handle_login(event))
        elif resource == '/auth/logout' and method == 'POST':
            return asyncio.run(handle_logout(event))
        elif resource == '/auth/forgot-password' and method == 'POST':
            return asyncio.run(handle_forgot_password(event))
        elif resource == '/auth/reset-password' and method == 'POST':
            return asyncio.run(handle_reset_password(event))
        elif resource == '/posts/create' and method == 'POST':
            return asyncio.run(handle_create_post(event))
        elif resource == '/posts/{post_id}' and method == 'GET':
            return asyncio.run(handle_get_post(event))
        elif resource == '/posts' and method == 'GET':
            return asyncio.run(handle_get_posts(event))
        elif resource == '/posts/{post_id}' and method == 'PUT':
            return asyncio.run(handle_update_post(event))
        elif resource == '/posts/{post_id}' and method == 'DELETE':
            return asyncio.run(handle_delete_post(event))
        elif resource == '/posts/{post_id}/vote' and method == 'POST':
            return asyncio.run(handle_vote_post(event))
        elif resource == '/comments/create' and method == 'POST':
            return create_comment_handler(event)
        elif resource == '/comments' and method == 'GET':
            return get_comments_handler(event)
        elif resource == '/comments/{comment_id}' and method == 'GET':
            return get_comment_by_id_handler(event)
        elif resource == '/comments/{comment_id}' and method == 'PUT':
            return update_comment_handler(event)
        elif resource == '/comments/{comment_id}' and method == 'DELETE':
            return delete_comment_handler(event)
        elif resource == '/comments/{comment_id}/vote' and method == 'POST':
            return vote_comment_handler(event)
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
            "error": {"details": str(e)}
        })
