"""User profile models for the Reddit Clone Backend."""

from datetime import datetime
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, EmailStr, Field, validator


class UserProfile(BaseModel):
    """User profile model with extended information."""
    
    # Basic info
    user_id: str = Field(..., alias="userId")
    email: EmailStr
    username: str
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    is_active: bool = Field(..., alias="isActive")
    
    # Profile info
    display_name: Optional[str] = Field(None, alias="displayName")
    bio: Optional[str] = None
    avatar: Optional[str] = None
    
    # Stats
    karma: int = Field(0, ge=0)
    post_count: int = Field(0, ge=0, alias="postCount")
    comment_count: int = Field(0, ge=0, alias="commentCount")
    
    # Privacy settings
    is_public: bool = Field(True, alias="isPublic")
    show_email: bool = Field(False, alias="showEmail")
    
    class Config:
        """Pydantic configuration."""
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }


class PublicUserProfile(BaseModel):
    """Public user profile model (without sensitive information)."""
    
    user_id: str = Field(..., alias="userId")
    username: str
    display_name: Optional[str] = Field(None, alias="displayName")
    bio: Optional[str] = None
    avatar: Optional[str] = None
    created_at: datetime = Field(..., alias="createdAt")
    karma: int = Field(0, ge=0)
    post_count: int = Field(0, ge=0, alias="postCount")
    comment_count: int = Field(0, ge=0, alias="commentCount")
    
    class Config:
        """Pydantic configuration."""
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }


class UpdateProfileRequest(BaseModel):
    """Request model for updating user profile."""
    
    display_name: Optional[str] = Field(None, min_length=1, max_length=50, alias="displayName")
    bio: Optional[str] = Field(None, max_length=500)
    avatar: Optional[str] = Field(None, max_length=500)
    is_public: Optional[bool] = Field(None, alias="isPublic")
    show_email: Optional[bool] = Field(None, alias="showEmail")
    
    @validator('display_name')
    def validate_display_name(cls, v):
        if v is not None and v.strip() == "":
            raise ValueError('Display name cannot be empty')
        return v.strip() if v else None
    
    @validator('bio')
    def validate_bio(cls, v):
        if v is not None and v.strip() == "":
            raise ValueError('Bio cannot be empty')
        return v.strip() if v else None
    
    @validator('avatar')
    def validate_avatar(cls, v):
        if v is not None and v.strip() == "":
            raise ValueError('Avatar URL cannot be empty')
        return v.strip() if v else None
    
    class Config:
        """Pydantic configuration."""
        populate_by_name = True


class ChangePasswordRequest(BaseModel):
    """Request model for changing password."""
    
    current_password: str = Field(..., min_length=1, alias="currentPassword")
    new_password: str = Field(..., min_length=8, alias="newPassword")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('New password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('New password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('New password must contain at least one number')
        return v
    
    class Config:
        """Pydantic configuration."""
        populate_by_name = True


class DeleteAccountRequest(BaseModel):
    """Request model for deleting user account."""
    
    password: str = Field(..., min_length=1)


class GetUserPostsRequest(BaseModel):
    """Request model for getting user posts."""
    
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)
    sort: str = Field("new", regex="^(new|hot|top)$")
    post_type: Optional[str] = Field(None, regex="^(text|link|image|video)$")
    is_nsfw: Optional[bool] = Field(None)


class GetUserCommentsRequest(BaseModel):
    """Request model for getting user comments."""
    
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)
    sort: str = Field("new", regex="^(new|hot|top)$")
    comment_type: Optional[str] = Field(None, regex="^(comment|reply)$")


class UserProfileResponse(BaseModel):
    """Response model for user profile operations."""
    
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class UserPostsResponse(BaseModel):
    """Response model for user posts."""
    
    posts: List[Dict[str, Any]]
    count: int
    user_id: str
    limit: int
    offset: int
    has_more: bool


class UserCommentsResponse(BaseModel):
    """Response model for user comments."""
    
    comments: List[Dict[str, Any]]
    count: int
    user_id: str
    limit: int
    offset: int
    has_more: bool
