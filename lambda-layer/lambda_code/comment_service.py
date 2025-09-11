"""
Comment service for handling comment operations
"""

import os
import boto3
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from botocore.exceptions import ClientError

from .comment_models import (
    CreateCommentRequest,
    UpdateCommentRequest,
    GetCommentsRequest,
    CommentResponse,
    CommentsResponse,
    VoteCommentRequest,
    VoteCommentResponse,
    CommentType,
    VoteType
)


class CommentService:
    """Service for comment operations"""
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.comments_table = self.dynamodb.Table(os.environ['COMMENTS_TABLE'])
        self.posts_table = self.dynamodb.Table(os.environ['POSTS_TABLE'])
    
    def create_comment(self, request: CreateCommentRequest, author_id: str) -> CommentResponse:
        """Create a new comment"""
        try:
            # Generate comment ID
            comment_id = f"comment_{int(datetime.now(timezone.utc).timestamp())}_{os.urandom(8).hex()}"
            
            # Check if post exists
            post_response = self.posts_table.get_item(
                Key={'postId': request.post_id}
            )
            
            if 'Item' not in post_response:
                raise ValueError("Post not found")
            
            # If this is a reply, check if parent comment exists
            if request.parent_id:
                parent_response = self.comments_table.get_item(
                    Key={'commentId': request.parent_id}
                )
                
                if 'Item' not in parent_response:
                    raise ValueError("Parent comment not found")
                
                # Update parent comment's reply count
                self.comments_table.update_item(
                    Key={'commentId': request.parent_id},
                    UpdateExpression="SET replyCount = replyCount + :inc",
                    ExpressionAttributeValues={':inc': 1}
                )
            
            # Create comment item
            now = datetime.now(timezone.utc).isoformat()
            comment_item = {
                'commentId': comment_id,
                'postId': request.post_id,
                'authorId': author_id,
                'parentId': request.parent_id,
                'content': request.content,
                'commentType': request.comment_type.value,
                'score': 0,
                'upvotes': 0,
                'downvotes': 0,
                'replyCount': 0,
                'createdAt': now,
                'updatedAt': now,
                'isDeleted': request.is_deleted,
                'isEdited': request.is_edited,
                'isLocked': request.is_locked,
                'isSticky': request.is_sticky,
                'isNsfw': request.is_nsfw,
                'isSpoiler': request.is_spoiler,
                'flair': request.flair,
                'tags': request.tags,
                'awards': request.awards
            }
            
            # Save comment
            self.comments_table.put_item(Item=comment_item)
            
            # Update post's comment count
            self.posts_table.update_item(
                Key={'postId': request.post_id},
                UpdateExpression="SET commentCount = commentCount + :inc",
                ExpressionAttributeValues={':inc': 1}
            )
            
            return CommentResponse(
                comment_id=comment_id,
                post_id=request.post_id,
                author_id=author_id,
                parent_id=request.parent_id,
                content=request.content,
                comment_type=request.comment_type,
                score=0,
                upvotes=0,
                downvotes=0,
                reply_count=0,
                created_at=now,
                updated_at=now,
                is_deleted=request.is_deleted,
                is_edited=request.is_edited,
                is_locked=request.is_locked,
                is_sticky=request.is_sticky,
                is_nsfw=request.is_nsfw,
                is_spoiler=request.is_spoiler,
                flair=request.flair,
                tags=request.tags,
                awards=request.awards,
                user_vote=None,
                replies=[]
            )
            
        except ClientError as e:
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error creating comment: {str(e)}")
    
    def get_comment(self, comment_id: str) -> Optional[CommentResponse]:
        """Get a single comment by ID"""
        try:
            response = self.comments_table.get_item(
                Key={'commentId': comment_id}
            )
            
            if 'Item' not in response:
                return None
            
            item = response['Item']
            return self._item_to_comment_response(item)
            
        except ClientError as e:
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error getting comment: {str(e)}")
    
    def get_comments(self, request: GetCommentsRequest) -> CommentsResponse:
        """Get comments for a post with filtering and pagination"""
        try:
            # Build query parameters
            query_params = {
                'KeyConditionExpression': 'postId = :post_id',
                'ExpressionAttributeValues': {':post_id': request.post_id},
                'ScanIndexForward': request.sort in ['new', 'old'],
                'Limit': request.limit + 1  # Get one extra to check if there are more
            }
            
            # Add parent_id filter if specified
            if request.parent_id:
                query_params['FilterExpression'] = 'parentId = :parent_id'
                query_params['ExpressionAttributeValues'][':parent_id'] = request.parent_id
            else:
                query_params['FilterExpression'] = 'attribute_not_exists(parentId)'
            
            # Add deleted filter
            if not request.include_deleted:
                if 'FilterExpression' in query_params:
                    query_params['FilterExpression'] += ' AND isDeleted = :is_deleted'
                else:
                    query_params['FilterExpression'] = 'isDeleted = :is_deleted'
                query_params['ExpressionAttributeValues'][':is_deleted'] = False
            
            # Add offset
            if request.offset > 0:
                # For offset, we need to scan and skip items
                # This is not efficient for large offsets, but works for now
                query_params['Limit'] = request.offset + request.limit + 1
            
            # Execute query
            response = self.comments_table.query(**query_params)
            items = response.get('Items', [])
            
            # Apply offset
            if request.offset > 0:
                items = items[request.offset:]
            
            # Check if there are more items
            has_more = len(items) > request.limit
            if has_more:
                items = items[:request.limit]
            
            # Convert to comment responses
            comments = [self._item_to_comment_response(item) for item in items]
            
            # Sort comments based on sort parameter
            if request.sort == 'hot':
                comments.sort(key=lambda x: x.score, reverse=True)
            elif request.sort == 'top':
                comments.sort(key=lambda x: x.upvotes, reverse=True)
            elif request.sort == 'controversial':
                comments.sort(key=lambda x: min(x.upvotes, x.downvotes), reverse=True)
            elif request.sort == 'new':
                comments.sort(key=lambda x: x.created_at, reverse=True)
            elif request.sort == 'old':
                comments.sort(key=lambda x: x.created_at)
            
            # Get total count
            count_response = self.comments_table.query(
                KeyConditionExpression='postId = :post_id',
                ExpressionAttributeValues={':post_id': request.post_id},
                Select='COUNT'
            )
            total_count = count_response.get('Count', 0)
            
            return CommentsResponse(
                comments=comments,
                total_count=total_count,
                has_more=has_more,
                next_offset=request.offset + len(comments)
            )
            
        except ClientError as e:
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error getting comments: {str(e)}")
    
    def update_comment(self, comment_id: str, request: UpdateCommentRequest, user_id: str) -> CommentResponse:
        """Update a comment"""
        try:
            # Get current comment
            response = self.comments_table.get_item(
                Key={'commentId': comment_id}
            )
            
            if 'Item' not in response:
                raise ValueError("Comment not found")
            
            item = response['Item']
            
            # Check if user is the author
            if item['authorId'] != user_id:
                raise ValueError("Access denied")
            
            # Build update expression
            update_expression = "SET updatedAt = :updated_at"
            expression_values = {':updated_at': datetime.now(timezone.utc).isoformat()}
            
            if request.content is not None:
                update_expression += ", content = :content, isEdited = :is_edited"
                expression_values[':content'] = request.content
                expression_values[':is_edited'] = True
            
            if request.is_nsfw is not None:
                update_expression += ", isNsfw = :is_nsfw"
                expression_values[':is_nsfw'] = request.is_nsfw
            
            if request.is_spoiler is not None:
                update_expression += ", isSpoiler = :is_spoiler"
                expression_values[':is_spoiler'] = request.is_spoiler
            
            if request.flair is not None:
                update_expression += ", flair = :flair"
                expression_values[':flair'] = request.flair
            
            if request.tags is not None:
                update_expression += ", tags = :tags"
                expression_values[':tags'] = request.tags
            
            # Update comment
            self.comments_table.update_item(
                Key={'commentId': comment_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values
            )
            
            # Get updated comment
            updated_response = self.comments_table.get_item(
                Key={'commentId': comment_id}
            )
            
            return self._item_to_comment_response(updated_response['Item'])
            
        except ClientError as e:
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error updating comment: {str(e)}")
    
    def delete_comment(self, comment_id: str, user_id: str) -> bool:
        """Delete a comment (soft delete)"""
        try:
            # Get current comment
            response = self.comments_table.get_item(
                Key={'commentId': comment_id}
            )
            
            if 'Item' not in response:
                raise ValueError("Comment not found")
            
            item = response['Item']
            
            # Check if user is the author
            if item['authorId'] != user_id:
                raise ValueError("Access denied")
            
            # Soft delete comment
            self.comments_table.update_item(
                Key={'commentId': comment_id},
                UpdateExpression="SET isDeleted = :is_deleted, updatedAt = :updated_at",
                ExpressionAttributeValues={
                    ':is_deleted': True,
                    ':updated_at': datetime.now(timezone.utc).isoformat()
                }
            )
            
            # Update post's comment count
            self.posts_table.update_item(
                Key={'postId': item['postId']},
                UpdateExpression="SET commentCount = commentCount - :dec",
                ExpressionAttributeValues={':dec': 1}
            )
            
            # If this is a reply, update parent comment's reply count
            if item.get('parentId'):
                self.comments_table.update_item(
                    Key={'commentId': item['parentId']},
                    UpdateExpression="SET replyCount = replyCount - :dec",
                    ExpressionAttributeValues={':dec': 1}
                )
            
            return True
            
        except ClientError as e:
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error deleting comment: {str(e)}")
    
    def vote_comment(self, comment_id: str, request: VoteCommentRequest, user_id: str) -> VoteCommentResponse:
        """Vote on a comment"""
        try:
            # Get current comment
            response = self.comments_table.get_item(
                Key={'commentId': comment_id}
            )
            
            if 'Item' not in response:
                raise ValueError("Comment not found")
            
            item = response['Item']
            
            # Get current vote for this user
            vote_key = f"vote_{user_id}_{comment_id}"
            vote_response = self.comments_table.get_item(
                Key={'commentId': vote_key}
            )
            
            current_vote = None
            if 'Item' in vote_response:
                current_vote = vote_response['Item']['voteType']
            
            # Calculate vote changes
            upvote_change = 0
            downvote_change = 0
            
            if request.vote_type == VoteType.UPVOTE:
                if current_vote == 'upvote':
                    # Already upvoted, remove vote
                    upvote_change = -1
                elif current_vote == 'downvote':
                    # Change from downvote to upvote
                    upvote_change = 1
                    downvote_change = -1
                else:
                    # New upvote
                    upvote_change = 1
            elif request.vote_type == VoteType.DOWNVOTE:
                if current_vote == 'downvote':
                    # Already downvoted, remove vote
                    downvote_change = -1
                elif current_vote == 'upvote':
                    # Change from upvote to downvote
                    upvote_change = -1
                    downvote_change = 1
                else:
                    # New downvote
                    downvote_change = 1
            elif request.vote_type == VoteType.REMOVE:
                if current_vote == 'upvote':
                    upvote_change = -1
                elif current_vote == 'downvote':
                    downvote_change = -1
            
            # Update comment stats
            update_expression = "SET upvotes = upvotes + :upvote_change, downvotes = downvotes + :downvote_change, score = score + :score_change"
            expression_values = {
                ':upvote_change': upvote_change,
                ':downvote_change': downvote_change,
                ':score_change': upvote_change - downvote_change
            }
            
            self.comments_table.update_item(
                Key={'commentId': comment_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values
            )
            
            # Update or create vote record
            if request.vote_type == VoteType.REMOVE:
                # Remove vote record
                self.comments_table.delete_item(
                    Key={'commentId': vote_key}
                )
            else:
                # Update or create vote record
                self.comments_table.put_item(
                    Item={
                        'commentId': vote_key,
                        'postId': item['postId'],
                        'commentId': comment_id,
                        'userId': user_id,
                        'voteType': request.vote_type.value,
                        'createdAt': datetime.now(timezone.utc).isoformat()
                    }
                )
            
            # Get updated stats
            updated_response = self.comments_table.get_item(
                Key={'commentId': comment_id}
            )
            
            updated_item = updated_response['Item']
            
            return VoteCommentResponse(
                stats={
                    'comment_id': comment_id,
                    'score': updated_item['score'],
                    'upvotes': updated_item['upvotes'],
                    'downvotes': updated_item['downvotes'],
                    'reply_count': updated_item['replyCount']
                }
            )
            
        except ClientError as e:
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error voting on comment: {str(e)}")
    
    def _item_to_comment_response(self, item: Dict[str, Any]) -> CommentResponse:
        """Convert DynamoDB item to CommentResponse"""
        return CommentResponse(
            comment_id=item['commentId'],
            post_id=item['postId'],
            author_id=item['authorId'],
            parent_id=item.get('parentId'),
            content=item['content'],
            comment_type=CommentType(item['commentType']),
            score=item['score'],
            upvotes=item['upvotes'],
            downvotes=item['downvotes'],
            reply_count=item['replyCount'],
            created_at=item['createdAt'],
            updated_at=item['updatedAt'],
            is_deleted=item['isDeleted'],
            is_edited=item['isEdited'],
            is_locked=item['isLocked'],
            is_sticky=item['isSticky'],
            is_nsfw=item['isNsfw'],
            is_spoiler=item['isSpoiler'],
            flair=item.get('flair'),
            tags=item.get('tags', []),
            awards=item.get('awards', []),
            user_vote=None,  # This would need to be populated based on current user
            replies=[]
        )
