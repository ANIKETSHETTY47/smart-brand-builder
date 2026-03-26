# Rule-based branding logic mapping
# Category -> (Style, Icon Type, Brand Tone)

BRANDING_RULES = {
    "technology": {"style": "tech", "icon_type": "hexagon", "brand_tone": "futuristic"},
    "fitness": {"style": "bold", "icon_type": "lightning", "brand_tone": "energetic"},
    "finance": {"style": "corporate", "icon_type": "shield", "brand_tone": "professional"},
    "health": {"style": "minimalist", "icon_type": "circle", "brand_tone": "calm"},
    "food": {"style": "bold", "icon_type": "circle", "brand_tone": "friendly"},
    "education": {"style": "corporate", "icon_type": "hexagon", "brand_tone": "professional"},
    "default": {"style": "tech", "icon_type": "hexagon", "brand_tone": "futuristic"}
}

def get_branding_attributes(category):
    """
    Returns the style, icon_type, and brand_tone for a given category.
    Falls back to 'default' if category is not recognized.
    """
    category_key = str(category).lower().strip()
    
    if category_key in BRANDING_RULES:
        return BRANDING_RULES[category_key]
    else:
        return BRANDING_RULES["default"]
