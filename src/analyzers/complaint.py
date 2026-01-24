"""
Complaint Location Analyzer - Business Logic
Combines OpenRouter LLM with Distance Matrix API to extract place names from complaints
and retrieve their coordinates.
"""

from typing import Optional, Dict, Any
from src.services.openrouter import OpenRouterService, extract_place_name
from src.services.distancematrix import DistanceMatrixService, geocode_address


class ComplaintAnalyzer:
    """Analyzes complaints to extract location information."""
    
    def __init__(
        self,
        llm_service: Optional[OpenRouterService] = None,
        geocoding_service: Optional[DistanceMatrixService] = None,
    ):
        """
        Initialize the complaint analyzer.
        
        Args:
            llm_service: Optional LLM service. If not provided, uses default.
            geocoding_service: Optional geocoding service. If not provided, uses default.
        """
        self.llm_service = llm_service or OpenRouterService()
        self.geocoding_service = geocoding_service or DistanceMatrixService()
    
    def extract_place_name(self, complaint: str) -> Optional[str]:
        """
        Extract place name from a complaint using LLM.
        
        Args:
            complaint: The user's complaint text
            
        Returns:
            The extracted place name, or None if no place is found
        """
        return self.llm_service.extract_place_name(complaint)
    
    def geocode_place(self, place_name: str) -> Dict[str, Any]:
        """
        Geocode a place name to get coordinates.
        
        Args:
            place_name: The place name to geocode
            
        Returns:
            Dictionary with lat, lng, formatted_address, and raw data
            
        Raises:
            ValueError: If geocoding fails
        """
        return self.geocoding_service.geocode_address(place_name)
    
    def analyze_complaint(self, complaint: str) -> Optional[Dict[str, Any]]:
        """
        Analyze a complaint to extract the place name and get its coordinates.
        
        Args:
            complaint: The user's complaint text
            
        Returns:
            Dictionary with location data (lat, lng, formatted_address, raw),
            or None if place name extraction or geocoding fails
        """
        # Step 1: Extract place name using LLM
        place_name = self.extract_place_name(complaint)
        
        if not place_name:
            return None
        
        # Step 2: Geocode the place name
        try:
            location_data = self.geocode_place(place_name)
            # Add the extracted place name to the result
            location_data["place_name"] = place_name
            return location_data
        except Exception:
            return None


# Create a default analyzer instance for convenience
default_analyzer = ComplaintAnalyzer()


def analyze_complaint(complaint: str) -> Optional[Dict[str, Any]]:
    """
    Convenience function to analyze a complaint using the default analyzer.
    
    Args:
        complaint: The user's complaint text
        
    Returns:
        Dictionary with location data (lat, lng, formatted_address, raw),
        or None if place name extraction or geocoding fails
    """
    return default_analyzer.analyze_complaint(complaint)
