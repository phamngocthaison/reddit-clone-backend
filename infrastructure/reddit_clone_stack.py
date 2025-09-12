"""Reddit Clone Backend CDK Stack."""

from pathlib import Path
from typing import Any

import aws_cdk as cdk
from aws_cdk import (
    aws_apigateway as apigateway,
    aws_cognito as cognito,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_lambda as lambda_,
)
from constructs import Construct


class RedditCloneStack(cdk.Stack):
    """CDK Stack for Reddit Clone Backend."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs: Any) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB Tables
        self.users_table = self._create_users_table()
        self.posts_table = self._create_posts_table()
        self.subreddits_table = self._create_subreddits_table()
        self.comments_table = self._create_comments_table()
        self.subscriptions_table = self._create_subscriptions_table()
        self.user_feeds_table = self._create_user_feeds_table()
        self.user_follows_table = self._create_user_follows_table()

        # Cognito User Pool
        self.user_pool, self.user_pool_client = self._create_cognito_resources()

        # Lambda execution role
        lambda_execution_role = self._create_lambda_execution_role()

        # Lambda functions
        auth_lambda = self._create_auth_lambda(lambda_execution_role)
        comments_lambda = self._create_comments_lambda(lambda_execution_role)
        subreddits_lambda = self._create_subreddits_lambda(lambda_execution_role)
        feeds_lambda = self._create_feeds_lambda(lambda_execution_role)
        user_profile_lambda = self._create_user_profile_lambda(lambda_execution_role)

        # API Gateway
        self.api = self._create_api_gateway(auth_lambda, comments_lambda, subreddits_lambda, feeds_lambda, user_profile_lambda)

        # Outputs
        self._create_outputs()

    def _create_users_table(self) -> dynamodb.Table:
        """Create DynamoDB table for users."""
        table = dynamodb.Table(
            self,
            "UsersTable",
            table_name="reddit-clone-users",
            partition_key=dynamodb.Attribute(
                name="userId", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY,  # Use RETAIN for production
            point_in_time_recovery=True,
        )

        # Add GSI for email lookup
        table.add_global_secondary_index(
            index_name="EmailIndex",
            partition_key=dynamodb.Attribute(
                name="email", type=dynamodb.AttributeType.STRING
            ),
        )

        return table

    def _create_posts_table(self) -> dynamodb.Table:
        """Create DynamoDB table for posts."""
        table = dynamodb.Table(
            self,
            "PostsTable",
            table_name="reddit-clone-posts",
            partition_key=dynamodb.Attribute(
                name="postId", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY,  # Use RETAIN for production
            point_in_time_recovery=True,
        )

        # GSI for posts by subreddit
        table.add_global_secondary_index(
            index_name="SubredditIndex",
            partition_key=dynamodb.Attribute(
                name="subredditId", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="createdAt", type=dynamodb.AttributeType.STRING
            ),
        )

        # GSI for posts by author
        table.add_global_secondary_index(
            index_name="AuthorIndex",
            partition_key=dynamodb.Attribute(
                name="authorId", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="createdAt", type=dynamodb.AttributeType.STRING
            ),
        )

        # GSI for posts by score (for hot/top sorting)
        table.add_global_secondary_index(
            index_name="ScoreIndex",
            partition_key=dynamodb.Attribute(
                name="score", type=dynamodb.AttributeType.NUMBER
            ),
            sort_key=dynamodb.Attribute(
                name="createdAt", type=dynamodb.AttributeType.STRING
            ),
        )

        # GSI for posts by type
        table.add_global_secondary_index(
            index_name="TypeIndex",
            partition_key=dynamodb.Attribute(
                name="postType", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="createdAt", type=dynamodb.AttributeType.STRING
            ),
        )

        return table

    def _create_comments_table(self) -> dynamodb.Table:
        """Create DynamoDB table for comments."""
        table = dynamodb.Table(
            self,
            "CommentsTable",
            table_name="reddit-clone-comments",
            partition_key=dynamodb.Attribute(
                name="commentId", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY,  # Use RETAIN for production
            point_in_time_recovery=True,
        )

        # GSI for comments by post
        table.add_global_secondary_index(
            index_name="PostIndex",
            partition_key=dynamodb.Attribute(
                name="postId", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="createdAt", type=dynamodb.AttributeType.STRING
            ),
        )

        # GSI for comments by author
        table.add_global_secondary_index(
            index_name="AuthorIndex",
            partition_key=dynamodb.Attribute(
                name="authorId", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="createdAt", type=dynamodb.AttributeType.STRING
            ),
        )

        # GSI for comments by score (for hot/top sorting)
        table.add_global_secondary_index(
            index_name="ScoreIndex",
            partition_key=dynamodb.Attribute(
                name="score", type=dynamodb.AttributeType.NUMBER
            ),
            sort_key=dynamodb.Attribute(
                name="createdAt", type=dynamodb.AttributeType.STRING
            ),
        )

        # GSI for replies by parent comment
        table.add_global_secondary_index(
            index_name="ParentIndex",
            partition_key=dynamodb.Attribute(
                name="parentId", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="createdAt", type=dynamodb.AttributeType.STRING
            ),
        )

        return table

    def _create_subreddits_table(self) -> dynamodb.Table:
        """Create DynamoDB table for subreddits."""
        table = dynamodb.Table(
            self,
            "SubredditsTable",
            table_name="reddit-clone-subreddits",
            partition_key=dynamodb.Attribute(
                name="subredditId", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY,  # Use RETAIN for production
            point_in_time_recovery=True,
        )

        # GSI for subreddits by name
        table.add_global_secondary_index(
            index_name="NameIndex",
            partition_key=dynamodb.Attribute(
                name="name", type=dynamodb.AttributeType.STRING
            ),
        )

        # GSI for subreddits by subscriber count
        table.add_global_secondary_index(
            index_name="SubscriberCountIndex",
            partition_key=dynamodb.Attribute(
                name="subscriberCount", type=dynamodb.AttributeType.NUMBER
            ),
            sort_key=dynamodb.Attribute(
                name="createdAt", type=dynamodb.AttributeType.STRING
            ),
        )

        return table

    def _create_subscriptions_table(self) -> dynamodb.Table:
        """Create DynamoDB table for subscriptions."""
        table = dynamodb.Table(
            self,
            "SubscriptionsTable",
            table_name="reddit-clone-subscriptions",
            partition_key=dynamodb.Attribute(
                name="subscriptionId", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY,  # Use RETAIN for production
            point_in_time_recovery=True,
        )

        # GSI for subscriptions by user
        table.add_global_secondary_index(
            index_name="UserIndex",
            partition_key=dynamodb.Attribute(
                name="userId", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="joinedAt", type=dynamodb.AttributeType.STRING
            ),
        )

        # GSI for subscriptions by subreddit
        table.add_global_secondary_index(
            index_name="SubredditIndex",
            partition_key=dynamodb.Attribute(
                name="subredditId", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="joinedAt", type=dynamodb.AttributeType.STRING
            ),
        )

        return table

    def _create_user_feeds_table(self) -> dynamodb.Table:
        """Create DynamoDB table for user feeds."""
        table = dynamodb.Table(
            self,
            "UserFeedsTable",
            table_name="reddit-clone-user-feeds",
            partition_key=dynamodb.Attribute(
                name="feedId", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="createdAt", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY,  # Use RETAIN for production
            point_in_time_recovery=True,
        )

        # GSI for feeds by user (chronological)
        table.add_global_secondary_index(
            index_name="UserFeedIndex",
            partition_key=dynamodb.Attribute(
                name="userId", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="createdAt", type=dynamodb.AttributeType.STRING
            ),
        )

        # GSI for feeds by user (by score)
        table.add_global_secondary_index(
            index_name="PostScoreIndex",
            partition_key=dynamodb.Attribute(
                name="userId", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="postScore", type=dynamodb.AttributeType.NUMBER
            ),
        )

        # GSI for feeds by subreddit
        table.add_global_secondary_index(
            index_name="SubredditFeedIndex",
            partition_key=dynamodb.Attribute(
                name="subredditId", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="createdAt", type=dynamodb.AttributeType.STRING
            ),
        )

        # GSI for feeds by author
        table.add_global_secondary_index(
            index_name="AuthorFeedIndex",
            partition_key=dynamodb.Attribute(
                name="authorId", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="createdAt", type=dynamodb.AttributeType.STRING
            ),
        )

        return table

    def _create_user_follows_table(self) -> dynamodb.Table:
        """Create DynamoDB table for user follows."""
        table = dynamodb.Table(
            self,
            "UserFollowsTable",
            table_name="reddit-clone-user-follows",
            partition_key=dynamodb.Attribute(
                name="followId", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="createdAt", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY,  # Use RETAIN for production
            point_in_time_recovery=True,
        )

        # GSI for follows by follower
        table.add_global_secondary_index(
            index_name="FollowerIndex",
            partition_key=dynamodb.Attribute(
                name="followerId", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="createdAt", type=dynamodb.AttributeType.STRING
            ),
        )

        # GSI for follows by following
        table.add_global_secondary_index(
            index_name="FollowingIndex",
            partition_key=dynamodb.Attribute(
                name="followingId", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="createdAt", type=dynamodb.AttributeType.STRING
            ),
        )

        return table

    def _create_cognito_resources(self) -> tuple[cognito.UserPool, cognito.UserPoolClient]:
        """Create Cognito User Pool and Client."""
        user_pool = cognito.UserPool(
            self,
            "RedditCloneUserPool",
            user_pool_name="reddit-clone-user-pool",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(email=True, username=True),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=False,
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(required=True, mutable=True),
                preferred_username=cognito.StandardAttribute(required=True, mutable=True),
            ),
            custom_attributes={
                "userId": cognito.StringAttribute(min_len=1, max_len=256, mutable=True),
            },
            removal_policy=cdk.RemovalPolicy.DESTROY,  # Use RETAIN for production
        )

        user_pool_client = cognito.UserPoolClient(
            self,
            "RedditCloneUserPoolClient",
            user_pool=user_pool,
            auth_flows=cognito.AuthFlow(
                user_password=True, 
                user_srp=True, 
                admin_user_password=True
            ),
            generate_secret=False,  # Set to True if using server-side authentication
        )

        return user_pool, user_pool_client

    def _create_lambda_execution_role(self) -> iam.Role:
        """Create IAM role for Lambda execution."""
        role = iam.Role(
            self,
            "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ],
        )

        # DynamoDB permissions
        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:Query",
                    "dynamodb:Scan",
                    "dynamodb:BatchWriteItem",
                    "dynamodb:BatchGetItem",
                ],
                resources=[
                    self.users_table.table_arn,
                    f"{self.users_table.table_arn}/index/*",
                    self.posts_table.table_arn,
                    f"{self.posts_table.table_arn}/index/*",
                    self.subreddits_table.table_arn,
                    f"{self.subreddits_table.table_arn}/index/*",
                    self.comments_table.table_arn,
                    f"{self.comments_table.table_arn}/index/*",
                    self.subscriptions_table.table_arn,
                    f"{self.subscriptions_table.table_arn}/index/*",
                    self.user_feeds_table.table_arn,
                    f"{self.user_feeds_table.table_arn}/index/*",
                    self.user_follows_table.table_arn,
                    f"{self.user_follows_table.table_arn}/index/*",
                ],
            )
        )

        # Cognito permissions
        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "cognito-idp:AdminCreateUser",
                    "cognito-idp:AdminDeleteUser",
                    "cognito-idp:AdminGetUser",
                    "cognito-idp:AdminUpdateUserAttributes",
                    "cognito-idp:ListUsers",
                    "cognito-idp:AdminSetUserPassword",
                    "cognito-idp:AdminConfirmSignUp",
                    "cognito-idp:AdminInitiateAuth",
                    "cognito-idp:ForgotPassword",
                    "cognito-idp:ConfirmForgotPassword",
                    "cognito-idp:GlobalSignOut",
                    "cognito-idp:AdminListGroupsForUser",
                    "cognito-idp:AdminAddUserToGroup",
                    "cognito-idp:AdminRemoveUserFromGroup",
                ],
                resources=[self.user_pool.user_pool_arn],
            )
        )

        return role

    def _create_auth_lambda(self, execution_role: iam.Role) -> lambda_.Function:
        """Create Lambda function for authentication and posts."""
        # Get the path to the Lambda code - use the deployment directory
        lambda_code_path = Path(__file__).parent.parent / "lambda-deployment"

        auth_lambda = lambda_.Function(
            self,
            "AuthLambda",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="lambda_handler_auth_posts.handler",  # Use the auth+posts handler
            code=lambda_.Code.from_asset(str(lambda_code_path)),
            role=execution_role,
            environment={
                "USER_POOL_ID": self.user_pool.user_pool_id,
                "CLIENT_ID": self.user_pool_client.user_pool_client_id,
                "USERS_TABLE": self.users_table.table_name,
                "POSTS_TABLE": self.posts_table.table_name,
                "SUBREDDITS_TABLE": self.subreddits_table.table_name,
                "COMMENTS_TABLE": self.comments_table.table_name,
                "SUBSCRIPTIONS_TABLE": self.subscriptions_table.table_name,
                "REGION": self.region,
            },
            timeout=cdk.Duration.seconds(30),
        )

        return auth_lambda

    def _create_comments_lambda(self, execution_role: iam.Role) -> lambda_.Function:
        """Create Lambda function for comments."""
        # Get the path to the Lambda code - use the deployment directory
        lambda_code_path = Path(__file__).parent.parent / "lambda-deployment"

        comments_lambda = lambda_.Function(
            self,
            "CommentsLambda",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="lambda_handler_comments.handler",  # Use the comments handler
            code=lambda_.Code.from_asset(str(lambda_code_path)),
            role=execution_role,
            environment={
                "USER_POOL_ID": self.user_pool.user_pool_id,
                "CLIENT_ID": self.user_pool_client.user_pool_client_id,
                "USERS_TABLE": self.users_table.table_name,
                "POSTS_TABLE": self.posts_table.table_name,
                "SUBREDDITS_TABLE": self.subreddits_table.table_name,
                "COMMENTS_TABLE": self.comments_table.table_name,
                "SUBSCRIPTIONS_TABLE": self.subscriptions_table.table_name,
                "REGION": self.region,
            },
            timeout=cdk.Duration.seconds(30),
        )

        return comments_lambda

    def _create_subreddits_lambda(self, execution_role: iam.Role) -> lambda_.Function:
        """Create Lambda function for subreddits."""
        # Get the path to the Lambda code - use the deployment directory
        lambda_code_path = Path(__file__).parent.parent / "lambda-deployment"

        subreddits_lambda = lambda_.Function(
            self,
            "SubredditsLambda",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="lambda_handler_subreddits.handler",  # Use the subreddits handler
            code=lambda_.Code.from_asset(str(lambda_code_path)),
            role=execution_role,
            environment={
                "USER_POOL_ID": self.user_pool.user_pool_id,
                "CLIENT_ID": self.user_pool_client.user_pool_client_id,
                "USERS_TABLE": self.users_table.table_name,
                "POSTS_TABLE": self.posts_table.table_name,
                "SUBREDDITS_TABLE": self.subreddits_table.table_name,
                "COMMENTS_TABLE": self.comments_table.table_name,
                "SUBSCRIPTIONS_TABLE": self.subscriptions_table.table_name,
                "REGION": self.region,
            },
            timeout=cdk.Duration.seconds(30),
        )

        return subreddits_lambda

    def _create_feeds_lambda(self, execution_role: iam.Role) -> lambda_.Function:
        """Create Lambda function for feeds."""
        # Get the path to the Lambda code - use the deployment directory
        lambda_code_path = Path(__file__).parent.parent / "lambda-deployment"

        feeds_lambda = lambda_.Function(
            self,
            "FeedsLambda",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="lambda_handler_feeds.handler",  # Use the feeds handler
            code=lambda_.Code.from_asset(str(lambda_code_path)),
            role=execution_role,
            environment={
                "USER_POOL_ID": self.user_pool.user_pool_id,
                "CLIENT_ID": self.user_pool_client.user_pool_client_id,
                "USERS_TABLE": self.users_table.table_name,
                "POSTS_TABLE": self.posts_table.table_name,
                "SUBREDDITS_TABLE": self.subreddits_table.table_name,
                "COMMENTS_TABLE": self.comments_table.table_name,
                "SUBSCRIPTIONS_TABLE": self.subscriptions_table.table_name,
                "USER_FEEDS_TABLE": self.user_feeds_table.table_name,
                "USER_FOLLOWS_TABLE": self.user_follows_table.table_name,
                "REGION": self.region,
            },
            timeout=cdk.Duration.seconds(30),
        )

        return feeds_lambda

    def _create_user_profile_lambda(self, execution_role: iam.Role) -> lambda_.Function:
        """Create user profile Lambda function."""
        user_profile_lambda = lambda_.Function(
            self,
            "UserProfileLambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="lambda_handler_user_profile.handler",
            code=lambda_.Code.from_asset("lambda-layer.zip"),
            role=execution_role,
            timeout=cdk.Duration.seconds(30),
            memory_size=512,
            environment={
                "USERS_TABLE_NAME": self.users_table.table_name,
                "POSTS_TABLE_NAME": self.posts_table.table_name,
                "COMMENTS_TABLE_NAME": self.comments_table.table_name,
                "USER_POOL_ID": self.user_pool.user_pool_id,
                "USER_POOL_CLIENT_ID": self.user_pool_client.user_pool_client_id,
            },
        )

        # Grant permissions to DynamoDB tables
        self.users_table.grant_read_write_data(user_profile_lambda)
        self.posts_table.grant_read_data(user_profile_lambda)
        self.comments_table.grant_read_data(user_profile_lambda)

        return user_profile_lambda

    def _create_api_gateway(self, auth_lambda: lambda_.Function, comments_lambda: lambda_.Function, subreddits_lambda: lambda_.Function, feeds_lambda: lambda_.Function, user_profile_lambda: lambda_.Function) -> apigateway.RestApi:
        """Create API Gateway with authentication endpoints."""
        api = apigateway.RestApi(
            self,
            "RedditCloneApi",
            rest_api_name="Reddit Clone API",
            description="API for Reddit Clone Backend",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=[
                    "Content-Type",
                    "X-Amz-Date",
                    "Authorization",
                    "X-Api-Key",
                    "X-Amz-Security-Token",
                    "X-User-ID",
                ],
            ),
        )

        # API Gateway integrations
        auth_integration = apigateway.LambdaIntegration(auth_lambda)
        comments_integration = apigateway.LambdaIntegration(comments_lambda)
        subreddits_integration = apigateway.LambdaIntegration(subreddits_lambda)
        feeds_integration = apigateway.LambdaIntegration(feeds_lambda)
        user_profile_integration = apigateway.LambdaIntegration(user_profile_lambda)

        # Auth endpoints - each endpoint needs its own resource path
        auth_resource = api.root.add_resource("auth")
        
        # Register endpoint
        register_resource = auth_resource.add_resource("register")
        register_resource.add_method("POST", auth_integration)
        
        # Login endpoint
        login_resource = auth_resource.add_resource("login")
        login_resource.add_method("POST", auth_integration)
        
        # Logout endpoint
        logout_resource = auth_resource.add_resource("logout")
        logout_resource.add_method("POST", auth_integration)
        
        # Forgot password endpoint
        forgot_password_resource = auth_resource.add_resource("forgot-password")
        forgot_password_resource.add_method("POST", auth_integration)
        
        # Reset password endpoint
        reset_password_resource = auth_resource.add_resource("reset-password")
        reset_password_resource.add_method("POST", auth_integration)

        # Posts endpoints
        posts_resource = api.root.add_resource("posts")
        
        # Create post endpoint
        posts_create_resource = posts_resource.add_resource("create")
        posts_create_resource.add_method("POST", auth_integration)
        
        # Get posts endpoint
        posts_resource.add_method("GET", auth_integration)
        
        # Individual post endpoints
        post_resource = posts_resource.add_resource("{post_id}")
        post_resource.add_method("GET", auth_integration)
        post_resource.add_method("PUT", auth_integration)
        post_resource.add_method("DELETE", auth_integration)
        
        # Vote post endpoint
        vote_resource = post_resource.add_resource("vote")
        vote_resource.add_method("POST", auth_integration)

        # Comments endpoints - use comments_lambda
        comments_resource = api.root.add_resource("comments")
        
        # Create comment endpoint
        comments_create_resource = comments_resource.add_resource("create")
        comments_create_resource.add_method("POST", comments_integration)
        
        # Get comments endpoint (all comments)
        comments_resource.add_method("GET", comments_integration)
        
        # Individual comment endpoints
        comment_resource = comments_resource.add_resource("{comment_id}")
        comment_resource.add_method("GET", comments_integration)
        comment_resource.add_method("PUT", comments_integration)
        comment_resource.add_method("DELETE", comments_integration)
        
        # Vote comment endpoint
        comment_vote_resource = comment_resource.add_resource("vote")
        comment_vote_resource.add_method("POST", comments_integration)
        
        # Get comments by post_id endpoint (separate path)
        comments_by_post_resource = post_resource.add_resource("comments")
        comments_by_post_resource.add_method("GET", comments_integration)

        # Subreddits endpoints - use subreddits_lambda
        subreddits_resource = api.root.add_resource("subreddits")
        
        # Create subreddit endpoint
        subreddits_create_resource = subreddits_resource.add_resource("create")
        subreddits_create_resource.add_method("POST", subreddits_integration)
        
        # Get subreddits list endpoint
        subreddits_resource.add_method("GET", subreddits_integration)
        
        # Get subreddit by name endpoint
        subreddits_name_resource = subreddits_resource.add_resource("name")
        subreddit_name_resource = subreddits_name_resource.add_resource("{name}")
        subreddit_name_resource.add_method("GET", subreddits_integration)
        
        # Individual subreddit endpoints
        subreddit_resource = subreddits_resource.add_resource("{subreddit_id}")
        subreddit_resource.add_method("GET", subreddits_integration)
        subreddit_resource.add_method("PUT", subreddits_integration)
        subreddit_resource.add_method("DELETE", subreddits_integration)
        
        # Join/Leave subreddit endpoints
        subreddit_join_resource = subreddit_resource.add_resource("join")
        subreddit_join_resource.add_method("POST", subreddits_integration)
        
        subreddit_leave_resource = subreddit_resource.add_resource("leave")
        subreddit_leave_resource.add_method("POST", subreddits_integration)
        
        # Get subreddit posts endpoint
        subreddit_posts_resource = subreddit_resource.add_resource("posts")
        subreddit_posts_resource.add_method("GET", subreddits_integration)
        
        # Moderator management endpoints
        subreddit_moderators_resource = subreddit_resource.add_resource("moderators")
        subreddit_moderators_resource.add_method("POST", subreddits_integration)
        
        subreddit_moderator_resource = subreddit_moderators_resource.add_resource("{user_id}")
        subreddit_moderator_resource.add_method("DELETE", subreddits_integration)
        
        # User subreddits endpoint
        subreddits_user_resource = subreddits_resource.add_resource("user")
        subreddit_user_resource = subreddits_user_resource.add_resource("{user_id}")
        subreddit_user_resource.add_method("GET", subreddits_integration)
        
        # Check user membership endpoint
        subreddit_members_resource = subreddit_resource.add_resource("members")
        subreddit_member_resource = subreddit_members_resource.add_resource("{user_id}")
        subreddit_member_resource.add_method("GET", subreddits_integration)

        # Feeds endpoints - use feeds_lambda
        feeds_resource = api.root.add_resource("feeds")
        
        # Get user feed endpoint
        feeds_resource.add_method("GET", feeds_integration)
        
        # Refresh feed endpoint
        feeds_refresh_resource = feeds_resource.add_resource("refresh")
        feeds_refresh_resource.add_method("POST", feeds_integration)
        
        # Feed statistics endpoint
        feeds_stats_resource = feeds_resource.add_resource("stats")
        feeds_stats_resource.add_method("GET", feeds_integration)

        # User Profile endpoints - use user_profile_lambda
        # Auth/me endpoints (current user profile)
        auth_me_resource = auth_resource.add_resource("me")
        auth_me_resource.add_method("GET", user_profile_integration)
        auth_me_resource.add_method("PUT", user_profile_integration)
        auth_me_resource.add_method("DELETE", user_profile_integration)
        
        # Change password endpoint
        auth_change_password_resource = auth_resource.add_resource("change-password")
        auth_change_password_resource.add_method("PUT", user_profile_integration)
        
        # Users endpoints (public user profiles)
        users_resource = api.root.add_resource("users")
        
        # Individual user profile endpoint
        user_resource = users_resource.add_resource("{user_id}")
        user_resource.add_method("GET", user_profile_integration)
        
        # User posts endpoint
        user_posts_resource = user_resource.add_resource("posts")
        user_posts_resource.add_method("GET", user_profile_integration)
        
        # User comments endpoint
        user_comments_resource = user_resource.add_resource("comments")
        user_comments_resource.add_method("GET", user_profile_integration)

        return api

    def _create_outputs(self) -> None:
        """Create CloudFormation outputs."""
        cdk.CfnOutput(
            self,
            "UserPoolId",
            value=self.user_pool.user_pool_id,
            description="Cognito User Pool ID",
        )

        cdk.CfnOutput(
            self,
            "UserPoolClientId",
            value=self.user_pool_client.user_pool_client_id,
            description="Cognito User Pool Client ID",
        )

        cdk.CfnOutput(
            self,
            "ApiGatewayUrl",
            value=self.api.url,
            description="API Gateway URL",
        )

        cdk.CfnOutput(
            self,
            "UsersTableName",
            value=self.users_table.table_name,
            description="DynamoDB Users Table Name",
        )

        cdk.CfnOutput(
            self,
            "PostsTableName",
            value=self.posts_table.table_name,
            description="DynamoDB Posts Table Name",
        )

        cdk.CfnOutput(
            self,
            "SubredditsTableName",
            value=self.subreddits_table.table_name,
            description="DynamoDB Subreddits Table Name",
        )

        cdk.CfnOutput(
            self,
            "SubscriptionsTableName",
            value=self.subscriptions_table.table_name,
            description="DynamoDB Subscriptions Table Name",
        )

        cdk.CfnOutput(
            self,
            "CommentsTableName",
            value=self.comments_table.table_name,
            description="DynamoDB Comments Table Name",
        )

        cdk.CfnOutput(
            self,
            "UserFeedsTableName",
            value=self.user_feeds_table.table_name,
            description="DynamoDB User Feeds Table Name",
        )

        cdk.CfnOutput(
            self,
            "UserFollowsTableName",
            value=self.user_follows_table.table_name,
            description="DynamoDB User Follows Table Name",
        )
