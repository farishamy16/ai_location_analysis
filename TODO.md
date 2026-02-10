# Make it into API

1. [ ] install FastAPI
2. [ ] get kintone API
3. [ ] understand kintone app field/structure
   - Geolocation apps
   - Reporting Sytem
4. [ ] improve routing accuracy in a simple way

{
"success": true,
"message": "Complaint processed successfully",
"timestamp": "2026-02-10T09:59:04.432396",
"location_data": {
"place_name": "klcc",
"formatted_address": "Jalan Ampang, Bukit Bintang, Kuala Lumpur 50400, Malaysia",
"lat": 3.1590889,
"lng": 101.712878
},
"routing_result": {
"ticket_id": "CMP-20260210-1E923",
"department": {
"id": "dept_safety",
"name": "Public Safety Department",
"email": "safety@city.gov",
"phone": "+60-3-4567-8901",
"categories": [
"crime",
"harassment",
"dangerous_area",
"safety",
"security"
]
},
"priority": "critical",
"estimated_response_hours": 8,
"classification": {
"category": "safety",
"severity": "high",
"urgency": "emergency",
"summary": "Fire at KLCC causing a dangerous situation.",
"keywords": [
"terbakar",
"fire"
],
"confidence": 0.95,
"classification_method": "llm",
"classification_confidence": 0.95,
"llm_category": null,
"semantic_category": null,
"all_scores": null
},
"user_info": {
"name": "faris",
"email": "abc@gmail.com",
"phone": "0132482939"
},
"routed_at": "2026-02-10T09:58:59.929155"
},
"notification_status": {
"department_notification_sent": false,
"user_confirmation_sent": false,
"department_notification_error": "SMTP not configured",
"user_notification_error": null
}
}
