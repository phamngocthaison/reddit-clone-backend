# Reddit Clone - Architecture Diagrams

## 🏗️ High-Level System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Browser<br/>React.js + TypeScript]
        MOBILE[Mobile App<br/>React Native - Future]
    end
    
    subgraph "CDN & Load Balancing"
        CF[CloudFront CDN<br/>Global Distribution]
        ALB[Application Load Balancer<br/>Traffic Distribution]
    end
    
    subgraph "API Gateway Layer"
        APIGW[API Gateway<br/>REST API Endpoints<br/>Rate Limiting & CORS]
    end
    
    subgraph "Authentication Layer"
        COGNITO[AWS Cognito<br/>User Pool<br/>JWT Token Management]
    end
    
    subgraph "Compute Layer - Lambda Functions"
        AUTH[Auth Lambda<br/>User Management<br/>Authentication]
        POSTS[Posts Lambda<br/>Post CRUD<br/>Voting System]
        COMMENTS[Comments Lambda<br/>Comment Management<br/>Nested Comments]
        SUBREDDITS[Subreddits Lambda<br/>Community Management<br/>Moderation]
        PROFILES[User Profile Lambda<br/>Profile Management<br/>User Stats]
        FEEDS[Feeds Lambda<br/>News Feed<br/>Personalization]
    end
    
    subgraph "Data Layer - DynamoDB"
        USERS_TABLE[(Users Table<br/>User Profiles<br/>Authentication Data)]
        POSTS_TABLE[(Posts Table<br/>Content Storage<br/>Voting Data)]
        COMMENTS_TABLE[(Comments Table<br/>Comment Threads<br/>Reply Chains)]
        SUBREDDITS_TABLE[(Subreddits Table<br/>Community Data<br/>Moderation Info)]
        SUBSCRIPTIONS_TABLE[(Subscriptions Table<br/>User Memberships<br/>Community Relations)]
        FEEDS_TABLE[(User Feeds Table<br/>Personalized Content<br/>Feed Generation)]
    end
    
    subgraph "Storage Layer"
        S3[S3 Bucket<br/>Media Files<br/>Static Assets]
    end
    
    subgraph "Monitoring & Logging"
        CW[CloudWatch<br/>Logs & Metrics<br/>Performance Monitoring]
        XRAY[X-Ray<br/>Distributed Tracing<br/>Request Flow Analysis]
    end
    
    subgraph "Security & IAM"
        IAM[IAM Roles<br/>Permissions<br/>Service Access]
        WAF[WAF<br/>DDoS Protection<br/>Security Rules]
    end
    
    %% Client to CDN
    WEB --> CF
    MOBILE --> CF
    
    %% CDN to Load Balancer
    CF --> ALB
    
    %% Load Balancer to API Gateway
    ALB --> APIGW
    
    %% API Gateway to Lambda Functions
    APIGW --> AUTH
    APIGW --> POSTS
    APIGW --> COMMENTS
    APIGW --> SUBREDDITS
    APIGW --> PROFILES
    APIGW --> FEEDS
    
    %% Authentication Flow
    AUTH --> COGNITO
    COGNITO --> USERS_TABLE
    
    %% Lambda to Database
    AUTH --> USERS_TABLE
    POSTS --> POSTS_TABLE
    POSTS --> SUBREDDITS_TABLE
    COMMENTS --> COMMENTS_TABLE
    COMMENTS --> POSTS_TABLE
    SUBREDDITS --> SUBREDDITS_TABLE
    SUBREDDITS --> SUBSCRIPTIONS_TABLE
    PROFILES --> USERS_TABLE
    PROFILES --> POSTS_TABLE
    PROFILES --> COMMENTS_TABLE
    FEEDS --> FEEDS_TABLE
    FEEDS --> POSTS_TABLE
    FEEDS --> SUBSCRIPTIONS_TABLE
    
    %% Storage Access
    POSTS --> S3
    COMMENTS --> S3
    SUBREDDITS --> S3
    
    %% Monitoring
    AUTH --> CW
    POSTS --> CW
    COMMENTS --> CW
    SUBREDDITS --> CW
    PROFILES --> CW
    FEEDS --> CW
    
    %% Security
    WAF --> APIGW
    IAM --> AUTH
    IAM --> POSTS
    IAM --> COMMENTS
    IAM --> SUBREDDITS
    IAM --> PROFILES
    IAM --> FEEDS
    
    %% Styling
    classDef clientStyle fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef cdnStyle fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef apiStyle fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef authStyle fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef lambdaStyle fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef dbStyle fill:#e0f2f1,stroke:#004d40,stroke-width:2px
    classDef storageStyle fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    classDef monitorStyle fill:#fff8e1,stroke:#f57f17,stroke-width:2px
    classDef securityStyle fill:#ffebee,stroke:#c62828,stroke-width:2px
    
    class WEB,MOBILE clientStyle
    class CF,ALB cdnStyle
    class APIGW apiStyle
    class COGNITO authStyle
    class AUTH,POSTS,COMMENTS,SUBREDDITS,PROFILES,FEEDS lambdaStyle
    class USERS_TABLE,POSTS_TABLE,COMMENTS_TABLE,SUBREDDITS_TABLE,SUBSCRIPTIONS_TABLE,FEEDS_TABLE dbStyle
    class S3 storageStyle
    class CW,XRAY monitorStyle
    class IAM,WAF securityStyle
