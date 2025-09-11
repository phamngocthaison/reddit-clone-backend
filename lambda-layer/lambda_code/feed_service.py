"""
Feed Service for News Feed System.
Handles feed generation, caching, and user following functionality.
"""

import os
import json
import boto3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from botocore.exceptions import ClientError
from feed_models import (
    FeedItem, GetFeedRequest, GetFeedResponse, FeedData, PaginationInfo, 
    FeedMetadata, RefreshFeedRequest, RefreshFeedResponse, RefreshFeedData,
    GetFeedStatsResponse, FeedStatsData, SortType, PostType, ErrorResponse
)


class FeedService:
    """Service class for feed operations."""
    
    def __init__(self):
        """Initialize FeedService with DynamoDB clients."""
        self.dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('REGION', 'ap-southeast-1'))
        
        # Table references
        self.user_feeds_table = self.dynamodb.Table(os.environ['USER_FEEDS_TABLE'])
        self.user_follows_table = self.dynamodb.Table(os.environ['USER_FOLLOWS_TABLE'])
        self.subscriptions_table = self.dynamodb.Table(os.environ['SUBSCRIPTIONS_TABLE'])
        self.posts_table = self.dynamodb.Table(os.environ['POSTS_TABLE'])
        self.subreddits_table = self.dynamodb.Table(os.environ['SUBREDDITS_TABLE'])
        self.users_table = self.dynamodb.Table(os.environ['USERS_TABLE'])
    
    def get_user_feed(self, user_id: str, request: GetFeedRequest) -> GetFeedResponse:
        """Get personalized feed for user."""
        try:
            # Get user subscriptions
            subscriptions = self._get_user_subscriptions(user_id)
            
            # Get user following
            following = self._get_user_following(user_id)
            
            # Collect posts from sources
            posts = []
            
            # From subscribed subreddits
            for subreddit_id in subscriptions:
                subreddit_posts = self._get_subreddit_posts(subreddit_id, limit=request.limit * 2)
                posts.extend(subreddit_posts)
            
            # From followed users
            for author_id in following:
                user_posts = self._get_user_posts(author_id, limit=request.limit)
                posts.extend(user_posts)
            
            # Apply filters
            filtered_posts = self._apply_filters(posts, request)
            
            # Apply sorting
            sorted_posts = self._apply_sorting(filtered_posts, request.sort)
            
            # Paginate
            paginated_posts = self._paginate_posts(sorted_posts, request.limit, request.offset)
            
            # Convert to feed items
            feed_items = self._convert_to_feed_items(paginated_posts)
            
            # Create response
            feed_data = FeedData(
                feeds=feed_items,
                pagination=PaginationInfo(
                    limit=request.limit,
                    offset=request.offset,
                    total=len(sorted_posts),
                    hasMore=request.offset + request.limit < len(sorted_posts),
                    nextOffset=request.offset + request.limit if request.offset + request.limit < len(sorted_posts) else None
                ),
                metadata=FeedMetadata(
                    generatedAt=datetime.utcnow().isoformat() + "Z",
                    sortType=request.sort.value,
                    cacheHit=False
                )
            )
            
            return GetFeedResponse(
                success=True,
                data=feed_data.dict(),
                message="Feed retrieved successfully"
            )
            
        except Exception as e:
            return GetFeedResponse(
                success=False,
                data={},
                message=f"Error retrieving feed: {str(e)}"
            )
    
    def refresh_user_feed(self, user_id: str, request: RefreshFeedRequest) -> RefreshFeedResponse:
        """Refresh user feed after changes."""
        try:
            # Clear existing feed items for user
            self._clear_user_feed(user_id)
            
            # Regenerate feed
            feed_request = GetFeedRequest(
                limit=100,  # Get more items for refresh
                offset=0,
                sort=SortType.NEW,
                includeNSFW=False,
                includeSpoilers=False
            )
            
            feed_response = self.get_user_feed(user_id, feed_request)
            
            if not feed_response.success:
                return RefreshFeedResponse(
                    success=False,
                    data={},
                    message="Failed to refresh feed"
                )
            
            # Store feed items in database
            new_items_count = self._store_feed_items(user_id, feed_response.data['feeds'])
            
            return RefreshFeedResponse(
                success=True,
                data=RefreshFeedData(
                    message="Feed refreshed successfully",
                    newItemsCount=new_items_count,
                    refreshedAt=datetime.utcnow().isoformat() + "Z"
                ).dict(),
                message="Feed refreshed successfully"
            )
            
        except Exception as e:
            return RefreshFeedResponse(
                success=False,
                data={},
                message=f"Error refreshing feed: {str(e)}"
            )
    
    def get_feed_stats(self, user_id: str) -> GetFeedStatsResponse:
        """Get feed statistics for user."""
        try:
            # Get subscription count
            subscriptions = self._get_user_subscriptions(user_id)
            total_subscriptions = len(subscriptions)
            
            # Get following count
            following = self._get_user_following(user_id)
            total_following = len(following)
            
            # Get feed items count
            feed_items_count = self._get_user_feed_count(user_id)
            
            # Get top subreddits
            top_subreddits = self._get_top_subreddits(user_id, limit=5)
            
            # Get top authors
            top_authors = self._get_top_authors(user_id, limit=5)
            
            # Calculate average score
            average_score = self._calculate_average_score(user_id)
            
            stats_data = FeedStatsData(
                totalSubscriptions=total_subscriptions,
                totalFollowing=total_following,
                feedItemsCount=feed_items_count,
                lastRefreshAt=self._get_last_refresh_time(user_id),
                averageScore=average_score,
                topSubreddits=top_subreddits,
                topAuthors=top_authors
            )
            
            return GetFeedStatsResponse(
                success=True,
                data=stats_data,
                message="Feed statistics retrieved successfully"
            )
            
        except Exception as e:
            return GetFeedStatsResponse(
                success=False,
                data=FeedStatsData(),
                message=f"Error retrieving feed statistics: {str(e)}"
            )
    
    def _get_user_subscriptions(self, user_id: str) -> List[str]:
        """Get user's subscribed subreddits."""
        try:
            response = self.subscriptions_table.query(
                IndexName='UserIndex',
                KeyConditionExpression='userId = :user_id',
                ExpressionAttributeValues={':user_id': user_id}
            )
            return [item['subredditId'] for item in response['Items']]
        except ClientError:
            return []
    
    def _get_user_following(self, user_id: str) -> List[str]:
        """Get users that the user is following."""
        try:
            response = self.user_follows_table.query(
                IndexName='FollowerIndex',
                KeyConditionExpression='followerId = :user_id',
                ExpressionAttributeValues={':user_id': user_id}
            )
            return [item['followingId'] for item in response['Items'] if item.get('isActive', True)]
        except ClientError:
            return []
    
    def _get_subreddit_posts(self, subreddit_id: str, limit: int) -> List[Dict[str, Any]]:
        """Get recent posts from a subreddit."""
        try:
            response = self.posts_table.query(
                IndexName='SubredditIndex',
                KeyConditionExpression='subredditId = :subreddit_id',
                ExpressionAttributeValues={':subreddit_id': subreddit_id},
                ScanIndexForward=False,  # Descending order
                Limit=limit
            )
            return response['Items']
        except ClientError:
            return []
    
    def _get_user_posts(self, author_id: str, limit: int) -> List[Dict[str, Any]]:
        """Get recent posts from a user."""
        try:
            response = self.posts_table.query(
                IndexName='AuthorIndex',
                KeyConditionExpression='authorId = :author_id',
                ExpressionAttributeValues={':author_id': author_id},
                ScanIndexForward=False,  # Descending order
                Limit=limit
            )
            return response['Items']
        except ClientError:
            return []
    
    def _apply_filters(self, posts: List[Dict[str, Any]], request: GetFeedRequest) -> List[Dict[str, Any]]:
        """Apply filters to posts."""
        filtered_posts = posts
        
        # NSFW filter
        if not request.includeNSFW:
            filtered_posts = [p for p in filtered_posts if not p.get('isNSFW', False)]
        
        # Spoiler filter
        if not request.includeSpoilers:
            filtered_posts = [p for p in filtered_posts if not p.get('isSpoiler', False)]
        
        # Subreddit filter
        if request.subredditId:
            filtered_posts = [p for p in filtered_posts if p.get('subredditId') == request.subredditId]
        
        # Author filter
        if request.authorId:
            filtered_posts = [p for p in filtered_posts if p.get('authorId') == request.authorId]
        
        return filtered_posts
    
    def _apply_sorting(self, posts: List[Dict[str, Any]], sort_type: SortType) -> List[Dict[str, Any]]:
        """Apply sorting algorithm to posts."""
        if sort_type == SortType.NEW:
            return sorted(posts, key=lambda x: x.get('createdAt', ''), reverse=True)
        elif sort_type == SortType.HOT:
            return sorted(posts, key=lambda x: self._calculate_hot_score(x), reverse=True)
        elif sort_type == SortType.TOP:
            return sorted(posts, key=lambda x: x.get('score', 0), reverse=True)
        elif sort_type == SortType.TRENDING:
            return sorted(posts, key=lambda x: self._calculate_trending_score(x), reverse=True)
        
        return posts
    
    def _calculate_hot_score(self, post: Dict[str, Any]) -> float:
        """Calculate hot score based on Reddit's algorithm."""
        score = post.get('upvotes', 0) - post.get('downvotes', 0)
        created_at = post.get('createdAt', '')
        
        if not created_at:
            return 0.0
        
        try:
            post_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            age_hours = (datetime.utcnow() - post_time).total_seconds() / 3600
            
            if age_hours < 1:
                return score * 2.0
            elif age_hours < 24:
                return score * 1.5
            else:
                return score * 1.0
        except:
            return float(score)
    
    def _calculate_trending_score(self, post: Dict[str, Any]) -> float:
        """Calculate trending score based on recent activity."""
        score = post.get('score', 0)
        comments_count = post.get('commentsCount', 0)
        
        # Simple trending calculation based on comments
        trending_boost = comments_count * 0.1
        return score + trending_boost
    
    def _paginate_posts(self, posts: List[Dict[str, Any]], limit: int, offset: int) -> List[Dict[str, Any]]:
        """Paginate posts list."""
        return posts[offset:offset + limit]
    
    def _convert_to_feed_items(self, posts: List[Dict[str, Any]]) -> List[FeedItem]:
        """Convert posts to feed items."""
        feed_items = []
        
        for post in posts:
            # Get subreddit name
            subreddit_name = self._get_subreddit_name(post.get('subredditId', ''))
            
            # Get author name
            author_name = self._get_author_name(post.get('authorId', ''))
            
            feed_item = FeedItem(
                feedId=f"feed_{post.get('authorId', '')}_{post.get('createdAt', '')}_{post.get('postId', '')}",
                postId=post.get('postId', ''),
                subredditId=post.get('subredditId', ''),
                authorId=post.get('authorId', ''),
                postTitle=post.get('title', ''),
                postContent=post.get('content', '')[:200] + '...' if len(post.get('content', '')) > 200 else post.get('content', ''),
                postImageUrl=post.get('imageUrl'),
                subredditName=subreddit_name,
                authorName=author_name,
                upvotes=post.get('upvotes', 0),
                downvotes=post.get('downvotes', 0),
                commentsCount=post.get('commentsCount', 0),
                isPinned=post.get('isPinned', False),
                isNSFW=post.get('isNSFW', False),
                isSpoiler=post.get('isSpoiler', False),
                tags=post.get('tags', []),
                createdAt=post.get('createdAt', ''),
                postScore=post.get('score', 0)
            )
            feed_items.append(feed_item)
        
        return feed_items
    
    def _get_subreddit_name(self, subreddit_id: str) -> str:
        """Get subreddit name by ID."""
        try:
            response = self.subreddits_table.get_item(Key={'subredditId': subreddit_id})
            return response.get('Item', {}).get('name', f'r/unknown-{subreddit_id}')
        except ClientError:
            return f'r/unknown-{subreddit_id}'
    
    def _get_author_name(self, author_id: str) -> str:
        """Get author name by ID."""
        try:
            response = self.users_table.get_item(Key={'userId': author_id})
            return response.get('Item', {}).get('username', f'user-{author_id}')
        except ClientError:
            return f'user-{author_id}'
    
    def _clear_user_feed(self, user_id: str) -> None:
        """Clear user's existing feed items."""
        try:
            # Get all feed items for user
            response = self.user_feeds_table.query(
                IndexName='UserFeedIndex',
                KeyConditionExpression='userId = :user_id',
                ExpressionAttributeValues={':user_id': user_id}
            )
            
            # Delete all items
            with self.user_feeds_table.batch_writer() as batch:
                for item in response['Items']:
                    batch.delete_item(Key={'feedId': item['feedId'], 'createdAt': item['createdAt']})
        except ClientError:
            pass
    
    def _store_feed_items(self, user_id: str, feed_items: List[Dict[str, Any]]) -> int:
        """Store feed items in database."""
        try:
            with self.user_feeds_table.batch_writer() as batch:
                for item in feed_items:
                    feed_item = {
                        'feedId': item['feedId'],
                        'userId': user_id,
                        'postId': item['postId'],
                        'subredditId': item['subredditId'],
                        'authorId': item['authorId'],
                        'createdAt': item['createdAt'],
                        'postScore': item['postScore'],
                        'postType': 'post',
                        'postTitle': item['postTitle'],
                        'postContent': item['postContent'],
                        'postImageUrl': item.get('postImageUrl'),
                        'subredditName': item['subredditName'],
                        'authorName': item['authorName'],
                        'upvotes': item['upvotes'],
                        'downvotes': item['downvotes'],
                        'commentsCount': item['commentsCount'],
                        'isPinned': item['isPinned'],
                        'isNSFW': item['isNSFW'],
                        'isSpoiler': item['isSpoiler'],
                        'tags': item['tags']
                    }
                    batch.put_item(Item=feed_item)
            
            return len(feed_items)
        except ClientError:
            return 0
    
    def _get_user_feed_count(self, user_id: str) -> int:
        """Get count of user's feed items."""
        try:
            response = self.user_feeds_table.query(
                IndexName='UserFeedIndex',
                KeyConditionExpression='userId = :user_id',
                ExpressionAttributeValues={':user_id': user_id},
                Select='COUNT'
            )
            return response['Count']
        except ClientError:
            return 0
    
    def _get_top_subreddits(self, user_id: str, limit: int) -> List[Dict[str, Any]]:
        """Get top subreddits for user."""
        try:
            # Get user's feed items
            response = self.user_feeds_table.query(
                IndexName='UserFeedIndex',
                KeyConditionExpression='userId = :user_id',
                ExpressionAttributeValues={':user_id': user_id}
            )
            
            # Count posts by subreddit
            subreddit_counts = {}
            for item in response['Items']:
                subreddit_id = item['subredditId']
                subreddit_name = item['subredditName']
                if subreddit_id not in subreddit_counts:
                    subreddit_counts[subreddit_id] = {
                        'subredditId': subreddit_id,
                        'subredditName': subreddit_name,
                        'postCount': 0,
                        'averageScore': 0.0
                    }
                subreddit_counts[subreddit_id]['postCount'] += 1
                subreddit_counts[subreddit_id]['averageScore'] += item['postScore']
            
            # Calculate averages and sort
            for subreddit in subreddit_counts.values():
                if subreddit['postCount'] > 0:
                    subreddit['averageScore'] /= subreddit['postCount']
            
            return sorted(subreddit_counts.values(), key=lambda x: x['postCount'], reverse=True)[:limit]
        except ClientError:
            return []
    
    def _get_top_authors(self, user_id: str, limit: int) -> List[Dict[str, Any]]:
        """Get top authors for user."""
        try:
            # Get user's feed items
            response = self.user_feeds_table.query(
                IndexName='UserFeedIndex',
                KeyConditionExpression='userId = :user_id',
                ExpressionAttributeValues={':user_id': user_id}
            )
            
            # Count posts by author
            author_counts = {}
            for item in response['Items']:
                author_id = item['authorId']
                author_name = item['authorName']
                if author_id not in author_counts:
                    author_counts[author_id] = {
                        'authorId': author_id,
                        'authorName': author_name,
                        'postCount': 0,
                        'averageScore': 0.0
                    }
                author_counts[author_id]['postCount'] += 1
                author_counts[author_id]['averageScore'] += item['postScore']
            
            # Calculate averages and sort
            for author in author_counts.values():
                if author['postCount'] > 0:
                    author['averageScore'] /= author['postCount']
            
            return sorted(author_counts.values(), key=lambda x: x['postCount'], reverse=True)[:limit]
        except ClientError:
            return []
    
    def _calculate_average_score(self, user_id: str) -> float:
        """Calculate average score for user's feed."""
        try:
            response = self.user_feeds_table.query(
                IndexName='UserFeedIndex',
                KeyConditionExpression='userId = :user_id',
                ExpressionAttributeValues={':user_id': user_id}
            )
            
            if not response['Items']:
                return 0.0
            
            total_score = sum(item['postScore'] for item in response['Items'])
            return total_score / len(response['Items'])
        except ClientError:
            return 0.0
    
    def _get_last_refresh_time(self, user_id: str) -> Optional[str]:
        """Get last refresh time for user's feed."""
        try:
            response = self.user_feeds_table.query(
                IndexName='UserFeedIndex',
                KeyConditionExpression='userId = :user_id',
                ExpressionAttributeValues={':user_id': user_id},
                ScanIndexForward=False,  # Get most recent first
                Limit=1
            )
            
            if response['Items']:
                return response['Items'][0]['createdAt']
            return None
        except ClientError:
            return None
