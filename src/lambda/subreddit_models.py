"""Pydantic models for Subreddit API."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator


class CreateSubredditRequest(BaseModel):
    """Request model for creating a subreddit."""
    name: str = Field(..., min_length=3, max_length=21, description="Subreddit name")
    display_name: str = Field(..., min_length=1, max_length=100, description="Display name")
    description: str = Field(..., min_length=1, max_length=500, description="Description")
    rules: List[str] = Field(default=[], description="Community rules")
    is_private: bool = Field(default=False, description="Private subreddit")
    is_nsfw: bool = Field(default=False, description="NSFW content")
    is_restricted: bool = Field(default=False, description="Restricted posting")
    primary_color: str = Field(default="#FF4500", description="Primary color")
    secondary_color: str = Field(default="#FFFFFF", description="Secondary color")
    language: str = Field(default="en", description="Language")
    country: str = Field(default="US", description="Country")
    icon: Optional[str] = Field(None, description="Subreddit icon URL")

    @validator('name')
    def validate_name(cls, v):
        """Validate subreddit name format."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Name must contain only letters, numbers, underscores, and hyphens')
        if v.startswith(('_', '-')) or v.endswith(('_', '-')):
            raise ValueError('Name cannot start or end with underscore or hyphen')
        return v.lower()

    @validator('primary_color', 'secondary_color')
    def validate_color(cls, v):
        """Validate color format."""
        if not v.startswith('#') or len(v) != 7:
            raise ValueError('Color must be in hex format (#RRGGBB)')
        return v.upper()


class UpdateSubredditRequest(BaseModel):
    """Request model for updating a subreddit."""
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    rules: Optional[List[str]] = Field(None)
    is_private: Optional[bool] = Field(None)
    is_nsfw: Optional[bool] = Field(None)
    is_restricted: Optional[bool] = Field(None)
    primary_color: Optional[str] = Field(None)
    secondary_color: Optional[str] = Field(None)
    language: Optional[str] = Field(None)
    country: Optional[str] = Field(None)
    icon: Optional[str] = Field(None, description="Subreddit icon URL")

    @validator('primary_color', 'secondary_color')
    def validate_color(cls, v):
        """Validate color format."""
        if v and (not v.startswith('#') or len(v) != 7):
            raise ValueError('Color must be in hex format (#RRGGBB)')
        return v.upper() if v else v


class JoinSubredditRequest(BaseModel):
    """Request model for joining a subreddit."""
    pass  # No additional fields needed


class SubredditResponse(BaseModel):
    """Response model for subreddit data."""
    subreddit_id: str
    name: str
    display_name: str
    description: str
    rules: List[str]
    owner_id: str
    moderators: List[str]
    subscriber_count: int
    post_count: int
    created_at: str
    updated_at: str
    is_private: bool
    is_nsfw: bool
    is_restricted: bool
    banner_image: Optional[str] = None
    icon: Optional[str] = None
    primary_color: str
    secondary_color: str
    language: str
    country: str
    is_subscribed: Optional[bool] = None
    user_role: Optional[str] = None


class SubredditListResponse(BaseModel):
    """Response model for subreddit list."""
    subreddits: List[SubredditResponse]
    total_count: int
    has_more: bool
    next_offset: Optional[int] = None


class GetSubredditsRequest(BaseModel):
    """Request model for getting subreddits list."""
    sort: str = Field(default="popular", description="Sort by: popular, new, trending")
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    search: Optional[str] = Field(None, description="Search query")
    is_nsfw: Optional[bool] = Field(None, description="Filter by NSFW status")
    language: Optional[str] = Field(None, description="Filter by language")
    country: Optional[str] = Field(None, description="Filter by country")

    @validator('sort')
    def validate_sort(cls, v):
        """Validate sort parameter."""
        allowed_sorts = ['popular', 'new', 'trending', 'subscribers']
        if v not in allowed_sorts:
            raise ValueError(f'Sort must be one of: {", ".join(allowed_sorts)}')
        return v


class GetSubredditPostsRequest(BaseModel):
    """Request model for getting posts in a subreddit."""
    sort: str = Field(default="hot", description="Sort by: hot, new, top, controversial")
    time_filter: str = Field(default="day", description="Time filter: hour, day, week, month, year, all")
    limit: int = Field(default=25, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    post_type: Optional[str] = Field(None, description="Filter by post type")
    is_nsfw: Optional[bool] = Field(None, description="Filter by NSFW status")

    @validator('sort')
    def validate_sort(cls, v):
        """Validate sort parameter."""
        allowed_sorts = ['hot', 'new', 'top', 'controversial', 'rising']
        if v not in allowed_sorts:
            raise ValueError(f'Sort must be one of: {", ".join(allowed_sorts)}')
        return v

    @validator('time_filter')
    def validate_time_filter(cls, v):
        """Validate time filter parameter."""
        allowed_filters = ['hour', 'day', 'week', 'month', 'year', 'all']
        if v not in allowed_filters:
            raise ValueError(f'Time filter must be one of: {", ".join(allowed_filters)}')
        return v


class SubscriptionResponse(BaseModel):
    """Response model for subscription data."""
    subscription_id: str
    user_id: str
    subreddit_id: str
    role: str
    joined_at: str
    is_active: bool


class ModeratorRequest(BaseModel):
    """Request model for moderator operations."""
    user_id: str = Field(..., description="User ID to add/remove as moderator")
    action: str = Field(..., description="Action: add or remove")

    @validator('action')
    def validate_action(cls, v):
        """Validate action parameter."""
        if v not in ['add', 'remove']:
            raise ValueError('Action must be either "add" or "remove"')
        return v


class BanUserRequest(BaseModel):
    """Request model for banning a user."""
    user_id: str = Field(..., description="User ID to ban")
    reason: str = Field(..., min_length=1, max_length=500, description="Ban reason")
    duration: Optional[int] = Field(None, ge=1, le=365, description="Ban duration in days (permanent if None)")


class SubredditStatsResponse(BaseModel):
    """Response model for subreddit statistics."""
    subreddit_id: str
    subscriber_count: int
    post_count: int
    comment_count: int
    daily_active_users: int
    weekly_active_users: int
    monthly_active_users: int
    growth_rate: float
    engagement_rate: float
    top_posts_count: int
    top_comments_count: int
    created_at: str
    last_activity: str
