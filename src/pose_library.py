"""Pose library handling functionality.

This module provides functions for:
- Extracting and finding poses in the pose library
- Composing pose prompts with placeholder replacement
- Validating pose compatibility with characters
- Figure type compatibility checking
"""

import re
import sys
from typing import Any, Dict, List, Optional, Tuple


class PromptNotFoundError(RuntimeError):
    """Exception raised when a pose prompt cannot be found."""
    pass


def extract_pose_library(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract the pose library from JSON (if present).
    
    Args:
        json_data: The loaded JSON data
        
    Returns:
        Dict containing pose library data, or empty dict if not present
    """
    return json_data.get("pose_library", {})


def find_pose_in_library(pose_library: Dict[str, Any], pose_id: str) -> Optional[Dict[str, Any]]:
    """Find a specific pose by pose_id in the library.
    
    Args:
        pose_library: The pose library data structure
        pose_id: The ID of the pose to find
        
    Returns:
        The pose definition dict if found, None otherwise
    """
    for pose in pose_library.get("poses", []):
        if pose.get("pose_id") == pose_id:
            return pose
    return None


def compose_pose_prompt_from_library(
    character_data: Dict[str, Any],
    pose_def: Dict[str, Any],
    pose_library: Dict[str, Any],
    json_data: Dict[str, Any],
    equipment: List[str]
) -> Tuple[str, str, Optional[int]]:
    """Compose a pose prompt by looking up a pose_library_ref.
    
    This function retrieves a pose from the library, replaces placeholders with actual
    equipment prop names, and validates figure type compatibility.
    
    Args:
        character_data: The character definition containing character_base
        pose_def: The pose/refinement containing pose_library_ref
        pose_library: The loaded pose library JSON
        json_data: Full JSON data for figure_type validation
        equipment: Resolved equipment list to extract hand-held props
        
    Returns:
        Tuple of (pose_details, pose_prompt, camera_rotation):
        - pose_details: Pose-specific character details (expression, posture, etc.) (str)
        - pose_prompt: The composed pose prompt with placeholders replaced (str)
        - camera_rotation: Optional camera rotation angle (Optional[int])
        
    Raises:
        PromptNotFoundError: If pose_library_ref is missing or not found in library
        
    Example:
        >>> character_data = {"name": "Warrior"}
        >>> pose_def = {"pose_library_ref": "unarmed_002"}
        >>> equipment = ["sword : main_hand : gripped"]
        >>> details, prompt, rotation = compose_pose_prompt_from_library(
        ...     character_data, pose_def, pose_library, json_data, equipment)
    """
    pose_ref = pose_def.get("pose_library_ref")
    if not pose_ref:
        raise PromptNotFoundError("pose_library_ref is missing in pose definition")
    
    # Find the pose in the library
    library_pose = find_pose_in_library(pose_library, pose_ref)
    if not library_pose:
        # Fall back to embedded pose definition if available
        if "pose_prompt" in pose_def:
            print(f"⚠️  Warning: Pose '{pose_ref}' not found in library, using embedded pose definition", file=sys.stderr)
            pose_details = pose_def.get("pose_details", "")
            pose_prompt = pose_def.get("pose_prompt", "")
            camera_rotation = pose_def.get("camera_rotation")
            return pose_details, pose_prompt, camera_rotation
        
        # If no embedded definition, raise error
        available_ids = [p.get("pose_id", "?") for p in pose_library.get("poses", [])[:15]]
        raise PromptNotFoundError(
            f"Pose '{pose_ref}' not found in pose library and no embedded 'pose_prompt' provided.\n"
            f"Available poses (first 15): {', '.join(available_ids)}"
        )
    
    # Get the pose prompt template from library
    pose_prompt = library_pose.get("pose_prompt", "")
    
    # Parse equipment to extract main_hand and off_hand props
    main_hand_prop = None
    off_hand_prop = None
    
    for item in equipment:
        if " : " in item:
            parts = item.split(" : ", 2)
            if len(parts) >= 2:
                prop_desc = parts[0].strip()
                position = parts[1].strip()
                
                # Extract prop name from description (before any parentheses or details)
                prop_name = prop_desc.split("(")[0].split("[")[0].strip()
                
                if position == "main_hand":
                    main_hand_prop = prop_name
                elif position == "off_hand":
                    off_hand_prop = prop_name
    
    # Replace placeholders in pose_prompt
    if main_hand_prop:
        pose_prompt = pose_prompt.replace("MAIN_HAND_PROP", main_hand_prop)
    
    if off_hand_prop:
        pose_prompt = pose_prompt.replace("OFF_HAND_PROP", off_hand_prop)
    
    # Enhance GRIP CLUSTER section with specific prop gripping details
    if (main_hand_prop or off_hand_prop) and "GRIP CLUSTER (MANDATORY):" in pose_prompt:
        grip_details = []
        if main_hand_prop:
            grip_details.append(f"the main hand (one of the two hands) actively grips {main_hand_prop}")
        if off_hand_prop:
            grip_details.append(f"the off hand (the other hand) actively grips {off_hand_prop}")
        
        grip_text = "; ".join(grip_details)
        
        # Insert grip details into GRIP CLUSTER section
        pose_prompt = pose_prompt.replace(
            "GRIP CLUSTER (MANDATORY): Hands are spatially locked together",
            f"GRIP CLUSTER (MANDATORY): {grip_text}; hands are spatially locked together"
        )

    
    # Validate figure types if present
    pose_figure_type = library_pose.get("figure_type")
    char_figure_type = pose_def.get("figure_type")
    
    if pose_figure_type and char_figure_type:
        # Define compatible mismatches
        compatible_mismatches = {
            'facultatively_bipedal': ['bipedal_humanoid'],
            'winged_bipedal': ['bipedal_humanoid'],
            'winged_centauroid': ['centauroid'],
            'multi_limbed_bipedal': ['bipedal_humanoid'],
            'multi_limbed_centauroid': ['centauroid']
        }
        
        compatible = (pose_figure_type == char_figure_type) or \
                     (char_figure_type in compatible_mismatches and 
                      pose_figure_type in compatible_mismatches[char_figure_type])
        
        if not compatible:
            print(f"⚠️  Warning: Figure type mismatch - pose expects '{pose_figure_type}' but character has '{char_figure_type}'", file=sys.stderr)
    
    # Get pose_details (for appearance/expression modifications)
    pose_details = pose_def.get("pose_details", "")
    
    # Extract camera_rotation if present
    camera_rotation = library_pose.get("camera_rotation")
    
    return pose_details, pose_prompt, camera_rotation


def validate_pose_compatibility(
    character_data: Dict[str, Any],
    character_pose_def: Dict[str, Any],
    library_pose_def: Dict[str, Any],
    pose_id: str,
    json_data: Dict[str, Any]
) -> List[str]:
    """Check if character weapons match pose requirements.
    
    This function validates that a character's equipment configuration is compatible
    with a pose's requirements, including handedness mode, prop classes, and figure types.
    
    Args:
        character_data: Character definition with weapons
        character_pose_def: Pose definition from character JSON (with overrides)
        library_pose_def: Pose definition from pose library
        pose_id: Pose ID for error messages
        json_data: The full JSON data (for figure_type validation from forms)
        
    Returns:
        List of warning messages (empty if no issues)
        
    Example:
        >>> warnings = validate_pose_compatibility(
        ...     character_data, pose_def, library_pose, "unarmed_002", json_data)
        >>> if warnings:
        ...     for warning in warnings:
        ...         print(f"⚠️  {warning}")
    """
    warnings = []
    
    # Get character weapon config
    weapons = character_data.get("weapons", {})
    main_hand_weapon = weapons.get("main_hand")
    off_hand_weapon = weapons.get("off_hand")
    holstered_items = weapons.get("holstered", [])
    
    # Get pose requirements from library
    handedness_mode = library_pose_def.get("handedness_mode", "unarmed")
    main_hand_slot = library_pose_def.get("main_hand", {})
    off_hand_slot = library_pose_def.get("off_hand", {})
    
    main_prop_classes = main_hand_slot.get("prop_class", [])
    off_prop_classes = off_hand_slot.get("prop_class", [])
    
    # Validate figure_type compatibility
    pose_figure_type = library_pose_def.get("figure_type", "bipedal_humanoid")
    character_figure_type = character_data.get("figure_type")
    
    # Also check if character is using a form with figure_type
    if not character_figure_type and "thematic_snippet" in character_pose_def:
        # Try to get figure_type from form
        thematic_forms = json_data.get("thematic_rules", {}).get("forms", {})
        for snippet in character_pose_def.get("thematic_snippet", []):
            if snippet in thematic_forms:
                form_data = thematic_forms[snippet]
                if isinstance(form_data, dict) and "figure_type" in form_data:
                    character_figure_type = form_data["figure_type"]
                    break
    
    # Define valid figure types
    VALID_FIGURE_TYPES = [
        "bipedal_humanoid",
        "quadrupedal",
        "facultatively_bipedal",
        "serpentine",
        "naga_form",
        "centauroid",
        "multi_limbed_bipedal",
        "multi_limbed_centauroid",
        "winged_bipedal",
        "winged_centauroid",
        "amorphous",
        "floating",
        "arachnoid"
    ]
    
    # Validate pose figure_type
    if pose_figure_type not in VALID_FIGURE_TYPES:
        warnings.append(
            f"Pose '{pose_id}' has invalid figure_type '{pose_figure_type}'. "
            f"Valid types: {', '.join(VALID_FIGURE_TYPES)}"
        )
    
    # Validate character figure_type if present
    if character_figure_type and character_figure_type not in VALID_FIGURE_TYPES:
        warnings.append(
            f"Character has invalid figure_type '{character_figure_type}'. "
            f"Valid types: {', '.join(VALID_FIGURE_TYPES)}"
        )
    
    # Check figure_type compatibility
    if character_figure_type and pose_figure_type != character_figure_type:
        # Check if it's a compatible mismatch
        compatible_mismatches = {
            # Facultatively bipedal can use bipedal poses when upright
            ("facultatively_bipedal", "bipedal_humanoid"): "acceptable (facultatively bipedal using bipedal pose)",
            # Winged variants can use base poses
            ("winged_bipedal", "bipedal_humanoid"): "acceptable (winged using bipedal base)",
            ("winged_centauroid", "centauroid"): "acceptable (winged using centauroid base)",
            # Multi-limbed can use base poses (just won't use all arms)
            ("multi_limbed_bipedal", "bipedal_humanoid"): "acceptable (multi-limbed using bipedal base)",
            ("multi_limbed_centauroid", "centauroid"): "acceptable (multi-limbed using centauroid base)",
        }
        
        mismatch_key = (character_figure_type, pose_figure_type)
        if mismatch_key in compatible_mismatches:
            # Compatible mismatch - just a note, not a warning
            pass
        else:
            warnings.append(
                f"Figure type mismatch: character is '{character_figure_type}' but pose '{pose_id}' "
                f"is designed for '{pose_figure_type}'. Pose may not work correctly."
            )
    
    return warnings


def remove_base_language(miniature_snippet: str) -> str:
    """Remove 'mounted on a ... base' phrase from the 40mm snippet.

    This keeps the rest of the 40mm miniature styling (materials, lighting, scale cues)
    while avoiding a physical base being depicted.
    
    Args:
        miniature_snippet: The miniature style snippet potentially containing base language
        
    Returns:
        The miniature snippet with base language removed
        
    Example:
        >>> snippet = "40mm miniature scale, mounted on a round gaming base (about 32mm)"
        >>> remove_base_language(snippet)
        "40mm miniature scale"
    """
    s = miniature_snippet

    # Remove common base phrases used in JSON and likely variants.
    base_patterns = [
        r",\s*mounted on a round gaming base\s*\(about 32mm\)\s*",
        r",\s*mounted on a round gaming base\s*",
        r",\s*on a round gaming base\s*\(about 32mm\)\s*",
        r",\s*on a round gaming base\s*",
        r",\s*mounted on a gaming base\s*",
        r",\s*on a gaming base\s*",
        r",\s*mounted on a base\s*",
        r",\s*on a base\s*",
        r",\s*round base\s*\(about 32mm\)\s*",
        r",\s*round base\s*",
        r",\s*display base\s*",
        r",\s*plinth\s*",
    ]
    for pat in base_patterns:
        s = re.sub(pat, ", ", s, flags=re.IGNORECASE)

    # Also remove any remaining comma-separated segments that still mention base/plinth.
    parts = [p.strip() for p in s.split(",") if p.strip()]
    parts = [
        p
        for p in parts
        if not re.search(r"\b(base|based|gaming base|round base|plinth)\b", p, flags=re.IGNORECASE)
    ]
    return ", ".join(parts)
