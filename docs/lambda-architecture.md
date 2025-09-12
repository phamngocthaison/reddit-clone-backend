# Lambda Architecture Documentation

## Overview

The Reddit Clone Backend uses a **separated Lambda architecture** where each major functionality is handled by a dedicated Lambda function. This approach provides better scalability, maintainability, and allows for independent deployment and scaling of different features.

## Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │    │   API Gateway   │    │   API Gateway   │
│   (REST API)    │    │   (REST API)    │    │   (REST API)    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │                      │                      │
┌─────────▼───────┐    ┌─────────▼───────┐    ┌─────────▼───────┐
│  AuthLambda     │    │ CommentsLambda  │    │SubredditsLambda │
│  (Auth + Posts) │    │   (Comments)    │    │  (Subreddits)   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │                      │                      │
┌─────────▼───────┐    ┌─────────▼───────┐    ┌─────────▼───────┐
│  FeedsLambda    │    │UserProfileLambda│    │   DynamoDB      │
│  (News Feeds)   │    │ (User Profiles) │    │   (Database)    │
└─────────┬───────┘    └─────────┬───────┘    └─────────────────┘
          │                      │
          └──────────────────────┘
```

## Lambda Functions

### 1. AuthLambda
**Handler**: `lambda_handler_auth_posts.py`  
**Purpose**: Handles user authentication and posts management  
**APIs**:
- `POST /auth/register` - User registration
- `POST /auth/login` - User login (email/username)
- `POST /auth/logout` - User logout
- `POST /auth/forgot-password` - Password reset request
- `POST /auth/reset-password` - Password reset with code
- `POST /posts/create` - Create new post
- `GET /posts` - Get posts with filtering
- `GET /posts/{post_id}` - Get post by ID
- `PUT /posts/{post_id}` - Update post
- `DELETE /posts/{post_id}` - Delete post
- `POST /posts/{post_id}/vote` - Vote on post

**Dependencies**:
- DynamoDB: Users, Posts tables
- Cognito: User authentication
- IAM: Read/write permissions

### 2. CommentsLambda
**Handler**: `lambda_handler_comments.py`  
**Purpose**: Handles comments management  
**APIs**:
- `POST /comments/create` - Create new comment
- `GET /comments` - Get comments with filtering
- `GET /posts/{post_id}/comments` - Get comments for post
- `GET /comments/{comment_id}` - Get comment by ID
- `PUT /comments/{comment_id}` - Update comment
- `DELETE /comments/{comment_id}` - Delete comment
- `POST /comments/{comment_id}/vote` - Vote on comment

**Dependencies**:
- DynamoDB: Comments table
- IAM: Read/write permissions

### 3. SubredditsLambda
**Handler**: `lambda_handler_subreddits.py`  
**Purpose**: Handles subreddit management  
**APIs**:
- `POST /subreddits/create` - Create new subreddit
- `GET /subreddits` - Get subreddits with filtering
- `GET /subreddits/{subreddit_id}` - Get subreddit by ID
- `GET /subreddits/name/{name}` - Get subreddit by name
- `PUT /subreddits/{subreddit_id}` - Update subreddit
- `DELETE /subreddits/{subreddit_id}` - Delete subreddit
- `POST /subreddits/{subreddit_id}/join` - Join subreddit
- `POST /subreddits/{subreddit_id}/leave` - Leave subreddit
- `GET /subreddits/{subreddit_id}/posts` - Get subreddit posts

**Dependencies**:
- DynamoDB: Subreddits, Subscriptions tables
- IAM: Read/write permissions

### 4. FeedsLambda
**Handler**: `lambda_handler_feeds.py`  
**Purpose**: Handles personalized news feeds  
**APIs**:
- `GET /feeds` - Get personalized news feed
- `POST /feeds/refresh` - Refresh user feed
- `GET /feeds/stats` - Get feed statistics

**Dependencies**:
- DynamoDB: Feeds, Subscriptions, Posts tables
- IAM: Read permissions

### 5. UserProfileLambda
**Handler**: `lambda_handler_user_profile.py`  
**Purpose**: Handles user profile management  
**APIs**:
- `GET /auth/me` - Get current user profile
- `PUT /auth/me` - Update current user profile
- `DELETE /auth/me` - Delete user account
- `PUT /auth/change-password` - Change password
- `GET /users/{user_id}` - Get public user profile
- `GET /users/{user_id}/posts` - Get user posts
- `GET /users/{user_id}/comments` - Get user comments

**Dependencies**:
- DynamoDB: Users, Posts, Comments tables
- Cognito: User authentication
- IAM: Read/write permissions

## Database Schema

### DynamoDB Tables

#### Users Table (`reddit-clone-users`)
- **Primary Key**: `userId` (String)
- **GSI**: `EmailIndex` - Partition Key: `email` (String)
- **Fields**: userId, email, username, displayName, bio, avatar, karma, postCount, commentCount, isPublic, showEmail, createdAt, updatedAt, isActive

#### Posts Table (`reddit-clone-posts`)
- **Primary Key**: `postId` (String)
- **GSI**: `UserIndex` - Partition Key: `userId`, Sort Key: `createdAt`
- **GSI**: `SubredditIndex` - Partition Key: `subredditId`, Sort Key: `createdAt`
- **Fields**: postId, userId, subredditId, title, content, postType, url, mediaUrls, upvotes, downvotes, score, commentCount, createdAt, updatedAt, isDeleted

#### Comments Table (`reddit-clone-comments`)
- **Primary Key**: `commentId` (String)
- **GSI**: `PostIndex` - Partition Key: `postId`, Sort Key: `createdAt`
- **GSI**: `UserIndex` - Partition Key: `userId`, Sort Key: `createdAt`
- **GSI**: `ParentIndex` - Partition Key: `parentCommentId`, Sort Key: `createdAt`
- **Fields**: commentId, postId, userId, parentCommentId, content, upvotes, downvotes, score, replyCount, createdAt, updatedAt, isDeleted

#### Subreddits Table (`reddit-clone-subreddits`)
- **Primary Key**: `subredditId` (String)
- **GSI**: `NameIndex` - Partition Key: `name` (String)
- **Fields**: subredditId, name, displayName, description, ownerId, moderators, subscriberCount, postCount, rules, isPrivate, isNsfw, isRestricted, primaryColor, secondaryColor, language, country, bannerImage, iconImage, createdAt, updatedAt

#### Subscriptions Table (`reddit-clone-subscriptions`)
- **Primary Key**: `subscriptionId` (String)
- **GSI**: `UserIndex` - Partition Key: `userId`, Sort Key: `subredditId`
- **GSI**: `SubredditIndex` - Partition Key: `subredditId`, Sort Key: `userId`
- **Fields**: subscriptionId, userId, subredditId, role, joinedAt, isActive

#### Feeds Table (`reddit-clone-feeds`)
- **Primary Key**: `feedId` (String)
- **GSI**: `UserIndex` - Partition Key: `userId`, Sort Key: `createdAt`
- **Fields**: feedId, userId, postId, subredditId, authorId, postTitle, postContent, postImageUrl, subredditName, authorName, upvotes, downvotes, commentsCount, isPinned, isNSFW, isSpoiler, tags, createdAt, postScore

## Authentication & Authorization

### JWT Token Authentication
- **Provider**: AWS Cognito
- **Token Types**: Access Token, Refresh Token, ID Token
- **Expiration**: Access tokens expire after 1 hour
- **Validation**: Each Lambda validates JWT tokens independently

### Hybrid Authentication (Testing)
- **JWT Tokens**: Production authentication method
- **X-User-ID Header**: Testing/development method
- **Fallback**: If JWT validation fails, check X-User-ID header

### Authorization Levels
1. **Public**: No authentication required
2. **User**: Requires valid user authentication
3. **Owner**: Requires ownership of the resource
4. **Moderator**: Requires moderator role in subreddit
5. **Admin**: Requires admin privileges

## Error Handling

### Common Error Codes
- `UNAUTHORIZED` - Invalid or missing authentication
- `FORBIDDEN` - Insufficient permissions
- `NOT_FOUND` - Resource not found
- `VALIDATION_ERROR` - Input validation failed
- `INTERNAL_ERROR` - Server error

### Error Response Format
```json
{
  "success": false,
  "message": "Error description",
  "error": {
    "code": "ERROR_CODE",
    "message": "Detailed error message"
  }
}
```

## Performance Considerations

### Cold Start Optimization
- **Memory Allocation**: 512MB for all functions
- **Timeout**: 30 seconds for all functions
- **Package Size**: Minimized dependencies in lambda-layer.zip
- **Connection Pooling**: Reuse DynamoDB connections

### Caching Strategy
- **Feed Generation**: Cache generated feeds in DynamoDB
- **User Profiles**: Cache frequently accessed profiles
- **Subreddit Data**: Cache subreddit metadata

### Scaling
- **Concurrent Executions**: Auto-scaling based on demand
- **Database**: DynamoDB on-demand billing
- **API Gateway**: Automatic scaling

## Monitoring & Logging

### CloudWatch Integration
- **Logs**: All Lambda functions log to CloudWatch
- **Metrics**: Custom metrics for API performance
- **Alarms**: Set up alarms for error rates and latency

### Logging Levels
- **INFO**: Normal operation logs
- **WARN**: Warning conditions
- **ERROR**: Error conditions
- **DEBUG**: Detailed debugging information

## Deployment

### CDK Infrastructure
- **Stack**: `RedditCloneStack`
- **Resources**: Lambda functions, API Gateway, DynamoDB tables, IAM roles
- **Environment**: Production and development environments

### Lambda Deployment
- **Package**: `lambda-layer.zip` contains all dependencies
- **Update**: Use AWS CLI to update function code
- **Rollback**: Maintain previous versions for rollback

## Security

### IAM Roles
- **Least Privilege**: Each Lambda has minimal required permissions
- **Resource-based**: Permissions scoped to specific resources
- **Rotation**: Regular key rotation for enhanced security

### Data Protection
- **Encryption**: All data encrypted at rest and in transit
- **PII Handling**: Sensitive data properly handled and protected
- **Access Logging**: All API access logged for audit

## Future Enhancements

### Planned Features
- **Real-time Notifications**: WebSocket support
- **File Upload**: S3 integration for media files
- **Search**: Elasticsearch integration
- **Analytics**: Advanced analytics and reporting

### Architecture Improvements
- **Event-driven**: SNS/SQS for async processing
- **Caching**: Redis/ElastiCache for better performance
- **CDN**: CloudFront for static content delivery
- **Microservices**: Further decomposition of services