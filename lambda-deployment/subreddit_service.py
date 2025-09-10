"""Subreddit service for handling subreddit business logic."""

import boto3
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from botocore.exceptions import ClientError

from subreddit_models import (
    CreateSubredditRequest,
    UpdateSubredditRequest,
    JoinSubredditRequest,
    SubredditResponse,
    SubredditListResponse,
    GetSubredditsRequest,
    GetSubredditPostsRequest,
    SubscriptionResponse,
    ModeratorRequest,
    BanUserRequest,
    SubredditStatsResponse
)


class SubredditService:
    """Service class for subreddit operations."""

    def __init__(self):
        """Initialize the service with DynamoDB resources."""
        self.dynamodb = boto3.resource('dynamodb')
        self.subreddits_table = self.dynamodb.Table('reddit-clone-subreddits')
        self.subscriptions_table = self.dynamodb.Table('reddit-clone-subscriptions')
        self.posts_table = self.dynamodb.Table('reddit-clone-posts')
        self.comments_table = self.dynamodb.Table('reddit-clone-comments')
        self.users_table = self.dynamodb.Table('reddit-clone-users')

    def create_subreddit(self, request: CreateSubredditRequest, owner_id: str) -> SubredditResponse:
        """Create a new subreddit."""
        try:
            # Check if subreddit name already exists
            if self._subreddit_name_exists(request.name):
                raise ValueError(f"Subreddit name '{request.name}' already exists")

            # Generate subreddit ID
            subreddit_id = f"subreddit_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
            current_time = datetime.now(timezone.utc).isoformat()

            # Create subreddit item
            subreddit_item = {
                'subredditId': subreddit_id,
                'name': request.name,
                'displayName': request.display_name,
                'description': request.description,
                'rules': request.rules,
                'ownerId': owner_id,
                'moderators': [owner_id],  # Owner is automatically a moderator
                'subscriberCount': 1,  # Owner is the first subscriber
                'postCount': 0,
                'createdAt': current_time,
                'updatedAt': current_time,
                'isPrivate': request.is_private,
                'isNSFW': request.is_nsfw,
                'isRestricted': request.is_restricted,
                'bannerImage': None,
                'iconImage': None,
                'primaryColor': request.primary_color,
                'secondaryColor': request.secondary_color,
                'language': request.language,
                'country': request.country
            }

            # Create subscription for owner
            subscription_id = f"sub_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
            subscription_item = {
                'subscriptionId': subscription_id,
                'userId': owner_id,
                'subredditId': subreddit_id,
                'role': 'owner',
                'joinedAt': current_time,
                'isActive': True
            }

            # Use transaction to create both items
            with self.subreddits_table.batch_writer() as batch:
                batch.put_item(Item=subreddit_item)
            
            with self.subscriptions_table.batch_writer() as batch:
                batch.put_item(Item=subscription_item)

            return self._item_to_subreddit_response(subreddit_item, owner_id)

        except ClientError as e:
            raise Exception(f"Failed to create subreddit: {str(e)}")

    def get_subreddit(self, subreddit_id: str, user_id: Optional[str] = None) -> SubredditResponse:
        """Get subreddit by ID."""
        try:
            response = self.subreddits_table.get_item(Key={'subredditId': subreddit_id})
            
            if 'Item' not in response:
                raise ValueError(f"Subreddit {subreddit_id} not found")

            item = response['Item']
            
            # Check if user is subscribed
            is_subscribed = None
            user_role = None
            if user_id:
                subscription = self._get_user_subscription(user_id, subreddit_id)
                is_subscribed = subscription is not None
                user_role = subscription.get('role') if subscription else None

            return self._item_to_subreddit_response(item, user_id, is_subscribed, user_role)

        except ClientError as e:
            raise Exception(f"Failed to get subreddit: {str(e)}")

    def get_subreddit_by_name(self, name: str, user_id: Optional[str] = None) -> SubredditResponse:
        """Get subreddit by name."""
        try:
            response = self.subreddits_table.query(
                IndexName='NameIndex',
                KeyConditionExpression='#name = :name',
                ExpressionAttributeNames={'#name': 'name'},
                ExpressionAttributeValues={':name': name}
            )
            
            if not response['Items']:
                raise ValueError(f"Subreddit '{name}' not found")

            item = response['Items'][0]
            
            # Check if user is subscribed
            is_subscribed = None
            user_role = None
            if user_id:
                subscription = self._get_user_subscription(user_id, item['subredditId'])
                is_subscribed = subscription is not None
                user_role = subscription.get('role') if subscription else None

            return self._item_to_subreddit_response(item, user_id, is_subscribed, user_role)

        except ClientError as e:
            raise Exception(f"Failed to get subreddit: {str(e)}")

    def update_subreddit(self, subreddit_id: str, request: UpdateSubredditRequest, user_id: str) -> SubredditResponse:
        """Update subreddit."""
        try:
            # Check if user has permission to update
            if not self._can_moderate_subreddit(user_id, subreddit_id):
                raise ValueError("Insufficient permissions to update subreddit")

            # Build update expression
            update_expression = "SET updatedAt = :updated_at"
            expression_values = {':updated_at': datetime.now(timezone.utc).isoformat()}
            expression_names = {}

            if request.display_name is not None:
                update_expression += ", displayName = :display_name"
                expression_values[':display_name'] = request.display_name

            if request.description is not None:
                update_expression += ", description = :description"
                expression_values[':description'] = request.description

            if request.rules is not None:
                update_expression += ", #rules = :rules"
                expression_values[':rules'] = request.rules
                expression_names['#rules'] = 'rules'

            if request.is_private is not None:
                update_expression += ", isPrivate = :is_private"
                expression_values[':is_private'] = request.is_private

            if request.is_nsfw is not None:
                update_expression += ", isNSFW = :is_nsfw"
                expression_values[':is_nsfw'] = request.is_nsfw

            if request.is_restricted is not None:
                update_expression += ", isRestricted = :is_restricted"
                expression_values[':is_restricted'] = request.is_restricted

            if request.primary_color is not None:
                update_expression += ", primaryColor = :primary_color"
                expression_values[':primary_color'] = request.primary_color

            if request.secondary_color is not None:
                update_expression += ", secondaryColor = :secondary_color"
                expression_values[':secondary_color'] = request.secondary_color

            if request.language is not None:
                update_expression += ", language = :language"
                expression_values[':language'] = request.language

            if request.country is not None:
                update_expression += ", country = :country"
                expression_values[':country'] = request.country

            # Update subreddit
            update_params = {
                'Key': {'subredditId': subreddit_id},
                'UpdateExpression': update_expression,
                'ExpressionAttributeValues': expression_values,
                'ReturnValues': 'ALL_NEW'
            }
            
            if expression_names:
                update_params['ExpressionAttributeNames'] = expression_names
                
            self.subreddits_table.update_item(**update_params)

            # Get updated subreddit
            return self.get_subreddit(subreddit_id, user_id)

        except ClientError as e:
            raise Exception(f"Failed to update subreddit: {str(e)}")

    def delete_subreddit(self, subreddit_id: str, user_id: str) -> bool:
        """Delete subreddit (only owner can delete)."""
        try:
            # Check if user is owner
            subreddit = self.get_subreddit(subreddit_id)
            if subreddit.owner_id != user_id:
                raise ValueError("Only the owner can delete the subreddit")

            # Delete all subscriptions
            subscriptions = self._get_subreddit_subscriptions(subreddit_id)
            for subscription in subscriptions:
                self.subscriptions_table.delete_item(
                    Key={'subscriptionId': subscription['subscriptionId']}
                )

            # Delete subreddit
            self.subreddits_table.delete_item(Key={'subredditId': subreddit_id})

            return True

        except ClientError as e:
            raise Exception(f"Failed to delete subreddit: {str(e)}")

    def join_subreddit(self, subreddit_id: str, user_id: str) -> SubscriptionResponse:
        """Join a subreddit."""
        try:
            # Check if already subscribed
            existing_subscription = self._get_user_subscription(user_id, subreddit_id)
            if existing_subscription and existing_subscription['isActive']:
                raise ValueError("User is already subscribed to this subreddit")

            # Check if subreddit exists
            subreddit = self.get_subreddit(subreddit_id)
            if subreddit.is_private:
                raise ValueError("Cannot join private subreddit without invitation")

            # Create or update subscription
            subscription_id = f"sub_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
            current_time = datetime.now(timezone.utc).isoformat()

            if existing_subscription:
                # Update existing subscription
                self.subscriptions_table.update_item(
                    Key={'subscriptionId': existing_subscription['subscriptionId']},
                    UpdateExpression="SET isActive = :is_active, joinedAt = :joined_at",
                    ExpressionAttributeValues={
                        ':is_active': True,
                        ':joined_at': current_time
                    }
                )
                subscription_id = existing_subscription['subscriptionId']
            else:
                # Create new subscription
                subscription_item = {
                    'subscriptionId': subscription_id,
                    'userId': user_id,
                    'subredditId': subreddit_id,
                    'role': 'subscriber',
                    'joinedAt': current_time,
                    'isActive': True
                }
                self.subscriptions_table.put_item(Item=subscription_item)

            # Update subscriber count
            self.subreddits_table.update_item(
                Key={'subredditId': subreddit_id},
                UpdateExpression="SET subscriberCount = subscriberCount + :inc",
                ExpressionAttributeValues={':inc': 1}
            )

            return SubscriptionResponse(
                subscription_id=subscription_id,
                user_id=user_id,
                subreddit_id=subreddit_id,
                role='subscriber',
                joined_at=current_time,
                is_active=True
            )

        except ClientError as e:
            raise Exception(f"Failed to join subreddit: {str(e)}")

    def leave_subreddit(self, subreddit_id: str, user_id: str) -> bool:
        """Leave a subreddit."""
        try:
            # Get subscription
            subscription = self._get_user_subscription(user_id, subreddit_id)
            if not subscription:
                raise ValueError("User is not subscribed to this subreddit")

            # Check if user is owner
            subreddit = self.get_subreddit(subreddit_id)
            if subreddit.owner_id == user_id:
                raise ValueError("Owner cannot leave their own subreddit")

            # Update subscription
            self.subscriptions_table.update_item(
                Key={'subscriptionId': subscription['subscriptionId']},
                UpdateExpression="SET isActive = :is_active",
                ExpressionAttributeValues={':is_active': False}
            )

            # Update subscriber count
            self.subreddits_table.update_item(
                Key={'subredditId': subreddit_id},
                UpdateExpression="SET subscriberCount = subscriberCount - :dec",
                ExpressionAttributeValues={':dec': 1}
            )

            return True

        except ClientError as e:
            raise Exception(f"Failed to leave subreddit: {str(e)}")

    def get_subreddits(self, request: GetSubredditsRequest, user_id: Optional[str] = None) -> SubredditListResponse:
        """Get list of subreddits."""
        try:
            if request.sort == 'popular':
                # Query by subscriber count - need to scan with filter
                response = self.subreddits_table.scan(
                    Limit=request.limit
                )
            else:
                # Query by creation date
                response = self.subreddits_table.scan(
                    Limit=request.limit
                )

            items = response['Items']
            
            # Apply filters
            if request.search:
                items = [item for item in items if request.search.lower() in item.get('name', '').lower() or 
                        request.search.lower() in item.get('displayName', '').lower()]

            if request.is_nsfw is not None:
                items = [item for item in items if item.get('isNSFW', False) == request.is_nsfw]

            if request.language:
                items = [item for item in items if item.get('language', 'en') == request.language]

            if request.country:
                items = [item for item in items if item.get('country', 'US') == request.country]

            # Sort if needed
            if request.sort == 'new':
                items.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
            elif request.sort == 'trending':
                # Simple trending algorithm based on recent activity
                items.sort(key=lambda x: x.get('subscriberCount', 0), reverse=True)

            # Apply pagination
            total_count = len(items)
            start_idx = request.offset
            end_idx = start_idx + request.limit
            items = items[start_idx:end_idx]

            # Convert to response objects
            subreddits = []
            for item in items:
                is_subscribed = None
                user_role = None
                if user_id:
                    subscription = self._get_user_subscription(user_id, item['subredditId'])
                    is_subscribed = subscription is not None and subscription.get('isActive', False)
                    user_role = subscription.get('role') if subscription else None

                subreddits.append(self._item_to_subreddit_response(item, user_id, is_subscribed, user_role))

            return SubredditListResponse(
                subreddits=subreddits,
                total_count=total_count,
                has_more=end_idx < total_count,
                next_offset=end_idx if end_idx < total_count else None
            )

        except ClientError as e:
            raise Exception(f"Failed to get subreddits: {str(e)}")

    def get_subreddit_posts(self, subreddit_id: str, request: GetSubredditPostsRequest) -> Dict[str, Any]:
        """Get posts in a subreddit."""
        try:
            # Check if subreddit exists
            subreddit = self.get_subreddit(subreddit_id)
            
            # Query posts by subreddit
            query_params = {
                'IndexName': 'SubredditIndex',
                'KeyConditionExpression': 'subredditId = :subreddit_id',
                'ExpressionAttributeValues': {':subreddit_id': subreddit_id},
                'Limit': request.limit
            }

            # Apply filters
            filter_expressions = []
            if request.post_type:
                filter_expressions.append('postType = :post_type')
                query_params['ExpressionAttributeValues'][':post_type'] = request.post_type

            if request.is_nsfw is not None:
                filter_expressions.append('isNSFW = :is_nsfw')
                query_params['ExpressionAttributeValues'][':is_nsfw'] = request.is_nsfw

            if filter_expressions:
                query_params['FilterExpression'] = ' AND '.join(filter_expressions)

            response = self.posts_table.query(**query_params)
            posts = response.get('Items', [])

            # Sort posts
            if request.sort == 'hot':
                posts.sort(key=lambda x: x.get('score', 0), reverse=True)
            elif request.sort == 'new':
                posts.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
            elif request.sort == 'top':
                posts.sort(key=lambda x: x.get('upvotes', 0), reverse=True)
            elif request.sort == 'controversial':
                # Sort by ratio of upvotes to downvotes
                posts.sort(key=lambda x: x.get('upvotes', 0) / max(x.get('downvotes', 1), 1), reverse=True)

            return {
                'posts': posts,
                'count': len(posts),
                'subreddit_id': subreddit_id
            }

        except ClientError as e:
            raise Exception(f"Failed to get subreddit posts: {str(e)}")

    def add_moderator(self, subreddit_id: str, request: ModeratorRequest, user_id: str) -> bool:
        """Add moderator to subreddit."""
        try:
            # Check if user has permission
            if not self._can_moderate_subreddit(user_id, subreddit_id):
                raise ValueError("Insufficient permissions to add moderators")

            # Check if user exists
            user_response = self.users_table.get_item(Key={'userId': request.user_id})
            if 'Item' not in user_response:
                raise ValueError("User not found")

            # Add moderator
            self.subreddits_table.update_item(
                Key={'subredditId': subreddit_id},
                UpdateExpression="SET moderators = list_append(moderators, :moderator)",
                ExpressionAttributeValues={':moderator': [request.user_id]}
            )

            return True

        except ClientError as e:
            raise Exception(f"Failed to add moderator: {str(e)}")

    def remove_moderator(self, subreddit_id: str, request: ModeratorRequest, user_id: str) -> bool:
        """Remove moderator from subreddit."""
        try:
            # Check if user has permission
            if not self._can_moderate_subreddit(user_id, subreddit_id):
                raise ValueError("Insufficient permissions to remove moderators")

            # Get current moderators
            subreddit = self.get_subreddit(subreddit_id)
            moderators = subreddit.moderators.copy()
            
            if request.user_id not in moderators:
                raise ValueError("User is not a moderator")

            # Remove moderator
            moderators.remove(request.user_id)
            self.subreddits_table.update_item(
                Key={'subredditId': subreddit_id},
                UpdateExpression="SET moderators = :moderators",
                ExpressionAttributeValues={':moderators': moderators}
            )

            return True

        except ClientError as e:
            raise Exception(f"Failed to remove moderator: {str(e)}")

    def _subreddit_name_exists(self, name: str) -> bool:
        """Check if subreddit name already exists."""
        try:
            response = self.subreddits_table.query(
                IndexName='NameIndex',
                KeyConditionExpression='#name = :name',
                ExpressionAttributeNames={'#name': 'name'},
                ExpressionAttributeValues={':name': name}
            )
            return len(response['Items']) > 0
        except ClientError:
            return False

    def _get_user_subscription(self, user_id: str, subreddit_id: str) -> Optional[Dict[str, Any]]:
        """Get user's subscription to a subreddit."""
        try:
            response = self.subscriptions_table.query(
                IndexName='UserIndex',
                KeyConditionExpression='userId = :user_id',
                FilterExpression='subredditId = :subreddit_id',
                ExpressionAttributeValues={
                    ':user_id': user_id,
                    ':subreddit_id': subreddit_id
                }
            )
            return response['Items'][0] if response['Items'] else None
        except ClientError:
            return None

    def _get_subreddit_subscriptions(self, subreddit_id: str) -> List[Dict[str, Any]]:
        """Get all subscriptions for a subreddit."""
        try:
            response = self.subscriptions_table.scan(
                FilterExpression='subredditId = :subreddit_id',
                ExpressionAttributeValues={':subreddit_id': subreddit_id}
            )
            return response['Items']
        except ClientError:
            return []

    def _can_moderate_subreddit(self, user_id: str, subreddit_id: str) -> bool:
        """Check if user can moderate subreddit."""
        try:
            subreddit = self.get_subreddit(subreddit_id)
            return user_id in subreddit.moderators
        except:
            return False

    def _item_to_subreddit_response(self, item: Dict[str, Any], user_id: Optional[str] = None, 
                                  is_subscribed: Optional[bool] = None, user_role: Optional[str] = None) -> SubredditResponse:
        """Convert DynamoDB item to SubredditResponse."""
        return SubredditResponse(
            subreddit_id=item['subredditId'],
            name=item['name'],
            display_name=item['displayName'],
            description=item['description'],
            rules=item.get('rules', []),
            owner_id=item['ownerId'],
            moderators=item.get('moderators', []),
            subscriber_count=item.get('subscriberCount', 0),
            post_count=item.get('postCount', 0),
            created_at=item['createdAt'],
            updated_at=item['updatedAt'],
            is_private=item.get('isPrivate', False),
            is_nsfw=item.get('isNSFW', False),
            is_restricted=item.get('isRestricted', False),
            banner_image=item.get('bannerImage'),
            icon_image=item.get('iconImage'),
            primary_color=item.get('primaryColor', '#FF4500'),
            secondary_color=item.get('secondaryColor', '#FFFFFF'),
            language=item.get('language', 'en'),
            country=item.get('country', 'US'),
            is_subscribed=is_subscribed,
            user_role=user_role
        )
