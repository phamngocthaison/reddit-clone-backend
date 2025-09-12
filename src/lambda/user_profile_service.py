"""User profile service for the Reddit Clone Backend."""

import logging
import os
import boto3
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError

from shared.aws_clients import AWSClients
from user_profile_models import (
    UserProfile,
    PublicUserProfile,
    UpdateProfileRequest,
    ChangePasswordRequest,
    GetUserPostsRequest,
    GetUserCommentsRequest,
    UserPostsResponse,
    UserCommentsResponse
)

logger = logging.getLogger(__name__)


class UserProfileService:
    """Service for managing user profiles."""
    
    def __init__(self):
        """Initialize the user profile service."""
        self.aws_clients = AWSClients()
        self.users_table = self.aws_clients.get_users_table()
        self.posts_table = self.aws_clients.dynamodb.Table(os.getenv("POSTS_TABLE_NAME"))
        self.comments_table = self.aws_clients.dynamodb.Table(os.getenv("COMMENTS_TABLE_NAME"))
        self.cognito_client = self.aws_clients.get_cognito_client()
    
    async def get_user_profile(self, user_id: str) -> UserProfile:
        """Get user profile by user ID."""
        try:
            response = self.users_table.get_item(Key={"userId": user_id})
            user_data = response.get("Item")
            
            if not user_data:
                raise ValueError("User not found")
            
            # Convert DynamoDB item to UserProfile
            return UserProfile(
                user_id=user_data["userId"],
                email=user_data["email"],
                username=user_data["username"],
                created_at=datetime.fromisoformat(user_data["createdAt"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(user_data["updatedAt"].replace("Z", "+00:00")),
                is_active=user_data.get("isActive", True),
                display_name=user_data.get("displayName"),
                bio=user_data.get("bio"),
                avatar=user_data.get("avatar"),
                karma=user_data.get("karma", 0),
                post_count=user_data.get("postCount", 0),
                comment_count=user_data.get("commentCount", 0),
                is_public=user_data.get("isPublic", True),
                show_email=user_data.get("showEmail", False)
            )
            
        except ClientError as e:
            logger.error(f"Error getting user profile: {e}")
            raise ValueError("Failed to retrieve user profile")
    
    async def get_public_user_profile(self, user_id: str) -> PublicUserProfile:
        """Get public user profile by user ID."""
        try:
            user_profile = await self.get_user_profile(user_id)
            
            # Check if user profile is public
            if not user_profile.is_public:
                raise ValueError("User profile is private")
            
            return PublicUserProfile(
                user_id=user_profile.user_id,
                username=user_profile.username,
                display_name=user_profile.display_name,
                bio=user_profile.bio,
                avatar=user_profile.avatar,
                created_at=user_profile.created_at,
                karma=user_profile.karma,
                post_count=user_profile.post_count,
                comment_count=user_profile.comment_count
            )
            
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error getting public user profile: {e}")
            raise ValueError("Failed to retrieve public user profile")
    
    async def update_user_profile(self, user_id: str, request: UpdateProfileRequest) -> UserProfile:
        """Update user profile."""
        try:
            # Get current user profile
            current_profile = await self.get_user_profile(user_id)
            
            # Prepare update expression
            update_expression = "SET updatedAt = :updated_at"
            expression_attribute_values = {
                ":updated_at": datetime.now(timezone.utc).isoformat() + "Z"
            }
            
            # Update fields if provided
            if request.display_name is not None:
                update_expression += ", displayName = :display_name"
                expression_attribute_values[":display_name"] = request.display_name
            
            if request.bio is not None:
                update_expression += ", bio = :bio"
                expression_attribute_values[":bio"] = request.bio
            
            if request.avatar is not None:
                update_expression += ", avatar = :avatar"
                expression_attribute_values[":avatar"] = request.avatar
            
            if request.is_public is not None:
                update_expression += ", isPublic = :is_public"
                expression_attribute_values[":is_public"] = request.is_public
            
            if request.show_email is not None:
                update_expression += ", showEmail = :show_email"
                expression_attribute_values[":show_email"] = request.show_email
            
            # Update user in DynamoDB
            self.users_table.update_item(
                Key={"userId": user_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
            
            # Return updated profile
            return await self.get_user_profile(user_id)
            
        except ClientError as e:
            logger.error(f"Error updating user profile: {e}")
            raise ValueError("Failed to update user profile")
    
    async def change_password(self, user_id: str, request: ChangePasswordRequest) -> bool:
        """Change user password."""
        try:
            # Get user email for Cognito
            user_profile = await self.get_user_profile(user_id)
            email = user_profile.email
            
            # Change password in Cognito
            self.cognito_client.admin_set_user_password(
                UserPoolId=self.aws_clients.get_user_pool_id(),
                Username=email,
                Password=request.new_password,
                Permanent=True
            )
            
            return True
            
        except ClientError as e:
            logger.error(f"Error changing password: {e}")
            if e.response['Error']['Code'] == 'NotAuthorizedException':
                raise ValueError("Current password is incorrect")
            raise ValueError("Failed to change password")
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            raise ValueError("Failed to change password")
    
    async def delete_user_account(self, user_id: str, password: str) -> bool:
        """Delete user account."""
        try:
            # Get user email for Cognito
            user_profile = await self.get_user_profile(user_id)
            email = user_profile.email
            
            # Delete user from Cognito
            self.cognito_client.admin_delete_user(
                UserPoolId=self.aws_clients.get_user_pool_id(),
                Username=email
            )
            
            # Delete user from DynamoDB
            self.users_table.delete_item(Key={"userId": user_id})
            
            return True
            
        except ClientError as e:
            logger.error(f"Error deleting user account: {e}")
            raise ValueError("Failed to delete user account")
        except Exception as e:
            logger.error(f"Error deleting user account: {e}")
            raise ValueError("Failed to delete user account")
    
    async def get_user_posts(self, user_id: str, request: GetUserPostsRequest) -> UserPostsResponse:
        """Get user posts."""
        try:
            # Query posts by user ID
            response = self.posts_table.query(
                IndexName="UserIndex",
                KeyConditionExpression="userId = :user_id",
                ExpressionAttributeValues={":user_id": user_id},
                ScanIndexForward=False,  # Sort by creation time descending
                Limit=request.limit
            )
            
            posts = response.get("Items", [])
            
            # Apply sorting
            if request.sort == "hot":
                posts.sort(key=lambda x: x.get("score", 0), reverse=True)
            elif request.sort == "top":
                posts.sort(key=lambda x: x.get("upvotes", 0), reverse=True)
            # "new" is already sorted by creation time
            
            # Apply filters
            if request.post_type:
                posts = [p for p in posts if p.get("postType") == request.post_type]
            
            if request.is_nsfw is not None:
                posts = [p for p in posts if p.get("isNsfw", False) == request.is_nsfw]
            
            # Apply pagination
            start_index = request.offset
            end_index = start_index + request.limit
            paginated_posts = posts[start_index:end_index]
            
            # Convert Decimal to int/float for JSON serialization
            for post in paginated_posts:
                for key, value in post.items():
                    if hasattr(value, 'as_tuple'):  # Decimal object
                        post[key] = int(value) if value % 1 == 0 else float(value)
            
            return UserPostsResponse(
                posts=paginated_posts,
                count=len(paginated_posts),
                user_id=user_id,
                limit=request.limit,
                offset=request.offset,
                has_more=len(posts) > end_index
            )
            
        except ClientError as e:
            logger.error(f"Error getting user posts: {e}")
            raise ValueError("Failed to retrieve user posts")
    
    async def get_user_comments(self, user_id: str, request: GetUserCommentsRequest) -> UserCommentsResponse:
        """Get user comments."""
        try:
            # Query comments by user ID
            response = self.comments_table.query(
                IndexName="UserIndex",
                KeyConditionExpression="userId = :user_id",
                ExpressionAttributeValues={":user_id": user_id},
                ScanIndexForward=False,  # Sort by creation time descending
                Limit=request.limit
            )
            
            comments = response.get("Items", [])
            
            # Apply sorting
            if request.sort == "hot":
                comments.sort(key=lambda x: x.get("score", 0), reverse=True)
            elif request.sort == "top":
                comments.sort(key=lambda x: x.get("upvotes", 0), reverse=True)
            # "new" is already sorted by creation time
            
            # Apply filters
            if request.comment_type:
                comments = [c for c in comments if c.get("commentType") == request.comment_type]
            
            # Apply pagination
            start_index = request.offset
            end_index = start_index + request.limit
            paginated_comments = comments[start_index:end_index]
            
            # Convert Decimal to int/float for JSON serialization
            for comment in paginated_comments:
                for key, value in comment.items():
                    if hasattr(value, 'as_tuple'):  # Decimal object
                        comment[key] = int(value) if value % 1 == 0 else float(value)
            
            return UserCommentsResponse(
                comments=paginated_comments,
                count=len(paginated_comments),
                user_id=user_id,
                limit=request.limit,
                offset=request.offset,
                has_more=len(comments) > end_index
            )
            
        except ClientError as e:
            logger.error(f"Error getting user comments: {e}")
            raise ValueError("Failed to retrieve user comments")
    
    async def update_user_stats(self, user_id: str, post_count_delta: int = 0, comment_count_delta: int = 0, karma_delta: int = 0) -> None:
        """Update user statistics."""
        try:
            # Get current user profile
            current_profile = await self.get_user_profile(user_id)
            
            # Calculate new stats
            new_post_count = max(0, current_profile.post_count + post_count_delta)
            new_comment_count = max(0, current_profile.comment_count + comment_count_delta)
            new_karma = max(0, current_profile.karma + karma_delta)
            
            # Update stats in DynamoDB
            self.users_table.update_item(
                Key={"userId": user_id},
                UpdateExpression="SET postCount = :post_count, commentCount = :comment_count, karma = :karma, updatedAt = :updated_at",
                ExpressionAttributeValues={
                    ":post_count": new_post_count,
                    ":comment_count": new_comment_count,
                    ":karma": new_karma,
                    ":updated_at": datetime.now(timezone.utc).isoformat() + "Z"
                }
            )
            
        except Exception as e:
            logger.warning(f"Failed to update user stats: {e}")
            # Don't raise error as this is not critical
