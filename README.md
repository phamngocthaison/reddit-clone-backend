# Reddit Clone Backend

A scalable Reddit clone backend built with AWS serverless technologies using separated Lambda architecture.

## Architecture

This project uses the following AWS services:

- **AWS Cognito** - User authentication and authorization
- **AWS API Gateway** - RESTful API endpoints
- **AWS Lambda** - Serverless compute functions (5 separate functions)
- **DynamoDB** - NoSQL database for storing application data
- **AWS CDK** - Infrastructure as Code

### Lambda Architecture
- **AuthLambda**: Handles Authentication + Posts APIs
- **CommentsLambda**: Handles Comments APIs
- **SubredditsLambda**: Handles Subreddit APIs
- **FeedsLambda**: Handles News Feed APIs
- **UserProfileLambda**: Handles User Profile APIs

## Features

### Phase 1 - Authentication ✅
- [x] User registration
- [x] User login/logout
- [x] JWT token validation
- [x] Password reset functionality

### Phase 2 - Posts System ✅
- [x] Create/Read/Update/Delete posts
- [x] Voting system (upvotes/downvotes)
- [x] Post types (text, link, image, video, poll)
- [x] Post filtering and sorting

### Phase 2.3 - Comments System ✅
- [x] Create/Read/Update/Delete comments
- [x] Nested comments (replies)
- [x] Comment voting system
- [x] Comment filtering and sorting

### Phase 3 - Subreddits System ✅
- [x] Create/Read/Update/Delete subreddits
- [x] Join/Leave subreddits
- [x] Moderator management
- [x] Subreddit posts filtering
- [x] Subreddit customization (colors, icons, banners)

### Phase 4 - News Feeds ✅
- [x] Personalized news feeds
- [x] Feed refresh functionality
- [x] Feed statistics
- [x] Advanced filtering and sorting

### Phase 5 - User Profiles ✅
- [x] User profile management
- [x] Public/private profiles
- [x] Password change functionality
- [x] User posts and comments history
- [x] Account deletion

### Phase 6 - Advanced Features (Planned)
- [ ] Real-time notifications
- [ ] Search functionality
- [ ] File upload support
- [ ] Advanced analytics

## Project Structure

```
reddit-clone-backend/
├── lambda_handler_auth_posts.py      # AuthLambda handler (Auth + Posts)
├── lambda_handler_comments.py        # CommentsLambda handler
├── lambda_handler_subreddits.py      # SubredditsLambda handler
├── lambda_handler_feeds.py           # FeedsLambda handler
├── lambda_handler_user_profile.py    # UserProfileLambda handler
├── lambda-layer.zip                  # Lambda deployment package
├── infrastructure/                   # AWS CDK infrastructure code
│   ├── app.py                       # CDK app entry point
│   └── reddit_clone_stack.py        # CDK stack definition
├── src/                             # Source code
│   ├── lambda/                      # Lambda function code
│   │   ├── models.py                # Pydantic models
│   │   ├── services/                # Business logic services
│   │   └── shared/                  # Shared utilities
│   └── tests/                       # Test files
├── docs/                            # Documentation
│   ├── api-contract.md              # API documentation
│   ├── database-schema.md           # Database schema
│   ├── Reddit_Clone_Backend_v2.4.postman_collection.json  # Postman collection
│   └── lambda-architecture.md       # Lambda architecture docs
├── tests/                           # Test files
│   ├── api/                         # API test scripts
│   ├── unit/                        # Unit tests
│   └── integration/                 # Integration tests
├── scripts/                         # Deployment and utility scripts
│   └── deploy.py                    # Automated deployment script
├── requirements.txt                 # Python dependencies
├── pyproject.toml                   # Python project configuration
└── README.md
```

## Prerequisites

- Python 3.9+
- AWS CLI configured
- AWS CDK CLI installed (`npm install -g aws-cdk`)
- Node.js (for CDK CLI only)

## Getting Started

1. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Bootstrap CDK (first time only):
   ```bash
   cdk bootstrap
   ```

4. Deploy infrastructure:
   ```bash
   python scripts/deploy.py
   ```

5. Run tests:
   ```bash
   python -m pytest
   ```

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login user (supports email/username)
- `POST /auth/logout` - Logout user
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password with code

### User Profile
- `GET /auth/me` - Get current user profile
- `PUT /auth/me` - Update current user profile
- `DELETE /auth/me` - Delete user account
- `PUT /auth/change-password` - Change password
- `GET /users/{user_id}` - Get public user profile
- `GET /users/{user_id}/posts` - Get user posts
- `GET /users/{user_id}/comments` - Get user comments

### Posts
- `POST /posts/create` - Create a new post
- `GET /posts` - Get posts with filtering
- `GET /posts/{post_id}` - Get post by ID
- `PUT /posts/{post_id}` - Update post
- `DELETE /posts/{post_id}` - Delete post
- `POST /posts/{post_id}/vote` - Vote on post

### Comments
- `POST /comments/create` - Create a new comment
- `GET /comments` - Get comments with filtering
- `GET /posts/{post_id}/comments` - Get comments for post
- `GET /comments/{comment_id}` - Get comment by ID
- `PUT /comments/{comment_id}` - Update comment
- `DELETE /comments/{comment_id}` - Delete comment
- `POST /comments/{comment_id}/vote` - Vote on comment

### Subreddits
- `POST /subreddits/create` - Create a new subreddit
- `GET /subreddits` - Get subreddits with filtering
- `GET /subreddits/{subreddit_id}` - Get subreddit by ID
- `GET /subreddits/name/{name}` - Get subreddit by name
- `PUT /subreddits/{subreddit_id}` - Update subreddit
- `DELETE /subreddits/{subreddit_id}` - Delete subreddit
- `POST /subreddits/{subreddit_id}/join` - Join subreddit
- `POST /subreddits/{subreddit_id}/leave` - Leave subreddit
- `GET /subreddits/{subreddit_id}/posts` - Get subreddit posts

### News Feeds
- `GET /feeds` - Get personalized news feed
- `POST /feeds/refresh` - Refresh user feed
- `GET /feeds/stats` - Get feed statistics

## Development

- `python -m black src/` - Format code
- `python -m flake8 src/` - Run linting
- `python -m mypy src/` - Run type checking
- `python -m pytest tests/` - Run tests
- `python -m pytest tests/ -v --cov=src` - Run tests with coverage
- `cdk synth` - Synthesize CDK template

## Deployment

The project uses AWS CDK for infrastructure deployment. All resources are defined as code in the `infrastructure/` directory.

### Automated Deployment
```bash
python scripts/deploy.py
```

### Manual Deployment
```bash
source .venv/bin/activate  # Activate virtual environment
cdk deploy
```

To destroy all resources:
```bash
cdk destroy
```

## Environment Variables

The following environment variables are automatically set by CDK during deployment:

- `USER_POOL_ID` - Cognito User Pool ID
- `CLIENT_ID` - Cognito User Pool Client ID  
- `USERS_TABLE` - DynamoDB Users Table name
- `REGION` - AWS Region

For local development/testing, you can create a `.env` file:

```env
AWS_REGION=us-east-1
USER_POOL_ID=your-user-pool-id
CLIENT_ID=your-client-id
USERS_TABLE=reddit-clone-users
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License
