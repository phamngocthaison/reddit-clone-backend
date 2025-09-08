#!/usr/bin/env python3
"""Reddit Clone Backend CDK App."""

import os
import aws_cdk as cdk
from reddit_clone_stack import RedditCloneStack


app = cdk.App()

RedditCloneStack(
    app,
    "RedditCloneStack",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region=os.getenv("CDK_DEFAULT_REGION"),
    ),
)

app.synth()
