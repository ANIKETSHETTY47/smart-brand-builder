import os
import json
import boto3
from datetime import datetime

AUDIT_TABLE_NAME = os.environ.get('AUDIT_TABLE', 'brand-domain-audit')
REGION = os.environ.get('AWS_REGION', 'us-east-1')

def lambda_handler(event, context):
    """
    SQS Consumer Lambda.
    Reads messages from the queue and writes an audit record to DynamoDB.
    """
    dynamodb = boto3.resource('dynamodb', region_name=REGION)
    table = dynamodb.Table(AUDIT_TABLE_NAME)
    
    for record in event.get('Records', []):
        try:
            body = record['body']
            # SQS payload is stringified JSON
            if isinstance(body, str):
                message = json.loads(body)
            else:
                message = body
                
            request_id = message.get('request_id', 'UNKNOWN')
            business_name = message.get('business_name', '')
            category = message.get('category', '')
            status = message.get('status', 'SUCCESS')
            
            timestamp = datetime.utcnow().isoformat()
            
            item = {
                'request_id': request_id, # Partition key
                'timestamp': timestamp,
                'business_name': business_name,
                'category': category,
                'status': status
            }
            
            table.put_item(Item=item)
            print(f"Successfully processed audit record for {request_id}")
            
        except Exception as e:
            print(f"Error processing SQS record: {e}")
            # If we raise here, SQS will likely retry the message based on DLQ/Visibility settings
            # In a resilient setup, raising is appropriate if it's a transient DB error.
            raise e
