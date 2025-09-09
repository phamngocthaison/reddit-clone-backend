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

        # Cognito User Pool
        self.user_pool, self.user_pool_client = self._create_cognito_resources()

        # Lambda execution role
        lambda_execution_role = self._create_lambda_execution_role()

        # Lambda function for authentication
        auth_lambda = self._create_auth_lambda(lambda_execution_role)

        # API Gateway
        self.api = self._create_api_gateway(auth_lambda)

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
                ],
                resources=[
                    self.users_table.table_arn,
                    f"{self.users_table.table_arn}/index/*",
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
        """Create Lambda function for authentication."""
        # Get the path to the Lambda code - use the deployment directory
        lambda_code_path = Path(__file__).parent.parent / "lambda-deployment"

        auth_lambda = lambda_.Function(
            self,
            "AuthLambda",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="lambda_handler_standalone_v1.handler",  # Use the standalone v1 handler
            code=lambda_.Code.from_asset(str(lambda_code_path)),
            role=execution_role,
            environment={
                "USER_POOL_ID": self.user_pool.user_pool_id,
                "CLIENT_ID": self.user_pool_client.user_pool_client_id,
                "USERS_TABLE": self.users_table.table_name,
                "REGION": self.region,
            },
            timeout=cdk.Duration.seconds(30),
        )

        return auth_lambda

    def _create_api_gateway(self, auth_lambda: lambda_.Function) -> apigateway.RestApi:
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
                ],
            ),
        )

        # API Gateway integration
        auth_integration = apigateway.LambdaIntegration(auth_lambda)

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
