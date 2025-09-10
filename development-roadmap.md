# Reddit Clone Backend - Development Roadmap

## 📋 Overview

This document outlines the complete development roadmap for building a Reddit-like forum backend, organized into phases with detailed technical specifications, API endpoints, database schemas, and implementation priorities.

## 🎯 Current Status

**Phase 1: Authentication System** ✅ **COMPLETED**
- User registration and login
- JWT token management
- Password reset functionality
- Cognito User Pool integration
- DynamoDB user storage
- API Gateway with CORS

**Phase 2: Posts System** ✅ **COMPLETED**
- Posts CRUD operations
- Post types (text, link, image, video, poll)
- Voting system
- Filtering and sorting
- Pagination
- DynamoDB posts table with GSIs
- API Gateway posts endpoints

**Phase 3: Comments System** ✅ **COMPLETED**
- Comments CRUD operations
- Nested replies system
- Comment threading and sorting
- GSI optimization for better performance
- Fixed filter expressions for missing fields
- Enhanced API endpoints for better organization

**Next Phase: Search & Discovery** 🚧 **IN PROGRESS**

---

## 🏗️ Phase 2: Posts System (Core Features) ✅ **COMPLETED**

### 📊 **2.1 Posts Management** ✅ **COMPLETED**

#### API Endpoints
```http
POST   /posts/create              # Tạo post mới
GET    /posts/{post_id}           # Lấy chi tiết post
PUT    /posts/{post_id}           # Sửa post
DELETE /posts/{post_id}           # Xóa post
GET    /posts/feed                # Lấy feed posts
GET    /posts/hot                 # Posts hot nhất
GET    /posts/new                 # Posts mới nhất
GET    /posts/top                 # Posts top
GET    /posts/controversial       # Posts controversial
GET    /posts/rising              # Posts đang lên
```

#### Database Schema
```python
# DynamoDB Table: reddit-posts
posts_table = {
    "postId": "post_1234567890",
    "title": "Reddit Clone Backend Development Guide",
    "content": "This is a detailed post content...",
    "authorId": "user_1234567890",
    "subredditId": "subreddit_4567890",
    "type": "text|link|image|video|poll",
    "url": "https://example.com",
    "mediaUrls": ["https://s3.../image1.jpg"],
    "score": 150,
    "upvotes": 200,
    "downvotes": 50,
    "commentCount": 25,
    "viewCount": 1000,
    "createdAt": "2025-01-09T10:00:00Z",
    "updatedAt": "2025-01-09T10:00:00Z",
    "isDeleted": False,
    "isLocked": False,
    "isSticky": False,
    "isNSFW": False,
    "isSpoiler": False,
    "tags": ["programming", "backend", "aws"],
    "flair": "Discussion",
    "awards": ["gold", "silver"],
    "gilding": 5
}
```

#### Implementation Priority
1. **Week 1**: Basic CRUD operations for posts
2. **Week 2**: Feed algorithms (hot, new, top)
3. **Week 3**: Post types (text, link, image, video)
4. **Week 4**: Advanced features (sticky, lock, NSFW)

---

### 🏘️ **2.2 Subreddit System (Communities)** ✅ **COMPLETED**

#### API Endpoints
```http
POST   /subreddits/create         # Tạo subreddit
GET    /subreddits/{id}           # Lấy thông tin subreddit
PUT    /subreddits/{id}           # Cập nhật subreddit
DELETE /subreddits/{id}           # Xóa subreddit
GET    /subreddits/popular        # Subreddits phổ biến
GET    /subreddits/new            # Subreddits mới
GET    /subreddits/search         # Tìm kiếm subreddits
POST   /subreddits/{id}/join      # Join subreddit
POST   /subreddits/{id}/leave     # Leave subreddit
GET    /subreddits/{id}/posts     # Lấy posts của subreddit
GET    /subreddits/{id}/moderators # Lấy danh sách moderators
```

