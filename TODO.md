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
"timestamp": "2026-02-09T16:42:01.140379",
"location_data": {
"place_name": "UiTM Shah Alam",
"formatted_address": "Lebuhraya Persekutuan, Shah Alam 40450, Malaysia",
"lat": 3.06277365,
"lng": 101.5012000990051,
"raw": {
"address_components": [
{
"long_name": "Malaysia",
"short_name": "MY",
"types": [
"country",
"political"
]
},
{
"long_name": "Shah Alam",
"short_name": "Shah Alam",
"types": [
"administrative_area_level_3",
"political"
]
},
{
"long_name": "40450",
"short_name": "40450",
"types": [
"postal_code"
]
},
{
"long_name": "Lebuhraya Persekutuan",
"short_name": "Lebuhraya Persekutuan",
"types": [
"route"
]
},
{
"long_name": "UiTM Shah Alam (U/C)",
"short_name": "UiTM Shah Alam (U/C)",
"types": [
"name"
]
},
{
"long_name": "Selangor",
"short_name": "Selangor",
"types": [
"state",
"administrative_area_level_1",
"political"
]
}
],
"formatted_address": "Lebuhraya Persekutuan, Shah Alam 40450, Malaysia",
"geometry": {
"location": {
"lat": 3.06277365,
"lng": 101.5012000990051
},
"location_type": "APPROXIMATE",
"viewport": {
"northeast": {
"lat": 3.06277365,
"lng": 101.5012000990051
},
"southwest": {
"lat": 3.06277365,
"lng": 101.5012000990051
}
}
},
"place_id": "1044627091",
"plus_code": {},
"types": [
"street_address"
]
}
},
"routing_result": {
"ticket_id": "CMP-20260209-23285",
"department": {
"id": "dept_infrastructure",
"name": "Infrastructure Maintenance",
"email": "infrastructure@city.gov",
"phone": "+60-3-3456-7890",
"categories": [
"street_lights",
"broken_facilities",
"potholes",
"infrastructure",
"maintenance"
]
},
"priority": "high",
"estimated_response_hours": 24,
"classification": {
"category": "infrastructure",
"severity": "high",
"urgency": "urgent",
"summary": "Flooding at UiTM Shah Alam causing significant disruption.",
"keywords": [
"banjir",
"flood"
],
"confidence": 0.9,
"classification_method": "llm",
"classification_confidence": 0.9,
"llm_category": null,
"semantic_category": null,
"all_scores": null
},
"location": {
"lat": 3.06277365,
"lng": 101.5012000990051,
"formatted_address": "Lebuhraya Persekutuan, Shah Alam 40450, Malaysia",
"raw": {
"address_components": [
{
"long_name": "Malaysia",
"short_name": "MY",
"types": [
"country",
"political"
]
},
{
"long_name": "Shah Alam",
"short_name": "Shah Alam",
"types": [
"administrative_area_level_3",
"political"
]
},
{
"long_name": "40450",
"short_name": "40450",
"types": [
"postal_code"
]
},
{
"long_name": "Lebuhraya Persekutuan",
"short_name": "Lebuhraya Persekutuan",
"types": [
"route"
]
},
{
"long_name": "UiTM Shah Alam (U/C)",
"short_name": "UiTM Shah Alam (U/C)",
"types": [
"name"
]
},
{
"long_name": "Selangor",
"short_name": "Selangor",
"types": [
"state",
"administrative_area_level_1",
"political"
]
}
],
"formatted_address": "Lebuhraya Persekutuan, Shah Alam 40450, Malaysia",
"geometry": {
"location": {
"lat": 3.06277365,
"lng": 101.5012000990051
},
"location_type": "APPROXIMATE",
"viewport": {
"northeast": {
"lat": 3.06277365,
"lng": 101.5012000990051
},
"southwest": {
"lat": 3.06277365,
"lng": 101.5012000990051
}
}
},
"place_id": "1044627091",
"plus_code": {},
"types": [
"street_address"
]
},
"place_name": "UiTM Shah Alam"
},
"user_info": {
"name": "faris",
"email": "abc@gmail.com",
"phone": "0123627475"
},
"routed_at": "2026-02-09T16:41:59.700319"
},
"notification_status": {
"department_notification_sent": false,
"user_confirmation_sent": false,
"department_notification_error": "'charmap' codec can't encode character '\\u274c' in position 0: character maps to <undefined>",
"user_notification_error": "'charmap' codec can't encode character '\\u274c' in position 0: character maps to <undefined>"
}
}
