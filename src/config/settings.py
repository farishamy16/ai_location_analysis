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
    def classification_temperature(self) -> float:
        """Temperature for complaint classification (lower for consistency)."""
        return float(os.getenv("CLASSIFICATION_TEMPERATURE", "0.1"))
    
    @property
    def high_confidence_threshold(self) -> float:
        """Threshold for high confidence classification."""
        return float(os.getenv("HIGH_CONFIDENCE_THRESHOLD", "0.8"))
    
    @property
    def medium_confidence_threshold(self) -> float:
        """Threshold for medium confidence classification."""
        return float(os.getenv("MEDIUM_CONFIDENCE_THRESHOLD", "0.6"))
    
    @property
    def enable_semantic_matching(self) -> bool:
        """Enable semantic similarity matching for classification."""
        return os.getenv("ENABLE_SEMANTIC_MATCHING", "true").lower() == "true"
    
    @property
    def distancematrix_geocode_url(self) -> str:
        """URL for Distance Matrix geocoding API."""
        return os.getenv("DISTANCEMATRIX_GEOCODE_URL", "https://api-v2.distancematrix.ai/maps/api/geocode/json")
    
    # Email Settings
    @property
    def smtp_server(self) -> Optional[str]:
        """SMTP server address for sending emails."""
        return os.getenv("SMTP_SERVER")
    
    @property
    def smtp_port(self) -> int:
        """SMTP server port."""
        return int(os.getenv("SMTP_PORT", "587"))
    
    @property
    def smtp_username(self) -> Optional[str]:
        """SMTP username for authentication."""
        return os.getenv("SMTP_USERNAME")
    
    @property
    def smtp_password(self) -> Optional[str]:
        """SMTP password for authentication."""
        return os.getenv("SMTP_PASSWORD")
    
    @property
    def from_email(self) -> str:
        """From email address for outgoing emails."""
        return os.getenv("FROM_EMAIL", "complaints@yourapp.com")
    
    @property
    def from_name(self) -> str:
        """From name for outgoing emails."""
        return os.getenv("FROM_NAME", "AI Complaint System")
    
    # Database Settings
    @property
    def database_url(self) -> str:
        """Database connection URL."""
        return os.getenv("DATABASE_URL", "sqlite:///complaints.db")


# Global settings instance
settings = Settings()