#### Database Schema
```python
# DynamoDB Table: reddit-subreddits
subreddits_table = {
    "subredditId": "subreddit_4567890",
    "name": "programming",
    "displayName": "Programming",
    "description": "Discussion about programming languages, frameworks, and best practices",
    "rules": [
        "Be respectful and civil",
        "No spam or self-promotion",
        "Use descriptive titles"
    ],
    "ownerId": "user_1234567890",
    "moderators": ["user_4567890", "user_7890123"],
    "subscriberCount": 50000,
    "postCount": 1200,
    "createdAt": "2025-01-01T00:00:00Z",
    "updatedAt": "2025-01-09T10:00:00Z",
    "isPrivate": False,
    "isNSFW": False,
    "isRestricted": False,
    "bannerImage": "https://s3.../banner.jpg",
    "iconImage": "https://s3.../icon.jpg",
    "primaryColor": "#FF4500",
    "secondaryColor": "#FFFFFF",
    "language": "en",
    "country": "US"
}

# DynamoDB Table: reddit-subscriptions
subscriptions_table = {
    "subscriptionId": "sub_1234567890",
    "userId": "user_1234567890",
    "subredditId": "subreddit_4567890",
    "role": "subscriber|moderator|owner",
    "joinedAt": "2025-01-05T15:30:00Z",
    "isActive": True
}
```

#### Implementation Priority
1. **Week 1**: Basic subreddit CRUD operations
2. **Week 2**: Subscription system
3. **Week 3**: Moderation tools
4. **Week 4**: Customization features

---

### 💬 **2.3 Comment System** ✅ **COMPLETED**

#### API Endpoints
```http
POST   /comments/create                 # Tạo comment mới
GET    /comments                        # Lấy tất cả comments (với filters)
GET    /posts/{post_id}/comments        # Lấy comments của post cụ thể
GET    /comments/{comment_id}           # Lấy chi tiết comment
PUT    /comments/{comment_id}           # Sửa comment
DELETE /comments/{comment_id}           # Xóa comment
POST   /comments/{comment_id}/vote      # Vote comment
```

#### Key Improvements (v2.3.0)
- **GSI Optimization**: Sử dụng PostIndex GSI thay vì scan operations
- **Enhanced Filtering**: Xử lý đúng các trường hợp field không tồn tại
- **Better Performance**: Query nhanh hơn với GSI
- **Improved Error Handling**: Xử lý null values trong DynamoDB

#### Database Schema
```python
# DynamoDB Table: reddit-comments
comments_table = {
    "commentId": "comment_7890123456",
    "postId": "post_1234567890",
    "parentId": None,  # None for top-level, commentId for replies
    "authorId": "user_1234567890",
    "content": "Great post! I agree with this approach. Here's my take...",
    "score": 25,
    "upvotes": 30,
    "downvotes": 5,
    "replyCount": 3,
    "createdAt": "2025-01-09T11:00:00Z",
    "updatedAt": "2025-01-09T11:00:00Z",
    "isDeleted": False,
    "isEdited": False,
    "depth": 0,  # 0 for top-level, 1+ for nested replies
    "path": "comment_7890123456",  # For hierarchical queries
    "awards": ["helpful"],
    "isSticky": False,
    "isLocked": False
}
```

#### Implementation Priority
1. **Week 1**: Basic comment CRUD operations
2. **Week 2**: Nested replies system
3. **Week 3**: Comment threading and sorting
4. **Week 4**: Advanced comment features

---

### 👍 **2.4 Voting System** ✅ **COMPLETED**

#### API Endpoints
```http
POST   /posts/{post_id}/vote            # Vote post
POST   /comments/{comment_id}/vote      # Vote comment
GET    /users/{user_id}/votes           # Lấy votes của user
DELETE /posts/{post_id}/vote            # Bỏ vote post
DELETE /comments/{comment_id}/vote      # Bỏ vote comment
```

#### Database Schema
```python
# DynamoDB Table: reddit-votes
votes_table = {
    "voteId": "vote_1011121314",
    "userId": "user_1234567890",
    "targetType": "post|comment",
    "targetId": "post_1234567890",
    "voteType": "upvote|downvote",
    "createdAt": "2025-01-09T12:00:00Z",
    "updatedAt": "2025-01-09T12:00:00Z"
}

# GSI: userId-targetType-index
# GSI: targetId-voteType-index
```

#### Implementation Priority
1. **Week 1**: Basic voting functionality
2. **Week 2**: Vote aggregation and scoring
3. **Week 3**: Vote history and analytics
4. **Week 4**: Advanced voting features

---

## 🔍 Phase 3: Search & Discovery

### **3.1 Search Functionality**

#### API Endpoints
```http
GET    /search/posts?q=query&sort=hot&time=day&subreddit=programming
GET    /search/comments?q=query&sort=top&author=username
GET    /search/subreddits?q=query&sort=subscribers
GET    /search/users?q=query&sort=relevance
GET    /search/suggestions?q=partial_query
```

