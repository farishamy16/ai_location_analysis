"""
Centralized configuration management for AI Location Analysis project.
Loads all environment variables and provides a single source of truth for configuration.
"""

import os
from typing import Optional
from dotenv import load_dotenv


class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
    @property
    def openrouter_api_key(self) -> str:
        """OpenRouter API key for LLM services."""
        key = os.getenv("OPENROUTER_API_KEY")
        if not key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        return key
    
    @property
    def distancematrix_api_key(self) -> str:
        """Distance Matrix API key for geocoding services."""
        key = os.getenv("DISTANCEMATRIX_API_KEY")
        if not key:
            raise ValueError("DISTANCEMATRIX_API_KEY not found in environment variables")
        return key
    
    @property
    def openrouter_base_url(self) -> str:
        """Base URL for OpenRouter API."""
        return os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    
    @property
    def openrouter_model(self) -> str:
        """Default model to use with OpenRouter."""
        return os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-v3.2")
    
    @property
    def openrouter_temperature(self) -> float:
        """Default temperature for OpenRouter LLM."""
        return float(os.getenv("OPENROUTER_TEMPERATURE", "0.7"))
    
    @property
    def distancematrix_geocode_url(self) -> str:
        """URL for Distance Matrix geocoding API."""
        return os.getenv("DISTANCEMATRIX_GEOCODE_URL", "https://api-v2.distancematrix.ai/maps/api/geocode/json")


# Global settings instance
settings = Settings()
