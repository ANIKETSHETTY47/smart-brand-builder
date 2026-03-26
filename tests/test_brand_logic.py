import pytest
from backend import brand_logic

def test_known_category():
    attr = brand_logic.get_branding_attributes("technology")
    assert attr["style"] == "tech"
    assert attr["icon_type"] == "hexagon"
    assert attr["brand_tone"] == "futuristic"

def test_unknown_category_fallback():
    attr = brand_logic.get_branding_attributes("unknown_category_xyz")
    assert attr["style"] == "tech"
    assert attr["icon_type"] == "hexagon"
    assert attr["brand_tone"] == "futuristic"

def test_case_insensitivity():
    attr1 = brand_logic.get_branding_attributes("FiTnEsS ")
    assert attr1["style"] == "bold"
    assert attr1["icon_type"] == "lightning"
    assert attr1["brand_tone"] == "energetic"