```

## 🔄 Data Flow Architecture

```mermaid
sequenceDiagram
    participant U as User
    participant CF as CloudFront
    participant AG as API Gateway
    participant AUTH as Auth Lambda
    participant POSTS as Posts Lambda
    participant DB as DynamoDB
    participant S3 as S3 Storage
    participant COG as Cognito
    
    Note over U,S3: User Authentication Flow
    U->>CF: Login Request
    CF->>AG: Forward Request
    AG->>AUTH: Route to Auth Lambda
    AUTH->>COG: Validate Credentials
    COG-->>AUTH: JWT Token
    AUTH->>DB: Store User Session
    AUTH-->>AG: Auth Response
    AG-->>CF: Return Token
    CF-->>U: Login Success + Token
    
    Note over U,S3: Post Creation Flow
    U->>CF: Create Post Request
    CF->>AG: Forward with Auth Header
    AG->>AUTH: Validate Token
    AUTH-->>AG: Token Valid
    AG->>POSTS: Route to Posts Lambda
    POSTS->>DB: Store Post Data
    POSTS->>S3: Upload Media Files
    POSTS->>DB: Update Post with Media URLs
    POSTS-->>AG: Post Created Response
    AG-->>CF: Return Success
    CF-->>U: Post Created Successfully
    
    Note over U,S3: Feed Generation Flow
    U->>CF: Get Feed Request
    CF->>AG: Forward Request
    AG->>POSTS: Route to Posts Lambda
    POSTS->>DB: Query User Subscriptions
    POSTS->>DB: Fetch Posts from Subscribed Subreddits
    POSTS->>DB: Get Post Metadata (votes, comments)
    POSTS-->>AG: Feed Data
    AG-->>CF: Return Feed
    CF-->>U: Display Feed
