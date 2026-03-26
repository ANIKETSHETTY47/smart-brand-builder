import os
import boto3
from botocore.exceptions import ClientError

DYNAMODB_TABLE_NAME = os.environ.get('RESULTS_TABLE', 'brand-domain-results')
S3_BUCKET_NAME = os.environ.get('LOGOS_BUCKET', 'brand-domain-logos-bucket')
REGION = os.environ.get('AWS_REGION', 'us-east-1')

def save_result_to_dynamodb(request_id, business_name, category, variations, branding, logo_key):
    """
    Saves the entire result payload to DynamoDB.
    """
    try:
        dynamodb = boto3.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(DYNAMODB_TABLE_NAME)
        
        item = {
            'request_id': request_id,
            'business_name': business_name,
            'category': category,
            'variations': variations,
            'style': branding['style'],
            'icon_type': branding['icon_type'],
            'brand_tone': branding['brand_tone'],
            'logo_s3_key': logo_key
        }
        
        table.put_item(Item=item)
        print(f"Result saved to DynamoDB with request_id: {request_id}")
    except Exception as e:
        # We don't want a DynamoDB failure to break the main response flow
        print(f"Error saving to DynamoDB: {e}")

def save_svg_to_s3(request_id, svg_content):
    """
    Saves the generated SVG string to S3 and returns the S3 key.
    """
    s3_key = f"logos/{request_id}.svg"
    try:
        s3 = boto3.client('s3', region_name=REGION)
        s3.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=svg_content,
            ContentType='image/svg+xml'
        )
        print(f"SVG saved to S3 at: s3://{S3_BUCKET_NAME}/{s3_key}")
        return s3_key
    except Exception as e:
        print(f"Error saving SVG to S3: {e}")
        return None
