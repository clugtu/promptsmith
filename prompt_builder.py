"""Prompt building functionality.

This module provides functions for:
- Building structured prompts from components
- Formatting prompts for different outputs
- Managing prompt sections (CHARACTER, PROPS, POSE, THEME, etc.)
"""

import sys
from typing import Any, Dict, List, Optional


def format_for_chat(prompt: str) -> str:
    """Format a prompt for copy/paste into ChatGPT.
    
    Args:
        prompt: The prompt text to format
        
    Returns:
        The formatted prompt with whitespace trimmed
    """
    return prompt.strip()


def build_final_prompt(
    base_prompt: str,
    *,
    gender: Optional[str] = None,
    thematic_snippets: List[str] = None,
    thematic_general: str = "",
    proportions: str = "",
    age: str = "",
    default_proportions: str = "",
    style_snippet: str = "",
    generic_snippet = None,  # Can be str, dict of sections, or None
    miniature_snippet: str = "",
    include_generic: bool = False,
    include_miniature: bool = False,
    no_base: bool = False,
    equipment: List[str] = None,
    character_id: str = "",
    character_name: str = "",
    form_id: str = "",
    pose_prompt: str = "",
    camera_rotation: Optional[int] = None,
    visual_notes: str = "",
) -> str:
    """Build the final prompt from components with structured sections.
    
    This function assembles a complete image generation prompt from various components,
    organizing them into well-defined sections for clarity and consistency.
    
    Args:
        base_prompt: Character base + pose description
        gender: Character gender (male, female, etc.)
        thematic_snippets: List of thematic form snippets
        thematic_general: General thematic prompt
        proportions: Character proportions override
        age: Character age (child, teen, young_adult, adult, older, elder)
        default_proportions: Default proportions if character has none
        style_snippet: Style rules
        generic_snippet: Generic render rules (str or dict of sections)
        miniature_snippet: Miniature-specific rules
        include_generic: Whether to include generic rules
        include_miniature: Whether to include miniature rules
        no_base: Whether to specify no base/stand
        equipment: List of equipment/props with placement descriptions
        character_id: Character ID for asset naming
        character_name: Character name for asset naming
        form_id: Form/pose ID for asset naming
        pose_prompt: Pose description from pose library
        camera_rotation: Camera rotation override (degrees, default 45)
        visual_notes: Visual styling notes
        
    Returns:
        Complete formatted prompt string with structured sections
        
    Example:
        >>> prompt = build_final_prompt(
        ...     "A warrior",
        ...     gender="male",
        ...     age="adult",
        ...     equipment=["sword : main_hand : gripped firmly"],
        ...     include_generic=True,
        ...     include_miniature=False,
        ...     generic_snippet={"framing": {"title": "FRAMING", "content": "..."}}
        ... )
    """
    sections = []
    
    # ASSET_NAME section
    # Debug output
    if False:  # Set to True for debugging
        print(f"DEBUG: character_id={character_id}, character_name={character_name}, gender={gender}, form_id={form_id}", file=sys.stderr)
    
    if character_name and gender:
        # Use ID + character name + gender for readable asset names
        if character_id:
            asset_name = f"{character_id}_{character_name}_{gender}".replace(" ", "_").lower()
        else:
            asset_name = f"{character_name}_{gender}".replace(" ", "_").lower()
        sections.append(f"ASSET_NAME: {asset_name}")
    elif character_id and form_id:
        # Fallback to ID-based naming
        asset_name = f"{character_id}_{form_id}"
        sections.append(f"ASSET_NAME: {asset_name}")
    
    # VISUAL section (if present, before CHARACTER)
    if visual_notes:
        sections.append(f"VISUAL:\n{visual_notes}")
    
    # CHARACTER section
    character_parts = [base_prompt.strip().rstrip(",")]
    
    # Add age and gender as demographic descriptors
    demographic_parts = []
    
    if age:
        demographic_parts.append(age.lower())
    
    if gender:
        gender_lower = gender.lower()
        base_lower = base_prompt.lower()
        
        # Check for explicit gender words
        has_gender = any(word in base_lower for word in [
            'female', 'male', 'woman', 'man ', ' man,', 'girl', 'boy',
            'feminine', 'masculine'
        ])
        
        # Add gender unless already present
        if not has_gender:
            demographic_parts.append(gender_lower)
    
    # Add demographics to character description
    if demographic_parts:
        character_parts.append(" ".join(demographic_parts))
    
    sections.append("CHARACTER:\n" + ", ".join(p.strip().rstrip(",") for p in character_parts if p.strip()))
    
    # PROPS section
    if equipment:
        formatted_props = []
        for item in equipment:
            # Parse structured format: "item (details) : position : description"
            if " : " in item:
                parts = item.split(" : ", 2)
                if len(parts) == 3:
                    item_with_details = parts[0].strip()
                    position = parts[1].strip()
                    description = parts[2].strip()
                    formatted_props.append(f"- {item_with_details} [{position}] {description}")
                else:
                    # Fallback for malformed entries
                    formatted_props.append(f"- {item}")
            else:
                # Legacy format without colons
                formatted_props.append(f"- {item}")
        
        props_lines = "\n".join(formatted_props)
        sections.append(f"PROPS:\n{props_lines}")
    
    # POSE section (from pose library)
    if pose_prompt:
        sections.append(f"POSE:\n{pose_prompt}")
    
    # THEME section
    theme_parts = []
    if thematic_snippets:
        theme_parts.extend(thematic_snippets)
    if thematic_general:
        theme_parts.append(thematic_general)
    
    if theme_parts:
        sections.append("THEME:\n" + ", ".join(p.strip().rstrip(",") for p in theme_parts))
    
    # PROPORTIONS section
    proportions_to_use = proportions if proportions else default_proportions
    if proportions_to_use:
        sections.append(f"PROPORTIONS:\n{proportions_to_use}")
    
    # STYLE section
    if style_snippet:
        sections.append(f"STYLE:\n{style_snippet}")
    
    # RENDER RULES sections (from generic_render_rules.json - includes 3D-safe geometry)
    if include_generic and generic_snippet:
        if isinstance(generic_snippet, dict):
            # New section-based format
            for section_key, section_data in generic_snippet.items():
                if isinstance(section_data, dict) and "title" in section_data:
                    title = section_data["title"]
                    content = section_data.get("content", "")
                    if content:
                        # Apply camera rotation override if present and this is the framing section
                        if section_key == "framing" and camera_rotation is not None:
                            # Get default rotation
                            default_rotation = section_data.get("default_camera_rotation", 45)
                            rotation_to_use = camera_rotation if camera_rotation is not None else default_rotation
                            content = content.replace("{camera_rotation}", str(rotation_to_use))
                        elif section_key == "framing":
                            # Use default if no override
                            default_rotation = section_data.get("default_camera_rotation", 45)
                            content = content.replace("{camera_rotation}", str(default_rotation))
                        sections.append(f"{title}:\n{content}")
        elif isinstance(generic_snippet, str) and generic_snippet:
            # Legacy prompt_snippet format
            sections.append(f"RENDER RULES:\n{generic_snippet}")
    
    # MINIATURE RULES section
    if include_miniature and miniature_snippet:
        sections.append(f"MINIATURE RULES:\n{miniature_snippet}")
    
    # BASE EXCLUSION section
    if no_base:
        sections.append("BASE EXCLUSION:\nno base, no stand, not mounted, no plinth, no pedestal, no ground plane")
    
    return "create image\n\n" + "\n\n".join(sections)
