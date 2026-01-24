"""
OpenRouter LLM service for AI-powered text processing.
Provides a clean interface to the OpenRouter API using LangChain.
"""

from typing import Optional, Dict, Any
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
