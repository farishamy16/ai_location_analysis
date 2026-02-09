"""
Test Phase 1: Multi-stage classification with confidence scoring.
Tests the improved routing system with semantic matching and confidence thresholds.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.router import ComplaintRouter
from src.services.semantic_matcher import SemanticMatcher
from src.services.openrouter import OpenRouterService


def test_semantic_matcher():
    """Test the semantic matcher with various complaints."""
    print("\n=== Testing Semantic Matcher ===\n")
    
    matcher = SemanticMatcher()
    
    test_cases = [
        ("Too many cars at UiTM Shah Alam", "traffic"),
        ("Heavy congestion on the highway", "traffic"),
        ("Parking is always full", "traffic"),
        ("Traffic is terrible downtown", "traffic"),
        ("Broken street light", "infrastructure"),
        ("Dirty food court", "commercial"),
        ("Trash everywhere", "sanitation"),
        ("Crime in the area", "safety"),
        ("Air pollution is bad", "environment"),
        ("General inquiry about services", "general"),
    ]
    
    for complaint, expected_category in test_cases:
        result = matcher.find_best_match(complaint)
        status = "✓" if result.category == expected_category else "✗"
        print(f"{status} Complaint: '{complaint}'")
        print(f"  Expected: {expected_category}, Got: {result.category}")
        print(f"  Similarity: {result.similarity:.2f}")
        print(f"  Matched keywords: {result.matched_keywords}")
        print()


def test_multi_stage_classification():
    """Test the multi-stage classification pipeline."""
    print("\n=== Testing Multi-Stage Classification ===\n")
    
    # Note: This test requires actual API keys to run
    # It's included for documentation purposes
    
    test_cases = [
        "Too many cars at UiTM Shah Alam",
        "Heavy congestion on the highway",
        "Parking is always full",
        "Traffic is terrible downtown",
        "Broken street light",
        "Dirty food court",
        "Trash everywhere",
        "Crime in the area",
        "Air pollution is bad",
        "General inquiry about services",
    ]
    
    print("Note: This test requires OPENROUTER_API_KEY to be set in .env")
    print("To run this test, uncomment the code below and ensure API keys are configured.\n")
    
    # Uncomment below to test with actual API calls:
    router = ComplaintRouter()
    
    for complaint in test_cases:
        result = router.route_complaint(complaint)
        print(f"Complaint: '{complaint}'")
        print(f"  Category: {result['classification']['category']}")
        print(f"  Method: {result['classification'].get('classification_method', 'unknown')}")
        print(f"  Confidence: {result['classification'].get('classification_confidence', 'N/A')}")
        print(f"  Department: {result['department']['name']}")
        print(f"  Priority: {result['priority']}")
        print()


def test_confidence_scoring():
    """Test confidence scoring in classification."""
    print("\n=== Testing Confidence Scoring ===\n")
    
    # Note: This test requires actual API keys to run
    print("Note: This test requires OPENROUTER_API_KEY to be set in .env")
    print("To run this test, uncomment the code below and ensure API keys are configured.\n")
    
    # Uncomment below to test with actual API calls:
    llm_service = OpenRouterService()
    
    test_complaints = [
        "Too many cars at UiTM Shah Alam",  # Should have high confidence
        "There's an issue somewhere",         # Should have low confidence
    ]
    
    for complaint in test_complaints:
        result = llm_service.classify_complaint(complaint)
        print(f"Complaint: '{complaint}'")
        print(f"  Category: {result['category']}")
        print(f"  Confidence: {result.get('confidence', 'N/A')}")
        print()


def test_keyword_matching():
    """Test keyword matching in semantic matcher."""
    print("\n=== Testing Keyword Matching ===\n")
    
    matcher = SemanticMatcher()
    
    # Test that related terms are matched
    test_cases = [
        ("Vehicles are blocking the road", ["vehicles", "road"]),
        ("Motorcycles are speeding", ["motorcycle", "speeding"]),
        ("Waste collection is late", ["waste collection"]),
        ("Pest control needed", ["pest control"]),
        ("Public facilities are broken", ["public facilities"]),
        ("Security concerns", ["security"]),
        ("Environmental hazards", ["environmental", "hazard"]),
        ("Food establishment violations", ["food establishment"]),
    ]
    
    for complaint, expected_keywords in test_cases:
        result = matcher.find_best_match(complaint)
        print(f"Complaint: '{complaint}'")
        print(f"  Matched keywords: {result.matched_keywords}")
        print(f"  Category: {result.category}")
        print(f"  Similarity: {result.similarity:.2f}")
        print()


def run_all_tests():
    """Run all Phase 1 tests."""
    print("\n" + "="*60)
    print("PHASE 1 ROUTING SYSTEM TESTS")
    print("="*60)
    
    test_semantic_matcher()
    test_keyword_matching()
    test_multi_stage_classification()
    test_confidence_scoring()
    
    print("\n" + "="*60)
    print("PHASE 1 TESTS COMPLETED")
    print("="*60)
    print("\nNote: Some tests require API keys to run fully.")
    print("To run all tests, ensure OPENROUTER_API_KEY is set in .env")
    print("and uncomment the test code in test_multi_stage_classification()")
    print("and test_confidence_scoring().\n")


if __name__ == "__main__":
    run_all_tests()
