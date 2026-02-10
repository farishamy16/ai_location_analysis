"""
Complaint Router Service
Intelligently routes complaints to appropriate departments based on analysis.

Combines LLM + Semantic + Registry to route complaints to departments
"""

from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from src.services.department_registry import DepartmentRegistry
from src.services.openrouter import OpenRouterService
from src.services.semantic_matcher import SemanticMatcher, SemanticMatchResult
from src.config.settings import settings


class ComplaintRouter:
    """Routes complaints to appropriate departments based on analysis."""
    
    def __init__(
        self,
        department_registry: Optional[DepartmentRegistry] = None,
        llm_service: Optional[OpenRouterService] = None,
        semantic_matcher: Optional[SemanticMatcher] = None,
    ):
        """
        Initialize the complaint router.
        
        Args:
            department_registry: Optional department registry. If not provided, uses default.
            llm_service: Optional LLM service. If not provided, uses default.
            semantic_matcher: Optional semantic matcher. If not provided, uses default.
        """
        self.department_registry = department_registry or DepartmentRegistry()
        self.llm_service = llm_service or OpenRouterService()
        self.semantic_matcher = semantic_matcher or SemanticMatcher()
    
    def generate_ticket_id(self) -> str:
        """
        Generate a unique ticket ID.
        
        Returns:
            A unique ticket ID in format CMP-YYYYMMDD-XXXXX
        """
        date_str = datetime.now().strftime("%Y%m%d")
        random_str = str(uuid.uuid4())[:5].upper()
        return f"CMP-{date_str}-{random_str}"
    
    def _multi_stage_classify(self, complaint: str) -> Dict[str, Any]:
        """
        Perform multi-stage classification using LLM and semantic matching.
        
        Args:
            complaint: The complaint text
            
        Returns:
            Classification dictionary with category and metadata
        """
        # Stage 1: LLM Classification with confidence scoring
        llm_classification = self.llm_service.classify_complaint(complaint)
        llm_confidence = llm_classification.get('confidence', 0.5)
        
        # Check if LLM confidence is high enough
        if llm_confidence >= settings.high_confidence_threshold:
            # High confidence - use LLM classification
            return {
                **llm_classification,
                'classification_method': 'llm',
                'classification_confidence': llm_confidence
            }
        
        # Stage 2: Semantic similarity matching
        if settings.enable_semantic_matching:
            semantic_result = self.semantic_matcher.find_best_match(complaint)
            
            # Check if semantic similarity is high enough
            if semantic_result.similarity >= settings.high_confidence_threshold:
                # High semantic similarity - use semantic match
                return {
                    'category': semantic_result.category,
                    'severity': llm_classification.get('severity', 'medium'),
                    'urgency': llm_classification.get('urgency', 'routine'),
                    'keywords': semantic_result.matched_keywords,
                    'summary': llm_classification.get('summary', complaint[:100]),
                    'confidence': semantic_result.similarity,
                    'classification_method': 'semantic',
                    'classification_confidence': semantic_result.similarity,
                    'all_scores': semantic_result.all_scores
                }
        
        # Stage 3: Hybrid approach - combine LLM and semantic
        if settings.enable_semantic_matching:
            semantic_result = self.semantic_matcher.find_best_match(complaint)
            
            # If semantic similarity is at least medium, use it
            if semantic_result.similarity >= settings.medium_confidence_threshold:
                # Use semantic match but keep LLM severity/urgency
                return {
                    'category': semantic_result.category,
                    'severity': llm_classification.get('severity', 'medium'),
                    'urgency': llm_classification.get('urgency', 'routine'),
                    'keywords': semantic_result.matched_keywords,
                    'summary': llm_classification.get('summary', complaint[:100]),
                    'confidence': max(llm_confidence, semantic_result.similarity),
                    'classification_method': 'hybrid',
                    'classification_confidence': max(llm_confidence, semantic_result.similarity),
                    'llm_category': llm_classification.get('category'),
                    'semantic_category': semantic_result.category,
                    'all_scores': semantic_result.all_scores
                }
        
        # Stage 4: Fallback to LLM classification with lower confidence
        return {
            **llm_classification,
            'classification_method': 'llm_fallback',
            'classification_confidence': llm_confidence
        }
    
    def route_complaint(
        self,
        complaint: str,
        location_data: Optional[Dict[str, Any]] = None,
        user_info: Optional[Dict[str, str]] = None,
        classification: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Route a complaint to the appropriate department.
        
        Args:
            complaint: The user's complaint text
            location_data: Optional location data (lat, lng, formatted_address, place_name)
            user_info: Optional user information (name, email, phone)
            classification: Optional pre-computed classification
            
        Returns:
            Dictionary with routing information:
            {
                'ticket_id': str,
                'department': dict,
                'priority': str,
                'estimated_response_hours': int,
                'classification': dict,
                'location': dict,
                'user_info': dict,
                'routed_at': str
            }
        """
        # Generate ticket ID
        ticket_id = self.generate_ticket_id()
        
        # Classify complaint using multi-stage approach if not provided
        if classification is None:
            classification = self._multi_stage_classify(complaint)
        
        # Get category from classification
        category = classification.get('category', 'general')
        
        # Get department based on category
        department = self.department_registry.get_department_by_category(category)
        
        # Fallback to general department if no department found
        if department is None:
            department = self.department_registry.get_department_by_category('general')
        
        # Final fallback - should never happen but ensures safety
        if department is None:
            # Create a default department structure
            department = {
                'id': 'dept_general',
                'name': 'General Services',
                'email': 'general@city.gov',
                'phone': '+60-3-7890-1234',
                'categories': ['general']
            }
        
        # Calculate response time based on severity
        severity = classification.get('severity', 'medium')
        estimated_response_hours = self.department_registry.get_response_time(
            department['id'],
            severity
        )
        
        # Determine priority based on severity and urgency
        priority = self._calculate_priority(
            severity,
            classification.get('urgency', 'routine')
        )
        
        # Build routing result
        routing_result = {
            'ticket_id': ticket_id,
            'department': {
                'id': department['id'],
                'name': department['name'],
                'email': department['email'],
                'phone': department['phone'],
                'categories': department['categories']
            },
            'priority': priority,
            'estimated_response_hours': estimated_response_hours,
            'classification': classification,
            'location': location_data or {},
            'user_info': user_info or {},
            'routed_at': datetime.now().isoformat()
        }
        
        return routing_result
    
    def _calculate_priority(self, severity: str, urgency: str) -> str:
        """
        Calculate overall priority based on severity and urgency.
        
        Args:
            severity: Severity level (low, medium, high, critical)
            urgency: Urgency level (routine, urgent, emergency)
            
        Returns:
            Priority level (low, medium, high, critical)
        """
        severity_weights = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        urgency_weights = {'routine': 1, 'urgent': 2, 'emergency': 3}
        
        score = severity_weights.get(severity, 2) + urgency_weights.get(urgency, 1)
        
        if score >= 6:
            return 'critical'
        elif score >= 4:
            return 'high'
        elif score >= 3:
            return 'medium'
        else:
            return 'low'
    
    def get_department_info(self, department_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific department.
        
        Args:
            department_id: The department ID
            
        Returns:
            Department information dictionary or None
        """
        return self.department_registry.get_department_by_id(department_id)
    
    def get_all_departments(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all available departments.
        
        Returns:
            Dictionary of all departments
        """
        return self.department_registry.get_all_departments()


# Create a default router instance for convenience
default_router = ComplaintRouter()


def route_complaint(
    complaint: str,
    location_data: Optional[Dict[str, Any]] = None,
    user_info: Optional[Dict[str, str]] = None,
    classification: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to route a complaint using the default router.
    
    Args:
        complaint: The user's complaint text
        location_data: Optional location data
        user_info: Optional user information
        classification: Optional pre-computed classification
        
    Returns:
        Routing information dictionary
    """
    return default_router.route_complaint(
        complaint=complaint,
        location_data=location_data,
        user_info=user_info,
        classification=classification
    )
