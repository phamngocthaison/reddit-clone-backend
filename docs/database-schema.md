# Database Schema

This document outlines the database schema for the Reddit Clone Backend using DynamoDB.

## Tables

### Users Table (`reddit-clone-users`)

**Primary Key**: `userId` (String)  
**Global Secondary Index**: `EmailIndex` - Partition Key: `email` (String)

| Attribute | Type | Description | Required |
|-----------|------|-------------|----------|
| `userId` | String | Unique user identifier | Yes |
| `email` | String | User's email address | Yes |
| `username` | String | User's display name | Yes |
| `createdAt` | String | ISO timestamp of account creation | Yes |
| `updatedAt` | String | ISO timestamp of last update | Yes |
| `isActive` | Boolean | Whether the user account is active | Yes |
| `displayName` | String | User's display name for profile | No |
| `bio` | String | User's bio/description | No |
| `avatar` | String | URL to user's avatar image | No |
| `karma` | Number | User's karma points | No |
| `postCount` | Number | Number of posts created | No |
| `commentCount` | Number | Number of comments made | No |
| `isPublic` | Boolean | Whether profile is public | No |
| `showEmail` | Boolean | Whether to show email publicly | No |

**Access Patterns**:
- Get user by userId (Primary Key)
- Get user by email (EmailIndex GSI)
- List all users (Scan - for admin purposes)

### Posts Table (`reddit-clone-posts`)

**Primary Key**: `postId` (String)  
**Global Secondary Indexes**:
- `UserIndex` - Partition Key: `userId`, Sort Key: `createdAt`
- `CommunityIndex` - Partition Key: `communityId`, Sort Key: `createdAt`

| Attribute | Type | Description |
|-----------|------|-------------|
| `postId` | String | Unique post identifier |
| `userId` | String | ID of user who created the post |
| `communityId` | String | ID of community/subreddit |
| `title` | String | Post title |
| `content` | String | Post content (text/markdown) |
| `postType` | String | Type: 'text', 'link', 'image' |
| `url` | String | External URL (for link posts) |
| `imageUrl` | String | Image URL (for image posts) |
| `upvotes` | Number | Number of upvotes |
| `downvotes` | Number | Number of downvotes |
| `score` | Number | Net score (upvotes - downvotes) |
| `commentCount` | Number | Number of comments |
| `createdAt` | String | ISO timestamp of creation |
| `updatedAt` | String | ISO timestamp of last update |
| `isDeleted` | Boolean | Soft delete flag |

### Comments Table (`reddit-clone-comments`)

**Primary Key**: `commentId` (String)  
**Global Secondary Indexes**:
- `PostIndex` - Partition Key: `postId`, Sort Key: `createdAt`
- `UserIndex` - Partition Key: `userId`, Sort Key: `createdAt`
- `ParentIndex` - Partition Key: `parentCommentId`, Sort Key: `createdAt`

| Attribute | Type | Description |
|-----------|------|-------------|
| `commentId` | String | Unique comment identifier |
| `postId` | String | ID of post being commented on |
| `userId` | String | ID of user who made the comment |
| `parentCommentId` | String | ID of parent comment (for nested comments) |
| `content` | String | Comment content (markdown) |
| `upvotes` | Number | Number of upvotes |
| `downvotes` | Number | Number of downvotes |
| `score` | Number | Net score (upvotes - downvotes) |
| `depth` | Number | Nesting level (0 for top-level) |
| `createdAt` | String | ISO timestamp of creation |
| `updatedAt` | String | ISO timestamp of last update |
| `isDeleted` | Boolean | Soft delete flag |

### Subreddits Table (`reddit-clone-subreddits`)

**Primary Key**: `subredditId` (String)  
**Global Secondary Index**: `NameIndex` - Partition Key: `name` (String)

| Attribute | Type | Description |
|-----------|------|-------------|
| `subredditId` | String | Unique subreddit identifier |
| `name` | String | Subreddit name (like r/programming) |
| `displayName` | String | Display name for UI |
| `description` | String | Subreddit description |
| `ownerId` | String | ID of user who created the subreddit |
| `moderators` | List | List of moderator user IDs |
| `subscriberCount` | Number | Number of subscribers |
| `postCount` | Number | Number of posts |
| `rules` | List | Subreddit rules |
| `isPrivate` | Boolean | Whether subreddit is private |
| `isNsfw` | Boolean | Whether subreddit is NSFW |
| `isRestricted` | Boolean | Whether subreddit is restricted |
| `primaryColor` | String | Primary color for UI |
| `secondaryColor` | String | Secondary color for UI |
| `language` | String | Subreddit language |
| `country` | String | Subreddit country |
| `bannerImage` | String | Banner image URL |
| `iconImage` | String | Icon image URL |
| `createdAt` | String | ISO timestamp of creation |
| `updatedAt` | String | ISO timestamp of last update |

