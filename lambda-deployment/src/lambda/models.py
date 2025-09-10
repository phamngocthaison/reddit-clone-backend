from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum

class PostType(str, Enum):
    TEXT = "text"
    LINK = "link"
    IMAGE = "image"
    VIDEO = "video"
    POLL = "poll"

class PostStatus(str, Enum):
    ACTIVE = "active"
    DELETED = "deleted"
    LOCKED = "locked"
    HIDDEN = "hidden"

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

# Request Models
class CreatePostRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=300, description="Post title")
    content: Optional[str] = Field(None, max_length=40000, description="Post content for text posts")
    subreddit_id: str = Field(..., description="Subreddit ID")
    post_type: PostType = Field(PostType.TEXT, description="Type of post")
    url: Optional[str] = Field(None, description="URL for link posts")
    media_urls: Optional[List[str]] = Field(None, description="Media URLs for image/video posts")
    is_nsfw: bool = Field(False, description="NSFW flag")
    is_spoiler: bool = Field(False, description="Spoiler flag")
    flair: Optional[str] = Field(None, max_length=100, description="Post flair")
    tags: Optional[List[str]] = Field(None, description="Post tags")
    
    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    @validator('content')
    def validate_content(cls, v, values):
        if values.get('post_type') == PostType.TEXT and not v:
            raise ValueError('Content is required for text posts')
        return v
    
    @validator('url')
    def validate_url(cls, v, values):
        if values.get('post_type') == PostType.LINK and not v:
            raise ValueError('URL is required for link posts')
        return v

class UpdatePostRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=300, description="Post title")
    content: Optional[str] = Field(None, max_length=40000, description="Post content")
    is_nsfw: Optional[bool] = Field(None, description="NSFW flag")
    is_spoiler: Optional[bool] = Field(None, description="Spoiler flag")
    flair: Optional[str] = Field(None, max_length=100, description="Post flair")
    tags: Optional[List[str]] = Field(None, description="Post tags")
    
    @validator('title')
    def validate_title(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip() if v else v

class GetPostsRequest(BaseModel):
    subreddit_id: Optional[str] = Field(None, description="Filter by subreddit")
    author_id: Optional[str] = Field(None, description="Filter by author")
    sort: PostSort = Field(PostSort.HOT, description="Sort order")
    time_filter: PostTimeFilter = Field(PostTimeFilter.DAY, description="Time filter for top/controversial")
    limit: int = Field(25, ge=1, le=100, description="Number of posts to return")
    offset: int = Field(0, ge=0, description="Offset for pagination")
    post_type: Optional[PostType] = Field(None, description="Filter by post type")
    is_nsfw: Optional[bool] = Field(None, description="Filter by NSFW flag")

class VotePostRequest(BaseModel):
    vote_type: Literal["upvote", "downvote", "remove"] = Field(..., description="Type of vote")

# Response Models
class PostResponse(BaseModel):
    post_id: str = Field(..., description="Post ID")
    title: str = Field(..., description="Post title")
    content: Optional[str] = Field(None, description="Post content")
    author_id: str = Field(..., description="Author user ID")
    author_username: str = Field(..., description="Author username")
    subreddit_id: str = Field(..., description="Subreddit ID")
    subreddit_name: str = Field(..., description="Subreddit name")
    post_type: PostType = Field(..., description="Type of post")
    url: Optional[str] = Field(None, description="URL for link posts")
    media_urls: Optional[List[str]] = Field(None, description="Media URLs")
    score: int = Field(0, description="Post score (upvotes - downvotes)")
    upvotes: int = Field(0, description="Number of upvotes")
    downvotes: int = Field(0, description="Number of downvotes")
    comment_count: int = Field(0, description="Number of comments")
    view_count: int = Field(0, description="Number of views")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_deleted: bool = Field(False, description="Is post deleted")
    is_locked: bool = Field(False, description="Is post locked")
    is_sticky: bool = Field(False, description="Is post sticky")
    is_nsfw: bool = Field(False, description="Is NSFW")
    is_spoiler: bool = Field(False, description="Is spoiler")
    flair: Optional[str] = Field(None, description="Post flair")
    tags: Optional[List[str]] = Field(None, description="Post tags")
    awards: Optional[List[str]] = Field(None, description="Awards received")
    user_vote: Optional[Literal["upvote", "downvote"]] = Field(None, description="User's vote on this post")

class PostListResponse(BaseModel):
    posts: List[PostResponse] = Field(..., description="List of posts")
    total_count: int = Field(..., description="Total number of posts")
    has_more: bool = Field(..., description="Whether there are more posts")
    next_offset: Optional[int] = Field(None, description="Next offset for pagination")

class PostStatsResponse(BaseModel):
    post_id: str = Field(..., description="Post ID")
    score: int = Field(..., description="Post score")
    upvotes: int = Field(..., description="Number of upvotes")
    downvotes: int = Field(..., description="Number of downvotes")
    comment_count: int = Field(..., description="Number of comments")
    view_count: int = Field(..., description="Number of views")

# Database Models (for DynamoDB)
class PostDB(BaseModel):
    post_id: str = Field(..., alias="postId")
    title: str = Field(..., alias="title")
    content: Optional[str] = Field(None, alias="content")
    author_id: str = Field(..., alias="authorId")
    subreddit_id: str = Field(..., alias="subredditId")
    post_type: PostType = Field(..., alias="postType")
    url: Optional[str] = Field(None, alias="url")
    media_urls: Optional[List[str]] = Field(None, alias="mediaUrls")
    score: int = Field(0, alias="score")
    upvotes: int = Field(0, alias="upvotes")
    downvotes: int = Field(0, alias="downvotes")
    comment_count: int = Field(0, alias="commentCount")
    view_count: int = Field(0, alias="viewCount")
    created_at: str = Field(..., alias="createdAt")
    updated_at: str = Field(..., alias="updatedAt")
    is_deleted: bool = Field(False, alias="isDeleted")
    is_locked: bool = Field(False, alias="isLocked")
    is_sticky: bool = Field(False, alias="isSticky")
    is_nsfw: bool = Field(False, alias="isNSFW")
    is_spoiler: bool = Field(False, alias="isSpoiler")
    flair: Optional[str] = Field(None, alias="flair")
    tags: Optional[List[str]] = Field(None, alias="tags")
    awards: Optional[List[str]] = Field(None, alias="awards")
    
    class Config:
        allow_population_by_field_name = True

# Error Models
class PostError(BaseModel):
    error_code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")

class PostNotFoundError(PostError):
    error_code: str = "POST_NOT_FOUND"
    message: str = "Post not found"

class PostAccessDeniedError(PostError):
    error_code: str = "POST_ACCESS_DENIED"
    message: str = "Access denied to this post"

class PostValidationError(PostError):
    error_code: str = "POST_VALIDATION_ERROR"
    message: str = "Post validation failed"
