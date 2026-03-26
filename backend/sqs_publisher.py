import os
import json
import boto3

SQS_QUEUE_URL = os.environ.get('AUDIT_QUEUE_URL', '')
REGION = os.environ.get('AWS_REGION', 'us-east-1')

def publish_audit_message(request_id, business_name, category, status="SUCCESS"):
    """
    Publishes a summary message to SQS for asynchronous audit logging.
    """
    if not SQS_QUEUE_URL:
        print("Warning: SQS_QUEUE_URL not set. Skipping audit message.")
        return
        
    try:
        sqs = boto3.client('sqs', region_name=REGION)
        
        message_body = {
            'request_id': request_id,
            'business_name': business_name,
            'category': category,
            'status': status
        }
        
        response = sqs.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps(message_body)
        )
        print(f"Audit message published to SQS. MessageId: {response.get('MessageId')}")
    except Exception as e:
        # SQS decoupling means failure here should NOT affect the user response
        print(f"Error publishing to SQS: {e}")
