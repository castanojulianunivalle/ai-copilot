#!/bin/bash
# Deployment script for Daily Reporter Lambda function

set -e

STACK_NAME="${STACK_NAME:-daily-reporter-v2}"
REGION="${AWS_REGION:-us-east-1}"

echo "🚀 Deploying Daily Reporter to AWS Lambda"
echo "Stack Name: $STACK_NAME"
echo "Region: $REGION"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install it first."
    exit 1
fi

# Check AWS credentials
echo "🔐 Checking AWS credentials..."
if ! aws sts get-caller-identity &>/dev/null; then
    echo "❌ AWS credentials not configured. Please configure them first:"
    echo "   aws configure"
    echo "   Or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables"
    exit 1
fi
echo "   ✅ AWS credentials configured"

# Check if stack exists
STACK_EXISTS=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" 2>&1 || echo "NOT_FOUND")

# Deploy or update CloudFormation stack FIRST (this creates the bucket)
echo "☁️  Deploying CloudFormation stack..."
if echo "$STACK_EXISTS" | grep -q "does not exist\|NOT_FOUND"; then
    echo "   Creating new stack (this will create the S3 bucket)..."
    aws cloudformation create-stack \
        --stack-name "$STACK_NAME" \
        --template-body file://cloudformation.yaml \
        --capabilities CAPABILITY_NAMED_IAM \
        --region "$REGION" \
        --parameters file://cloudformation-params.json
    
    echo "⏳ Waiting for stack creation to complete..."
    aws cloudformation wait stack-create-complete --stack-name "$STACK_NAME" --region "$REGION"
    echo "   ✅ Stack created successfully"
else
    echo "   Updating existing stack..."
    UPDATE_OUTPUT=$(aws cloudformation update-stack \
        --stack-name "$STACK_NAME" \
        --template-body file://cloudformation.yaml \
        --capabilities CAPABILITY_NAMED_IAM \
        --region "$REGION" \
        --parameters file://cloudformation-params.json 2>&1 || true)
    
    if echo "$UPDATE_OUTPUT" | grep -q "No updates are to be performed"; then
        echo "   (No changes to apply)"
    else
        if echo "$UPDATE_OUTPUT" | grep -q "An error occurred"; then
            echo "$UPDATE_OUTPUT"
            exit 1
        fi
        echo "⏳ Waiting for stack update to complete..."
        aws cloudformation wait stack-update-complete --stack-name "$STACK_NAME" --region "$REGION"
        echo "   ✅ Stack updated successfully"
    fi
fi

# Get the bucket name from stack outputs (now it should exist)
echo "📦 Getting deployment bucket from stack..."
PACKAGE_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`DeploymentBucketName`].OutputValue' \
    --output text)

if [ -z "$PACKAGE_BUCKET" ]; then
    echo "❌ Error: Could not get bucket name from stack outputs"
    exit 1
fi
echo "   Using bucket: $PACKAGE_BUCKET"

# Create deployment package
echo "📦 Creating deployment package..."
PACKAGE_DIR=".lambda_package"
rm -rf "$PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR"

# Copy Python files
cp -r daily_reporter "$PACKAGE_DIR/"
cp lambda_handler.py "$PACKAGE_DIR/"
cp requirements.txt "$PACKAGE_DIR/"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt -t "$PACKAGE_DIR" --quiet

# Create ZIP file
ZIP_FILE="daily-reporter-$(date +%Y%m%d-%H%M%S).zip"
S3_KEY="lambda-code/$ZIP_FILE"
cd "$PACKAGE_DIR"
zip -r "../$ZIP_FILE" . -q
cd ..

# Upload to S3 (now the bucket exists)
echo "📤 Uploading package to S3..."
aws s3 cp "$ZIP_FILE" "s3://$PACKAGE_BUCKET/$S3_KEY" --region "$REGION"
echo "   ✅ Uploaded to s3://$PACKAGE_BUCKET/$S3_KEY"

# Update Lambda function code
echo "🔄 Updating Lambda function code..."
aws lambda update-function-code \
    --function-name "${STACK_NAME}-daily-reporter" \
    --s3-bucket "$PACKAGE_BUCKET" \
    --s3-key "$S3_KEY" \
    --region "$REGION" \
    --no-cli-pager

echo "⏳ Waiting for Lambda update to complete..."
aws lambda wait function-updated --function-name "${STACK_NAME}-daily-reporter" --region "$REGION"
echo "   ✅ Lambda function updated"

echo "✅ Deployment complete!"
echo ""
echo "📊 Stack outputs:"
aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs' \
    --output table

# Cleanup
rm -rf "$PACKAGE_DIR"
rm -f "$ZIP_FILE"

echo ""
echo "💡 To view logs:"
echo "   aws logs tail /aws/lambda/${STACK_NAME}-daily-reporter --follow --region $REGION"