```

## 🗄️ Database Schema Architecture

```mermaid
erDiagram
    USERS {
        string user_id PK
        string username UK
        string email UK
        string display_name
        string bio
        string avatar
        boolean is_public
        datetime created_at
        datetime updated_at
    }
    
    POSTS {
        string post_id PK
        string title
        string content
        string author_id FK
        string subreddit_id FK
        string post_type
        string url
        array media_urls
        int score
        int upvotes
        int downvotes
        int comment_count
        int view_count
        boolean is_nsfw
        boolean is_spoiler
        string flair
        array tags
        datetime created_at
        datetime updated_at
    }
    
    COMMENTS {
        string comment_id PK
        string content
        string author_id FK
        string post_id FK
        string parent_comment_id FK
        string comment_type
        int score
        int upvotes
        int downvotes
        boolean is_nsfw
        boolean is_spoiler
        string flair
        array tags
        datetime created_at
        datetime updated_at
    }
    
    SUBREDDITS {
        string subreddit_id PK
        string name UK
        string display_name
        string description
        array rules
        string owner_id FK
        array moderators
        int subscriber_count
        int post_count
        string primary_color
        string secondary_color
        string icon
        string banner
        boolean is_private
        boolean is_nsfw
        boolean is_restricted
        string language
        string country
        datetime created_at
        datetime updated_at
    }
    
    SUBSCRIPTIONS {
        string subscription_id PK
        string user_id FK
        string subreddit_id FK
        datetime subscribed_at
    }
    
    USER_FEEDS {
        string feed_id PK
        string user_id FK
        string post_id FK
        int score
        datetime created_at
    }
    
    %% Relationships
    USERS ||--o{ POSTS : "creates"
    USERS ||--o{ COMMENTS : "writes"
    USERS ||--o{ SUBREDDITS : "owns"
    USERS ||--o{ SUBSCRIPTIONS : "subscribes"
    USERS ||--o{ USER_FEEDS : "has"
    
    SUBREDDITS ||--o{ POSTS : "contains"
    SUBREDDITS ||--o{ SUBSCRIPTIONS : "has"
    
    POSTS ||--o{ COMMENTS : "has"
    POSTS ||--o{ USER_FEEDS : "appears_in"
    
    COMMENTS ||--o{ COMMENTS : "replies_to"
```

## 🔐 Security Architecture

```mermaid
graph TB
    subgraph "External Threats"
        DDOS[DDoS Attacks]
        BOT[Bot Traffic]
        INJ[Injection Attacks]
        XSS[XSS Attacks]
    end
    
    subgraph "Security Layers"
        WAF[WAF<br/>Web Application Firewall<br/>• DDoS Protection<br/>• Bot Detection<br/>• Rate Limiting]
        CORS[CORS Policy<br/>Cross-Origin Resource Sharing<br/>• Allowed Origins<br/>• Allowed Methods<br/>• Allowed Headers]
        AUTH[Authentication<br/>AWS Cognito<br/>• JWT Tokens<br/>• Password Policy<br/>• MFA Support]
        IAM[IAM Roles<br/>Identity & Access Management<br/>• Least Privilege<br/>• Service Permissions<br/>• Resource Access]
    end
    
    subgraph "Data Protection"
        ENCRYPT[Encryption<br/>• Data at Rest (DynamoDB)<br/>• Data in Transit (HTTPS)<br/>• Key Management (KMS)]
        VALID[Input Validation<br/>• Pydantic Models<br/>• Data Sanitization<br/>• SQL Injection Prevention]
        LOG[Audit Logging<br/>• CloudWatch Logs<br/>• API Gateway Logs<br/>• Lambda Execution Logs]
    end
    
    subgraph "Monitoring & Alerting"
        CW[CloudWatch<br/>• Security Metrics<br/>• Anomaly Detection<br/>• Real-time Alerts]
        XRAY[X-Ray Tracing<br/>• Request Flow<br/>• Performance Monitoring<br/>• Error Tracking]
    end
    
    %% Threat to Security Flow
    DDOS --> WAF
    BOT --> WAF
    INJ --> VALID
    XSS --> VALID
    
    %% Security Layer Flow
    WAF --> CORS
    CORS --> AUTH
    AUTH --> IAM
    
    %% Data Protection Flow
    IAM --> ENCRYPT
    ENCRYPT --> VALID
    VALID --> LOG
    
    %% Monitoring Flow
    LOG --> CW
    CW --> XRAY
    
    %% Styling
    classDef threatStyle fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef securityStyle fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef dataStyle fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef monitorStyle fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    
    class DDOS,BOT,INJ,XSS threatStyle
    class WAF,CORS,AUTH,IAM securityStyle
    class ENCRYPT,VALID,LOG dataStyle
    class CW,XRAY monitorStyle
```

## 📊 Performance & Scalability Architecture

```mermaid
graph TB
    subgraph "Client-Side Optimization"
        CDN[CloudFront CDN<br/>• Global Edge Locations<br/>• Static Asset Caching<br/>• Gzip Compression]
        CACHE[Browser Caching<br/>• HTTP Cache Headers<br/>• Service Worker<br/>• Local Storage]
    end
    
    subgraph "API Layer Optimization"
        RATE[Rate Limiting<br/>• Per-User Limits<br/>• API Throttling<br/>• Burst Handling]
        COMPRESS[Response Compression<br/>• Gzip Encoding<br/>• JSON Minification<br/>• Image Optimization]
    end
    
    subgraph "Compute Optimization"
        WARM[Lambda Warm-up<br/>• Provisioned Concurrency<br/>• Connection Pooling<br/>• Cold Start Mitigation]
        ASYNC[Async Processing<br/>• Non-blocking Operations<br/>• Background Tasks<br/>• Event-driven Architecture]
    end
    
    subgraph "Database Optimization"
        INDEX[Database Indexing<br/>• GSI Optimization<br/>• Query Patterns<br/>• Partition Keys]
        CACHE_DB[Database Caching<br/>• DynamoDB Accelerator<br/>• Query Result Caching<br/>• Session Storage]
    end
    
    subgraph "Monitoring & Auto-scaling"
        METRICS[Performance Metrics<br/>• Response Times<br/>• Throughput<br/>• Error Rates]
        AUTO[Auto-scaling<br/>• Lambda Concurrency<br/>• DynamoDB Capacity<br/>• CloudFront Distribution]
    end
    
    %% Flow
    CDN --> CACHE
    CACHE --> RATE
    RATE --> COMPRESS
    COMPRESS --> WARM
    WARM --> ASYNC
    ASYNC --> INDEX
    INDEX --> CACHE_DB
    CACHE_DB --> METRICS
    METRICS --> AUTO
    
    %% Styling
    classDef clientStyle fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef apiStyle fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef computeStyle fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef dbStyle fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef monitorStyle fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    
    class CDN,CACHE clientStyle
    class RATE,COMPRESS apiStyle
    class WARM,ASYNC computeStyle
    class INDEX,CACHE_DB dbStyle
    class METRICS,AUTO monitorStyle
```

## 🚀 Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        DEV_CODE[Development Code<br/>• Local Development<br/>• Feature Branches<br/>• Unit Testing]
        DEV_DEPLOY[Dev Deployment<br/>• Staging Environment<br/>• Integration Testing<br/>• Performance Testing]
    end
    
    subgraph "CI/CD Pipeline"
        GIT[Git Repository<br/>• Code Versioning<br/>• Pull Requests<br/>• Code Reviews]
        GHA[GitHub Actions<br/>• Automated Testing<br/>• Build Process<br/>• Deployment Triggers]
        CDK[AWS CDK<br/>• Infrastructure as Code<br/>• Environment Management<br/>• Resource Provisioning]
    end
    
    subgraph "Production Environment"
        PROD_LAMBDA[Production Lambda<br/>• Multi-region Deployment<br/>• Auto-scaling<br/>• Monitoring]
        PROD_DB[Production Database<br/>• DynamoDB Global Tables<br/>• Backup & Recovery<br/>• Point-in-time Recovery]
        PROD_CDN[Production CDN<br/>• Global Distribution<br/>• Edge Caching<br/>• SSL/TLS Termination]
    end
    
    subgraph "Monitoring & Maintenance"
        ALERTS[Alerting System<br/>• CloudWatch Alarms<br/>• SNS Notifications<br/>• PagerDuty Integration]
        LOGS[Centralized Logging<br/>• CloudWatch Logs<br/>• Log Aggregation<br/>• Log Analysis]
        BACKUP[Backup & Recovery<br/>• Automated Backups<br/>• Disaster Recovery<br/>• Data Retention]
    end
    
    %% Development Flow
    DEV_CODE --> GIT
    GIT --> GHA
    GHA --> DEV_DEPLOY
    
    %% CI/CD Flow
    GHA --> CDK
    CDK --> PROD_LAMBDA
    CDK --> PROD_DB
    CDK --> PROD_CDN
    
    %% Production Flow
    PROD_LAMBDA --> ALERTS
    PROD_DB --> BACKUP
    PROD_CDN --> LOGS
    
    %% Styling
    classDef devStyle fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef cicdStyle fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef prodStyle fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef monitorStyle fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    
    class DEV_CODE,DEV_DEPLOY devStyle
    class GIT,GHA,CDK cicdStyle
    class PROD_LAMBDA,PROD_DB,PROD_CDN prodStyle
    class ALERTS,LOGS,BACKUP monitorStyle
```

## 📱 Frontend Architecture

```mermaid
graph TB
    subgraph "Presentation Layer"
        UI[UI Components<br/>• Material-UI<br/>• Custom Components<br/>• Responsive Design]
        ROUTES[Routing<br/>• React Router<br/>• Protected Routes<br/>• Lazy Loading]
    end
    
    subgraph "State Management"
        REDUX[Redux Store<br/>• Centralized State<br/>• Predictable Updates<br/>• Time Travel Debugging]
        SLICES[Redux Slices<br/>• Auth Slice<br/>• Posts Slice<br/>• Comments Slice<br/>• Subreddits Slice]
    end
    
    subgraph "Business Logic"
        SERVICES[API Services<br/>• HTTP Client<br/>• Request/Response<br/>• Error Handling]
        HOOKS[Custom Hooks<br/>• Data Fetching<br/>• State Management<br/>• Side Effects]
    end
    
    subgraph "Data Layer"
        API[Backend API<br/>• REST Endpoints<br/>• Authentication<br/>• Data Validation]
        CACHE[Client Cache<br/>• Local Storage<br/>• Session Storage<br/>• Memory Cache]
    end
    
    subgraph "Performance Optimization"
        LAZY[Code Splitting<br/>• Dynamic Imports<br/>• Route-based Splitting<br/>• Component Lazy Loading]
        MEMO[Memoization<br/>• React.memo<br/>• useMemo<br/>• useCallback]
    end
    
    %% Flow
    UI --> ROUTES
    ROUTES --> REDUX
    REDUX --> SLICES
    SLICES --> SERVICES
    SERVICES --> HOOKS
    HOOKS --> API
    API --> CACHE
    CACHE --> LAZY
    LAZY --> MEMO
    
    %% Styling
    classDef uiStyle fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef stateStyle fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef logicStyle fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef dataStyle fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef perfStyle fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    
    class UI,ROUTES uiStyle
    class REDUX,SLICES stateStyle
    class SERVICES,HOOKS logicStyle
    class API,CACHE dataStyle
    class LAZY,MEMO perfStyle
```

---

## 📋 Architecture Summary

### **Key Components:**
- **6 Lambda Functions** for microservices architecture
- **6 DynamoDB Tables** with optimized indexing
- **API Gateway** for unified API management
- **CloudFront CDN** for global content delivery
- **AWS Cognito** for authentication and authorization
- **S3 Storage** for media and static assets

### **Scalability Features:**
- **Serverless Architecture** for automatic scaling
- **Global Distribution** with CloudFront
- **Database Sharding** with DynamoDB
- **Caching Strategy** at multiple layers
- **Performance Monitoring** with CloudWatch

### **Security Measures:**
- **Multi-layer Security** with WAF, IAM, and encryption
- **JWT Authentication** with AWS Cognito
- **Input Validation** and sanitization
- **Audit Logging** and monitoring

### **Deployment Strategy:**
- **Infrastructure as Code** with AWS CDK
- **CI/CD Pipeline** with GitHub Actions
- **Environment Management** for dev/staging/prod
- **Automated Testing** and deployment

This architecture provides a robust, scalable, and secure foundation for the Reddit Clone application with room for future enhancements and growth.
