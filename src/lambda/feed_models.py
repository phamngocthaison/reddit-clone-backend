"""
Pydantic models for News Feed System.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class SortType(str, Enum):
    """Feed sorting types."""
    NEW = "new"
    HOT = "hot"
    TOP = "top"
    TRENDING = "trending"


class PostType(str, Enum):
    """Post types in feed."""
    POST = "post"
    COMMENT = "comment"
    ANNOUNCEMENT = "announcement"


class FeedItem(BaseModel):
    """Individual feed item."""
    feedId: str = Field(..., description="Unique feed item ID")
    postId: str = Field(..., description="Post ID")
    subredditId: str = Field(..., description="Subreddit ID")
    authorId: str = Field(..., description="Author ID")
    postTitle: str = Field(..., description="Post title")
    postContent: str = Field(..., description="Post content preview")
    postImageUrl: Optional[str] = Field(None, description="Post image URL")
    postUrl: Optional[str] = Field(None, description="Post URL for link posts")
    postType: str = Field(..., description="Post type (text, link, image, video)")
    subredditName: str = Field(..., description="Subreddit name")
    authorName: str = Field(..., description="Author username")
    upvotes: int = Field(0, description="Post upvotes")
    downvotes: int = Field(0, description="Post downvotes")
    commentsCount: int = Field(0, description="Comments count")
    isPinned: bool = Field(False, description="Is pinned post")
    isNSFW: bool = Field(False, description="Is NSFW content")
    isSpoiler: bool = Field(False, description="Is spoiler content")
    tags: List[str] = Field(default_factory=list, description="Post tags")
    createdAt: str = Field(..., description="Feed entry timestamp")
    postScore: int = Field(0, description="Post score for sorting")


class PaginationInfo(BaseModel):
    """Pagination information."""
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Current offset")
    total: int = Field(..., description="Total items available")
    hasMore: bool = Field(..., description="Has more items")
    nextOffset: Optional[int] = Field(None, description="Next offset for pagination")


class FeedMetadata(BaseModel):
    """Feed generation metadata."""
    generatedAt: str = Field(..., description="Feed generation timestamp")
    sortType: str = Field(..., description="Sort type used")
    cacheHit: bool = Field(False, description="Whether data came from cache")


class GetFeedRequest(BaseModel):
    """Request model for getting user feed."""
    limit: int = Field(20, ge=1, le=100, description="Number of items to return")
    offset: int = Field(0, ge=0, description="Offset for pagination")
    sort: SortType = Field(SortType.NEW, description="Sort type")
    includeNSFW: bool = Field(False, description="Include NSFW content")
    includeSpoilers: bool = Field(False, description="Include spoiler content")
    subredditId: Optional[str] = Field(None, description="Filter by subreddit ID")
    authorId: Optional[str] = Field(None, description="Filter by author ID")


class GetFeedResponse(BaseModel):
    """Response model for getting user feed."""
    success: bool = Field(True, description="Request success status")
    data: Dict[str, Any] = Field(..., description="Response data")
    message: Optional[str] = Field(None, description="Response message")


class FeedData(BaseModel):
    """Feed data container."""
    feeds: List[FeedItem] = Field(..., description="List of feed items")
    pagination: PaginationInfo = Field(..., description="Pagination information")
    metadata: FeedMetadata = Field(..., description="Feed metadata")


class RefreshFeedRequest(BaseModel):
    """Request model for refreshing user feed."""
    reason: str = Field(..., description="Reason for refresh")
    subredditId: Optional[str] = Field(None, description="Subreddit ID if applicable")
    userId: Optional[str] = Field(None, description="User ID if applicable")


class RefreshFeedResponse(BaseModel):
    """Response model for refreshing user feed."""
    success: bool = Field(True, description="Request success status")
    data: Dict[str, Any] = Field(..., description="Response data")
    message: Optional[str] = Field(None, description="Response message")


class RefreshFeedData(BaseModel):
    """Refresh feed data container."""
    message: str = Field(..., description="Success message")
    newItemsCount: int = Field(0, description="Number of new items added")
    refreshedAt: str = Field(..., description="Refresh timestamp")


class FeedStatsData(BaseModel):
    """Feed statistics data."""
    totalSubscriptions: int = Field(0, description="Total subreddit subscriptions")
    totalFollowing: int = Field(0, description="Total users following")
    feedItemsCount: int = Field(0, description="Total feed items")
    lastRefreshAt: Optional[str] = Field(None, description="Last refresh timestamp")
    averageScore: float = Field(0.0, description="Average post score")
    topSubreddits: List[Dict[str, Any]] = Field(default_factory=list, description="Top subreddits")
    topAuthors: List[Dict[str, Any]] = Field(default_factory=list, description="Top authors")


class GetFeedStatsResponse(BaseModel):
    """Response model for getting feed statistics."""
    success: bool = Field(True, description="Request success status")
    data: FeedStatsData = Field(..., description="Feed statistics data")
    message: Optional[str] = Field(None, description="Response message")


class FollowUserRequest(BaseModel):
    """Request model for following a user."""
    userId: str = Field(..., description="User ID to follow")


class FollowUserResponse(BaseModel):
    """Response model for following a user."""
    success: bool = Field(True, description="Request success status")
    data: Dict[str, Any] = Field(..., description="Response data")
    message: Optional[str] = Field(None, description="Response message")


class UnfollowUserResponse(BaseModel):
    """Response model for unfollowing a user."""
    success: bool = Field(True, description="Request success status")
    data: Dict[str, Any] = Field(..., description="Response data")
    message: Optional[str] = Field(None, description="Response message")


class GetFollowingResponse(BaseModel):
    """Response model for getting following list."""
    success: bool = Field(True, description="Request success status")
    data: Dict[str, Any] = Field(..., description="Response data")
    message: Optional[str] = Field(None, description="Response message")


class GetFollowersResponse(BaseModel):
    """Response model for getting followers list."""
    success: bool = Field(True, description="Request success status")
    data: Dict[str, Any] = Field(..., description="Response data")
    message: Optional[str] = Field(None, description="Response message")


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = Field(False, description="Request success status")
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    timestamp: str = Field(..., description="Error timestamp")
