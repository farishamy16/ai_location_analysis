"""
Semantic Matcher Service
Uses advanced keyword matching to semantically match complaints to categories.
This approach uses weighted keywords, synonyms, and contextual matching.
"""

from typing import Dict, List, Any, Optional
from collections import Counter
import re


class SemanticMatchResult:
    """Result of semantic matching."""
    
    def __init__(
        self,
        category: str,
        similarity: float,
        all_scores: Dict[str, float],
        matched_keywords: Optional[List[str]] = None
    ):
        """
        Initialize semantic match result.
        
        Args:
            category: The matched category
            similarity: Similarity score (0.0 to 1.0)
            all_scores: Dictionary of all category scores
            matched_keywords: List of keywords that matched
        """
        self.category = category
        self.similarity = similarity
        self.all_scores = all_scores
        self.matched_keywords = matched_keywords or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'category': self.category,
            'similarity': self.similarity,
            'all_scores': self.all_scores,
            'matched_keywords': self.matched_keywords
        }


class SemanticMatcher:
    """
    Semantic matcher using advanced keyword matching with weights and synonyms.
    """
    
    def __init__(self):
        """Initialize the semantic matcher with category keywords."""
        self.category_keywords = self._load_category_keywords()
    
    def _load_category_keywords(self) -> Dict[str, Dict[str, float]]:
        """
        Load weighted keywords for each category.
        
        Returns:
            Dictionary mapping category names to their weighted keywords
        """
        return {
            'traffic': {
                # High weight keywords (primary indicators)
                'traffic': 1.0,
                'congestion': 1.0,
                'parking': 1.0,
                'traffic jam': 1.0,
                'gridlock': 1.0,
                
                # Medium weight keywords (strong indicators)
                'cars': 0.8,
                'vehicles': 0.8,
                'road': 0.8,
                'highway': 0.8,
                'motorcycle': 0.8,
                'vehicle': 0.8,
                'car': 0.8,
                
                # Lower weight keywords (supporting indicators)
                'speeding': 0.6,
                'accident': 0.6,
                'rush hour': 0.6,
                'driving': 0.6,
                'commute': 0.6,
                'transportation': 0.6,
                'heavy traffic': 0.6,
                'traffic volume': 0.6,
                'too many cars': 0.6,
                'traffic flow': 0.6,
                'traffic delays': 0.6,
            },
            'sanitation': {
                # High weight keywords
                'trash': 1.0,
                'garbage': 1.0,
                'waste': 1.0,
                'dirty': 1.0,
                'cleanliness': 1.0,
                
                # Medium weight keywords
                'rubbish': 0.8,
                'unclean': 0.8,
                'filthy': 0.8,
                'bin': 0.8,
                'pest': 0.8,
                
                # Lower weight keywords
                'rodent': 0.6,
                'cockroach': 0.6,
                'overflowing': 0.6,
                'waste collection': 0.6,
                'pest control': 0.6,
                'unhygienic': 0.6,
                'garbage collection': 0.6,
            },
            'infrastructure': {
                # High weight keywords
                'street light': 1.0,
                'broken': 1.0,
                'pothole': 1.0,
                'maintenance': 1.0,
                'facility': 1.0,
                
                # Medium weight keywords
                'damaged': 0.8,
                'faulty': 0.8,
                'equipment': 0.8,
                'sidewalk': 0.8,
                'drainage': 0.8,
                
                # Lower weight keywords
                'bench': 0.6,
                'pedestrian': 0.6,
                'public facilities': 0.6,
                'road maintenance': 0.6,
                'pedestrian path': 0.6,
                'broken facilities': 0.6,
                'broken bench': 0.6,
                'damaged road': 0.6,
            },
            'safety': {
                # High weight keywords
                'crime': 1.0,
                'harassment': 1.0,
                'dangerous': 1.0,
                'security': 1.0,
                'theft': 1.0,
                
                # Medium weight keywords
                'assault': 0.8,
                'robbery': 0.8,
                'suspicious': 0.8,
                'unsafe': 0.8,
                'emergency': 0.8,
                
                # Lower weight keywords
                'public safety': 0.6,
                'security concerns': 0.6,
                'criminal': 0.6,
                'police': 0.6,
                'security issue': 0.6,
                'dangerous area': 0.6,
                'suspicious activity': 0.6,
            },
            'environment': {
                # High weight keywords
                'pollution': 1.0,
                'noise': 1.0,
                'air quality': 1.0,
                'environment': 1.0,
                
                # Medium weight keywords
                'water pollution': 0.8,
                'air pollution': 0.8,
                'noise pollution': 0.8,
                'toxic': 0.8,
                'dumping': 0.8,
                
                # Lower weight keywords
                'hazard': 0.6,
                'green space': 0.6,
                'environmental': 0.6,
                'environmental health': 0.6,
                'pollution control': 0.6,
                'illegal dumping': 0.6,
                'environmental hazard': 0.6,
            },
            'commercial': {
                # High weight keywords
                'food hygiene': 1.0,
                'restaurant': 1.0,
                'shop': 1.0,
                'business': 1.0,
                
                # Medium weight keywords
                'food safety': 0.8,
                'violation': 0.8,
                'consumer': 0.8,
                'service': 0.8,
                
                # Lower weight keywords
                'commercial': 0.6,
                'food establishment': 0.6,
                'business licensing': 0.6,
                'business violation': 0.6,
                'consumer complaint': 0.6,
                'service quality': 0.6,
                'shop complaint': 0.6,
            },
            'general': {
                # High weight keywords
                'inquiry': 1.0,
                'feedback': 1.0,
                'suggestion': 1.0,
                'general': 1.0,
                
                # Medium weight keywords
                'other': 0.8,
                'not sure': 0.8,
                'unclear': 0.8,
                
                # Lower weight keywords
                'information': 0.6,
                'question': 0.6,
                'general complaint': 0.6,
                'general matter': 0.6,
                'general inquiry': 0.6,
            }
        }
    
    def find_best_match(self, complaint: str) -> SemanticMatchResult:
        """
        Find the best matching category for a complaint using semantic similarity.
        
        Args:
            complaint: The complaint text
            
        Returns:
            SemanticMatchResult with the best match and similarity scores
        """
        # Calculate similarity scores for all categories
        similarities = {}
        all_matched_keywords = {}
        
        for category, keywords in self.category_keywords.items():
            score, matched = self._calculate_category_score(complaint, keywords)
            similarities[category] = score
            all_matched_keywords[category] = matched
        
        # Find the best match
        best_category = max(similarities.items(), key=lambda x: x[1])[0]
        best_similarity = similarities[best_category]
        
        return SemanticMatchResult(
            category=best_category,
            similarity=best_similarity,
            all_scores=similarities,
            matched_keywords=all_matched_keywords[best_category]
        )
    
    def _calculate_category_score(
        self,
        complaint: str,
        keywords: Dict[str, float]
    ) -> tuple[float, List[str]]:
        """
        Calculate similarity score for a category based on keyword matching.
        
        Args:
            complaint: The complaint text
            keywords: Dictionary of keywords and their weights
            
        Returns:
            Tuple of (score, list of matched keywords)
        """
        complaint_lower = complaint.lower()
        total_score = 0.0
        matched_keywords = []
        
        # Check each keyword
        for keyword, weight in keywords.items():
            if keyword.lower() in complaint_lower:
                total_score += weight
                matched_keywords.append(keyword)
        
        # Normalize score based on maximum possible score
        max_score = sum(keywords.values())
        if max_score > 0:
            normalized_score = total_score / max_score
        else:
            normalized_score = 0.0
        
        return normalized_score, matched_keywords


# Create a default matcher instance for convenience
default_matcher = SemanticMatcher()


def find_best_match(complaint: str) -> SemanticMatchResult:
    """
    Convenience function to find best match using default matcher.
    
    Args:
        complaint: The complaint text
        
    Returns:
        SemanticMatchResult with the best match
    """
    return default_matcher.find_best_match(complaint)
