# Deployment Guide - Daily Reporter AWS Lambda

This guide explains how to deploy the Daily Reporter to AWS Lambda using CloudFormation.

## Prerequisites

1. **AWS CLI** installed and configured with appropriate credentials
   - See [AWS_CREDENTIALS.md](AWS_CREDENTIALS.md) for detailed setup instructions
   - Quick setup: `aws configure`
2. **Python 3.11+** installed
3. **AWS Account** with permissions to create:
   - Lambda functions
   - IAM roles and policies
   - EventBridge rules
   - CloudWatch Logs
   - S3 buckets (for deployment packages)

**Note**: The CloudFormation template will automatically create the S3 bucket for deployment packages. You don't need to create it manually.

## Cost Estimation

This infrastructure is optimized for minimal cost:

- **Lambda**: Free tier includes 1M requests/month and 400,000 GB-seconds/month
  - With 3 executions/day × 30 days = 90 executions/month
  - Estimated cost: **$0.00** (within free tier)
  
- **EventBridge**: First 14 custom events/month are free
  - 3 rules × 30 days = 90 events/month
  - Estimated cost: **~$0.00** (mostly within free tier, ~$0.01 if exceeded)

- **CloudWatch Logs**: First 5 GB ingestion/month is free
  - With 7-day retention, estimated cost: **$0.00** (within free tier)

- **S3**: First 5 GB storage/month is free
  - Deployment packages are small (~10-20 MB)
  - Estimated cost: **$0.00** (within free tier)

**Total estimated monthly cost: $0.00 - $0.10** (well within AWS free tier)

## Step 1: Prepare Parameters File

Copy the example parameters file and fill in your values:

```bash
cp cloudformation-params.json.example cloudformation-params.json
```

Edit `cloudformation-params.json` with your actual values:

- `ClickUpToken`: Your ClickUp API token (pk_...)
- `ClickUpListId`: Your ClickUp List ID
- `ClickUpTaskTemplateId`: Your ClickUp Task Template ID (if using templates)
- `ClickUpWriteMode`: `merge`, `description`, or `comment`
- `ClickUpHeader*TaskId`: Header task IDs (required if using `merge` mode)
- `JiraBaseUrl`: Your JIRA base URL
- `JiraEmail`: Your JIRA email
- `JiraApiToken`: Your JIRA API token
- Board IDs: Your JIRA board IDs

## Step 2: Configure AWS Credentials

Before deploying, make sure your AWS credentials are configured:

```bash
# Verify credentials are configured
aws sts get-caller-identity
```

If not configured, see [AWS_CREDENTIALS.md](AWS_CREDENTIALS.md) for detailed instructions.

Quick setup:
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter default region (e.g., us-east-1)
# Enter default output format (json)
```

## Step 3: Deploy Using Script (Recommended)

The deployment script automates the entire process:

```bash
chmod +x deploy.sh
export STACK_NAME=daily-reporter
export AWS_REGION=us-east-1
./deploy.sh
```

**Note**: The script will automatically use the S3 bucket created by CloudFormation. You don't need to specify `PACKAGE_BUCKET`.

The script will:
1. Verify AWS credentials are configured
2. Get/create the S3 bucket from CloudFormation stack
3. Install dependencies and create a deployment package
4. Upload the package to S3
5. Create/update the CloudFormation stack
6. Update the Lambda function code

## Step 4: Manual Deployment (Alternative)

If you prefer to deploy manually:

### 4.1 Create Deployment Package

```bash
# Create package directory
mkdir -p .lambda_package
cp -r daily_reporter .lambda_package/
cp lambda_handler.py .lambda_package/
cp requirements.txt .lambda_package/

# Install dependencies
pip3 install -r requirements.txt -t .lambda_package/

# Create ZIP
cd .lambda_package
zip -r ../daily-reporter.zip .
cd ..
```

### 4.2 Get Bucket Name from Stack

First, create the stack to get the bucket name, or get it from existing stack:

```bash
# Get bucket name from stack outputs
BUCKET_NAME=$(aws cloudformation describe-stacks \
  --stack-name daily-reporter \
  --query 'Stacks[0].Outputs[?OutputKey==`DeploymentBucketName`].OutputValue' \
  --output text)

