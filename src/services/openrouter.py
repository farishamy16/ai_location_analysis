"""
OpenRouter LLM service for AI-powered text processing.
Provides a clean interface to the OpenRouter API using LangChain.
"""

import json
from typing import Optional, Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.config.settings import settings


class OpenRouterService:
    """Service for interacting with OpenRouter LLM API."""
    
    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: Optional[float] = None,
    ):
        """
        Initialize the OpenRouter service.
        
        Args:
            model: Model name to use. If not provided, uses settings.
            api_key: API key. If not provided, uses settings.
            base_url: Base URL for API. If not provided, uses settings.
            temperature: Temperature for LLM. If not provided, uses settings.
        """
        self.model = model or settings.openrouter_model
        self.api_key = api_key or settings.openrouter_api_key
        self.base_url = base_url or settings.openrouter_base_url
        self.temperature = temperature if temperature is not None else settings.openrouter_temperature
        
        self.llm = ChatOpenAI(
            model=self.model,
            api_key=self.api_key, # type: ignore
            base_url=self.base_url,
            temperature=self.temperature,
        )
    
    def invoke(self, messages: list) -> str:
        """
        Invoke the LLM with a list of messages.
        
        Args:
            messages: List of messages (HumanMessage, SystemMessage, etc.)
            
        Returns:
            The LLM response content
        """
        response = self.llm.invoke(messages)
        content = response.content
        # Handle both string and list responses
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            # If it's a list, convert to string
            return str(content)
        return str(content)
    
    def create_chain(
        self,
        prompt_template: ChatPromptTemplate,
        output_parser: Optional[StrOutputParser] = None,
    ):
        """
        Create a LangChain chain with the given prompt template.
        
        Args:
            prompt_template: The prompt template to use
            output_parser: Optional output parser (defaults to StrOutputParser)
            
        Returns:
            A LangChain chain
        """
        parser = output_parser or StrOutputParser()
        return prompt_template | self.llm | parser
    
    def extract_place_name(self, complaint: str) -> Optional[str]:
        """
        Use LLM to extract place name from a complaint.
        
        Args:
            complaint: The user's complaint text
            
        Returns:
            The extracted place name, or None if no place is found
        """
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
        
        chain = self.create_chain(prompt)
        
        try:
            place_name = chain.invoke({"complaint": complaint}).strip()
            
            if place_name.lower() == "no place found" or not place_name:
                return None
                
            return place_name
        except Exception as e:
            raise RuntimeError(f"Error extracting place name: {e}") from e
    
    def classify_complaint(self, complaint: str) -> Dict[str, Any]:
        """
        Use LLM to classify a complaint into category, severity, and urgency.
        
        Args:
            complaint: The user's complaint text
            
        Returns:
            Dictionary with classification results:
            {
                'category': str,           # Main category (traffic, sanitation, etc.)
                'severity': str,           # Severity level (low, medium, high, critical)
                'urgency': str,            # Urgency level (routine, urgent, emergency)
                'keywords': List[str],     # Key terms extracted
                'summary': str             # Brief summary of the complaint
            }
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant that classifies user complaints.
Your task is to analyze the complaint and extract key information.

Categories:
- traffic: parking, traffic lights, road conditions, traffic jams, congestion, heavy traffic, traffic volume, too many cars, traffic flow, traffic accidents, speeding, vehicles, cars, motorcycles, traffic congestion, gridlock, rush hour traffic, traffic delays
- sanitation: trash, cleanliness, pest control, waste management, garbage, rubbish, dirty, unclean, rodents, cockroaches, pests, waste collection, overflowing bins
- infrastructure: street lights, broken facilities, potholes, maintenance, broken benches, damaged roads, faulty equipment, public facilities, sidewalks, pedestrian paths, drainage
- safety: crime, harassment, dangerous areas, security concerns, theft, assault, robbery, suspicious activity, unsafe conditions, emergency situations
- environment: pollution, noise, green spaces, air quality, water pollution, air pollution, noise pollution, environmental hazards, toxic waste, illegal dumping
- commercial: food hygiene, shop complaints, business issues, restaurant hygiene, food safety, business violations, consumer complaints, service quality
- general: other complaints that don't fit specific categories, general inquiries, feedback, suggestions

Severity Levels:
- low: minor inconvenience, no immediate impact, cosmetic issues
- medium: affects daily activities, should be addressed soon, moderate discomfort
- high: significant impact, needs immediate attention, major disruption
- critical: dangerous situation, emergency response required, life-threatening

Urgency Levels:
- routine: can be handled during normal operations, no time pressure
- urgent: should be prioritized, affects many people
- emergency: requires immediate action, dangerous situation

Classification Guidelines:
1. Look for specific keywords related to each category
2. Consider the context and main issue being reported
3. If multiple categories apply, choose the most prominent one
4. Examples:
   - "Too many cars at UiTM Shah Alam" -> traffic (traffic volume/congestion)
   - "Heavy congestion on the highway" -> traffic
   - "Parking is always full" -> traffic
   - "Traffic is terrible downtown" -> traffic
   - "Broken street light" -> infrastructure
   - "Dirty food court" -> commercial
   - "Trash everywhere" -> sanitation

Output Format (JSON only):
{{
    "category": "category_name",
    "severity": "severity_level",
    "urgency": "urgency_level",
    "keywords": ["keyword1", "keyword2"],
    "summary": "Brief summary of the complaint"
}}"""),
            ("human", "Complaint: {complaint}\n\nClassification:")
        ])
        
        chain = self.create_chain(prompt)
        
        try:
            result = chain.invoke({"complaint": complaint}).strip()
            
            # Parse JSON response
            classification = json.loads(result)
            
            # Validate and normalize the response
            valid_categories = ['traffic', 'sanitation', 'infrastructure', 'safety', 'environment', 'commercial', 'general']
            valid_severity = ['low', 'medium', 'high', 'critical']
            valid_urgency = ['routine', 'urgent', 'emergency']
            
            classification['category'] = classification.get('category', 'general').lower()
            if classification['category'] not in valid_categories:
                classification['category'] = 'general'
            
            classification['severity'] = classification.get('severity', 'medium').lower()
            if classification['severity'] not in valid_severity:
                classification['severity'] = 'medium'
            
            classification['urgency'] = classification.get('urgency', 'routine').lower()
            if classification['urgency'] not in valid_urgency:
                classification['urgency'] = 'routine'
            
            classification['keywords'] = classification.get('keywords', [])
            classification['summary'] = classification.get('summary', complaint[:100])
            
            return classification
        except json.JSONDecodeError as e:
            # Fallback to basic classification if JSON parsing fails
            return {
                'category': 'general',
                'severity': 'medium',
                'urgency': 'routine',
                'keywords': [],
                'summary': complaint[:100]
            }
        except Exception as e:
            raise RuntimeError(f"Error classifying complaint: {e}") from e


# Create a default service instance for convenience
default_service = OpenRouterService()


def extract_place_name(complaint: str) -> Optional[str]:
    """
    Convenience function to extract place name using the default service.
    
    Args:
        complaint: The user's complaint text
        
    Returns:
        The extracted place name, or None if no place is found
    """
    return default_service.extract_place_name(complaint)
