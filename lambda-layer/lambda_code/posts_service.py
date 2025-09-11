import os
import json
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import boto3
from botocore.exceptions import ClientError
from .models import (
    CreatePostRequest, UpdatePostRequest, GetPostsRequest, VotePostRequest,
    PostResponse, PostListResponse, PostStatsResponse, PostDB,
    PostType, PostSort, PostTimeFilter, PostNotFoundError, PostAccessDeniedError
)

class PostsService:
    """Service for managing posts."""
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=os.getenv('REGION', 'ap-southeast-1'))
        self.posts_table = self.dynamodb.Table(os.getenv('POSTS_TABLE', 'reddit-clone-posts'))
        self.users_table = self.dynamodb.Table(os.getenv('USERS_TABLE', 'reddit-clone-users'))
        self.subreddits_table = self.dynamodb.Table(os.getenv('SUBREDDITS_TABLE', 'reddit-clone-subreddits'))
    
    def create_post(self, request: CreatePostRequest, author_id: str) -> PostResponse:
        """Create a new post."""
        try:
            # Generate post ID
            post_id = f"post_{int(datetime.now().timestamp())}_{str(uuid.uuid4())[:8]}"
            current_time = datetime.now(timezone.utc).isoformat()
            
            # Get author info
            author = self._get_user(author_id)
            if not author:
                raise PostAccessDeniedError(message="Author not found")
            
            # Get subreddit info
            subreddit = self._get_subreddit(request.subreddit_id)
            if not subreddit:
                raise PostAccessDeniedError(message="Subreddit not found")
            
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
            return PostResponse(
                post_id=post_id,
                title=request.title,
                content=request.content,
                author_id=author_id,
                author_username=author.get('username', 'Unknown'),
                subreddit_id=request.subreddit_id,
                subreddit_name=subreddit.get('name', 'Unknown'),
                post_type=request.post_type,
                url=request.url,
                media_urls=request.media_urls,
                score=0,
                upvotes=0,
                downvotes=0,
                comment_count=0,
                view_count=0,
                created_at=datetime.fromisoformat(current_time.replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(current_time.replace('Z', '+00:00')),
                is_deleted=False,
                is_locked=False,
                is_sticky=False,
                is_nsfw=request.is_nsfw,
                is_spoiler=request.is_spoiler,
                flair=request.flair,
                tags=request.tags,
                awards=None,
                user_vote=None
            )
            
        except ClientError as e:
            raise PostAccessDeniedError(message=f"Database error: {str(e)}")
    
    def get_post(self, post_id: str, user_id: Optional[str] = None) -> PostResponse:
        """Get a single post by ID."""
        try:
            response = self.posts_table.get_item(Key={"postId": post_id})
            
            if 'Item' not in response:
                raise PostNotFoundError(message="Post not found")
            
            post_data = response['Item']
            
            # Check if post is deleted
            if post_data.get('isDeleted', False):
                raise PostNotFoundError(message="Post not found")
            
            # Get author and subreddit info
            author = self._get_user(post_data['authorId'])
            subreddit = self._get_subreddit(post_data['subredditId'])
            
            # Get user's vote if user_id provided
            user_vote = None
            if user_id:
                user_vote = self._get_user_vote(post_id, user_id)
            
            return PostResponse(
                post_id=post_data['postId'],
                title=post_data['title'],
                content=post_data.get('content'),
                author_id=post_data['authorId'],
                author_username=author.get('username', 'Unknown') if author else 'Unknown',
                subreddit_id=post_data['subredditId'],
                subreddit_name=subreddit.get('name', 'Unknown') if subreddit else 'Unknown',
                post_type=PostType(post_data['postType']),
                url=post_data.get('url'),
                media_urls=post_data.get('mediaUrls', []),
                score=post_data.get('score', 0),
                upvotes=post_data.get('upvotes', 0),
                downvotes=post_data.get('downvotes', 0),
                comment_count=post_data.get('commentCount', 0),
                view_count=post_data.get('viewCount', 0),
                created_at=datetime.fromisoformat(post_data['createdAt'].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(post_data['updatedAt'].replace('Z', '+00:00')),
                is_deleted=post_data.get('isDeleted', False),
                is_locked=post_data.get('isLocked', False),
                is_sticky=post_data.get('isSticky', False),
                is_nsfw=post_data.get('isNSFW', False),
                is_spoiler=post_data.get('isSpoiler', False),
                flair=post_data.get('flair'),
                tags=post_data.get('tags', []),
                awards=post_data.get('awards', []),
                user_vote=user_vote
            )
            
        except ClientError as e:
            raise PostAccessDeniedError(message=f"Database error: {str(e)}")
    
    def update_post(self, post_id: str, request: UpdatePostRequest, user_id: str) -> PostResponse:
        """Update an existing post."""
        try:
            # Get existing post
            existing_post = self.get_post(post_id, user_id)
            
            # Check if user is the author
            if existing_post.author_id != user_id:
                raise PostAccessDeniedError(message="Only the author can update this post")
            
            # Prepare update expression
            update_expression = "SET updatedAt = :updated_at"
            expression_values = {
                ":updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Add fields to update
            if request.title is not None:
                update_expression += ", title = :title"
                expression_values[":title"] = request.title
            
            if request.content is not None:
                update_expression += ", content = :content"
                expression_values[":content"] = request.content
            
            if request.is_nsfw is not None:
                update_expression += ", isNSFW = :is_nsfw"
                expression_values[":is_nsfw"] = request.is_nsfw
            
            if request.is_spoiler is not None:
                update_expression += ", isSpoiler = :is_spoiler"
                expression_values[":is_spoiler"] = request.is_spoiler
            
            if request.flair is not None:
                update_expression += ", flair = :flair"
                expression_values[":flair"] = request.flair
            
            if request.tags is not None:
                update_expression += ", tags = :tags"
                expression_values[":tags"] = request.tags
            
            # Update post
            self.posts_table.update_item(
                Key={"postId": post_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values
            )
            
            # Return updated post
            return self.get_post(post_id, user_id)
            
        except ClientError as e:
            raise PostAccessDeniedError(message=f"Database error: {str(e)}")
    
    def delete_post(self, post_id: str, user_id: str) -> bool:
        """Delete a post (soft delete)."""
        try:
            # Get existing post
            existing_post = self.get_post(post_id, user_id)
            
            # Check if user is the author
            if existing_post.author_id != user_id:
                raise PostAccessDeniedError(message="Only the author can delete this post")
            
            # Soft delete
            self.posts_table.update_item(
                Key={"postId": post_id},
                UpdateExpression="SET isDeleted = :is_deleted, updatedAt = :updated_at",
                ExpressionAttributeValues={
                    ":is_deleted": True,
                    ":updated_at": datetime.now(timezone.utc).isoformat()
                }
            )
            
            return True
            
        except ClientError as e:
            raise PostAccessDeniedError(message=f"Database error: {str(e)}")
    
    def get_posts(self, request: GetPostsRequest, user_id: Optional[str] = None) -> PostListResponse:
        """Get posts with filtering and sorting."""
        try:
            posts = []
            total_count = 0
            
            # Determine which GSI to use
            if request.subreddit_id:
                # Query by subreddit
                response = self._query_posts_by_subreddit(request)
            elif request.author_id:
                # Query by author
                response = self._query_posts_by_author(request)
            else:
                # Query all posts (scan with filters)
                response = self._scan_posts(request)
            
            # Process results
            for item in response.get('Items', []):
                if item.get('isDeleted', False):
                    continue
                
                # Get author and subreddit info
                author = self._get_user(item['authorId'])
                subreddit = self._get_subreddit(item['subredditId'])
                
                # Get user's vote if user_id provided
                user_vote = None
                if user_id:
                    user_vote = self._get_user_vote(item['postId'], user_id)
                
                post = PostResponse(
                    post_id=item['postId'],
                    title=item['title'],
                    content=item.get('content'),
                    author_id=item['authorId'],
                    author_username=author.get('username', 'Unknown') if author else 'Unknown',
                    subreddit_id=item['subredditId'],
                    subreddit_name=subreddit.get('name', 'Unknown') if subreddit else 'Unknown',
                    post_type=PostType(item['postType']),
                    url=item.get('url'),
                    media_urls=item.get('mediaUrls', []),
                    score=item.get('score', 0),
                    upvotes=item.get('upvotes', 0),
                    downvotes=item.get('downvotes', 0),
                    comment_count=item.get('commentCount', 0),
                    view_count=item.get('viewCount', 0),
                    created_at=datetime.fromisoformat(item['createdAt'].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(item['updatedAt'].replace('Z', '+00:00')),
                    is_deleted=item.get('isDeleted', False),
                    is_locked=item.get('isLocked', False),
                    is_sticky=item.get('isSticky', False),
                    is_nsfw=item.get('isNSFW', False),
                    is_spoiler=item.get('isSpoiler', False),
                    flair=item.get('flair'),
                    tags=item.get('tags', []),
                    awards=item.get('awards', []),
                    user_vote=user_vote
                )
                posts.append(post)
            
            # Apply pagination
            start_idx = request.offset
            end_idx = start_idx + request.limit
            paginated_posts = posts[start_idx:end_idx]
            
            return PostListResponse(
                posts=paginated_posts,
                total_count=len(posts),
                has_more=end_idx < len(posts),
                next_offset=end_idx if end_idx < len(posts) else None
            )
            
        except ClientError as e:
            raise PostAccessDeniedError(message=f"Database error: {str(e)}")
    
    def vote_post(self, post_id: str, request: VotePostRequest, user_id: str) -> PostStatsResponse:
        """Vote on a post."""
        try:
            # Get existing post
            post = self.get_post(post_id, user_id)
            
            # Get current vote
            current_vote = self._get_user_vote(post_id, user_id)
            
            # Calculate vote changes
            upvote_change = 0
            downvote_change = 0
            
            if request.vote_type == "upvote":
                if current_vote == "upvote":
                    # Remove upvote
                    upvote_change = -1
                elif current_vote == "downvote":
                    # Change downvote to upvote
                    upvote_change = 1
                    downvote_change = -1
                else:
                    # Add upvote
                    upvote_change = 1
            elif request.vote_type == "downvote":
                if current_vote == "downvote":
                    # Remove downvote
                    downvote_change = -1
                elif current_vote == "upvote":
                    # Change upvote to downvote
                    upvote_change = -1
                    downvote_change = 1
                else:
                    # Add downvote
                    downvote_change = 1
            elif request.vote_type == "remove":
                if current_vote == "upvote":
                    upvote_change = -1
                elif current_vote == "downvote":
                    downvote_change = -1
            
            # Update post stats
            new_upvotes = post.upvotes + upvote_change
            new_downvotes = post.downvotes + downvote_change
            new_score = new_upvotes - new_downvotes
            
            self.posts_table.update_item(
                Key={"postId": post_id},
                UpdateExpression="SET upvotes = :upvotes, downvotes = :downvotes, score = :score, updatedAt = :updated_at",
                ExpressionAttributeValues={
                    ":upvotes": new_upvotes,
                    ":downvotes": new_downvotes,
                    ":score": new_score,
                    ":updated_at": datetime.now(timezone.utc).isoformat()
                }
            )
            
            # TODO: Update user's vote in votes table (to be implemented)
            
            return PostStatsResponse(
                post_id=post_id,
                score=new_score,
                upvotes=new_upvotes,
                downvotes=new_downvotes,
                comment_count=post.comment_count,
                view_count=post.view_count
            )
            
        except ClientError as e:
            raise PostAccessDeniedError(message=f"Database error: {str(e)}")
    
    def _get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information."""
        try:
            response = self.users_table.get_item(Key={"userId": user_id})
            return response.get('Item')
        except ClientError:
            return None
    
    def _get_subreddit(self, subreddit_id: str) -> Optional[Dict[str, Any]]:
        """Get subreddit information."""
        try:
            response = self.subreddits_table.get_item(Key={"subredditId": subreddit_id})
            return response.get('Item')
        except ClientError:
            return None
    
    def _get_user_vote(self, post_id: str, user_id: str) -> Optional[str]:
        """Get user's vote on a post."""
        # TODO: Implement votes table query
        # For now, return None (no voting implemented yet)
        return None
    
    def _query_posts_by_subreddit(self, request: GetPostsRequest) -> Dict[str, Any]:
        """Query posts by subreddit."""
        query_params = {
            "IndexName": "SubredditIndex",
            "KeyConditionExpression": "subredditId = :subreddit_id",
            "ExpressionAttributeValues": {
                ":subreddit_id": request.subreddit_id
            },
            "ScanIndexForward": request.sort in [PostSort.NEW, PostSort.RISING],
            "Limit": request.limit + request.offset
        }
        
        # Add filters
        filter_expressions = []
        if request.post_type:
            filter_expressions.append("postType = :post_type")
            query_params["ExpressionAttributeValues"][":post_type"] = request.post_type.value
        
        if request.is_nsfw is not None:
            filter_expressions.append("isNSFW = :is_nsfw")
            query_params["ExpressionAttributeValues"][":is_nsfw"] = request.is_nsfw
        
        if filter_expressions:
            query_params["FilterExpression"] = " AND ".join(filter_expressions)
        
        return self.posts_table.query(**query_params)
    
    def _query_posts_by_author(self, request: GetPostsRequest) -> Dict[str, Any]:
        """Query posts by author."""
        query_params = {
            "IndexName": "AuthorIndex",
            "KeyConditionExpression": "authorId = :author_id",
            "ExpressionAttributeValues": {
                ":author_id": request.author_id
            },
            "ScanIndexForward": request.sort in [PostSort.NEW, PostSort.RISING],
            "Limit": request.limit + request.offset
        }
        
        # Add filters
        filter_expressions = []
        if request.post_type:
            filter_expressions.append("postType = :post_type")
            query_params["ExpressionAttributeValues"][":post_type"] = request.post_type.value
        
        if request.is_nsfw is not None:
            filter_expressions.append("isNSFW = :is_nsfw")
            query_params["ExpressionAttributeValues"][":is_nsfw"] = request.is_nsfw
        
        if filter_expressions:
            query_params["FilterExpression"] = " AND ".join(filter_expressions)
        
        return self.posts_table.query(**query_params)
    
    def _scan_posts(self, request: GetPostsRequest) -> Dict[str, Any]:
        """Scan all posts with filters."""
        scan_params = {
            "Limit": request.limit + request.offset
        }
        
        # Add filters
        filter_expressions = []
        expression_values = {}
        
        if request.post_type:
            filter_expressions.append("postType = :post_type")
            expression_values[":post_type"] = request.post_type.value
        
        if request.is_nsfw is not None:
            filter_expressions.append("isNSFW = :is_nsfw")
            expression_values[":is_nsfw"] = request.is_nsfw
        
        if filter_expressions:
            scan_params["FilterExpression"] = " AND ".join(filter_expressions)
            scan_params["ExpressionAttributeValues"] = expression_values
        
        return self.posts_table.scan(**scan_params)
