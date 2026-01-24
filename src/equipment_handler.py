"""Equipment and prop handling functionality.

This module provides functions for:
- Resolving prop references to full descriptions
- Validating hand assignments for equipment
- Supporting multi-limbed characters
- Handling prop definitions
"""

import sys
from typing import Any, Dict, List


def resolve_prop_references(equipment: List[str], prop_definitions: Dict[str, str]) -> List[str]:
    """Resolve prop references to their full descriptions with positioning.
    
    Args:
        equipment: List of equipment strings, either:
                  - New format: "prop_id : position : pose_description"
                  - Legacy format: "full description (details) : position : pose_description"
        prop_definitions: Dict mapping prop_id to "description (details)"
        
    Returns:
        List of resolved equipment strings in format "description (details) : position : pose_description"
    
    Examples:
        >>> equipment = ["sword : main_hand : gripped"]
        >>> prop_defs = {"sword": "steel sword (sharp blade)"}
        >>> resolve_prop_references(equipment, prop_defs)
        ["steel sword (sharp blade) : main_hand : gripped"]
        
        >>> equipment = ["leather armor (studded) : worn : on torso"]
        >>> resolve_prop_references(equipment, {})
        ["leather armor (studded) : worn : on torso"]
    """
    resolved = []
    for item in equipment:
        if " : " in item:
            parts = item.split(" : ", 2)
            if len(parts) >= 2:
                first_part = parts[0].strip()
                # Check if first part is a prop_id reference (no parentheses/brackets)
                if first_part in prop_definitions and "(" not in first_part and "[" not in first_part:
                    # It's a prop reference - resolve it
                    prop_desc = prop_definitions[first_part]
                    # Reconstruct with resolved description
                    remaining = " : ".join(parts[1:])
                    resolved.append(f"{prop_desc} : {remaining}")
                else:
                    # It's already a full description (legacy format)
                    resolved.append(item)
            else:
                resolved.append(item)
        else:
            # No colons - legacy format
            resolved.append(item)
    return resolved


def validate_hand_assignments(equipment: List[str], character_id: str, form_id: str, char_data: Dict[str, Any]) -> None:
    """Validate that equipment hand assignments don't exceed available hands.
    
    This function checks that the number of items assigned to hands (main_hand, off_hand, both_hands)
    doesn't exceed the character's available hands. For multi-limbed characters, violations result in
    warnings rather than errors.
    
    Args:
        equipment: List of equipment strings in format "item (details) : position : description"
        character_id: Character identifier for error messages
        form_id: Form/pose identifier for error messages (can be None)
        char_data: Character data dict (to check for multi-limbed figure type)
        
    Raises:
        ValueError: If hand assignments are invalid and character is not multi-limbed
        
    Examples:
        Valid assignments:
        - ["sword : main_hand : gripped", "shield : off_hand : held"]
        - ["greatsword : both_hands : gripped with both hands"]
        
        Invalid assignments (for bipedal_humanoid):
        - ["sword1 : main_hand : gripped", "sword2 : main_hand : held"]  # Multiple main_hand
        - ["greatsword : both_hands : gripped", "dagger : main_hand : held"]  # both_hands + main_hand
        
        Multi-limbed characters (e.g., "multi_limbed_bipedal") allow these conflicts but show warnings.
    """
    # Check if character is multi-limbed (has more than 2 arms)
    figure_type = char_data.get("figure_type", "bipedal_humanoid")
    is_multi_limbed = "multi_limbed" in figure_type
    max_hands = 4 if is_multi_limbed else 2  # Multi-limbed gets 4 hands
    
    # Count hand assignments by parsing equipment strings
    main_hand_count = 0
    off_hand_count = 0
    both_hands_count = 0
    
    for item in equipment:
        # Parse format: "item (details) : position : description"
        if " : " in item:
            parts = item.split(" : ", 2)
            if len(parts) >= 2:
                position = parts[1].strip()
                if position == "main_hand":
                    main_hand_count += 1
                elif position == "off_hand":
                    off_hand_count += 1
                elif position == "both_hands":
                    both_hands_count += 1
    
    # Check for conflicts
    total_hands_needed = main_hand_count + off_hand_count + (both_hands_count * 2)
    
    if both_hands_count > 0 and (main_hand_count > 0 or off_hand_count > 0):
        error_msg = (
            f"[{character_id}:{form_id}] HAND CONFLICT: Equipment requires both_hands "
            f"({both_hands_count} item{'s' if both_hands_count > 1 else ''}) "
            f"but also assigns main_hand ({main_hand_count}) and/or off_hand ({off_hand_count}). "
            f"Character only has {max_hands} hands!"
        )
        if not is_multi_limbed:
            raise ValueError(error_msg)
        else:
            print(f"WARNING: {error_msg}", file=sys.stderr)
    elif total_hands_needed > max_hands:
        error_msg = (
            f"[{character_id}:{form_id}] HAND CONFLICT: Equipment requires {total_hands_needed} hands "
            f"(main_hand: {main_hand_count}, off_hand: {off_hand_count}, both_hands: {both_hands_count}). "
            f"Character only has {max_hands} hands!"
        )
        if not is_multi_limbed:
            raise ValueError(error_msg)
        else:
            print(f"WARNING: {error_msg}", file=sys.stderr)
    elif main_hand_count > 1:
        error_msg = f"[{character_id}:{form_id}] HAND CONFLICT: Multiple items ({main_hand_count}) assigned to main_hand."
        if not is_multi_limbed:
            raise ValueError(error_msg)
        else:
            print(f"WARNING: {error_msg}", file=sys.stderr)
    elif off_hand_count > 1:
        error_msg = f"[{character_id}:{form_id}] HAND CONFLICT: Multiple items ({off_hand_count}) assigned to off_hand."
        if not is_multi_limbed:
            raise ValueError(error_msg)
        else:
            print(f"WARNING: {error_msg}", file=sys.stderr)
