# Reddit Clone Backend

A scalable Reddit clone backend built with AWS serverless technologies.

## Architecture

This project uses the following AWS services:

- **AWS Cognito** - User authentication and authorization
- **AWS API Gateway** - RESTful API endpoints
- **AWS Lambda** - Serverless compute functions
- **DynamoDB/RDS** - Database for storing application data
- **AWS CDK** - Infrastructure as Code

## Features

### Phase 1 - Authentication (Current)
- [x] User registration
- [x] User login/logout
- [x] JWT token validation
- [x] Password reset functionality

### Phase 2 - Core Reddit Features (Planned)
- [ ] Create/Read posts
- [ ] Voting system (upvotes/downvotes)
- [ ] Comments system
- [ ] User profiles
- [ ] Subreddit-like communities

## Project Structure

```
reddit-clone-backend/
├── src/
│   └── lambda/
│       ├── auth/          # Authentication Lambda functions
│       │   ├── main.py           # Lambda handler
│       │   └── auth_service.py   # Business logic
│       └── shared/        # Shared utilities and types
│           ├── models.py         # Pydantic models
│           ├── utils.py          # Utility functions
│           └── aws_clients.py    # AWS service clients
├── infrastructure/        # AWS CDK infrastructure code (Python)
│   ├── app.py            # CDK app entry point
│   └── reddit_clone_stack.py  # CDK stack definition
├── tests/                # Test files
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── conftest.py       # Test configuration
├── scripts/              # Deployment and utility scripts
│   └── deploy.py         # Automated deployment script
├── docs/                 # Documentation
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Python project configuration
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
