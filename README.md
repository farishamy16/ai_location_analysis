# AI Location Analysis

AI-powered complaint location analyzer and routing system using OpenRouter LLM and Distance Matrix API. Extracts place names from user complaints, geocodes them, and intelligently routes complaints to appropriate departments with confidence scoring.

## Features

- **Intelligent Place Extraction**: Uses OpenRouter LLM to identify and extract place names from natural language complaints
- **Geocoding Integration**: Leverages Distance Matrix API to convert place names into precise coordinates
- **Smart Complaint Routing**: Multi-stage classification system with confidence scoring (0.0-1.0)
- **Department Registry**: Automatic routing to appropriate departments based on complaint category
- **Semantic Matching**: Advanced keyword matching with weighted scoring
- **Interactive CLI**: User-friendly command-line interface with 4 modes
- **Email Notifications**: Optional SMTP-based notification system

## Installation

### Prerequisites

- Python 3.14 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd ai_location_analysis
```

2. Install dependencies:

```bash
uv sync
```

3. Configure environment variables (see below)

## Configuration

Create a `.env` file in the project root based on [`.env.example`](.env.example):

**Required:**

```bash
OPENROUTER_API_KEY=your_openrouter_api_key_here
DISTANCEMATRIX_API_KEY=your_distancematrix_api_key_here
```

**Optional:**

```bash
# OpenRouter Configuration
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=deepseek/deepseek-v3.2
OPENROUTER_TEMPERATURE=0.7

# Classification Configuration
CLASSIFICATION_TEMPERATURE=0.1
HIGH_CONFIDENCE_THRESHOLD=0.8
MEDIUM_CONFIDENCE_THRESHOLD=0.6
ENABLE_SEMANTIC_MATCHING=true

# Email Configuration (SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=complaints@yourapp.com
FROM_NAME=AI Complaint System
```

## Usage

### CLI Interface

Run the application from the project root:

```bash
python cli/main.py
```

Select a mode:

1. **Interactive Location Extraction Analysis**: Enter your own complaints for location analysis
2. **Location Extraction Analysis Tests**: Run predefined test cases
3. **Routing System Tests**: Test the multi-stage classification and routing system
4. **Submit Complaint (Full Workflow)**: Complete complaint submission with routing and notifications

**Example Output (Mode 1):**

```
Your complaint: The parking at UiTM Shah Alam is terrible and always full.

📋 Analyzing: The parking at UiTM Shah Alam is terrible and always full.
✅ Location: UiTM Shah Alam
📍 Address: Shah Alam, Selangor, Malaysia
🌐 Coordinates: 3.0732, 101.5184
```

**Example Output (Mode 4):**

```
📋 Analyzing: Broken street light at Central Market
✅ Location: Central Market
   Address: Kuala Lumpur, Malaysia
   Coordinates: 3.1517, 101.6945

🔍 Category: Infrastructure
📊 Severity: High | Urgency: Routine
🤖 Method: LLM (AI)
🟢 Confidence: 90%

🎫 Ticket: CMP-20260209-XYZ34
🏢 Department: Infrastructure Maintenance
⚡ Priority: HIGH
⏱️  Response: 24 hours
```

### Programmatic Usage

**Basic Complaint Analysis:**

```python
from src.analyzers.complaint import ComplaintAnalyzer

analyzer = ComplaintAnalyzer()
result = analyzer.analyze_complaint("The food court at Sunway Pyramid is very dirty.")
print(f"Place: {result['place_name']}")
print(f"Coordinates: ({result['lat']}, {result['lng']})")
```

**Complaint Routing:**

```python
from src.services.router import ComplaintRouter

router = ComplaintRouter()
result = router.route_complaint("Broken street light at Central Market")

print(f"Ticket ID: {result['ticket_id']}")
print(f"Department: {result['department']['name']}")
print(f"Priority: {result['priority']}")
print(f"Confidence: {result['classification']['classification_confidence']}")
```

**Geocoding:**

```python
from src.services.distancematrix import geocode_address

location = geocode_address("UiTM Shah Alam")
print(f"Coordinates: {location['lat']}, {location['lng']}")
print(f"Address: {location['formatted_address']}")
```

## Project Structure

```
ai_location_analysis/
├── src/
│   ├── config/
│   │   └── settings.py              # Configuration management
│   ├── services/
│   │   ├── distancematrix.py        # Distance Matrix API client
│   │   ├── openrouter.py           # OpenRouter LLM client
│   │   ├── router.py               # Complaint routing service
│   │   ├── semantic_matcher.py     # Semantic matching service
│   │   ├── department_registry.py  # Department registry
│   │   └── notifier.py             # Email notification service
│   └── analyzers/
│       └── complaint.py            # Complaint analysis logic
├── cli/
│   └── main.py                      # CLI interface
├── tests/                           # Test directory
├── .env.example                     # Environment variables template
├── pyproject.toml                   # Project configuration
├── PHASE1_IMPLEMENTATION.md         # Phase 1 documentation
└── README.md                        # This file
```

## Key Services

### ComplaintAnalyzer

Analyzes complaints and extracts location information.

### OpenRouterService

Interacts with OpenRouter LLM API for place extraction and complaint classification.

### ComplaintRouter

Routes complaints to appropriate departments using multi-stage classification with confidence scoring.

### DepartmentRegistry

Manages department assignments based on complaint category.

**Available Departments:**

- Traffic Management Department
- City Sanitation Services
- Infrastructure Maintenance
- Public Safety Department
- Environmental Services
- Commercial Services Department
- General Services

## Testing

Run built-in test modes via the CLI:

```bash
python cli/main.py
# Select option 2 for Location Extraction Tests
# Select option 3 for Routing System Tests
```

## Troubleshooting

**Import Errors:** Ensure you're running from the project root directory.

**Missing Dependencies:** Run `uv sync` to reinstall.

**API Key Errors:** Verify your `.env` file contains valid `OPENROUTER_API_KEY` and `DISTANCEMATRIX_API_KEY`.

**Geocoding Failures:** Check your Distance Matrix API key and internet connection.

**Low Confidence Scores:** Ensure complaint text is clear and specific. Adjust confidence thresholds in `.env` if needed.

**Email Notifications Not Sending:** Verify SMTP settings and credentials in `.env`.

## License

This project is provided as-is for educational and commercial use.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.
