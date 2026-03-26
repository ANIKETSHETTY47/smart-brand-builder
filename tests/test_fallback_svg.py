import pytest
from backend import logo_client

def test_fallback_svg_generation():
    svg = logo_client.get_fallback_svg("Nexus", "tech", "hexagon")
    assert "<svg" in svg
    assert "NE" in svg
    assert "polygon" in svg  # Hexagon shape element expects polygon
    assert "#00d2ff" in svg  # Tech style hex color

def test_fallback_svg_defaults():
    svg = logo_client.get_fallback_svg("", "unknown_style", "unknown_shape")
    assert "LG" in svg # Default initials
    assert "circle" in svg # Default shape 
