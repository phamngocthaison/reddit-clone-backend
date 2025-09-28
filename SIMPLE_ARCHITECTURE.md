# Reddit Clone - Simple Architecture Overview

## 🏗️ System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Web Browser   │  │   Mobile App    │  │   Admin Panel   │  │
│  │   (React.js)    │  │  (Future)       │  │   (Future)      │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CLOUDFRONT CDN                              │
│              Global Content Delivery Network                    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   REST API      │  │   Rate Limiting │  │   CORS Policy   │  │
│  │   Endpoints     │  │   & Throttling  │  │   & Security    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AWS LAMBDA FUNCTIONS                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │    Auth     │ │   Posts     │ │  Comments   │ │ Subreddits  │ │
│  │  Lambda     │ │  Lambda     │ │  Lambda     │ │  Lambda     │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
│  ┌─────────────┐ ┌─────────────┐                                │
│  │   User      │ │    Feeds    │                                │
│  │  Profile    │ │   Lambda    │                                │
│  │  Lambda     │ │             │                                │
│  └─────────────┘ └─────────────┘                                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AWS COGNITO                               │
│              User Authentication & Authorization                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DYNAMODB TABLES                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │    Users    │ │    Posts    │ │  Comments   │ │ Subreddits  │ │
│  │   Table     │ │   Table     │ │   Table     │ │   Table     │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
│  ┌─────────────┐ ┌─────────────┐                                │
│  │Subscriptions│ │ User Feeds  │                                │
│  │   Table     │ │   Table     │                                │
│  └─────────────┘ └─────────────┘                                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        AWS S3                                  │
│              File Storage for Media & Assets                   │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow

### 1. User Authentication
```
User → CloudFront → API Gateway → Auth Lambda → Cognito → DynamoDB
```

### 2. Create Post
```
User → CloudFront → API Gateway → Posts Lambda → DynamoDB + S3
```

### 3. View Feed
```
User → CloudFront → API Gateway → Feeds Lambda → DynamoDB (Multiple Tables)
```

## 🗄️ Database Structure

### Core Tables:
- **Users**: User profiles and authentication data
- **Posts**: Content posts with voting and metadata
- **Comments**: Comment threads with nested replies
- **Subreddits**: Community information and settings
- **Subscriptions**: User-community relationships
- **User Feeds**: Personalized content feeds

### Key Relationships:
- Users create Posts and Comments
- Posts belong to Subreddits
- Comments belong to Posts
- Users subscribe to Subreddits
- Feeds aggregate content from subscribed Subreddits

## 🔐 Security Layers

1. **CloudFront CDN**: DDoS protection and global distribution
2. **API Gateway**: Rate limiting and CORS policy
3. **AWS Cognito**: JWT authentication and user management
4. **IAM Roles**: Service-level permissions
5. **DynamoDB**: Encryption at rest and in transit
6. **S3**: Secure file storage with access controls

## 📊 Performance Features

- **Serverless Architecture**: Auto-scaling based on demand
- **Global CDN**: Fast content delivery worldwide
- **Database Indexing**: Optimized query performance
- **Caching**: Multiple layers of caching
- **Monitoring**: Real-time performance tracking

## 🚀 Deployment Process

1. **Code Push**: Developer pushes to GitHub
2. **CI/CD**: GitHub Actions triggers build and test
3. **CDK Deploy**: AWS CDK deploys infrastructure
4. **Lambda Update**: Functions are updated with new code
5. **Testing**: Automated tests verify deployment
6. **Monitoring**: CloudWatch tracks performance

---

## 📱 Frontend Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    REACT APPLICATION                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Components    │  │   Pages         │  │   Services      │  │
│  │   • PostCard    │  │   • HomePage    │  │   • API Client  │  │
│  │   • Comment     │  │   • PostPage    │  │   • Auth Service│  │
│  │   • Subreddit   │  │   • ProfilePage │  │   • Data Fetch  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Redux Store   │  │   Routing       │  │   Hooks         │  │
│  │   • Auth Slice  │  │   • React Router│  │   • useAuth     │  │
│  │   • Posts Slice │  │   • Protected   │  │   • usePosts    │  │
│  │   • UI State    │  │   • Lazy Load   │  │   • useComments  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND API                               │
│              RESTful API with 32+ Endpoints                    │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Key Features

### Backend Features:
- ✅ User Authentication & Authorization
- ✅ Post Creation & Management
- ✅ Comment System with Replies
- ✅ Subreddit Communities
- ✅ Voting System (Upvote/Downvote)
- ✅ User Profiles & Statistics
- ✅ Personalized News Feeds
- ✅ Real-time Notifications (Future)

### Frontend Features:
- ✅ Responsive Web Design
- ✅ Material-UI Components
- ✅ State Management with Redux
- ✅ TypeScript for Type Safety
- ✅ Code Splitting & Lazy Loading
- ✅ Error Handling & Loading States
- ✅ Dark/Light Theme (Future)
- ✅ PWA Support (Future)

## 📈 Scalability

- **Horizontal Scaling**: Lambda functions auto-scale
- **Global Distribution**: CloudFront edge locations
- **Database Scaling**: DynamoDB on-demand capacity
- **Caching Strategy**: Multi-layer caching
- **Performance Monitoring**: Real-time metrics

## 🔧 Technology Stack

### Backend:
- **Language**: Python 3.11
- **Framework**: AWS Lambda
- **Database**: DynamoDB (NoSQL)
- **Authentication**: AWS Cognito
- **Storage**: AWS S3
- **Infrastructure**: AWS CDK

### Frontend:
- **Framework**: React.js 18+
- **Language**: TypeScript
- **UI Library**: Material-UI
- **State Management**: Redux Toolkit
- **Routing**: React Router v6
- **HTTP Client**: Axios

### DevOps:
- **CI/CD**: GitHub Actions
- **Infrastructure as Code**: AWS CDK
- **Monitoring**: CloudWatch
- **Version Control**: Git/GitHub

---

*This architecture provides a modern, scalable, and maintainable foundation for the Reddit Clone application.*
