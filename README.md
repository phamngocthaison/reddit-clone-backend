# Reddit Clone Backend

A scalable Reddit clone backend built with AWS serverless technologies using separated Lambda architecture.

## Architecture

This project uses the following AWS services:

- **AWS Cognito** - User authentication and authorization
- **AWS API Gateway** - RESTful API endpoints
- **AWS Lambda** - Serverless compute functions (2 separate functions)
- **DynamoDB** - NoSQL database for storing application data
- **AWS CDK** - Infrastructure as Code

### Lambda Architecture
- **AuthLambda**: Handles Authentication + Posts APIs
- **CommentsLambda**: Handles Comments APIs

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

### Phase 3 - Advanced Features (Planned)
- [ ] User profiles
- [ ] Subreddit-like communities
- [ ] Real-time notifications
- [ ] Search functionality

## Project Structure

```
reddit-clone-backend/
├── lambda_handler_auth_posts.py    # AuthLambda handler (Auth + Posts)
├── lambda_handler_comments.py      # CommentsLambda handler
├── lambda_handler_standalone_v1.py # Original auth-only handler
├── lambda_handler_phase2.py        # Combined handler (deprecated)
├── lambda-deployment/              # Lambda deployment package
│   ├── requirements.txt            # Python dependencies
│   └── [deployment files]          # Zipped for Lambda
├── infrastructure/                 # AWS CDK infrastructure code
│   ├── app.py                     # CDK app entry point
│   └── reddit_clone_stack.py      # CDK stack definition
├── docs/                          # Documentation
│   ├── api-contract.md            # API documentation
│   ├── postman-collection.json    # Postman collection
│   └── lambda-architecture.md     # Lambda architecture docs
├── tests/                         # Test files
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   └── conftest.py                # Test configuration
├── scripts/                       # Deployment and utility scripts
│   └── deploy.py                  # Automated deployment script
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Python project configuration
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
- `POST /auth/login` - Login user
- `POST /auth/logout` - Logout user
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password with code

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
