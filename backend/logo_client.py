import json
import requests

PEER_API_URL = "http://logo-generator-env-v2.eba-mtn7tphy.us-east-1.elasticbeanstalk.com/api/logos/generate/"

# Color mapping for peer API integration
STYLE_COLORS = {
    "tech": {"primary": "#00d2ff", "secondary": "#0a1628"},
    "bold": {"primary": "#ff4b1f", "secondary": "#1f1c2c"},
    "corporate": {"primary": "#1d2b64", "secondary": "#f8cdda"},
    "minimalist": {"primary": "#e0eafc", "secondary": "#cfdef3"}
}

def get_fallback_svg(company_name, style, icon_type):
    """Generates a simple, rule-based fallback SVG if the peer API fails."""
    width = 200
    height = 200
    
    # Colors based on style
    colors = {
        "tech": "#00d2ff",
        "bold": "#ff4b1f",
        "corporate": "#1d2b64",
        "minimalist": "#e0eafc"
    }
    fill_color = colors.get(style, "#333333")
    
    initials = company_name[:2].upper() if company_name else "LG"
    
    shape_svg = ""
    if icon_type == "circle":
        shape_svg = f'<circle cx="{width/2}" cy="{height/2}" r="80" fill="{fill_color}" />'
    elif icon_type == "hexagon":
        shape_svg = f'<polygon points="100,20 170,60 170,140 100,180 30,140 30,60" fill="{fill_color}" />'
    elif icon_type == "shield":
        shape_svg = f'<path d="M 100 20 L 170 40 L 170 100 C 170 150 100 180 100 180 C 100 180 30 150 30 100 L 30 40 Z" fill="{fill_color}" />'
    elif icon_type == "lightning":
        shape_svg = f'<polygon points="110,20 40,110 90,110 70,180 160,80 110,80" fill="{fill_color}" />'
    else:
        # Default to circle
        shape_svg = f'<circle cx="{width/2}" cy="{height/2}" r="80" fill="{fill_color}" />'
        
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  {shape_svg}
  <text x="50%" y="55%" dominant-baseline="middle" text-anchor="middle" fill="#ffffff" font-family="Arial, sans-serif" font-size="48px" font-weight="bold">
    {initials}
  </text>
</svg>'''
    
    return svg_content

def generate_logo(company_name, style, icon_type):
    """
    Calls the peer Logo Generator API synchronously.
    Graceful fallback: returns a placeholder SVG upon timeout or error.
    """
    colors = STYLE_COLORS.get(style, {"primary": "#3B82F6", "secondary": "#1E3A5F"})
    
    payload = {
        "company_name": company_name,
        "tagline": "",
        "style": style,
        "icon_type": icon_type,
        "primary_color": colors["primary"],
        "secondary_color": colors["secondary"]
    }
    
    try:
        response = requests.post(PEER_API_URL, json=payload, timeout=8)
        response.raise_for_status()
        data = response.json()
        
        if "svg" in data and data["svg"]:
            return data["svg"]
        else:
            print("Warning: Peer API returned success but no SVG data. Using fallback.")
            return get_fallback_svg(company_name, style, icon_type)
            
    except Exception as e:
        # Logging to CloudWatch gracefully handled by simple print in Lambda runtime
        print(f"Error calling Peer Logo API: {e}. Falling back to placeholder.")
        return get_fallback_svg(company_name, style, icon_type)