### Subscriptions Table (`reddit-clone-subscriptions`)

**Primary Key**: `subscriptionId` (String)  
**Global Secondary Indexes**:
- `UserIndex` - Partition Key: `userId`, Sort Key: `subredditId`
- `SubredditIndex` - Partition Key: `subredditId`, Sort Key: `userId`

| Attribute | Type | Description |
|-----------|------|-------------|
| `subscriptionId` | String | Unique subscription identifier |
| `userId` | String | ID of user who subscribed |
| `subredditId` | String | ID of subreddit being subscribed to |
| `role` | String | User role: 'subscriber', 'moderator', 'owner' |
| `joinedAt` | String | ISO timestamp of subscription |
| `isActive` | Boolean | Whether subscription is active |

### Feeds Table (`reddit-clone-feeds`)

**Primary Key**: `feedId` (String)  
**Global Secondary Index**: `UserIndex` - Partition Key: `userId`, Sort Key: `createdAt`

| Attribute | Type | Description |
|-----------|------|-------------|
| `feedId` | String | Unique feed item identifier |
| `userId` | String | ID of user this feed belongs to |
| `postId` | String | ID of post in feed |
| `subredditId` | String | ID of subreddit the post belongs to |
| `authorId` | String | ID of post author |
| `postTitle` | String | Post title |
| `postContent` | String | Post content preview |
| `postImageUrl` | String | Post image URL |
| `subredditName` | String | Subreddit name |
| `authorName` | String | Author username |
| `upvotes` | Number | Number of upvotes |
| `downvotes` | Number | Number of downvotes |
| `commentsCount` | Number | Number of comments |
| `isPinned` | Boolean | Whether post is pinned |
| `isNSFW` | Boolean | Whether post is NSFW |
| `isSpoiler` | Boolean | Whether post is spoiler |
| `tags` | List | Post tags |
| `createdAt` | String | ISO timestamp of creation |
| `postScore` | Number | Post score for ranking |

### Votes Table (`reddit-clone-votes`)

**Primary Key**: `voteId` (String)  
**Global Secondary Indexes**:
- `UserItemIndex` - Partition Key: `userId`, Sort Key: `itemId`
- `ItemIndex` - Partition Key: `itemId`, Sort Key: `userId`

| Attribute | Type | Description |
|-----------|------|-------------|
| `voteId` | String | Unique vote identifier |
| `userId` | String | ID of user who voted |
| `itemId` | String | ID of item being voted on (post or comment) |
| `itemType` | String | Type: 'post' or 'comment' |
| `voteType` | String | Type: 'upvote' or 'downvote' |
| `createdAt` | String | ISO timestamp of vote |
| `updatedAt` | String | ISO timestamp of last update |

## Design Principles

1. **Single Table Design**: While we use multiple tables here for clarity, DynamoDB best practices often suggest single table design for better performance.

2. **Access Patterns First**: All GSI designs are based on expected query patterns.

3. **Denormalization**: Some data is duplicated (like vote counts) to avoid expensive aggregations.

4. **Soft Deletes**: Use `isDeleted` flags instead of actually deleting records to maintain data integrity.

5. **Timestamps**: All records include creation and update timestamps for auditing.

## Query Examples

### Get User Posts
```
Query on PostsTable using UserIndex:
PK = userId, SK begins_with createdAt (for pagination)
```

### Get Post Comments
```
Query on CommentsTable using PostIndex:
PK = postId, SK begins_with createdAt
```

### Get User's Vote on Post
```
Query on VotesTable using UserItemIndex:
PK = userId, SK = postId
```

## Scaling Considerations

- **Read/Write Capacity**: Use on-demand billing initially, switch to provisioned for cost optimization
- **Hot Partitions**: Monitor for hot partitions and adjust partition keys if needed
- **GSI Costs**: Each GSI costs additional read/write capacity
- **Item Size**: DynamoDB has 400KB item size limit
- **Batch Operations**: Use batch operations for bulk reads/writes
