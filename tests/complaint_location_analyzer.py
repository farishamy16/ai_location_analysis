"""
Complaint Location Analyzer
Combines OpenRouter LLM with Distance Matrix API to extract place names from complaints
and retrieve their coordinates.
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import requests
import json

# Load environment variables
load_dotenv()

# API Keys
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DISTANCEMATRIX_API_KEY = os.getenv("DISTANCEMATRIX_API_KEY")


def geocode_address(address: str) -> Dict[str, Any]:
    """
    Geocode an address using Distance Matrix API
    
    Args:
        address: The place name or address to geocode
        
    Returns:
        Dictionary with lat, lng, formatted_address, and raw data
        
    Raises:
        ValueError: If geocoding fails
    """
    url = "https://api-v2.distancematrix.ai/maps/api/geocode/json"
    params = {
        "address": address,
        "key": DISTANCEMATRIX_API_KEY,
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()

    if data.get("status") != "OK" or not data.get("result"):
        raise ValueError(f"Geocoding failed: {data.get('status')}")

    first = data["result"][0]
    location = first["geometry"]["location"]
    return {
        "lat": location["lat"],
        "lng": location["lng"],
        "formatted_address": first.get("formatted_address"),
        "raw": first,
    }


def extract_place_name(complaint: str) -> Optional[str]:
    """
    Use LLM to extract the place name from a complaint
    
    Args:
        complaint: The user's complaint text
        
    Returns:
        The extracted place name, or None if no place is found or an error occurs
    """
    model_name = "deepseek/deepseek-v3.2"
    
    llm = ChatOpenAI(
        model=model_name,
        api_key=OPENROUTER_API_KEY or "",  # type: ignore
        base_url="https://openrouter.ai/api/v1",
        temperature=0.3,  # Lower temperature for more consistent extraction
    )

    # Create a prompt template for place name extraction
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant that extracts place names from user complaints.
Your task is to identify and extract ONLY the place name mentioned in the complaint.

Rules:
- Extract only the place name (e.g., "UiTM Shah Alam", "KLCC", "Central Market")
- Do not include any other text or explanation
- If no place name is found, respond with "No place found"
- Keep the place name as specific as possible"""),
        ("human", "Complaint: {complaint}\n\nPlace name:")
    ])
    
    # Create the chain
    chain = prompt | llm | StrOutputParser()
    
    try:
        place_name = chain.invoke({"complaint": complaint})
        place_name = place_name.strip()
        
        if place_name.lower() == "no place found" or not place_name:
            return None
            
        return place_name
    except Exception as e:
        print(f"❌ Error extracting place name: {e}")
        return None


def analyze_complaint(complaint: str) -> Optional[Dict[str, Any]]:
    """
    Analyze a complaint to extract the place name and get its coordinates
    
    Args:
        complaint: The user's complaint text
        
    Returns:
        Dictionary with location data (lat, lng, formatted_address, raw), 
        or None if place name extraction or geocoding fails
    """
    print("=" * 60)
    print("📋 Complaint Analysis")
    print("=" * 60)
    print(f"Complaint: {complaint}\n")
    
    # Step 1: Extract place name using LLM
    print("🤖 Step 1: Extracting place name using LLM...")
    place_name = extract_place_name(complaint)
    
    if not place_name:
        print("❌ No place name found in the complaint.")
        return None
    
    print(f"✅ Place name extracted: {place_name}\n")
    
    # Step 2: Geocode the place name
    print("📍 Step 2: Geocoding place name...")
    try:
        location_data = geocode_address(place_name)
        print(f"✅ Geocoding successful!\n")
        
        # Display results
        print("=" * 60)
        print("📍 Location Details")
        print("=" * 60)
        print(f"Place Name: {place_name}")
        print(f"Formatted Address: {location_data['formatted_address']}")
        print(f"Latitude: {location_data['lat']}")
        print(f"Longitude: {location_data['lng']}")
        print("=" * 60)
        
        return location_data
    except Exception as e:
        print(f"❌ Geocoding failed: {e}")
        return None


def interactive_mode():
    """
    Run the analyzer in interactive mode
    """
    print("\n" + "=" * 60)
    print("🏢 Complaint Location Analyzer")
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
        
        analyze_complaint(complaint)


def test_mode():
    """
    Run the analyzer in test mode with predefined complaints
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
        analyze_complaint(complaint)
        input("\nPress Enter to continue to next test case...")


if __name__ == "__main__":
    # Check API keys
    if not OPENROUTER_API_KEY:
        print("❌ OPENROUTER_API_KEY not found in environment variables!")
        print("Please set your OpenRouter API key in .env file")
        exit(1)
    
    if not DISTANCEMATRIX_API_KEY:
        print("❌ DISTANCEMATRIX_API_KEY not found in environment variables!")
        print("Please set your Distance Matrix API key in .env file")
        exit(1)
    
    print("✅ API keys loaded successfully!")
    
    # Ask user for mode
    print("\nSelect mode:")
    print("1. Interactive mode (enter your own complaints)")
    print("2. Test mode (run predefined test cases)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "2":
        test_mode()
    else:
        interactive_mode()
