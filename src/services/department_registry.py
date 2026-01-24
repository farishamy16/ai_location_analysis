"""
Department Registry Service
Manages department assignments based on complaint type and location.
"""

from typing import Dict, List, Any, Optional


class DepartmentRegistry:
    """Registry for managing departments and their responsibilities."""
    
    def __init__(self):
        """Initialize the department registry with default departments."""
        self._departments = self._load_default_departments()
    
    def _load_default_departments(self) -> Dict[str, Dict[str, Any]]:
        """
        Load default department configuration.
        
        Returns:
            Dictionary of departments keyed by category
        """
        return {
            'traffic': {
                'id': 'dept_traffic',
                'name': 'Traffic Management Department',
                'email': 'traffic@city.gov',
                'phone': '+60-3-1234-5678',
                'jurisdictions': ['all'],  # 'all' means covers all areas
                'categories': ['parking', 'traffic_lights', 'road_conditions', 'traffic'],
                'priority_levels': {
                    'low': 72,      # hours
                    'medium': 48,
                    'high': 24,
                    'critical': 4
                },
                'description': 'Handles all traffic-related complaints including parking, traffic lights, and road conditions.'
            },
            'sanitation': {
                'id': 'dept_sanitation',
                'name': 'City Sanitation Services',
                'email': 'sanitation@city.gov',
                'phone': '+60-3-2345-6789',
                'jurisdictions': ['all'],
                'categories': ['trash', 'cleanliness', 'pest_control', 'sanitation', 'waste'],
                'priority_levels': {
                    'low': 48,
                    'medium': 24,
                    'high': 12,
                    'critical': 2
                },
                'description': 'Manages waste collection, cleanliness, and pest control services.'
            },
            'infrastructure': {
                'id': 'dept_infrastructure',
                'name': 'Infrastructure Maintenance',
                'email': 'infrastructure@city.gov',
                'phone': '+60-3-3456-7890',
                'jurisdictions': ['all'],
                'categories': ['street_lights', 'broken_facilities', 'potholes', 'infrastructure', 'maintenance'],
                'priority_levels': {
                    'low': 72,
                    'medium': 48,
                    'high': 24,
                    'critical': 8
                },
                'description': 'Responsible for public infrastructure maintenance including street lights and facilities.'
            },
            'safety': {
                'id': 'dept_safety',
                'name': 'Public Safety Department',
                'email': 'safety@city.gov',
                'phone': '+60-3-4567-8901',
                'jurisdictions': ['all'],
                'categories': ['crime', 'harassment', 'dangerous_area', 'safety', 'security'],
                'priority_levels': {
                    'low': 48,
                    'medium': 24,
                    'high': 8,
                    'critical': 1
                },
                'description': 'Handles public safety concerns and security-related complaints.'
            },
            'environment': {
                'id': 'dept_environment',
                'name': 'Environmental Services',
                'email': 'environment@city.gov',
                'phone': '+60-3-5678-9012',
                'jurisdictions': ['all'],
                'categories': ['pollution', 'noise', 'green_spaces', 'environment', 'air_quality'],
                'priority_levels': {
                    'low': 72,
                    'medium': 48,
                    'high': 24,
                    'critical': 6
                },
                'description': 'Manages environmental concerns including pollution, noise, and green spaces.'
            },
            'commercial': {
                'id': 'dept_commercial',
                'name': 'Commercial Services Department',
                'email': 'commercial@city.gov',
                'phone': '+60-3-6789-0123',
                'jurisdictions': ['all'],
                'categories': ['food_hygiene', 'shop_complaints', 'commercial', 'business'],
                'priority_levels': {
                    'low': 72,
                    'medium': 48,
                    'high': 24,
                    'critical': 4
                },
                'description': 'Handles complaints related to commercial establishments and businesses.'
            },
            'general': {
                'id': 'dept_general',
                'name': 'General Services',
                'email': 'general@city.gov',
                'phone': '+60-3-7890-1234',
                'jurisdictions': ['all'],
                'categories': ['other', 'general', 'inquiry'],
                'priority_levels': {
                    'low': 96,
                    'medium': 72,
                    'high': 48,
                    'critical': 24
                },
                'description': 'Catches all complaints that don\'t fit into specific categories.'
            }
        }
    
    def get_department_by_category(self, category: str) -> Optional[Dict[str, Any]]:
        """
        Get department information by complaint category.
        
        Args:
            category: The complaint category
            
        Returns:
            Department dictionary or None if not found
        """
        # Try exact match first
        if category in self._departments:
            return self._departments[category]
        
        # Try partial match
        for dept_key, dept_info in self._departments.items():
            if category.lower() in [c.lower() for c in dept_info['categories']]:
                return dept_info
        
        # Return general department as fallback
        return self._departments.get('general')
    
    def get_department_by_id(self, department_id: str) -> Optional[Dict[str, Any]]:
        """
        Get department information by department ID.
        
        Args:
            department_id: The department ID
            
        Returns:
            Department dictionary or None if not found
        """
        for dept_info in self._departments.values():
            if dept_info['id'] == department_id:
                return dept_info
        return None
    
    def get_all_departments(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all registered departments.
        
        Returns:
            Dictionary of all departments
        """
        return self._departments.copy()
    
    def get_categories_for_department(self, department_id: str) -> List[str]:
        """
        Get all categories handled by a specific department.
        
        Args:
            department_id: The department ID
            
        Returns:
            List of category strings
        """
        dept = self.get_department_by_id(department_id)
        if dept:
            return dept.get('categories', [])
        return []
    
    def get_response_time(self, department_id: str, severity: str) -> int:
        """
        Get expected response time in hours for a department and severity.
        
        Args:
            department_id: The department ID
            severity: The complaint severity (low, medium, high, critical)
            
        Returns:
            Expected response time in hours
        """
        dept = self.get_department_by_id(department_id)
        if dept:
            return dept.get('priority_levels', {}).get(severity.lower(), 72)
        return 72  # Default: 72 hours
    
    def add_department(self, department_id: str, name: str, email: str, 
                      categories: List[str], **kwargs) -> None:
        """
        Add a new department to the registry.
        
        Args:
            department_id: Unique identifier for the department
            name: Department name
            email: Department email address
            categories: List of categories this department handles
            **kwargs: Additional department properties
        """
        self._departments[department_id] = {
            'id': department_id,
            'name': name,
            'email': email,
            'categories': categories,
            'jurisdictions': kwargs.get('jurisdictions', ['all']),
            'phone': kwargs.get('phone', ''),
            'priority_levels': kwargs.get('priority_levels', {
                'low': 72, 'medium': 48, 'high': 24, 'critical': 8
            }),
            'description': kwargs.get('description', '')
        }
    
    def update_department(self, department_id: str, **kwargs) -> bool:
        """
        Update an existing department's information.
        
        Args:
            department_id: The department ID to update
            **kwargs: Fields to update
            
        Returns:
            True if updated, False if department not found
        """
        for dept_key, dept_info in self._departments.items():
            if dept_info['id'] == department_id:
                self._departments[dept_key].update(kwargs)
                return True
        return False
    
    def remove_department(self, department_id: str) -> bool:
        """
        Remove a department from the registry.
        
        Args:
            department_id: The department ID to remove
            
        Returns:
            True if removed, False if department not found
        """
        for dept_key in list(self._departments.keys()):
            if self._departments[dept_key]['id'] == department_id:
                del self._departments[dept_key]
                return True
        return False


# Create a default registry instance for convenience
default_registry = DepartmentRegistry()


def get_department_by_category(category: str) -> Optional[Dict[str, Any]]:
    """
    Convenience function to get department by category using default registry.
    
    Args:
        category: The complaint category
        
    Returns:
        Department dictionary or None if not found
    """
    return default_registry.get_department_by_category(category)
