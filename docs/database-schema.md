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

**Access Patterns**:
- Get user by userId (Primary Key)
- Get user by email (EmailIndex GSI)
- List all users (Scan - for admin purposes)

### Future Tables (Planned)

#### Posts Table (`reddit-clone-posts`)

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

#### Comments Table (`reddit-clone-comments`)

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

#### Communities Table (`reddit-clone-communities`)

**Primary Key**: `communityId` (String)  
**Global Secondary Index**: `NameIndex` - Partition Key: `name` (String)

| Attribute | Type | Description |
|-----------|------|-------------|
| `communityId` | String | Unique community identifier |
| `name` | String | Community name (like subreddit name) |
| `displayName` | String | Display name for UI |
| `description` | String | Community description |
| `creatorId` | String | ID of user who created the community |
| `memberCount` | Number | Number of members |
| `postCount` | Number | Number of posts |
| `rules` | String | Community rules (JSON string) |
| `isPrivate` | Boolean | Whether community is private |
| `createdAt` | String | ISO timestamp of creation |
| `updatedAt` | String | ISO timestamp of last update |

#### Votes Table (`reddit-clone-votes`)

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
