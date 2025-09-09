#!/bin/bash

# Deploy script with Lambda import fix

echo "🚀 Deploying Reddit Clone Backend with Lambda import fix..."

# Check if CDK is installed
if ! command -v cdk &> /dev/null; then
    echo "❌ CDK not found. Please install AWS CDK first."
    echo "   npm install -g aws-cdk"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "cdk.json" ]; then
    echo "❌ cdk.json not found. Please run this script from the project root."
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Build the project
echo "🔨 Building CDK project..."
cdk synth

# Deploy the stack
echo "🚀 Deploying to AWS..."
cdk deploy --require-approval never

echo "✅ Deployment completed!"
echo ""
echo "📋 Next steps:"
echo "1. Test the API endpoints using the Postman collection"
echo "2. Check CloudWatch logs if there are any issues"
echo "3. Update your Frontend to use the new API URL"
echo ""
echo "🔗 API URL: Check the CloudFormation outputs for the API Gateway URL"
