"""
Test file for complaint routing workflow.
Tests the complete flow from complaint submission to routing and notification.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.analyzers.complaint import ComplaintAnalyzer
from src.services.router import ComplaintRouter
from src.services.notifier import NotificationService
from src.db.connection import init_db, close_db_connection
from src.db.repositories import ComplaintRepository


def test_complaint_routing():
    """Test the complete complaint routing workflow."""
    
    print("=" * 60)
    print("🧪 Testing Complaint Routing Workflow")
    print("=" * 60)
    
    # Initialize database
    print("\n1️⃣  Initializing database...")
    init_db()
    
    # Create service instances
    analyzer = ComplaintAnalyzer()
    router = ComplaintRouter()
    notifier = NotificationService()
    
    # Test complaint
    test_complaints = [
        {
            'text': 'The parking at UiTM Shah Alam is terrible and always full.',
            'user_info': {'name': 'Test User', 'email': 'test@example.com'}
        },
        {
            'text': 'There are broken street lights in Central Market area.',
            'user_info': {'name': 'Test User 2', 'email': 'test2@example.com'}
        },
        {
            'text': 'The food court at Sunway Pyramid is very dirty.',
            'user_info': {'name': 'Test User 3', 'email': 'test3@example.com'}
        }
    ]
    
    for i, test_case in enumerate(test_complaints, 1):
        print(f"\n{'=' * 60}")
        print(f"Test Case {i}/{len(test_complaints)}")
        print(f"{'=' * 60}")
        
        complaint_text = test_case['text']
        user_info = test_case['user_info']
        
        print(f"\n📝 Complaint: {complaint_text}")
        print(f"👤 User: {user_info['name']} ({user_info['email']})")
        
        # Step 1: Analyze complaint (extract location)
        print("\n📍 Step 1: Analyzing complaint...")
        location_data = analyzer.analyze_complaint(complaint_text)
        
        if location_data:
            print(f"   ✅ Location found: {location_data.get('place_name', 'N/A')}")
            print(f"   📍 Address: {location_data.get('formatted_address', 'N/A')}")
        else:
            print("   ⚠️  No location found")
            location_data = {}
        
        # Step 2: Classify complaint
        print("\n🔍 Step 2: Classifying complaint...")
        classification = router.llm_service.classify_complaint(complaint_text)
        print(f"   ✅ Category: {classification['category']}")
        print(f"   ✅ Severity: {classification['severity']}")
        print(f"   ✅ Urgency: {classification['urgency']}")
        print(f"   📝 Summary: {classification['summary']}")
        
        # Step 3: Route complaint
        print("\n🧭 Step 3: Routing complaint...")
        routing_result = router.route_complaint(
            complaint=complaint_text,
            location_data=location_data,
            user_info=user_info,
            classification=classification
        )
        print(f"   ✅ Ticket ID: {routing_result['ticket_id']}")
        print(f"   ✅ Department: {routing_result['department']['name']}")
        print(f"   ✅ Priority: {routing_result['priority']}")
        print(f"   ✅ Expected Response: {routing_result['estimated_response_hours']} hours")
        
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
        print(f"   {'✅' if department_sent else '⚠️ '} Department notified")
        
        # Send confirmation to user
        user_sent = notifier.send_user_confirmation(
            user_info['email'],
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
        print(f"   {'✅' if user_sent else '⚠️ '} User confirmation sent")
        
        print(f"\n✅ Test case {i} completed successfully!")
    
    # Display statistics
    print(f"\n{'=' * 60}")
    print("📊 Database Statistics")
    print(f"{'=' * 60}")
    stats = ComplaintRepository.get_statistics()
    print(f"Total complaints: {stats['total']}")
    print(f"\nBy status:")
    for status, count in stats['by_status'].items():
        print(f"  - {status}: {count}")
    
    print(f"\nBy category:")
    for category, count in stats['by_category'].items():
        print(f"  - {category}: {count}")
    
    print(f"\nBy severity:")
    for severity, count in stats['by_severity'].items():
        print(f"  - {severity}: {count}")
    
    # Close database connection
    close_db_connection()
    
    print(f"\n{'=' * 60}")
    print("✅ All tests completed successfully!")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    try:
        test_complaint_routing()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
