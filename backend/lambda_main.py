import json
import uuid
import domain_logic
import brand_logic
import domain_checker
import logo_client
import storage
import sqs_publisher

def format_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*" 
        },
        "body": json.dumps(body)
    }

def lambda_handler(event, context):
    try:
        body = event.get('body')
        if not body:
            return format_response(400, {"error": "Bad Request", "message": "Empty request body"})
            
        if isinstance(body, str):
            body = json.loads(body)
            
        action = body.get('action', 'generate')
        
        if action == 'check_domain':
            domain_to_check = body.get('domain')
            if not domain_to_check:
                return format_response(400, {"error": "Bad Request", "message": "domain is required"})
            
            # Use the existing check_domains which returns a list of dicts
            result = domain_checker.check_domains([domain_to_check])
            return format_response(200, result[0])
            
        elif action == 'generate':
            business_name = body.get('business_name')
            category = body.get('category')
            
            if not business_name or not category:
                return format_response(400, {"error": "Bad Request", "message": "business_name and category are required"})
                
            request_id = str(uuid.uuid4())
            
            raw_domains = domain_logic.generate_domains(business_name)
            
            # Create domain dicts with "unknown" availability to bypass latency
            domain_results = [{'domain': d, 'available': None} for d in raw_domains]
            suggested_domains = domain_logic.score_and_sort_domains(domain_results)
            
            branding = brand_logic.get_branding_attributes(category)
            svg_content = logo_client.generate_logo(business_name, branding['style'], branding['icon_type'])
            
            logo_key = storage.save_svg_to_s3(request_id, svg_content)
            storage.save_result_to_dynamodb(
                request_id=request_id,
                business_name=business_name,
                category=category,
                variations=suggested_domains,
                branding=branding,
                logo_key=logo_key
            )
            
            sqs_publisher.publish_audit_message(request_id, business_name, category, "SUCCESS")
            
            response_body = {
                "available_domains": [], # TBD by client clicks
                "suggested_domains": suggested_domains,
                "style": branding['style'],
                "icon_type": branding['icon_type'],
                "brand_tone": branding['brand_tone'],
                "logo_svg": svg_content,
                "request_id": request_id
            }
            
            return format_response(200, response_body)
            
        else:
            return format_response(400, {"error": "Bad Request", "message": "Unknown action"})

    except Exception as e:
        print(f"Internal Server Error: {e}")
        return format_response(500, {"error": "Internal Server Error", "message": str(e)})
