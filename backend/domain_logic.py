import re

def generate_domains(business_name):
    """Generates a list of domain variations based on the business name."""
    # Clean the business name: remove special characters, spaces, and make lowercase
    clean_name = re.sub(r'[^a-zA-Z0-9-]', '', business_name).lower()
    clean_name_no_hyphen = clean_name.replace('-', '')
    
    variations = [
        f"{clean_name}.com",
        f"get{clean_name_no_hyphen}.com",
        f"{clean_name_no_hyphen}app.com",
        f"{clean_name}.io"
    ]
    
    # Deduplicate while preserving order
    return list(dict.fromkeys(variations))

def score_and_sort_domains(domain_availabilities):
    """
    Scores domains based on rules and sorts them.
    domain_availabilities: list of dicts [{'domain': '...', 'available': True/False}]
    Rules:
    - Available domains ranked above unavailable ones.
    - Shorter domains score higher.
    - Domains without hyphens score higher.
    Returns: list of dicts sorted by score.
    """
    for entry in domain_availabilities:
        domain = entry['domain']
        available = entry['available']
        
        score = 0
        
        # Rule 1: Availability is the strongest multiplier
        if available:
            score += 1000
            
        # Rule 2: Shorter domains score higher (baseline 100, subtract length)
        score += max(0, 100 - len(domain))
        
        # Rule 3: Domains without hyphens score higher
        if '-' not in domain:
            score += 50
            
        entry['score'] = score
        
    # Sort descending by score
    sorted_domains = sorted(domain_availabilities, key=lambda x: x['score'], reverse=True)
    return sorted_domains