# Or create stack first (bucket will be created automatically)
aws cloudformation create-stack \
  --stack-name daily-reporter \
  --template-body file://cloudformation.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameters file://cloudformation-params.json

# Wait for stack creation, then get bucket name
aws cloudformation wait stack-create-complete --stack-name daily-reporter
BUCKET_NAME=$(aws cloudformation describe-stacks \
  --stack-name daily-reporter \
  --query 'Stacks[0].Outputs[?OutputKey==`DeploymentBucketName`].OutputValue' \
  --output text)
```

### 4.3 Upload to S3

```bash
aws s3 cp daily-reporter.zip "s3://$BUCKET_NAME/"
```

### 4.4 Create/Update CloudFormation Stack

```bash
aws cloudformation create-stack \
  --stack-name daily-reporter \
  --template-body file://cloudformation.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameters file://cloudformation-params.json \
  --region us-east-1
```

### 4.5 Update Lambda Code

After the stack is created, update the Lambda function code:

```bash
BUCKET_NAME=$(aws cloudformation describe-stacks \
  --stack-name daily-reporter \
  --query 'Stacks[0].Outputs[?OutputKey==`DeploymentBucketName`].OutputValue' \
  --output text)

aws lambda update-function-code \
  --function-name daily-reporter-daily-reporter \
  --s3-bucket "$BUCKET_NAME" \
  --s3-key daily-reporter.zip \
  --region us-east-1
```

## Step 5: Verify Deployment

### Check Stack Status

```bash
aws cloudformation describe-stacks \
  --stack-name daily-reporter \
  --query 'Stacks[0].StackStatus'
```

### Test Lambda Function

```bash
aws lambda invoke \
  --function-name daily-reporter-daily-reporter \
  --payload '{"phase": "report1", "force_run": true}' \
  --region us-east-1 \
  response.json

cat response.json
```

### View Logs

```bash
aws logs tail /aws/lambda/daily-reporter-daily-reporter --follow
```

## Step 6: Monitor Execution

The EventBridge rules are configured to run at:
- **11:00 AM Colombia** (4:00 PM UTC) - Report #1
- **2:00 PM Colombia** (7:00 PM UTC) - Report #2
- **6:00 PM Colombia** (11:00 PM UTC) - Close

You can verify the rules are active:

```bash
aws events list-rules --name-prefix daily-reporter
```

## Updating the Function

To update the Lambda function code after making changes:

```bash
# Re-run the deployment script
./deploy.sh

# Or manually update the code
# (follow steps 3.1, 3.2, and 3.4)
```

## Updating Configuration

To update environment variables or other parameters:

1. Edit `cloudformation-params.json`
2. Update the stack:

```bash
aws cloudformation update-stack \
  --stack-name daily-reporter \
  --template-body file://cloudformation.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameters file://cloudformation-params.json
```

## Troubleshooting

### Lambda Function Fails

Check CloudWatch Logs:

```bash
aws logs tail /aws/lambda/daily-reporter-daily-reporter --follow
```

Common issues:
- Missing environment variables
- Invalid API tokens
- Network timeouts (increase Lambda timeout if needed)

### EventBridge Rules Not Triggering

Verify rules are enabled:

```bash
aws events describe-rule --name daily-reporter-report1-11am
```

Check Lambda permissions:

```bash
aws lambda get-policy --function-name daily-reporter-daily-reporter
```

### Cost Concerns

To minimize costs:
- Keep CloudWatch Log retention at 7 days (already configured)
- Use Lambda with minimum memory (256 MB, already configured)
- Monitor usage in AWS Cost Explorer

## Cleanup

To delete the entire stack:

```bash
aws cloudformation delete-stack --stack-name daily-reporter
```

This will delete:
- Lambda function
- EventBridge rules
- IAM role
- CloudWatch Log group

**Note**: The S3 bucket and deployment packages are NOT deleted automatically. Delete them manually if needed:

```bash
aws s3 rm s3://daily-reporter-packages --recursive
aws s3 rb s3://daily-reporter-packages
```

