"""
Pydantic models for Comment system
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class CommentType(str, Enum):
    """Comment types"""
    COMMENT = "comment"
    REPLY = "reply"


class VoteType(str, Enum):
    """Vote types for comments"""
    UPVOTE = "upvote"
    DOWNVOTE = "downvote"
    REMOVE = "remove"


class CommentBase(BaseModel):
    """Base comment model"""
    content: str = Field(..., min_length=1, max_length=10000, description="Comment content")
    parent_id: Optional[str] = Field(None, description="Parent comment ID for replies")
    comment_type: CommentType = Field(CommentType.COMMENT, description="Type of comment")
    is_deleted: bool = Field(False, description="Whether comment is deleted")
    is_edited: bool = Field(False, description="Whether comment has been edited")
    is_locked: bool = Field(False, description="Whether comment is locked")
    is_sticky: bool = Field(False, description="Whether comment is sticky")
    is_nsfw: bool = Field(False, description="Whether comment is NSFW")
    is_spoiler: bool = Field(False, description="Whether comment is spoiler")
    flair: Optional[str] = Field(None, max_length=50, description="Comment flair")
    tags: List[str] = Field(default_factory=list, max_items=5, description="Comment tags")
    awards: List[Dict[str, Any]] = Field(default_factory=list, description="Comment awards")
    
    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()
    
    @validator('tags')
    def validate_tags(cls, v):
        if len(v) > 5:
            raise ValueError('Maximum 5 tags allowed')
        for tag in v:
            if len(tag) > 30:
                raise ValueError('Tag length cannot exceed 30 characters')
        return v


class CreateCommentRequest(CommentBase):
    """Request model for creating a comment"""
    post_id: str = Field(..., min_length=1, description="Post ID this comment belongs to")
    
    @validator('post_id')
    def validate_post_id(cls, v):
        if not v or not v.strip():
            raise ValueError('Post ID cannot be empty')
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "post_id": "post_1757473451_1f984949",
                "content": "This is a great post! Thanks for sharing.",
                "parent_id": None,
                "comment_type": "comment",
                "is_nsfw": False,
                "is_spoiler": False,
                "flair": "Discussion",
                "tags": ["feedback", "positive"]
            }
        }


class UpdateCommentRequest(BaseModel):
    """Request model for updating a comment"""
    content: Optional[str] = Field(None, min_length=1, max_length=10000, description="Updated comment content")
    is_nsfw: Optional[bool] = Field(None, description="Whether comment is NSFW")
    is_spoiler: Optional[bool] = Field(None, description="Whether comment is spoiler")
    flair: Optional[str] = Field(None, max_length=50, description="Comment flair")
    tags: Optional[List[str]] = Field(None, max_items=5, description="Comment tags")
    
    @validator('content')
    def validate_content(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip() if v else v
    
    @validator('tags')
    def validate_tags(cls, v):
        if v is not None:
            if len(v) > 5:
                raise ValueError('Maximum 5 tags allowed')
            for tag in v:
                if len(tag) > 30:
                    raise ValueError('Tag length cannot exceed 30 characters')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "content": "Updated comment content",
                "is_nsfw": False,
                "is_spoiler": True,
                "flair": "Updated Flair",
                "tags": ["updated", "feedback"]
            }
        }


class GetCommentsRequest(BaseModel):
    """Request model for getting comments"""
    post_id: str = Field(..., description="Post ID to get comments for")
    parent_id: Optional[str] = Field(None, description="Parent comment ID for replies")
    sort: str = Field("hot", description="Sort order")
    limit: int = Field(20, ge=1, le=100, description="Number of comments to return")
    offset: int = Field(0, ge=0, description="Number of comments to skip")
    include_deleted: bool = Field(False, description="Include deleted comments")
    
    @validator('sort')
    def validate_sort(cls, v):
        valid_sorts = ['hot', 'new', 'top', 'controversial', 'old']
        if v not in valid_sorts:
            raise ValueError(f'Sort must be one of: {", ".join(valid_sorts)}')
        return v


class CommentResponse(BaseModel):
    """Response model for a single comment"""
    comment_id: str = Field(..., description="Comment ID")
    post_id: str = Field(..., description="Post ID")
    author_id: str = Field(..., description="Author user ID")
    parent_id: Optional[str] = Field(None, description="Parent comment ID")
    content: str = Field(..., description="Comment content")
    comment_type: CommentType = Field(..., description="Type of comment")
    score: int = Field(..., description="Comment score")
    upvotes: int = Field(..., description="Number of upvotes")
    downvotes: int = Field(..., description="Number of downvotes")
    reply_count: int = Field(..., description="Number of replies")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    is_deleted: bool = Field(..., description="Whether comment is deleted")
    is_edited: bool = Field(..., description="Whether comment has been edited")
    is_locked: bool = Field(..., description="Whether comment is locked")
    is_sticky: bool = Field(..., description="Whether comment is sticky")
    is_nsfw: bool = Field(..., description="Whether comment is NSFW")
    is_spoiler: bool = Field(..., description="Whether comment is spoiler")
    flair: Optional[str] = Field(None, description="Comment flair")
    tags: List[str] = Field(..., description="Comment tags")
    awards: List[Dict[str, Any]] = Field(..., description="Comment awards")
    user_vote: Optional[str] = Field(None, description="Current user's vote")
    subreddit_id: str = Field(..., description="Subreddit ID")
    subreddit_name: str = Field(..., description="Subreddit name")
    replies: List['CommentResponse'] = Field(default_factory=list, description="Nested replies")
    
    class Config:
        schema_extra = {
            "example": {
                "comment_id": "comment_1757473451_1f984949",
                "post_id": "post_1757473451_1f984949",
                "author_id": "user_1757432106_d66ab80f40704b1",
                "parent_id": None,
                "content": "This is a great post! Thanks for sharing.",
                "comment_type": "comment",
                "score": 15,
                "upvotes": 18,
                "downvotes": 3,
                "reply_count": 2,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "is_deleted": False,
                "is_edited": False,
                "is_locked": False,
                "is_sticky": False,
                "is_nsfw": False,
                "is_spoiler": False,
                "flair": "Discussion",
                "tags": ["feedback", "positive"],
                "awards": [],
                "user_vote": "upvote",
                "subreddit_id": "subreddit_1757518063_01b8625d",
                "subreddit_name": "programming",
                "replies": []
            }
        }


class CommentsResponse(BaseModel):
    """Response model for multiple comments"""
    comments: List[CommentResponse] = Field(..., description="List of comments")
    total_count: int = Field(..., description="Total number of comments")
    has_more: bool = Field(..., description="Whether there are more comments")
    next_offset: int = Field(..., description="Next offset for pagination")
    
    class Config:
        schema_extra = {
            "example": {
                "comments": [],
                "total_count": 25,
                "has_more": True,
                "next_offset": 20
            }
        }


class VoteCommentRequest(BaseModel):
    """Request model for voting on a comment"""
    vote_type: VoteType = Field(..., description="Type of vote")
    
    class Config:
        schema_extra = {
            "example": {
                "vote_type": "upvote"
            }
        }


class VoteCommentResponse(BaseModel):
    """Response model for comment vote"""
    stats: Dict[str, Any] = Field(..., description="Updated comment stats")
    
    class Config:
        schema_extra = {
            "example": {
                "stats": {
                    "comment_id": "comment_1757473451_1f984949",
                    "score": 16,
                    "upvotes": 19,
                    "downvotes": 3,
                    "reply_count": 2
                }
            }
        }


# Update forward references
CommentResponse.model_rebuild()
