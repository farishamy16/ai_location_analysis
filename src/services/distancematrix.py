"""
Distance Matrix API service for geocoding addresses and locations.
Provides a clean interface to the Distance Matrix geocoding API.
"""

import requests
from typing import Dict, Any, Optional
from src.config.settings import settings


class DistanceMatrixService:
    """Service for interacting with Distance Matrix geocoding API."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize the Distance Matrix service.
        
        Args:
            api_key: Optional API key. If not provided, uses settings.
            base_url: Optional base URL. If not provided, uses settings.
        """
        self.api_key = api_key or settings.distancematrix_api_key
        self.base_url = base_url or settings.distancematrix_geocode_url
    
    def geocode_address(self, address: str) -> Dict[str, Any]:
        """
        Geocode an address using Distance Matrix API.
        
        Args:
            address: The place name or address to geocode
            
        Returns:
            Dictionary with lat, lng, formatted_address, and raw data
            
        Raises:
            ValueError: If geocoding fails
            requests.HTTPError: If the API request fails
        """
        params = {
            "address": address,
            "key": self.api_key,
        }
        
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
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


# Create a default service instance for convenience
default_service = DistanceMatrixService()


def geocode_address(address: str) -> Dict[str, Any]:
    """
    Convenience function to geocode an address using the default service.
    
    Args:
        address: The place name or address to geocode
        
    Returns:
        Dictionary with lat, lng, formatted_address, and raw data
        
    Raises:
        ValueError: If geocoding fails
        requests.HTTPError: If the API request fails
    """
    return default_service.geocode_address(address)