#### Implementation Options
1. **Elasticsearch/OpenSearch** (Recommended)
   - Full-text search capabilities
   - Advanced filtering and sorting
   - Real-time indexing
   - Faceted search

2. **DynamoDB Global Secondary Indexes**
   - Basic search functionality
   - Cost-effective for small scale
   - Limited search capabilities

3. **Algolia** (Search-as-a-Service)
   - Easy integration
   - Advanced search features
   - Real-time search analytics

#### Implementation Priority
1. **Week 1**: Basic search with DynamoDB GSI
2. **Week 2**: Elasticsearch integration
3. **Week 3**: Advanced search features
4. **Week 4**: Search analytics and optimization

---

### **3.2 Recommendation System**

#### API Endpoints
```http
GET    /recommendations/posts           # Recommended posts
GET    /recommendations/subreddits      # Recommended subreddits
GET    /recommendations/users           # Recommended users to follow
```

#### Implementation Priority
1. **Week 1**: Basic recommendation algorithms
2. **Week 2**: Machine learning integration
3. **Week 3**: Personalization features
4. **Week 4**: A/B testing and optimization

---

## 🔔 Phase 4: Notifications & Communication

### **4.1 Notification System**

#### API Endpoints
```http
GET    /notifications                   # Lấy notifications
PUT    /notifications/{id}/read         # Đánh dấu đã đọc
POST   /notifications/mark-all-read     # Đánh dấu tất cả đã đọc
GET    /notifications/unread-count      # Số lượng chưa đọc
PUT    /notifications/settings          # Cài đặt notifications
```

#### Database Schema
```python
# DynamoDB Table: reddit-notifications
notifications_table = {
    "notificationId": "notif_1314151617",
    "userId": "user_1234567890",
    "type": "post_reply|comment_reply|post_upvote|comment_upvote|subreddit_join|award_received",
    "title": "New reply to your post",
    "message": "user_4567890 replied to your post 'Reddit Clone Backend'",
    "relatedId": "comment_7890123456",
    "relatedType": "comment",
    "isRead": False,
    "createdAt": "2025-01-09T13:00:00Z",
    "readAt": None,
    "priority": "low|medium|high",
    "actionUrl": "/posts/1234567890#comment_7890123456"
}
```

#### Implementation Priority
1. **Week 1**: Basic notification system
2. **Week 2**: Real-time notifications with WebSocket
3. **Week 3**: Email notifications
4. **Week 4**: Push notifications

---

### **4.2 Direct Messaging**

#### API Endpoints
```http
POST   /messages/send                   # Gửi tin nhắn
GET    /messages                        # Lấy danh sách tin nhắn
GET    /messages/{conversation_id}      # Lấy tin nhắn trong cuộc trò chuyện
PUT    /messages/{message_id}/read      # Đánh dấu đã đọc
DELETE /messages/{message_id}           # Xóa tin nhắn
```

#### Implementation Priority
1. **Week 1**: Basic messaging system
2. **Week 2**: Real-time messaging
3. **Week 3**: File sharing in messages
4. **Week 4**: Message encryption

---

## 👮 Phase 5: Moderation & Administration

### **5.1 Moderation Tools**

#### API Endpoints
```http
POST   /moderation/ban-user             # Ban user
POST   /moderation/remove-post          # Xóa post
POST   /moderation/remove-comment       # Xóa comment
POST   /moderation/approve-post         # Duyệt post
GET    /moderation/reports              # Lấy reports
POST   /moderation/report               # Báo cáo content
POST   /moderation/mute-user            # Mute user
POST   /moderation/distinguish          # Distinguish comment/post
```

#### Database Schema
```python
# DynamoDB Table: reddit-reports
reports_table = {
    "reportId": "report_1819202122",
    "reporterId": "user_1234567890",
    "targetType": "post|comment|user",
    "targetId": "post_1234567890",
    "reason": "spam|harassment|hate_speech|violence|misinformation",
    "description": "This post contains spam content",
    "status": "pending|approved|rejected",
    "moderatorId": "user_4567890",
    "actionTaken": "removed|approved|no_action",
    "createdAt": "2025-01-09T14:00:00Z",
    "resolvedAt": "2025-01-09T15:00:00Z"
}

# DynamoDB Table: reddit-bans
bans_table = {
    "banId": "ban_2324252627",
    "userId": "user_1234567890",
    "subredditId": "subreddit_4567890",
    "moderatorId": "user_4567890",
    "reason": "Violation of community rules",
    "banType": "temporary|permanent",
    "duration": 7,  # days for temporary bans
    "createdAt": "2025-01-09T16:00:00Z",
    "expiresAt": "2025-01-16T16:00:00Z",
    "isActive": True
}
```

