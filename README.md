# AI Location Analysis

AI-powered complaint location analyzer using OpenRouter LLM and Distance Matrix API. This tool extracts place names from user complaints and geocodes them to provide precise location information.

## Features

- **Intelligent Place Extraction**: Uses OpenRouter LLM to identify and extract place names from natural language complaints
- **Geocoding Integration**: Leverages Distance Matrix API to convert place names into precise coordinates
- **Interactive CLI**: User-friendly command-line interface for real-time complaint analysis
- **Test Mode**: Predefined test cases for quick validation and demonstration
- **Modular Architecture**: Clean separation of concerns with services, analyzers, and configuration

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

3. Configure environment variables (see [Configuration](#configuration))

## Configuration

Create a `.env` file in the project root based on [`.env.example`](.env.example):

```bash
# Required: OpenRouter API Key
# Get your API key from https://openrouter.ai/keys
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Required: Distance Matrix API Key
# Get your API key from https://distancematrix.ai/
DISTANCEMATRIX_API_KEY=your_distancematrix_api_key_here

# Optional: OpenRouter Configuration
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=deepseek/deepseek-v3.2
OPENROUTER_TEMPERATURE=0.7

# Optional: Distance Matrix Configuration
DISTANCEMATRIX_GEOCODE_URL=https://api-v2.distancematrix.ai/maps/api/geocode/json
```

## Usage

### CLI Interface

Run the application from the project root:

```bash
python cli/main.py
```

You'll be prompted to select a mode:

1. **Interactive Mode**: Enter your own complaints for analysis
2. **Test Mode**: Run predefined test cases to demonstrate functionality

#### Interactive Mode Example

```
What's your complaint? Please provide the place name too.
(Type 'quit' or 'exit' to end)

Your complaint: The parking at UiTM Shah Alam is terrible and always full.

📋 Complaint Analysis
============================================================
Complaint: The parking at UiTM Shah Alam is terrible and always full.

🤖 Step 1: Extracting place name using LLM...
✅ Place name extracted: UiTM Shah Alam

📍 Step 2: Geocoding place name...
✅ Geocoding successful!

============================================================
📍 Location Details
============================================================
Place Name: UiTM Shah Alam
Formatted Address: Shah Alam, Selangor, Malaysia
Latitude: 3.0732
Longitude: 101.5184
============================================================
```

### Programmatic Usage

#### Distance Matrix Service

```python
from src.services.distancematrix import geocode_address

# Geocode an address
location = geocode_address("UiTM Shah Alam")
print(f"Coordinates: {location['lat']}, {location['lng']}")
print(f"Address: {location['formatted_address']}")
```

#### OpenRouter LLM Service

```python
from src.services.openrouter import OpenRouterService

# Extract place name from complaint
service = OpenRouterService()
place_name = service.extract_place_name("The parking at KLCC is bad.")
print(f"Extracted place: {place_name}")
```

#### Complaint Analyzer

```python
from src.analyzers.complaint import ComplaintAnalyzer

# Analyze a complaint
analyzer = ComplaintAnalyzer()
result = analyzer.analyze_complaint("The food court at Sunway Pyramid is very dirty.")

if result:
    print(f"Place: {result['place_name']}")
    print(f"Address: {result['formatted_address']}")
    print(f"Coordinates: ({result['lat']}, {result['lng']})")
```

## Project Structure

```
ai_location_analysis/
├── src/
│   ├── config/
│   │   └── settings.py          # Configuration management
│   ├── services/
│   │   ├── distancematrix.py    # Distance Matrix API client
│   │   └── openrouter.py       # OpenRouter LLM client
│   └── analyzers/
│       └── complaint.py        # Complaint analysis logic
├── cli/
│   └── main.py                  # CLI interface
├── tests/
│   ├── test_openrouter.py
│   ├── test_complaint_analyzer.py
│   └── distancematrix.py
├── .env.example                 # Environment variables template
├── pyproject.toml              # Project configuration
└── README.md                   # This file
```

## API Reference

### ComplaintAnalyzer

Main class for analyzing complaints and extracting location information.

**Methods:**

- [`analyze_complaint(complaint: str) -> dict`](src/analyzers/complaint.py): Analyzes a complaint and returns location data

**Returns:**

```python
{
    'place_name': str,           # Extracted place name
    'formatted_address': str,     # Full address
    'lat': float,                # Latitude
    'lng': float                 # Longitude
}
```

### OpenRouterService

Service for interacting with OpenRouter LLM API.

**Methods:**

- [`extract_place_name(complaint: str) -> str`](src/services/openrouter.py): Extracts place name from complaint text

### Distance Matrix Service

Service for geocoding addresses using Distance Matrix API.

**Functions:**

- [`geocode_address(address: str) -> dict`](src/services/distancematrix.py): Converts address to coordinates

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python tests/test_openrouter.py
python tests/test_complaint_analyzer.py

# Run with uv
uv run pytest tests/
```

## Troubleshooting

### Import Errors

If you encounter import errors, ensure you're running commands from the project root directory:

```bash
cd c:/Users/dev2_/Documents/Projects/ai_location_analysis
python cli/main.py
```

### Missing Dependencies

If dependencies are missing, reinstall them:

```bash
uv sync
```

### API Key Errors

If you see API key errors:

1. Verify your `.env` file exists in the project root
2. Ensure it contains both required keys:
   - `OPENROUTER_API_KEY`
   - `DISTANCEMATRIX_API_KEY`
3. Check that the keys are valid and active

### Geocoding Failures

If geocoding fails:

1. Verify the Distance Matrix API key is valid
2. Ensure the place name is recognizable
3. Check your internet connection

## License

This project is provided as-is for educational and commercial use.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.
