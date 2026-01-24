"""Reference sheet generation functionality.

This module provides functions for:
- Parsing page specifications with subrefinement filtering
- Deduplicating common sections across multiple figures
- Generating combined reference sheet prompts for multiple poses/characters
"""

import re
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple, Union

from pose_library import PromptNotFoundError


def deduplicate_figure_sections(figure_descriptions: List[str]) -> Tuple[List[str], Dict[str, str]]:
    """Analyze figure descriptions and extract common repeated sections.
    
    Args:
        figure_descriptions: List of full figure description strings
        
    Returns:
        Tuple of (deduplicated_descriptions, common_sections)
        - deduplicated_descriptions: Figure descriptions with common sections removed
        - common_sections: Dict mapping section names to their common content
        
    Example:
        >>> figures = [
        ...     "Figure 1 [char1:1]: CHARACTER: warrior. PROPORTIONS: heroic",
        ...     "Figure 2 [char1:2]: CHARACTER: mage. PROPORTIONS: heroic"
        ... ]
        >>> deduplicated, common = deduplicate_figure_sections(figures)
        >>> common['PROPORTIONS']
        'heroic'
    """
    if len(figure_descriptions) < 2:
        return figure_descriptions, {}
    
    # Extract the figure label and content separately
    # Format: "Figure N [label]: content"
    figure_pattern = r'^(Figure \d+ \[[^\]]+\]: )(.*?)$'
    
    parsed_figures = []
    for desc in figure_descriptions:
        match = re.match(figure_pattern, desc, re.DOTALL)
        if match:
            prefix = match.group(1)
            content = match.group(2)
            parsed_figures.append((prefix, content))
        else:
            parsed_figures.append(('', desc))
    
    # Extract PROPORTIONS sections (always at the end after a period)
    proportions_pattern = r'\.\s*PROPORTIONS:\s*(.+?)$'
    proportions_values = []
    
    for prefix, content in parsed_figures:
        match = re.search(proportions_pattern, content)
        if match:
            proportions_values.append(match.group(1).strip())
    
    # Check if all PROPORTIONS are identical
    common_proportions = None
    if len(proportions_values) == len(parsed_figures):
        counter = Counter(proportions_values)
        most_common, count = counter.most_common(1)[0]
        if count == len(parsed_figures):
            common_proportions = most_common
    
    # Extract RENDER SCOPE sections from within POSE
    # Pattern: "RENDER SCOPE (CRITICAL): ... view only. "
    render_scope_pattern = r'(RENDER SCOPE \(CRITICAL\): .*?view only\.)\s+'
    render_scope_values = []
    
    for prefix, content in parsed_figures:
        match = re.search(render_scope_pattern, content, re.DOTALL)
        if match:
            render_scope_values.append(match.group(1).strip())
    
    # Check if all RENDER SCOPE are identical
    common_render_scope = None
    if len(render_scope_values) == len(parsed_figures):
        counter = Counter(render_scope_values)
        most_common, count = counter.most_common(1)[0]
        if count == len(parsed_figures):
            common_render_scope = most_common
    
    # Rebuild figure descriptions without the common sections
    common_sections = {}
    deduplicated = []
    
    for prefix, content in parsed_figures:
        new_content = content
        
        # Remove common PROPORTIONS
        if common_proportions:
            proportions_full = r'\.\s*PROPORTIONS:\s*' + re.escape(common_proportions)
            new_content = re.sub(proportions_full, '', new_content)
            common_sections['PROPORTIONS'] = common_proportions
        
        # Remove common RENDER SCOPE
        if common_render_scope:
            render_scope_full = re.escape(common_render_scope) + r'\s+'
            new_content = re.sub(render_scope_full, '', new_content)
            common_sections['RENDER_SCOPE'] = common_render_scope
        
        # Clean up any double periods or extra spaces
        new_content = re.sub(r'\.\s*\.', '.', new_content)
        new_content = re.sub(r'\s+', ' ', new_content).strip()
        
        deduplicated.append(prefix + new_content)
    
    return deduplicated, common_sections


def parse_page_spec(spec: str) -> Tuple[Union[int, str], Optional[List[int]]]:
    """Parse page specification with optional subrefinement selection.
    
    Args:
        spec: Page specification string. Can be:
            - 'all' - all pages
            - '1' - page 1, all subrefinements  
            - '1:1' - page 1, only subrefinement 1
            - '1:{1:3}' - page 1, subrefinements 1-3
            - '1:{1,4,5}' - page 1, subrefinements 1, 4, and 5
            
    Returns:
        Tuple of (page_spec, subrefinement_indices)
        - page_spec: Either 'all' or an integer page number
        - subrefinement_indices: None for all subrefinements, or list of 1-indexed subrefinement numbers
        
    Raises:
        ValueError: If the specification is invalid
        
    Example:
        >>> parse_page_spec('1')
        (1, None)
        >>> parse_page_spec('1:1')
        (1, [1])
        >>> parse_page_spec('1:{1:3}')
        (1, [1, 2, 3])
    """
    spec = spec.strip()
    
    # Handle 'all' pages
    if spec.lower() == 'all':
        return ('all', None)
    
    # Check for subrefinement specification
    if ':' not in spec:
        # Simple page number
        try:
            page_num = int(spec)
            if page_num < 1:
                raise ValueError("Page number must be 1 or greater")
            return (page_num, None)
        except ValueError:
            raise ValueError(f"Invalid page specification: {spec}")
    
    # Parse page:subrefinement syntax
    parts = spec.split(':', 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid page specification: {spec}")
    
    try:
        page_num = int(parts[0])
        if page_num < 1:
            raise ValueError("Page number must be 1 or greater")
    except ValueError:
        raise ValueError(f"Invalid page number in specification: {spec}")
    
    subref_spec = parts[1].strip()
    
    # Check for bracketed syntax: {1:3} or {1,4,5}
    if subref_spec.startswith('{') and subref_spec.endswith('}'):
        subref_spec = subref_spec[1:-1].strip()
    
    # Parse subrefinement indices
    subrefinement_indices = []
    
    # Check for range syntax: 1:3
    if ':' in subref_spec:
        range_parts = subref_spec.split(':', 1)
        if len(range_parts) != 2:
            raise ValueError(f"Invalid subrefinement range: {subref_spec}")
        try:
            start = int(range_parts[0])
            end = int(range_parts[1])
            if start < 1 or end < start:
                raise ValueError(f"Invalid subrefinement range: {start}:{end}")
            subrefinement_indices = list(range(start, end + 1))
        except ValueError as e:
            raise ValueError(f"Invalid subrefinement range in {spec}: {e}")
    # Check for comma-separated list: 1,4,5
    elif ',' in subref_spec:
        try:
            subrefinement_indices = [int(x.strip()) for x in subref_spec.split(',')]
            if any(idx < 1 for idx in subrefinement_indices):
                raise ValueError("Subrefinement indices must be 1 or greater")
        except ValueError as e:
            raise ValueError(f"Invalid subrefinement list in {spec}: {e}")
    # Single subrefinement: 1
    else:
        try:
            idx = int(subref_spec)
            if idx < 1:
                raise ValueError("Subrefinement index must be 1 or greater")
            subrefinement_indices = [idx]
        except ValueError as e:
            raise ValueError(f"Invalid subrefinement index in {spec}: {e}")
    
    return (page_num, subrefinement_indices)