#### Implementation Priority
1. **Week 1**: Basic moderation tools
2. **Week 2**: Reporting system
3. **Week 3**: Automated moderation
4. **Week 4**: Advanced moderation features

---

### **5.2 Admin Panel**

#### API Endpoints
```http
GET    /admin/stats                     # Thống kê tổng quan
GET    /admin/users                     # Quản lý users
GET    /admin/subreddits                # Quản lý subreddits
GET    /admin/reports                   # Quản lý reports
POST   /admin/announcements             # Tạo thông báo
GET    /admin/logs                      # Xem logs hệ thống
```

#### Implementation Priority
1. **Week 1**: Basic admin dashboard
2. **Week 2**: User management
3. **Week 3**: System monitoring
4. **Week 4**: Advanced admin features

---

## 📊 Phase 6: Analytics & Monitoring

### **6.1 Analytics Dashboard**

#### API Endpoints
```http
GET    /analytics/posts/trending        # Posts trending
GET    /analytics/subreddits/popular    # Subreddits phổ biến
GET    /analytics/users/active          # Users hoạt động
GET    /analytics/engagement            # Engagement metrics
GET    /analytics/revenue               # Revenue analytics
```

#### Implementation Priority
1. **Week 1**: Basic analytics
2. **Week 2**: Advanced metrics
3. **Week 3**: Real-time analytics
4. **Week 4**: Predictive analytics

---

### **6.2 System Monitoring**

#### Implementation Priority
1. **Week 1**: Basic monitoring with CloudWatch
2. **Week 2**: Application performance monitoring
3. **Week 3**: Error tracking and alerting
4. **Week 4**: Advanced monitoring features

---

## 🗂️ Database Architecture

### **DynamoDB Tables Required**

```python
# Core Tables
tables = [
    "reddit-users",              # User accounts (Phase 1 ✅)
    "reddit-posts",              # Posts content
    "reddit-subreddits",         # Communities
    "reddit-comments",           # Comments and replies
    "reddit-votes",              # Upvotes/downvotes
    "reddit-notifications",      # User notifications
    "reddit-reports",            # Content reports
    "reddit-subscriptions",      # User subscriptions
    "reddit-moderators",         # Moderator relationships
    "reddit-flairs",             # User/post flairs
    "reddit-awards",             # Awards system
    "reddit-messages",           # Direct messages
    "reddit-saved",              # Saved posts/comments
    "reddit-hidden",             # Hidden posts
    "reddit-blocked",            # Blocked users
    "reddit-bans",               # User bans
    "reddit-mutes",              # User mutes
    "reddit-follows",            # User follows
    "reddit-bookmarks",          # Bookmarked content
    "reddit-history",            # User activity history
    "reddit-sessions",           # User sessions
    "reddit-api-keys",           # API access keys
    "reddit-webhooks",           # Webhook configurations
    "reddit-audit-logs",         # System audit logs
]
```

### **Global Secondary Indexes**

```python
# GSI Patterns for each table
gsi_patterns = {
    "reddit-posts": [
        "subredditId-createdAt-index",      # Posts by subreddit
        "authorId-createdAt-index",         # Posts by author
        "score-createdAt-index",            # Top posts
        "type-createdAt-index",             # Posts by type
        "isSticky-createdAt-index",         # Sticky posts
    ],
    "reddit-comments": [
        "postId-createdAt-index",           # Comments by post
        "authorId-createdAt-index",         # Comments by author
        "parentId-createdAt-index",         # Comment replies
        "score-createdAt-index",            # Top comments
    ],
    "reddit-votes": [
        "userId-targetType-index",          # Votes by user
        "targetId-voteType-index",          # Votes by target
        "userId-createdAt-index",           # Vote history
    ],
    "reddit-notifications": [
        "userId-isRead-index",              # Notifications by user
        "userId-createdAt-index",           # Notification history
        "type-createdAt-index",             # Notifications by type
    ]
}
```

---

## ☁️ Infrastructure Requirements

### **AWS Services Needed**

