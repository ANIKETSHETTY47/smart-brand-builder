import os
import requests
import boto3

# Use environment variable with fallback for the parameter name
SSM_PARAMETER_NAME = os.environ.get('WHOISXML_API_KEY_PARAM', '/brand-domain/whoisxml-api-key')
WHOISXML_API_URL = "https://domain-availability.whoisxmlapi.com/api/v1"

def get_api_key():
    """Retrieves the WhoisXML API key from AWS SSM Parameter Store."""
    try:
        # SSM requires knowing the region, mostly handled by Lambda runtime environment
        ssm = boto3.client('ssm')
        response = ssm.get_parameter(
            Name=SSM_PARAMETER_NAME,
            WithDecryption=True
        )
        return response['Parameter']['Value']
    except Exception as e:
        print(f"Error retrieving API key from SSM: {e}")
        return None

def check_domains(domains):
    """
    Calls the WhoisXML API to check availability for a list of domains.
    Returns: [{'domain': '...', 'available': True/False}]
    """
    api_key = get_api_key()
    if not api_key:
        print("Warning: Could not retrieve WhoisXML API Key. Defaulting all domains to unavailable.")
        return [{'domain': d, 'available': False} for d in domains]

    results = []
    
    for domain in domains:
        try:
            params = {
                'apiKey': api_key,
                'domainName': domain,
                'credits': 'DA'
            }
            response = requests.get(WHOISXML_API_URL, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            # domainAvailability is 'AVAILABLE' or 'UNAVAILABLE'
            availability = data.get('DomainInfo', {}).get('domainAvailability', 'UNAVAILABLE')
            is_available = (availability == 'AVAILABLE')
            
            results.append({
                'domain': domain,
                'available': is_available
            })
        except Exception as e:
            print(f"Error checking domain {domain}: {e}")
            results.append({
                'domain': domain,
                'available': False
            })
            
    return results
