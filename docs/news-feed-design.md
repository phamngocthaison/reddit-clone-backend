# News Feed System - Technical Design Document

## 📋 Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Database Design](#database-design)
4. [API Design](#api-design)
5. [Feed Generation Algorithm](#feed-generation-algorithm)
6. [Performance Considerations](#performance-considerations)
7. [Implementation Plan](#implementation-plan)
8. [Testing Strategy](#testing-strategy)
9. [Monitoring & Analytics](#monitoring--analytics)

---

## 🎯 Overview

### Purpose
News Feed System cung cấp personalized content feed cho users dựa trên:
- Subreddits mà user đã subscribe
- Users mà user đã follow
- Trending content và popular posts
- User behavior và preferences

### Key Requirements
- **Performance**: Feed generation < 200ms
- **Scalability**: Support 10,000+ concurrent users
- **Relevance**: 95% user satisfaction với feed content
- **Real-time**: Support real-time updates (Phase 3)

---

## 🏗️ System Architecture

### High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Mobile App    │    │   Web App       │    │   Admin Panel   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │      API Gateway          │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │      FeedsLambda          │
                    │  (Feed Generation & API)  │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │      DynamoDB             │
                    │  - user_feeds            │
                    │  - user_follows          │
                    │  - posts                 │
                    │  - subreddits            │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │      Redis Cache          │
                    │  (Optional - Phase 2)    │
                    └───────────────────────────┘
```

### Component Responsibilities

#### **FeedsLambda**
- Handle all feed-related API requests
- Generate personalized feeds
- Manage feed caching
- Handle real-time updates

#### **Database Layer**
- **DynamoDB**: Primary data storage
- **Redis**: Caching layer for hot data
- **GSI Indexes**: Optimize query performance

#### **External Dependencies**
- **SubredditsLambda**: Get user subscriptions
- **PostsLambda**: Get post data
- **UsersLambda**: Get user following data

---

## 🗄️ Database Design

### 1. User Feeds Table

#### **Table: `user_feeds`**
```sql
Primary Key: feedId (String)
Sort Key: createdAt (String)

Attributes:
├── feedId: String (PK) - "feed_{userId}_{timestamp}_{postId}"
├── userId: String (GSI) - User ID
├── postId: String - Post ID
├── subredditId: String - Subreddit ID
├── authorId: String - Post author ID
├── createdAt: String (SK) - Feed entry timestamp
├── postScore: Number - Post score for sorting
├── postType: String - "post" | "comment" | "announcement"
├── postTitle: String - Post title
├── postContent: String - Post content preview
├── postImageUrl: String - Post image URL
├── subredditName: String - Subreddit name
├── authorName: String - Author username
├── upvotes: Number - Post upvotes
├── downvotes: Number - Post downvotes
├── commentsCount: Number - Comments count
├── isPinned: Boolean - Is pinned post
├── isNSFW: Boolean - Is NSFW content
├── isSpoiler: Boolean - Is spoiler content
└── tags: List<String> - Post tags
```

#### **GSI Indexes:**
```sql
1. UserFeedIndex:
   - Partition Key: userId
   - Sort Key: createdAt
   - Purpose: Get user's feed chronologically

2. PostScoreIndex:
   - Partition Key: userId
   - Sort Key: postScore
   - Purpose: Get user's feed by score (hot, top)

3. SubredditFeedIndex:
   - Partition Key: subredditId
   - Sort Key: createdAt
   - Purpose: Get subreddit's recent posts

4. AuthorFeedIndex:
   - Partition Key: authorId
   - Sort Key: createdAt
   - Purpose: Get author's recent posts
```

### 2. User Follows Table

#### **Table: `user_follows`**
```sql
Primary Key: followId (String)
Sort Key: createdAt (String)

Attributes:
├── followId: String (PK) - "follow_{followerId}_{followingId}"
├── followerId: String (GSI) - User who follows
├── followingId: String (GSI) - User being followed
├── createdAt: String (SK) - Follow timestamp
├── isActive: Boolean - Is follow active
└── notificationSettings: Map - Notification preferences
```

#### **GSI Indexes:**
```sql
1. FollowerIndex:
   - Partition Key: followerId
   - Sort Key: createdAt
   - Purpose: Get users that a user follows

2. FollowingIndex:
   - Partition Key: followingId
   - Sort Key: createdAt
   - Purpose: Get followers of a user
```

### 3. Feed Cache Table (Optional)

#### **Table: `feed_cache`**
```sql
Primary Key: cacheKey (String)
Sort Key: createdAt (String)

Attributes:
├── cacheKey: String (PK) - "feed_{userId}_{sortType}_{page}"
├── userId: String (GSI) - User ID
├── sortType: String - "new" | "hot" | "top" | "trending"
├── page: Number - Page number
├── feedData: List<Map> - Cached feed items
├── createdAt: String (SK) - Cache timestamp
├── expiresAt: String - Cache expiration
└── lastUpdated: String - Last update timestamp
```

---

## 🔌 API Design

### 1. Get User Feed

#### **GET /feeds**
```http
GET /feeds?limit=20&offset=0&sort=new&includeNSFW=false

Headers:
- Authorization: Bearer <jwt_token>
- X-User-ID: <user_id>

Query Parameters:
- limit: Number (default: 20, max: 100)
- offset: Number (default: 0)
- sort: String (new|hot|top|trending)
- includeNSFW: Boolean (default: false)
- includeSpoilers: Boolean (default: false)
- subredditId: String (optional, filter by subreddit)
- authorId: String (optional, filter by author)

Response:
{
  "success": true,
  "data": {
    "feeds": [
      {
        "feedId": "feed_user123_2025-09-10T10:30:00Z_post456",
        "postId": "post456",
        "subredditId": "subreddit789",
        "authorId": "user456",
        "postTitle": "Amazing post title",
        "postContent": "Post content preview...",
        "postImageUrl": "https://example.com/image.jpg",
        "subredditName": "r/programming",
        "authorName": "john_doe",
        "upvotes": 150,
        "downvotes": 5,
        "commentsCount": 23,
        "isPinned": false,
        "isNSFW": false,
        "isSpoiler": false,
        "tags": ["programming", "javascript"],
        "createdAt": "2025-09-10T10:30:00Z",
        "postScore": 145
      }
    ],
    "pagination": {
      "limit": 20,
      "offset": 0,
      "total": 150,
      "hasMore": true,
      "nextOffset": 20
    },
    "metadata": {
      "generatedAt": "2025-09-10T10:35:00Z",
      "sortType": "new",
      "cacheHit": false
    }
  }
}
```

### 2. Refresh User Feed

#### **POST /feeds/refresh**
```http
POST /feeds/refresh

Headers:
- Authorization: Bearer <jwt_token>
- X-User-ID: <user_id>

Request Body:
{
  "reason": "subreddit_joined", // subreddit_joined|subreddit_left|user_followed|user_unfollowed|manual
  "subredditId": "subreddit789", // optional
  "userId": "user456" // optional
}

Response:
{
  "success": true,
  "data": {
    "message": "Feed refreshed successfully",
    "newItemsCount": 15,
    "refreshedAt": "2025-09-10T10:35:00Z"
  }
}
```

### 3. Get Feed Statistics

#### **GET /feeds/stats**
```http
GET /feeds/stats

Headers:
- Authorization: Bearer <jwt_token>
- X-User-ID: <user_id>

Response:
{
  "success": true,
  "data": {
    "totalSubscriptions": 25,
    "totalFollowing": 150,
    "feedItemsCount": 1250,
    "lastRefreshAt": "2025-09-10T10:30:00Z",
    "averageScore": 85.5,
    "topSubreddits": [
      {
        "subredditId": "subreddit789",
        "subredditName": "r/programming",
        "postCount": 45,
        "averageScore": 92.3
      }
    ],
    "topAuthors": [
      {
        "authorId": "user456",
        "authorName": "john_doe",
        "postCount": 12,
        "averageScore": 88.7
      }
    ]
  }
}
```

---

## 🧮 Feed Generation Algorithm

### 1. Basic Feed Generation

#### **Step 1: Collect Source Data**
```python
def generate_user_feed(user_id: str, sort_type: str, limit: int):
    # Get user subscriptions
    subscriptions = get_user_subscriptions(user_id)
    
    # Get user following
    following = get_user_following(user_id)
    
    # Collect posts from sources
    posts = []
    
    # From subscribed subreddits
    for subreddit_id in subscriptions:
        subreddit_posts = get_subreddit_posts(subreddit_id, limit=limit*2)
        posts.extend(subreddit_posts)
    
    # From followed users
    for author_id in following:
        user_posts = get_user_posts(author_id, limit=limit)
        posts.extend(user_posts)
    
    return posts
```

#### **Step 2: Apply Sorting Algorithm**
```python
def apply_sorting_algorithm(posts: List[Dict], sort_type: str):
    if sort_type == "new":
        return sorted(posts, key=lambda x: x['createdAt'], reverse=True)
    
    elif sort_type == "hot":
        return sorted(posts, key=lambda x: calculate_hot_score(x), reverse=True)
    
    elif sort_type == "top":
        return sorted(posts, key=lambda x: x['postScore'], reverse=True)
    
    elif sort_type == "trending":
        return sorted(posts, key=lambda x: calculate_trending_score(x), reverse=True)
    
    return posts

def calculate_hot_score(post: Dict) -> float:
    """Calculate hot score based on Reddit's algorithm"""
    score = post['upvotes'] - post['downvotes']
    age_hours = (datetime.now() - post['createdAt']).total_seconds() / 3600
    
    if age_hours < 1:
        return score * 2.0
    elif age_hours < 24:
        return score * 1.5
    else:
        return score * 1.0

def calculate_trending_score(post: Dict) -> float:
    """Calculate trending score based on recent activity"""
    recent_comments = get_recent_comments(post['postId'], hours=24)
    comment_velocity = len(recent_comments) / 24  # comments per hour
    
    return post['postScore'] * (1 + comment_velocity * 0.1)
```

#### **Step 3: Apply Filters**
```python
def apply_filters(posts: List[Dict], filters: Dict) -> List[Dict]:
    filtered_posts = posts
    
    # NSFW filter
    if not filters.get('includeNSFW', False):
        filtered_posts = [p for p in filtered_posts if not p.get('isNSFW', False)]
    
    # Spoiler filter
    if not filters.get('includeSpoilers', False):
        filtered_posts = [p for p in filtered_posts if not p.get('isSpoiler', False)]
    
    # Subreddit filter
    if filters.get('subredditId'):
        filtered_posts = [p for p in filtered_posts if p['subredditId'] == filters['subredditId']]
    
    # Author filter
    if filters.get('authorId'):
        filtered_posts = [p for p in filtered_posts if p['authorId'] == filters['authorId']]
    
    return filtered_posts
```

### 2. Advanced Feed Generation (Phase 3)

#### **Machine Learning Recommendations**
```python
def generate_ml_recommendations(user_id: str, limit: int) -> List[Dict]:
    # Get user behavior data
    user_behavior = get_user_behavior_data(user_id)
    
    # Get user preferences
    preferences = get_user_preferences(user_id)
    
    # Get candidate posts
    candidate_posts = get_candidate_posts(limit=limit*3)
    
    # Apply ML model
    recommendations = ml_model.predict(
        user_features=user_behavior,
        post_features=candidate_posts,
        preferences=preferences
    )
    
    return recommendations[:limit]
```

---

## ⚡ Performance Considerations

### 1. Caching Strategy

#### **Redis Cache Structure**
```redis
# User feed cache
feed:user:{userId}:{sortType}:{page} = {
  "data": [...],
  "expires_at": "2025-09-10T11:00:00Z",
  "generated_at": "2025-09-10T10:30:00Z"
}

# Subreddit posts cache
posts:subreddit:{subredditId}:{sortType} = {
  "data": [...],
  "expires_at": "2025-09-10T11:00:00Z"
}

# User subscriptions cache
subscriptions:user:{userId} = {
  "data": [...],
  "expires_at": "2025-09-10T11:00:00Z"
}
```

#### **Cache TTL Strategy**
- **User Feed**: 5 minutes
- **Subreddit Posts**: 2 minutes
- **User Subscriptions**: 10 minutes
- **User Following**: 10 minutes

### 2. Database Optimization

#### **Query Optimization**
```python
# Use GSI for efficient queries
def get_user_feed_optimized(user_id: str, sort_type: str, limit: int):
    if sort_type == "new":
        # Use UserFeedIndex with createdAt sort
        response = user_feeds_table.query(
            IndexName='UserFeedIndex',
            KeyConditionExpression='userId = :user_id',
            ExpressionAttributeValues={':user_id': user_id},
            ScanIndexForward=False,  # Descending order
            Limit=limit
        )
    elif sort_type == "hot":
        # Use PostScoreIndex with postScore sort
        response = user_feeds_table.query(
            IndexName='PostScoreIndex',
            KeyConditionExpression='userId = :user_id',
            ExpressionAttributeValues={':user_id': user_id},
            ScanIndexForward=False,  # Descending order
            Limit=limit
        )
    
    return response['Items']
```

#### **Batch Operations**
```python
def batch_generate_feeds(user_ids: List[str]):
    # Batch get user subscriptions
    subscriptions_batch = batch_get_user_subscriptions(user_ids)
    
    # Batch get subreddit posts
    subreddit_ids = set()
    for subs in subscriptions_batch.values():
        subreddit_ids.update(subs)
    
    posts_batch = batch_get_subreddit_posts(list(subreddit_ids))
    
    # Generate feeds in parallel
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(generate_user_feed, user_id, "new", 20): user_id
            for user_id in user_ids
        }
        
        results = {}
        for future in as_completed(futures):
            user_id = futures[future]
            results[user_id] = future.result()
    
    return results
```

### 3. Lambda Optimization

#### **Cold Start Mitigation**
```python
# Pre-warm Lambda with scheduled events
def pre_warm_lambda():
    # Trigger Lambda every 5 minutes
    # Keep Lambda warm for better performance
    pass

# Use provisioned concurrency for critical functions
# Set memory to 1024MB for better performance
# Use ARM64 architecture for cost optimization
```

---

## 🚀 Implementation Plan

### Phase 1: Basic Feed (Week 1-2)

#### **Week 1: Database & Models**
- [ ] Create `user_feeds` table
- [ ] Create `user_follows` table
- [ ] Set up GSI indexes
- [ ] Create Pydantic models
- [ ] Write database migration scripts

#### **Week 2: Basic API**
- [ ] Create `FeedsLambda` function
- [ ] Implement `GET /feeds` endpoint
- [ ] Implement basic feed generation
- [ ] Add pagination support
- [ ] Write unit tests

### Phase 2: Enhanced Features (Week 3-4)

#### **Week 3: Advanced Sorting**
- [ ] Implement "hot" algorithm
- [ ] Implement "top" sorting
- [ ] Add trending calculation
- [ ] Implement filters (NSFW, spoilers)
- [ ] Add feed statistics API

#### **Week 4: Performance & Caching**
- [ ] Add Redis caching
- [ ] Implement feed refresh API
- [ ] Optimize database queries
- [ ] Add background feed generation
- [ ] Performance testing

### Phase 3: Real-time Features (Week 5-6)

#### **Week 5: Real-time Updates**
- [ ] Add WebSocket support
- [ ] Implement real-time feed updates
- [ ] Add push notifications
- [ ] Live voting updates

#### **Week 6: ML Recommendations**
- [ ] Implement basic ML model
- [ ] Add user behavior tracking
- [ ] A/B testing framework
- [ ] Recommendation accuracy metrics

---

## 🧪 Testing Strategy

### 1. Unit Tests
```python
def test_feed_generation():
    # Test basic feed generation
    user_id = "user123"
    subscriptions = ["subreddit1", "subreddit2"]
    
    feed = generate_user_feed(user_id, "new", 20)
    
    assert len(feed) <= 20
    assert all(post['subredditId'] in subscriptions for post in feed)

def test_sorting_algorithms():
    posts = [
        {"postScore": 100, "createdAt": "2025-09-10T10:00:00Z"},
        {"postScore": 200, "createdAt": "2025-09-10T09:00:00Z"},
        {"postScore": 50, "createdAt": "2025-09-10T11:00:00Z"}
    ]
    
    # Test new sorting
    new_sorted = apply_sorting_algorithm(posts, "new")
    assert new_sorted[0]["createdAt"] == "2025-09-10T11:00:00Z"
    
    # Test top sorting
    top_sorted = apply_sorting_algorithm(posts, "top")
    assert top_sorted[0]["postScore"] == 200
```

### 2. Integration Tests
```python
def test_feed_api_integration():
    # Test complete API flow
    response = client.get("/feeds?sort=new&limit=10")
    
    assert response.status_code == 200
    assert "feeds" in response.json()["data"]
    assert len(response.json()["data"]["feeds"]) <= 10

def test_feed_refresh():
    # Test feed refresh functionality
    response = client.post("/feeds/refresh", json={"reason": "manual"})
    
    assert response.status_code == 200
    assert "newItemsCount" in response.json()["data"]
```

### 3. Load Testing
```python
def test_feed_performance():
    # Test with 1000 concurrent users
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [
            executor.submit(get_user_feed, f"user{i}", "new", 20)
            for i in range(1000)
        ]
        
        results = [future.result() for future in futures]
        
        # Assert all requests completed successfully
        assert all(result["success"] for result in results)
        
        # Assert response time < 200ms
        assert all(result["response_time"] < 200 for result in results)
```

---

## 📊 Monitoring & Analytics

### 1. Key Metrics

#### **Performance Metrics**
- Feed generation time (target: < 200ms)
- API response time (target: < 500ms)
- Cache hit rate (target: > 80%)
- Database query time (target: < 100ms)

#### **Business Metrics**
- Daily active users
- Feed engagement rate
- User retention rate
- Content diversity score

#### **Error Metrics**
- API error rate (target: < 1%)
- Lambda timeout rate (target: < 0.1%)
- Database error rate (target: < 0.1%)

### 2. CloudWatch Dashboards

#### **Feed Performance Dashboard**
```yaml
Widgets:
  - Feed Generation Time
  - API Response Time
  - Cache Hit Rate
  - Database Query Time
  - Error Rate
  - Active Users
```

#### **Business Metrics Dashboard**
```yaml
Widgets:
  - Daily Active Users
  - Feed Engagement Rate
  - User Retention Rate
  - Content Diversity Score
  - Top Subreddits
  - Top Authors
```

### 3. Alerting

#### **Critical Alerts**
- Feed generation time > 500ms
- API error rate > 5%
- Database connection errors
- Lambda timeout rate > 1%

#### **Warning Alerts**
- Cache hit rate < 70%
- Database query time > 200ms
- High memory usage > 80%

---

## 🔒 Security Considerations

### 1. Data Privacy
- User feed data is private to each user
- No cross-user data leakage
- Secure API authentication
- Data encryption at rest

### 2. Rate Limiting
- API rate limits per user
- Feed refresh rate limits
- Database query rate limits
- Cache access rate limits

### 3. Content Filtering
- NSFW content filtering
- Spam detection
- Inappropriate content flagging
- User-reported content moderation

---

## 📈 Future Enhancements

### Phase 4: Advanced Features
- **Machine Learning**: Personalized recommendations
- **Real-time**: WebSocket live updates
- **Social**: User following and social features
- **Analytics**: Advanced user behavior analytics

### Phase 5: Enterprise Features
- **Admin Panel**: Feed management tools
- **A/B Testing**: Feed algorithm testing
- **Monetization**: Ad integration
- **Scalability**: Multi-region deployment

---

*Last Updated: September 10, 2025*
*Version: 1.0.0*
*Author: Development Team*
