"""
CLI interface for the Complaint Location Analyzer.
Provides interactive, test, and submission modes for analyzing and routing complaints.
"""

import sys
from src.analyzers.complaint import ComplaintAnalyzer
from src.services.router import ComplaintRouter
from src.services.notifier import NotificationService
from src.config.settings import settings


# Module-level constants for test data
LOCATION_TEST_COMPLAINTS = [
    "The parking at UiTM Shah Alam is terrible and always full.",
    "There's a lot of traffic near KLCC Mall during rush hour.",
    "The street lights in Central Market area are broken.",
    "The food court at Sunway Pyramid is very dirty.",
]

ROUTING_TEST_COMPLAINTS = [
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


def display_routing_result(routing_data: dict) -> None:
    """Display routing result in a formatted way."""
    print(f"\n🎫 Ticket: {routing_data['ticket_id']}")
    print(f"🏢 Department: {routing_data['department']['name']}")
    print(f"⚡ Priority: {routing_data['priority'].upper()}")
    print(f"⏱️  Response: {routing_data['estimated_response_hours']} hours")
    print(f"📧 Contact: {routing_data['department']['email']}")
    
    # Display keywords if available
    classification = routing_data.get('classification', {})
    if 'keywords' in classification and classification['keywords']:
        print(f"🔑 Keywords: {', '.join(classification['keywords'])}")


def display_classification_result(classification: dict) -> None:
    """Display classification result in a formatted way."""
    print(f"\n🔍 Category: {classification['category'].title()}")
    print(f"📊 Severity: {classification['severity'].title()} | Urgency: {classification['urgency'].title()}")
    
    # Display Phase 1 enhancements
    if 'classification_method' in classification:
        method = classification['classification_method']
        method_display = {
            'llm': 'LLM (AI)',
            'semantic': 'Semantic (Keywords)',
            'hybrid': 'Hybrid (LLM + Keywords)',
            'llm_fallback': 'LLM Fallback'
        }.get(method, method)
        print(f"🤖 Method: {method_display}")
    
    if 'classification_confidence' in classification:
        confidence = classification['classification_confidence']
        confidence_percent = int(confidence * 100)
        confidence_emoji = '🟢' if confidence >= 0.8 else '🟡' if confidence >= 0.6 else '🔴'
        print(f"{confidence_emoji} Confidence: {confidence_percent}%")


def analyze_complaint_cli(complaint: str, analyzer: ComplaintAnalyzer) -> None:
    """
    Analyze a complaint and display results via CLI.
    
    Args:
        complaint: The user's complaint text
        analyzer: The ComplaintAnalyzer instance to use
    """
    print(f"\n📋 Analyzing: {complaint}")
    
    result = analyzer.analyze_complaint(complaint)
    
    if not result:
        print("❌ No location found")
        return
    
    print(f"✅ Location: {result.get('place_name', 'N/A')}")
    print(f"📍 Address: {result.get('formatted_address', 'N/A')}")
    if result.get('lat') and result.get('lng'):
        print(f"🌐 Coordinates: {result.get('lat')}, {result.get('lng')}")


def interactive_mode(analyzer: ComplaintAnalyzer) -> None:
    """
    Run the analyzer in interactive location analysis mode.
    
    Args:
        analyzer: The ComplaintAnalyzer instance to use
    """
    print("\n🏢 Interactive Location Analysis (type 'quit' to exit)")
    
    while True:
        complaint = input("\nYour complaint: ").strip()
        
        if complaint.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if not complaint:
            print("⚠️  Please enter a complaint.")
            continue
        
        analyze_complaint_cli(complaint, analyzer)


def test_mode(analyzer: ComplaintAnalyzer) -> None:
    """
    Run location analysis tests with predefined complaints.
    
    Args:
        analyzer: The ComplaintAnalyzer instance to use
    """
    print("\n🧪 Location Analysis Tests")
    
    for i, complaint in enumerate(LOCATION_TEST_COMPLAINTS, 1):
        print(f"\n{'─' * 40}")
        print(f"Test {i}/{len(LOCATION_TEST_COMPLAINTS)}")
        print(f"{'─' * 40}")
        analyze_complaint_cli(complaint, analyzer)
        input("\nPress Enter to continue...")


def routing_test_mode(router: ComplaintRouter) -> None:
    """
    Test the routing system with various complaints.
    
    Args:
        router: The ComplaintRouter instance to use
    """
    print("\n🧪 Routing System Tests")
    print("Demonstrates multi-stage classification with confidence scoring\n")
    
    for i, complaint in enumerate(ROUTING_TEST_COMPLAINTS, 1):
        print(f"\n{'─' * 50}")
        print(f"Test {i}/{len(ROUTING_TEST_COMPLAINTS)}")
        print(f"{'─' * 50}")
        print(f"📋 Complaint: {complaint}")
        
        result = router.route_complaint(complaint)
        
        # Display classification using the existing function
        display_classification_result(result['classification'])
        
        # Display routing result
        display_routing_result(result)
        
        input("\nPress Enter to continue...")


def submit_complaint_mode(analyzer: ComplaintAnalyzer, router: ComplaintRouter, notifier: NotificationService) -> None:
    """
    Submit a new complaint with full routing and notification (complete workflow).
    
    Args:
        analyzer: The ComplaintAnalyzer instance to use
        router: The ComplaintRouter instance to use
        notifier: The NotificationService instance to use
    """
    print("\n📝 Submit Complaint (Full Workflow)")
    
    # Get complaint text
    complaint = input("\nDescribe your complaint: ").strip()
    if not complaint:
        print("⚠️  Complaint cannot be empty.")
        return
    
    # Get user information (optional)
    print("\nContact info (optional, press Enter to skip):")
    user_name = input("  Name: ").strip() or None
    user_email = input("  Email: ").strip() or None
    user_phone = input("  Phone: ").strip() or None
    
    user_info = {}
    if user_name:
        user_info['name'] = user_name
    if user_email:
        user_info['email'] = user_email
    if user_phone:
        user_info['phone'] = user_phone
    
    # Analyze complaint
    print(f"\n📋 Analyzing: {complaint}")
    
    # Extract location
    location_data = analyzer.analyze_complaint(complaint)
    if location_data:
        print(f"✅ Location: {location_data.get('place_name', 'N/A')}")
        print(f"   Address: {location_data.get('formatted_address', 'N/A')}")
        if location_data.get('lat') and location_data.get('lng'):
            print(f"   Coordinates: {location_data.get('lat')}, {location_data.get('lng')}")
    else:
        print("⚠️  No location found")
        location_data = {}
    
    # Route complaint (includes multi-stage classification)
    routing_result = router.route_complaint(
        complaint=complaint,
        location_data=location_data,
        user_info=user_info
    )
    
    # Display classification and routing results
    display_classification_result(routing_result['classification'])
    display_routing_result(routing_result)
    
    # Send notifications
    print("\n📧 Sending notifications...")
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
    
    user_sent = False
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
    
    # Final summary
    print(f"\n{'─' * 40}")
    print("✅ Complaint Submitted!")
    print(f"{'─' * 40}")
    print(f"🎫 Ticket: {routing_result['ticket_id']}")
    print(f"🏢 Department: {routing_result['department']['name']}")
    print(f"📧 Notified: {'Yes' if department_sent else 'No (SMTP not configured)'}")
    if user_email:
        print(f"📧 User confirmation: {'Yes' if user_sent else 'No (SMTP not configured)'}")
    print(f"⏱️  Response time: {routing_result['estimated_response_hours']} hours")
    print(f"{'─' * 40}")
    print("Thank you for your feedback!")
    print(f"{'─' * 40}")


def main() -> None:
    """Main entry point for the CLI application."""
    try:
        # Validate API keys by accessing settings
        _ = settings.openrouter_api_key
        _ = settings.distancematrix_api_key
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nRequired API keys in .env file:")
        print("- OPENROUTER_API_KEY")
        print("- DISTANCEMATRIX_API_KEY")
        sys.exit(1)
    
    # Ask user for mode
    print("\nSelect mode:")
    print("1. Interactive Location Extraction Analysis")
    print("2. Location Extraction Analysis Tests")
    print("3. Routing System Tests")
    print("4. Submit Complaint (Full Workflow)")
    
    choice = input("\nEnter choice (1, 2, 3, or 4): ").strip()
    
    # Validate input
    valid_choices = {"1", "2", "3", "4"}
    if choice not in valid_choices:
        print(f"⚠️  Invalid choice '{choice}'. Defaulting to interactive mode.")
        choice = "1"
    
    # Lazy initialize services based on mode selection
    if choice == "2":
        # Test mode only needs analyzer
        analyzer = ComplaintAnalyzer()
        test_mode(analyzer)
    elif choice == "3":
        # Routing test mode only needs router
        router = ComplaintRouter()
        routing_test_mode(router)
    elif choice == "4":
        # Submit mode needs all services
        analyzer = ComplaintAnalyzer()
        router = ComplaintRouter()
        notifier = NotificationService()
        submit_complaint_mode(analyzer, router, notifier)
    else:
        # Interactive mode only needs analyzer
        analyzer = ComplaintAnalyzer()
        interactive_mode(analyzer)


if __name__ == "__main__":
    main()
