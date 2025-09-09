# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Testing
```bash
# Run all tests
python -m pytest

# Run tests with coverage
python -m pytest tests/ -v --cov=src

# Run unit tests only
python -m pytest tests/unit/ -m unit

# Run integration tests only
python -m pytest tests/integration/ -m integration

# Run specific test file
python -m pytest tests/unit/test_auth_service.py -v
```

### Code Quality
```bash
# Format code with Black
python -m black src/

# Run linting with flake8
python -m flake8 src/

# Run type checking with MyPy
python -m mypy src/

# Run import sorting with isort
python -m isort src/
```

### AWS CDK Deployment
```bash
# Bootstrap CDK (first time only)
cdk bootstrap

# Synthesize CloudFormation template
cdk synth

# Deploy infrastructure
python scripts/deploy.py

# Manual deployment
cdk deploy

# Destroy all resources
cdk destroy
```

### Local Development
```bash
# Run tests in watch mode during development
python -m pytest --looponfail

# Check test configuration
python -m pytest --collect-only
```

## Architecture Overview

This is an AWS serverless Reddit clone backend built with Python and AWS CDK for infrastructure as code.

### Core AWS Services
- **AWS Cognito**: User authentication and authorization
- **AWS API Gateway**: RESTful API endpoints with CORS enabled
- **AWS Lambda**: Serverless compute functions (Python 3.9)
- **DynamoDB**: Primary database with GSI for email lookups
- **AWS CDK**: Infrastructure as Code using Python

### Project Structure
- `src/lambda/auth/`: Authentication Lambda functions and business logic
- `src/lambda/shared/`: Shared utilities, models, and AWS clients across Lambdas
- `infrastructure/`: AWS CDK stack definitions and app entry point
- `tests/`: Unit and integration tests with pytest and moto for AWS mocking
- `scripts/`: Deployment and utility scripts
- `docs/`: Technical documentation including database schema

### Key Architecture Patterns

#### Lambda Handler Pattern
Each Lambda function follows a consistent pattern:
- `main.py`: Lambda entry point with event routing and error handling
- `*_service.py`: Business logic layer with async/await patterns
- Shared utilities for response formatting and request parsing

#### Pydantic Models
- Request/response validation using Pydantic models with field aliases
- Consistent data models across the application in `src/lambda/shared/models.py`
- Snake_case internally, camelCase for API responses

#### AWS Resource Management
- CDK Stack in `infrastructure/reddit_clone_stack.py` defines all AWS resources
- Proper IAM roles with least privilege access
- Environment variables automatically injected by CDK
- CloudFormation outputs for resource ARNs and IDs

#### Database Design
- Single DynamoDB Users table with GSI for email lookups
- Designed for future expansion with Posts, Comments, Communities, and Votes tables
- Follows DynamoDB best practices with proper access patterns

### Authentication Flow
1. User registration via Cognito with email verification
2. Login returns JWT tokens (access, refresh, ID)
3. Password reset flow using Cognito's forgot password mechanism
4. Logout invalidates tokens globally

### Development Phase Status
- **Phase 1 (Current)**: Authentication system complete
- **Phase 2 (Planned)**: Posts, voting, comments, and communities

### Configuration
- `pyproject.toml`: Python project configuration with Black, MyPy, and pytest settings
- `cdk.json`: CDK configuration with watch mode for development
- Environment variables set by CDK: `USER_POOL_ID`, `CLIENT_ID`, `USERS_TABLE`, `REGION`

### Testing Strategy
- Unit tests for business logic using moto for AWS service mocking
- Integration tests for Lambda handlers with full AWS integration
- Coverage reporting configured in pyproject.toml
- Test markers for unit/integration/slow test categorization
