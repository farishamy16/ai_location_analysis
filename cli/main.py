"""
CLI interface for the Complaint Location Analyzer.
Provides interactive, test, and submission modes for analyzing and routing complaints.
"""

import sys
from src.analyzers.complaint import ComplaintAnalyzer
from src.services.router import ComplaintRouter
from src.services.notifier import NotificationService
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


def display_routing_result(routing_data: dict) -> None:
    """Display routing result in a formatted way."""
    print("\n" + "=" * 60)
    print("🎫 Routing Result")
    print("=" * 60)
    print(f"Ticket ID: {routing_data['ticket_id']}")
    print(f"Department: {routing_data['department']['name']}")
    print(f"Priority: {routing_data['priority'].upper()}")
    print(f"Expected Response: {routing_data['estimated_response_hours']} hours")
    print(f"Contact Email: {routing_data['department']['email']}")
    print(f"Contact Phone: {routing_data['department']['phone']}")
    print("=" * 60)


def display_classification_result(classification: dict) -> None:
    """Display classification result in a formatted way."""
    print("\n" + "=" * 60)
    print("🔍 Classification Result")
    print("=" * 60)
    print(f"Category: {classification['category'].title()}")
    print(f"Severity: {classification['severity'].title()}")
    print(f"Urgency: {classification['urgency'].title()}")
    print(f"Summary: {classification['summary']}")
    print(f"Keywords: {', '.join(classification.get('keywords', ['N/A']))}")
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


def submit_complaint_mode(analyzer: ComplaintAnalyzer, router: ComplaintRouter, notifier: NotificationService) -> None:
    """
    Submit a new complaint with full routing and notification.
    
    Args:
        analyzer: The ComplaintAnalyzer instance to use
        router: The ComplaintRouter instance to use
        notifier: The NotificationService instance to use
    """
    print("\n" + "=" * 60)
    print("📝 Submit New Complaint")
    print("=" * 60)
    
    # Get complaint text
    complaint = input("\nDescribe your complaint: ").strip()
    if not complaint:
        print("⚠️  Complaint cannot be empty.")
        return
    
    # Get user information (optional)
    print("\nOptional: Provide your contact information for tracking")
    user_name = input("Your name (optional, press Enter to skip): ").strip() or None
    user_email = input("Your email (optional, press Enter to skip): ").strip() or None
    user_phone = input("Your phone (optional, press Enter to skip): ").strip() or None
    
    user_info = {}
    if user_name:
        user_info['name'] = user_name
    if user_email:
        user_info['email'] = user_email
    if user_phone:
        user_info['phone'] = user_phone
    
    print("\n" + "=" * 60)
    print("📋 Complaint Analysis")
    print("=" * 60)
    print(f"Complaint: {complaint}\n")
    
    # Step 1: Extract place name and geocode
    print("🤖 Step 1: Extracting place name and geocoding...")
    location_data = analyzer.analyze_complaint(complaint)
    
    if not location_data:
        print("⚠️  No location found. Proceeding without location data.")
        location_data = {}
    else:
        print(f"✅ Location: {location_data.get('place_name', 'N/A')}")
        print(f"   Address: {location_data.get('formatted_address', 'N/A')}")
    
    # Step 2: Classify complaint
    print("\n🔍 Step 2: Classifying complaint...")
    classification = router.llm_service.classify_complaint(complaint)
    display_classification_result(classification)
    
    # Step 3: Route complaint
    print("\n🧭 Step 3: Routing complaint to department...")
    routing_result = router.route_complaint(
        complaint=complaint,
        location_data=location_data,
        user_info=user_info,
        classification=classification
    )
    display_routing_result(routing_result)
    
    # Step 4: Send notifications
    print("\n📧 Step 4: Sending notifications...")
    
    # Send to department
    department_sent = notifier.send_department_notification(
        routing_result['department']['email'],
        {
            'ticket_id': routing_result['ticket_id'],
            'department': routing_result['department'],
            'priority': routing_result['priority'],
            'estimated_response_hours': routing_result['estimated_response_hours'],
            'classification': routing_result['classification'],
            'location': routing_result['location'],
            'user_info': routing_result['user_info'],
            'routed_at': routing_result['routed_at']
        }
    )
    
    # Send confirmation to user if email provided
    if user_email:
        user_sent = notifier.send_user_confirmation(
            user_email,
            {
                'ticket_id': routing_result['ticket_id'],
                'department': routing_result['department'],
                'priority': routing_result['priority'],
                'estimated_response_hours': routing_result['estimated_response_hours'],
                'classification': routing_result['classification'],
                'location': routing_result['location'],
                'routed_at': routing_result['routed_at']
            }
        )
    else:
        user_sent = False
    
    # Final summary
    print("\n" + "=" * 60)
    print("✅ Complaint Submitted Successfully!")
    print("=" * 60)
    print(f"🎫 Ticket ID: {routing_result['ticket_id']}")
    print(f"🏢 Department: {routing_result['department']['name']}")
    print(f"📧 Department notified: {'Yes' if department_sent else 'No (SMTP not configured)'}")
    if user_email:
        print(f"📧 Confirmation sent to user: {'Yes' if user_sent else 'No (SMTP not configured)'}")
    print(f"⏱️  Expected response time: {routing_result['estimated_response_hours']} hours")
    print("\n" + "=" * 60)
    print("Thank you for your feedback!")
    print("=" * 60)


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
    
    # Create service instances
    analyzer = ComplaintAnalyzer()
    router = ComplaintRouter()
    notifier = NotificationService()
    
    # Ask user for mode
    print("\nSelect mode:")
    print("1. Interactive mode (enter your own complaints)")
    print("2. Test mode (run predefined test cases)")
    print("3. Submit complaint (with routing and email notifications)")
    
    choice = input("\nEnter choice (1, 2, or 3): ").strip()
    
    if choice == "2":
        test_mode(analyzer)
    elif choice == "3":
        submit_complaint_mode(analyzer, router, notifier)
    else:
        interactive_mode(analyzer)


if __name__ == "__main__":
    main()
