# Reddit Clone Backend - Lambda Architecture

## Overview

Reddit Clone Backend sử dụng kiến trúc serverless với 2 Lambda functions riêng biệt để xử lý các chức năng khác nhau, giúp dễ dàng quản lý, scale và maintain.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway                              │
│  https://ugn2h0yxwf.execute-api.ap-southeast-1.amazonaws.com │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ AuthLambda  │ │CommentsLambda│ │   DynamoDB  │
│             │ │             │ │             │
│ • Auth APIs │ │ • Comments  │ │ • Users     │
│ • Posts APIs│ │   APIs      │ │ • Posts     │
│             │ │             │ │ • Comments  │
└─────────────┘ └─────────────┘ └─────────────┘
```

## Lambda Functions

### 1. AuthLambda
**Handler**: `lambda_handler_auth_posts.handler`  
**Function Name**: `RedditCloneStack-AuthLambda6BB8C88C-5Eb0T2wKncvH`

#### Responsibilities:
- **Authentication APIs**:
  - `POST /auth/register` - User registration
  - `POST /auth/login` - User login
  - `POST /auth/logout` - User logout
  - `POST /auth/forgot-password` - Password reset request
  - `POST /auth/reset-password` - Password reset confirmation

- **Posts APIs**:
  - `POST /posts/create` - Create new post
  - `GET /posts` - Get posts list
  - `GET /posts/{post_id}` - Get post by ID
  - `PUT /posts/{post_id}` - Update post
  - `DELETE /posts/{post_id}` - Delete post
  - `POST /posts/{post_id}/vote` - Vote on post

#### Dependencies:
- DynamoDB Tables: `users`, `posts`, `subreddits`, `comments`
- Cognito User Pool
- IAM permissions for DynamoDB and Cognito

### 2. CommentsLambda
**Handler**: `lambda_handler_comments.handler`  
**Function Name**: `RedditCloneStack-CommentsLambdaF3F5A903-eNCdCVXj6TiC`

#### Responsibilities:
- **Comments APIs**:
  - `POST /comments/create` - Create new comment
  - `GET /comments` - Get comments list
  - `GET /comments/{comment_id}` - Get comment by ID
  - `PUT /comments/{comment_id}` - Update comment
  - `DELETE /comments/{comment_id}` - Delete comment
  - `POST /comments/{comment_id}/vote` - Vote on comment

#### Dependencies:
- DynamoDB Tables: `users`, `posts`, `comments`
- IAM permissions for DynamoDB

## Data Flow

### Authentication Flow
1. User sends auth request to API Gateway
2. API Gateway routes to AuthLambda
3. AuthLambda validates credentials with Cognito
4. AuthLambda returns JWT tokens

### Posts Flow
1. User sends posts request to API Gateway
2. API Gateway routes to AuthLambda
3. AuthLambda processes posts CRUD operations
4. AuthLambda interacts with DynamoDB
5. AuthLambda returns response

### Comments Flow
1. User sends comments request to API Gateway
2. API Gateway routes to CommentsLambda
3. CommentsLambda processes comments CRUD operations
4. CommentsLambda interacts with DynamoDB
5. CommentsLambda returns response

## Benefits of Separated Architecture

### 1. **Scalability**
- Mỗi Lambda có thể scale độc lập
- Comments có thể scale cao hơn khi có nhiều traffic
- Auth có thể scale thấp hơn vì ít thay đổi

### 2. **Maintainability**
- Code được tách biệt rõ ràng
- Dễ debug và fix issues
- Team có thể work parallel trên các features khác nhau

### 3. **Performance**
- Cold start time ngắn hơn cho từng function
- Memory usage tối ưu cho từng use case
- Timeout settings phù hợp với từng function

### 4. **Security**
- IAM permissions được tách biệt
- Comments Lambda không cần Cognito permissions
- Auth Lambda có full permissions

### 5. **Cost Optimization**
- Pay only for what you use
- Comments Lambda có thể có higher concurrency
- Auth Lambda có thể có lower concurrency

## Environment Variables

### AuthLambda
```bash
USER_POOL_ID=ap-southeast-1_tcwIJSUFS
CLIENT_ID=1et6o5qdvfgcrj18qqbglkpkm1
USERS_TABLE=reddit-clone-users
POSTS_TABLE=reddit-clone-posts
SUBREDDITS_TABLE=reddit-clone-subreddits
COMMENTS_TABLE=reddit-clone-comments
REGION=ap-southeast-1
```

### CommentsLambda
```bash
USER_POOL_ID=ap-southeast-1_tcwIJSUFS
CLIENT_ID=1et6o5qdvfgcrj18qqbglkpkm1
USERS_TABLE=reddit-clone-users
POSTS_TABLE=reddit-clone-posts
SUBREDDITS_TABLE=reddit-clone-subreddits
COMMENTS_TABLE=reddit-clone-comments
REGION=ap-southeast-1
```

## Deployment

### CDK Stack
```typescript
// Infrastructure defined in reddit_clone_stack.py
const authLambda = new lambda.Function(this, 'AuthLambda', {
  handler: 'lambda_handler_auth_posts.handler',
  // ... configuration
});

const commentsLambda = new lambda.Function(this, 'CommentsLambda', {
  handler: 'lambda_handler_comments.handler',
  // ... configuration
});
```

### API Gateway Integration
```typescript
// Auth endpoints
authResource.addMethod('POST', new apigateway.LambdaIntegration(authLambda));

// Comments endpoints  
commentsResource.addMethod('POST', new apigateway.LambdaIntegration(commentsLambda));
```

## Monitoring & Logging

### CloudWatch Logs
- **AuthLambda**: `/aws/lambda/RedditCloneStack-AuthLambda6BB8C88C-5Eb0T2wKncvH`
- **CommentsLambda**: `/aws/lambda/RedditCloneStack-CommentsLambdaF3F5A903-eNCdCVXj6TiC`

### Metrics
- Invocation count
- Duration
- Error rate
- Throttle count
- Memory usage

## Future Enhancements

### 1. **Additional Lambda Functions**
- **ModerationLambda**: Content moderation
- **NotificationLambda**: Push notifications
- **SearchLambda**: Search functionality

### 2. **Event-Driven Architecture**
- SNS/SQS for async processing
- EventBridge for event routing
- Step Functions for complex workflows

### 3. **Caching Layer**
- ElastiCache for frequently accessed data
- API Gateway caching
- Lambda response caching

## Troubleshooting

### Common Issues

1. **Cold Start**: Use provisioned concurrency for critical functions
2. **Timeout**: Adjust timeout settings based on function complexity
3. **Memory**: Monitor memory usage and adjust allocation
4. **Permissions**: Ensure IAM roles have correct permissions

### Debug Commands

```bash
# Check Lambda function status
aws lambda get-function --function-name RedditCloneStack-AuthLambda6BB8C88C-5Eb0T2wKncvH

# View CloudWatch logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/RedditCloneStack"

# Test Lambda function
aws lambda invoke --function-name RedditCloneStack-AuthLambda6BB8C88C-5Eb0T2wKncvH response.json
```
