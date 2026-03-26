#!/bin/bash
# Smart Brand & Domain Availability Platform - AWS Learner Lab Setup

# 1. Variables
REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
RESULTS_TABLE="brand-domain-results"
AUDIT_TABLE="brand-domain-audit"
# Generating a random suffix for global uniqueness of S3 buckets
SUFFIX=$RANDOM
LOGOS_BUCKET="brand-domain-logos-bucket-${SUFFIX}"
FRONTEND_BUCKET="brand-domain-frontend-bucket-${SUFFIX}"
SQS_QUEUE_NAME="brand-domain-audit-queue"
LAMBDA_MAIN="brand-domain-api-lambda"
LAMBDA_AUDIT="brand-domain-audit-lambda"
API_NAME="brand-domain-api"

echo "Using Suffix: ${SUFFIX} for S3 buckets"

# 2. DynamoDB Tables
echo "Creating DynamoDB Tables..."
aws dynamodb create-table \
    --table-name ${RESULTS_TABLE} \
    --attribute-definitions AttributeName=request_id,AttributeType=S \
    --key-schema AttributeName=request_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region ${REGION}

aws dynamodb create-table \
    --table-name ${AUDIT_TABLE} \
    --attribute-definitions AttributeName=request_id,AttributeType=S \
    --key-schema AttributeName=request_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region ${REGION}

# 3. S3 Buckets
echo "Creating S3 Buckets..."
aws s3api create-bucket --bucket ${LOGOS_BUCKET} --region ${REGION}
aws s3api create-bucket --bucket ${FRONTEND_BUCKET} --region ${REGION}

# Enable Static Website Hosting for Frontend
aws s3 website s3://${FRONTEND_BUCKET}/ --index-document index.html

# Disable Block Public Access for Frontend Bucket to allow policy
aws s3api put-public-access-block --bucket ${FRONTEND_BUCKET} \
    --public-access-block-configuration BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false

# Apply Public Read Policy for Frontend Bucket
cat <<EOF > frontend-policy.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::${FRONTEND_BUCKET}/*"
        }
    ]
}
EOF
aws s3api put-bucket-policy --bucket ${FRONTEND_BUCKET} --policy file://frontend-policy.json

# Disable Block Public Access for Logos Bucket to allow direct linking of images
aws s3api put-public-access-block --bucket ${LOGOS_BUCKET} \
    --public-access-block-configuration BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false

cat <<EOF > logos-policy.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::${LOGOS_BUCKET}/*"
        }
    ]
}
EOF
aws s3api put-bucket-policy --bucket ${LOGOS_BUCKET} --policy file://logos-policy.json

# 4. SQS Queue
echo "Creating SQS Queue..."
QUEUE_URL=$(aws sqs create-queue --queue-name ${SQS_QUEUE_NAME} --query 'QueueUrl' --output text --region ${REGION})
QUEUE_ARN=$(aws sqs get-queue-attributes --queue-url ${QUEUE_URL} --attribute-names QueueArn --query 'Attributes.QueueArn' --output text)

# 5. SSM Parameter Store
echo "Storing API Key in SSM..."
aws ssm put-parameter \
    --name "/brand-domain/whoisxml-api-key" \
    --value "at_WYA748Gp6nHGW1C4RZo3VeBg072eT" \
    --type "SecureString" \
    --overwrite \
    --region ${REGION}

# 6. IAM Roles & Policies (Learner Lab usually uses LabRole)
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/LabRole"
echo "Assuming usage of standard AWSAcademy LabRole. ARN: ${ROLE_ARN}"

# 7. Lambda Functions
echo "Creating Lambda Functions..."
# Dummy zip to create function initially
echo "def lambda_handler(event, context): return {}" > dummy.py
zip default.zip dummy.py

aws lambda create-function \
    --function-name ${LAMBDA_MAIN} \
    --runtime python3.11 \
    --role ${ROLE_ARN} \
    --handler lambda_main.lambda_handler \
    --zip-file fileb://default.zip \
    --timeout 20 \
    --environment Variables="{RESULTS_TABLE=${RESULTS_TABLE},LOGOS_BUCKET=${LOGOS_BUCKET},AUDIT_QUEUE_URL=${QUEUE_URL}}" \
    --region ${REGION}

aws lambda create-function \
    --function-name ${LAMBDA_AUDIT} \
    --runtime python3.11 \
    --role ${ROLE_ARN} \
    --handler lambda_audit.lambda_handler \
    --zip-file fileb://default.zip \
    --timeout 10 \
    --environment Variables="{AUDIT_TABLE=${AUDIT_TABLE}}" \
    --region ${REGION}

# 8. SQS trigger for Audit Lambda
aws lambda create-event-source-mapping \
    --function-name ${LAMBDA_AUDIT} \
    --batch-size 10 \
    --event-source-arn ${QUEUE_ARN}

# 9. API Gateway Setup
echo "Creating API Gateway..."
API_ID=$(aws apigateway create-rest-api --name ${API_NAME} --query 'id' --output text --region ${REGION})
PARENT_ID=$(aws apigateway get-resources --rest-api-id ${API_ID} --query 'items[0].id' --output text --region ${REGION})

# /api/brand-domain resource setup
API_RESOURCE_ID=$(aws apigateway create-resource --rest-api-id ${API_ID} --parent-id ${PARENT_ID} --path-part "api" --query 'id' --output text --region ${REGION})
RESOURCE_ID=$(aws apigateway create-resource --rest-api-id ${API_ID} --parent-id ${API_RESOURCE_ID} --path-part "brand-domain" --query 'id' --output text --region ${REGION})

# POST method & Integration
aws apigateway put-method --rest-api-id ${API_ID} --resource-id ${RESOURCE_ID} --http-method POST --authorization-type "NONE" --region ${REGION}
LAMBDA_URI="arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:${LAMBDA_MAIN}/invocations"
aws apigateway put-integration \
    --rest-api-id ${API_ID} \
    --resource-id ${RESOURCE_ID} \
    --http-method POST \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri ${LAMBDA_URI} \
    --region ${REGION}

# Lambda Permissions for API Gateway
aws lambda add-permission \
    --function-name ${LAMBDA_MAIN} \
    --statement-id apigateway-test-2 \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/POST/api/brand-domain" \
    --region ${REGION}

# Deploy
aws apigateway create-deployment --rest-api-id ${API_ID} --stage-name prod --region ${REGION}

echo "=========================================="
echo "Deployment Complete!"
echo "Frontend URL: http://${FRONTEND_BUCKET}.s3-website-${REGION}.amazonaws.com"
echo "API Endpoint: https://${API_ID}.execute-api.${REGION}.amazonaws.com/prod/api/brand-domain/"
echo "=========================================="

rm -f frontend-policy.json logos-policy.json default.zip dummy.py
