"""Character and pose lookup/resolution functions.

This module provides functions for finding characters, refinements (poses), and
parsing character/pose identifiers from JSON data.
"""

from typing import Any, Dict, List, Optional, Union


def find_character_by_id_or_name(
    json_data: Dict[str, Any], identifier: Union[int, str]
) -> Optional[Dict[str, Any]]:
    """Find a character by numeric ID or string name.
    
    Args:
        json_data: Loaded JSON data containing characters
        identifier: Character ID (int) or name (str)
        
    Returns:
        Character dictionary if found, None otherwise
    """
    characters = json_data.get("characters", [])
    
    # Try as integer ID first
    if isinstance(identifier, int):
        for char in characters:
            if char.get("id") == identifier:
                return char
    
    # Try as string (name or string representation of number)
    id_str = str(identifier).lower()
    
    # Try as numeric string
    try:
        num_id = int(identifier)
        for char in characters:
            if char.get("id") == num_id:
                return char
    except (ValueError, TypeError):
        pass
    
    # Try as name
    for char in characters:
        if char.get("name", "").lower() == id_str:
            return char
    
    return None


def find_refinement_by_id_or_name(
    refinements: List[Dict[str, Any]], identifier: Union[int, str]
) -> Optional[Dict[str, Any]]:
    """Find a refinement (pose/form) by numeric ID or string name.
    
    Args:
        refinements: List of refinement dictionaries
        identifier: Refinement ID (int) or name (str)
        
    Returns:
        Refinement dictionary if found, None otherwise
    """
    # Try as integer ID
    if isinstance(identifier, int):
        for ref in refinements:
            if ref.get("id") == identifier:
                return ref
    
    # Try as string
    id_str = str(identifier).lower()
    
    # Try as numeric string
    try:
        num_id = int(identifier)
        for ref in refinements:
            if ref.get("id") == num_id:
                return ref
    except (ValueError, TypeError):
        pass
    
    # Try as name
    for ref in refinements:
        if ref.get("name", "").lower() == id_str:
            return ref
    
    return None


def parse_refinement_path(path_str: str) -> List[str]:
    """Parse a refinement path like '1:1' or 'alpha:human' into components.
    
    Args:
        path_str: Colon-separated refinement path
        
    Returns:
        List of path components
        
    Examples:
        >>> parse_refinement_path("1:1")
        ['1', '1']
        >>> parse_refinement_path("alpha:human")
        ['alpha', 'human']
    """
    return [p.strip() for p in path_str.split(":") if p.strip()]
