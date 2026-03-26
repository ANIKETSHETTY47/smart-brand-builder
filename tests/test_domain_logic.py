import pytest
from backend import domain_logic

def test_generate_domains():
    domains = domain_logic.generate_domains("Tech Corp")
    assert "techcorp.com" in domains
    assert "gettechcorp.com" in domains
    assert "techcorpapp.com" in domains
    assert "techcorp.io" in domains
    assert len(domains) == 4

def test_score_and_sort_domains():
    availabilities = [
        {"domain": "longdomainwithouthyphen.com", "available": True},
        {"domain": "short.com", "available": True},
        {"domain": "short-hyphen.com", "available": True},
        {"domain": "taken.com", "available": False}
    ]
    
    sorted_domains = domain_logic.score_and_sort_domains(availabilities)
    
    # 1. Available should rank above unavailable
    assert sorted_domains[-1]['domain'] == "taken.com"
    
    # 2. Between available ones, shorter and no-hyphen score higher.
    # short.com (9 chars) vs longdomainwithouthyphen.com (27 chars) vs short-hyphen.com (16 chars, has hyphen)
    assert sorted_domains[0]['domain'] == "short.com"
