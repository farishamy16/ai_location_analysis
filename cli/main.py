"""
CLI interface for the Complaint Location Analyzer.
Provides interactive and test modes for analyzing complaints.
"""

import sys
from src.analyzers.complaint import ComplaintAnalyzer
from src.config.settings import settings


def display_location_details(location_data: dict) -> None:
    """Display location analysis results in a formatted way."""
    print("=" * 60)
    print("📍 Location Details")
    print("=" * 60)
    print(f"Place Name: {location_data.get('place_name', 'N/A')}")
    print(f"Formatted Address: {location_data.get('formatted_address', 'N/A')}")
    print(f"Latitude: {location_data.get('lat', 'N/A')}")
    print(f"Longitude: {location_data.get('lng', 'N/A')}")
    print("=" * 60)


def analyze_complaint_cli(complaint: str, analyzer: ComplaintAnalyzer) -> None:
    """
    Analyze a complaint and display results via CLI.
    
    Args:
        complaint: The user's complaint text
        analyzer: The ComplaintAnalyzer instance to use
    """
    print("=" * 60)
    print("📋 Complaint Analysis")
    print("=" * 60)
    print(f"Complaint: {complaint}\n")
    
    # Step 1: Extract place name using LLM
    print("🤖 Step 1: Extracting place name using LLM...")
    result = analyzer.analyze_complaint(complaint)
    
    if not result:
        print("❌ No place name found in the complaint or geocoding failed.")
        return
    
    print(f"✅ Place name extracted: {result['place_name']}\n")
    
    # Step 2: Display geocoding results
    print("📍 Step 2: Geocoding place name...")
    print(f"✅ Geocoding successful!\n")
    
    display_location_details(result)


def interactive_mode(analyzer: ComplaintAnalyzer) -> None:
    """
    Run the analyzer in interactive mode.
    
    Args:
        analyzer: The ComplaintAnalyzer instance to use
    """
    print("\n" + "=" * 60)
    print("🏢 Complaint Location Analyzer - Interactive Mode")
    print("=" * 60)
    
    while True:
        print("\nWhat's your complaint? Please provide the place name too.")
        print("(Type 'quit' or 'exit' to end)")
        
        complaint = input("\nYour complaint: ").strip()
        
        if complaint.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Thank you for using Complaint Location Analyzer!")
            break
        
        if not complaint:
            print("⚠️  Please enter a complaint.")
            continue
        
        analyze_complaint_cli(complaint, analyzer)


def test_mode(analyzer: ComplaintAnalyzer) -> None:
    """
    Run the analyzer in test mode with predefined complaints.
    
    Args:
        analyzer: The ComplaintAnalyzer instance to use
    """
    test_complaints = [
        "The parking at UiTM Shah Alam is terrible and always full.",
        "There's a lot of traffic near KLCC Mall during rush hour.",
        "The street lights in Central Market area are broken.",
        "The food court at Sunway Pyramid is very dirty.",
    ]
    
    print("\n" + "=" * 60)
    print("🧪 Running in Test Mode")
    print("=" * 60)
    
    for i, complaint in enumerate(test_complaints, 1):
        print(f"\n\n{'=' * 60}")
        print(f"Test Case {i}/{len(test_complaints)}")
        print(f"{'=' * 60}")
        analyze_complaint_cli(complaint, analyzer)
        input("\nPress Enter to continue to next test case...")


def main() -> None:
    """Main entry point for the CLI application."""
    try:
        # Validate API keys by accessing settings
        _ = settings.openrouter_api_key
        _ = settings.distancematrix_api_key
        print("✅ API keys loaded successfully!")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nPlease ensure you have set the required API keys in your .env file:")
        print("- OPENROUTER_API_KEY")
        print("- DISTANCEMATRIX_API_KEY")
        sys.exit(1)
    
    # Create analyzer instance
    analyzer = ComplaintAnalyzer()
    
    # Ask user for mode
    print("\nSelect mode:")
    print("1. Interactive mode (enter your own complaints)")
    print("2. Test mode (run predefined test cases)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "2":
        test_mode(analyzer)
    else:
        interactive_mode(analyzer)


if __name__ == "__main__":
    main()