```python
# Core Services (Phase 1 ✅)
core_services = [
    "Lambda Functions",           # Serverless compute
    "API Gateway",               # API management
    "DynamoDB",                  # NoSQL database
    "Cognito",                   # User authentication
    "CloudWatch",                # Monitoring
    "X-Ray",                     # Tracing
]

# Additional Services (Phases 2-6)
additional_services = [
    "S3 Bucket",                 # File storage
    "CloudFront",                # CDN
    "Elasticsearch/OpenSearch",  # Search engine
    "SNS",                       # Push notifications
    "SES",                       # Email notifications
    "SQS",                       # Message queuing
    "EventBridge",               # Event processing
    "Step Functions",            # Workflow orchestration
    "Secrets Manager",           # Secret management
    "Parameter Store",           # Configuration management
    "KMS",                       # Encryption
    "WAF",                       # Web application firewall
    "Shield",                    # DDoS protection
    "Route 53",                  # DNS management
    "Certificate Manager",       # SSL certificates
    "Config",                    # Configuration compliance
    "CloudTrail",                # API logging
    "GuardDuty",                 # Threat detection
    "Macie",                     # Data security
    "Inspector",                 # Security assessment
    "Trusted Advisor",           # Cost optimization
    "Cost Explorer",             # Cost analysis
    "Billing",                   # Billing management
]
```

### **Lambda Functions Architecture**

```python
# Microservices Lambda Functions
lambda_functions = [
    "auth-service",              # Authentication (Phase 1 ✅)
    "posts-service",             # Posts management
    "subreddits-service",        # Subreddit management
    "comments-service",          # Comment system
    "votes-service",             # Voting system
    "search-service",            # Search functionality
    "notifications-service",     # Notification system
    "moderation-service",        # Moderation tools
    "analytics-service",         # Analytics and metrics
    "media-service",             # File upload/processing
    "email-service",             # Email notifications
    "websocket-service",         # Real-time communication
    "scheduler-service",         # Scheduled tasks
    "cleanup-service",           # Data cleanup
    "backup-service",            # Data backup
    "migration-service",         # Data migration
    "api-gateway-service",       # API Gateway integration
    "webhook-service",           # Webhook handling
    "audit-service",             # Audit logging
    "monitoring-service",        # System monitoring
]
```

---

## 📅 Implementation Timeline

### **Phase 2: Posts System (4 weeks)** ✅ **COMPLETED**
- **Week 1**: Posts CRUD operations
- **Week 2**: Subreddit system
- **Week 3**: Comment system
- **Week 4**: Voting system

### **Phase 3: Comments System (2 weeks)** ✅ **COMPLETED**
- **Week 1**: Basic comment CRUD operations
- **Week 2**: GSI optimization and performance improvements

### **Phase 4: Search & Discovery (4 weeks)**
- **Week 1**: Basic search functionality
- **Week 2**: Elasticsearch integration
- **Week 3**: Advanced search features
- **Week 4**: Recommendation system

### **Phase 4: Notifications & Communication (4 weeks)**
- **Week 1**: Notification system
- **Week 2**: Real-time notifications
- **Week 3**: Direct messaging
- **Week 4**: Email and push notifications

### **Phase 5: Moderation & Administration (4 weeks)**
- **Week 1**: Basic moderation tools
- **Week 2**: Reporting system
- **Week 3**: Admin panel
- **Week 4**: Advanced moderation features

### **Phase 6: Analytics & Monitoring (4 weeks)**
- **Week 1**: Basic analytics
- **Week 2**: Advanced metrics
- **Week 3**: System monitoring
- **Week 4**: Performance optimization

---

## 🎯 Success Metrics

### **Technical Metrics**
- **API Response Time**: < 200ms for 95% of requests
- **Uptime**: 99.9% availability
- **Error Rate**: < 0.1% error rate
- **Concurrent Users**: Support 10,000+ concurrent users
- **Database Performance**: < 100ms query response time

### **Business Metrics**
- **User Engagement**: Daily active users, session duration
- **Content Quality**: Post/comment quality scores
- **Community Growth**: Subreddit creation and growth rates
- **User Retention**: Monthly active user retention
- **Revenue**: If monetization is implemented

---

## 🚀 Next Steps

1. **Immediate**: Start Phase 4 - Search & Discovery
2. **Week 1**: Implement basic search functionality with DynamoDB GSI
3. **Week 2**: Integrate Elasticsearch for advanced search
4. **Week 3**: Add recommendation system
5. **Week 4**: Implement search analytics and optimization

**Ready to begin Phase 4 implementation!** 🎉

---

*Last Updated: 2025-09-10*  
*Version: 2.3*  
*Status: Phase 3 Complete - Ready for Phase 4 Implementation*
