#!/usr/bin/env python
"""create_image.py

Generate an image from prompts stored in a JSON file (garou.json).

Usage examples (PowerShell):
  python create_image.py garou.json 1:1
  python create_image.py myproject.json alpha:human --dry-run
  python create_image.py garou.json --character 1 --form human
  python create_image.py garou.json 1 --all
  python create_image.py garou.json --list

Notes:
- First argument is the JSON filename (required)
- API calls require an OpenAI API key in the environment:
        $env:OPENAI_API_KEY = "..."
- If you only want a copy/paste prompt for ChatGPT, use --prompt-only (no API key needed).
- Supports nested refinements: use 1:1 or alpha:human or mixed (1:human, alpha:1)
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


def sanitize_for_ascii(text: str) -> str:
    """Replace common Unicode characters with ASCII equivalents for safe terminal output."""
    replacements = {
        '\u00b0': ' degrees',  # ° (degree symbol)
        '\u2013': '-',         # – (en dash)
        '\u2014': '--',        # — (em dash)
        '\u2018': "'",         # ' (left single quote)
        '\u2019': "'",         # ' (right single quote)
        '\u201c': '"',         # " (left double quote)
        '\u201d': '"',         # " (right double quote)
        '\u2026': '...',       # … (ellipsis)
        '\u00a0': ' ',         # non-breaking space
    }
    for unicode_char, ascii_equiv in replacements.items():
        text = text.replace(unicode_char, ascii_equiv)
    return text


def format_for_chat(prompt: str) -> str:
    """Format a prompt for copy/paste into ChatGPT."""
    return prompt.strip()


def copy_to_clipboard_windows(text: str) -> None:
    """Copy text to Windows clipboard using PowerShell."""
    try:
        # Pipe text to PowerShell's Set-Clipboard cmdlet via stdin
        result = subprocess.run(
            ["powershell", "-Command", "$input | Set-Clipboard"],
            input=text.encode('utf-8'),
            check=True,
            timeout=5,
            capture_output=True
        )
    except Exception as e:
        # Silently fail if clipboard copy doesn't work
        print(f"Warning: Could not copy to clipboard: {e}", file=sys.stderr)


@dataclass
class CharacterData:
    """Holds JSON data for a character."""
    data: Dict[str, Any]
    generic_snippet: str
    miniature_snippet: str

    def get_id(self) -> int:
        return self.data.get("id", 0)

    def get_name(self) -> str:
        return self.data.get("name", "")

    def get_refinements(self) -> List[Dict[str, Any]]:
        return self.data.get("refinements", [])


def load_json_data(json_path: Path) -> Dict[str, Any]:
    """Load and parse the JSON file, resolving any imports."""
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Resolve imports if present.
    # Intentionally resolve relative import paths against the current working directory
    # (the directory create_image.py is run from) to make libraries portable across machines.
    if "imports" in data:
        data = resolve_imports(data, Path.cwd())
    
    return data


def resolve_imports(data: Dict[str, Any], base_path: Path) -> Dict[str, Any]:
    """Resolve file references in the imports section and merge them into the data.
    
    This function loads referenced JSON files and merges their content into the main data structure.
    Files are cached to avoid loading the same file multiple times.
    """
    imports = data.get("imports", {})
    if not imports:
        return data
    
    # Cache for loaded files to avoid duplicate loads
    file_cache = {}
    
    # Resolve generic_render_rules
    if "generic_render_rules" in imports:
        rules_path = resolve_path(imports["generic_render_rules"], base_path)
        if rules_path not in file_cache:
            with open(rules_path, "r", encoding="utf-8") as f:
                file_cache[rules_path] = json.load(f)
        data["generic_render_rules"] = file_cache[rules_path].get("generic_render_rules", {})
    
    # Resolve miniature_scale_rules
    if "miniature_scale_rules" in imports:
        rules_path = resolve_path(imports["miniature_scale_rules"], base_path)
        if rules_path not in file_cache:
            with open(rules_path, "r", encoding="utf-8") as f:
                file_cache[rules_path] = json.load(f)
        data["miniature_scale_rules"] = file_cache[rules_path].get("miniature_scale_rules", {})
    
    # Resolve common_thematic_forms
    if "common_thematic_forms" in imports:
        forms_path = resolve_path(imports["common_thematic_forms"], base_path)
        if forms_path not in file_cache:
            with open(forms_path, "r", encoding="utf-8") as f:
                file_cache[forms_path] = json.load(f)
        # Merge common forms into thematic_rules.forms
        common_forms = file_cache[forms_path].get("common_thematic_forms", {})
        if "thematic_rules" not in data:
            data["thematic_rules"] = {}
        if "forms" not in data["thematic_rules"]:
            data["thematic_rules"]["forms"] = {}
        # Merge common forms (character file forms take precedence)
        for form_name, form_data in common_forms.items():
            if form_name not in data["thematic_rules"]["forms"]:
                data["thematic_rules"]["forms"][form_name] = form_data
    
    # Resolve style_rules
    if "style_rules" in imports:
        style_path = resolve_path(imports["style_rules"], base_path)
        if style_path not in file_cache:
            with open(style_path, "r", encoding="utf-8") as f:
                file_cache[style_path] = json.load(f)
        # Import the entire style file content (it has prompt_snippet at root level)
        data["style_rules"] = file_cache[style_path]
    
    # Resolve pose_library
    if "pose_library" in imports:
        pose_path = resolve_path(imports["pose_library"], base_path)
        if pose_path not in file_cache:
            with open(pose_path, "r", encoding="utf-8") as f:
                file_cache[pose_path] = json.load(f)
        data["pose_library"] = file_cache[pose_path]
    
    return data


def resolve_path(path_str: str, base_path: Path) -> Path:
    """Resolve a path string relative to base_path or as absolute."""
    path = Path(path_str)
    if path.is_absolute():
        return path
    return (base_path / path).resolve()


def extract_generic_snippet(json_data: Dict[str, Any]) -> str:
    """Extract the generic render rules sections from JSON."""
    sections = json_data.get("generic_render_rules", {}).get("sections", {})
    # For backwards compatibility, also check for prompt_snippet
    if not sections:
        return json_data.get("generic_render_rules", {}).get("prompt_snippet", "")
    return sections


def extract_miniature_snippet(json_data: Dict[str, Any]) -> str:
    """Extract the miniature scale rules prompt snippet from JSON."""
    return json_data.get("miniature_scale_rules", {}).get("prompt_snippet", "")


def extract_thematic_snippet(json_data: Dict[str, Any]) -> str:
    """Extract the general thematic rules prompt snippet from JSON."""
    return json_data.get("thematic_rules", {}).get("prompt_snippet", "")


def extract_style_snippet(json_data: Dict[str, Any]) -> str:
    """Extract the style rules prompt snippet from JSON."""
    return json_data.get("style_rules", {}).get("prompt_snippet", "")


def extract_default_proportions(json_data: Dict[str, Any]) -> str:
    """Extract default proportions from style rules."""
    return json_data.get("style_rules", {}).get("default_proportions", "")


def extract_pose_library(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract the pose library from JSON (if present)."""
    return json_data.get("pose_library", {})


def find_pose_in_library(pose_library: Dict[str, Any], pose_id: str) -> Optional[Dict[str, Any]]:
    """Find a specific pose by pose_id in the library."""
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
) -> Tuple[str, str]:
    """Compose a pose prompt by looking up a pose_library_ref.
    
    Args:
        character_data: The character definition containing character_base
        pose_def: The pose/refinement containing pose_library_ref
        pose_library: The loaded pose library JSON
        json_data: Full JSON data for figure_type validation
        equipment: Resolved equipment list to extract hand-held props
        
    Returns:
        Tuple of (character_override, pose_prompt) - both strings
        
    Raises:
        PromptNotFoundError: If pose_library_ref is missing or not found in library
    """
    import sys
    
    pose_ref = pose_def.get("pose_library_ref")
    if not pose_ref:
        raise PromptNotFoundError("pose_library_ref is missing in pose definition")
    
    # Find the pose in the library
    library_pose = find_pose_in_library(pose_library, pose_ref)
    if not library_pose:
        available_ids = [p.get("pose_id", "?") for p in pose_library.get("poses", [])[:15]]
        raise PromptNotFoundError(
            f"Pose '{pose_ref}' not found in pose library.\n"
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
    
    # Get character_override (for appearance/expression modifications)
    character_override = pose_def.get("character_override", "")
    
    return character_override, pose_prompt


def extract_thematic_forms(json_data: Dict[str, Any]) -> Dict[str, str]:
    """Extract form definitions from thematic_rules.forms.
    Returns a dict mapping form names to their prompt_snippet."""
    forms = json_data.get("thematic_rules", {}).get("forms", {})
    result = {}
    for name, form in forms.items():
        # Skip non-dict entries (like _comment)
        if not isinstance(form, dict):
            continue
        result[name] = form.get("prompt_snippet", "")
    return result


def remove_base_language(miniature_snippet: str) -> str:
    """Remove 'mounted on a ... base' phrase from the 40mm snippet.

    This keeps the rest of the 40mm miniature styling (materials, lighting, scale cues)
    while avoiding a physical base being depicted.
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


class PromptNotFoundError(RuntimeError):
    pass


def find_character_by_id_or_name(
    json_data: Dict[str, Any], identifier: Union[int, str]
) -> Optional[Dict[str, Any]]:
    """Find a character by numeric ID or string name."""
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
    """Find a refinement by numeric ID or string name."""
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
    """Parse a refinement path like '1:1' or 'alpha:human' into components."""
    return [p.strip() for p in path_str.split(":") if p.strip()]


def validate_pose_compatibility(
    character_data: Dict[str, Any],
    character_pose_def: Dict[str, Any],
    library_pose_def: Dict[str, Any],
    pose_id: str,
    json_data: Dict[str, Any]
) -> List[str]:
    """Check if character weapons match pose requirements.
    
    Args:
        character_data: Character definition with weapons
        character_pose_def: Pose definition from character JSON (with overrides)
        library_pose_def: Pose definition from pose library
        pose_id: Pose ID for error messages
        json_data: The full JSON data (for figure_type validation from forms)
        
    Returns:
        List of warning messages (empty if no issues)
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


def resolve_prop_references(equipment: List[str], prop_definitions: Dict[str, str]) -> List[str]:
    """Resolve prop references to their full descriptions with positioning.
    
    Args:
        equipment: List of equipment strings, either:
                  - New format: "prop_id : position : pose_description"
                  - Legacy format: "full description (details) : position : pose_description"
        prop_definitions: Dict mapping prop_id to "description (details)"
        
    Returns:
        List of resolved equipment strings in format "description (details) : position : pose_description"
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
    
    Args:
        equipment: List of equipment strings in format "item [...] [hand_position] ..."
        character_id: Character identifier for error messages
        form_id: Form/pose identifier for error messages
        char_data: Character data dict (to check for multi-limbed figure type)
        
    Raises:
        ValueError: If hand assignments are invalid and character is not multi-limbed
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


def resolve_prompt_from_json(
    json_data: Dict[str, Any], 
    character: Optional[Union[int, str]] = None,
    form: Optional[str] = None,
    refinement_path: Optional[str] = None
) -> Tuple[str, List[str], Optional[str], str, List[str]]:
    """Resolve a prompt from JSON using various addressing methods.
    
    Args:
        json_data: The loaded JSON data
        character: Character ID (int) or name (str)
        form: Form/refinement name (or pose name in v2 structure)
        refinement_path: Full path like '1:1' or 'alpha:human'
    
    Returns:
        Tuple of (prompt string, list of thematic snippets, gender or None, proportions string, equipment list)
    """
    # Extract form definitions once
    thematic_forms = extract_thematic_forms(json_data)
    
    # Extract pose library if present
    pose_library = extract_pose_library(json_data)
    
    # Parse refinement_path if provided
    if refinement_path:
        parts = parse_refinement_path(refinement_path)
        if len(parts) >= 1:
            character = parts[0]
        if len(parts) >= 2:
            form = parts[1]
    
    if character is None:
        raise PromptNotFoundError("Character must be specified")
    
    # Find the character
    char_data = find_character_by_id_or_name(json_data, character)
    if not char_data:
        # List available characters
        chars = json_data.get("characters", [])
        if chars:
            available = [f"{c.get('id')}:{c.get('name')}" for c in chars]
            raise PromptNotFoundError(
                f"Character '{character}' not found.\n"
                f"Available characters: {', '.join(available)}"
            )
        else:
            raise PromptNotFoundError(f"Character '{character}' not found (no characters in database)")
    
    # Get character_base if present
    character_base = char_data.get("character_base", "").strip()
    
    # Get proportions from character data
    proportions = char_data.get("proportions", "").strip()
    
    # Get gender from character data (refinements may override)
    char_gender = char_data.get("gender", None)
    
    # Check if this is a v2 structure with 'poses' instead of 'refinements'
    poses = char_data.get("poses", [])
    refinements = char_data.get("refinements", [])
    
    # Use whichever is present
    items_to_search = poses if poses else refinements
    
    # If no form specified, return character description or first item
    if form is None:
        if not items_to_search:
            raise PromptNotFoundError(
                f"No poses/refinements found for character: {character}"
            )
        # Return the first item's prompt and its thematic snippet
        first_item = items_to_search[0]
        thematic = []
        if "thematic_snippet" in first_item:
            snippet_val = first_item["thematic_snippet"]
            if isinstance(snippet_val, list):
                # List of references - resolve each one
                for ref in snippet_val:
                    if ref in thematic_forms and thematic_forms[ref]:
                        thematic.append(thematic_forms[ref])
                    else:
                        # Not a form reference, use as-is
                        thematic.append(ref)
            else:
                # Legacy: single string value
                thematic.append(snippet_val)
        
        # Use item-level gender if present, else character-level
        gender = first_item.get("gender", char_gender)
        
        # Extract equipment array - check for pose-level equipment_override first
        equipment = first_item.get("equipment_override", char_data.get("equipment", []))
        
        # Resolve prop references if prop_definitions exist
        prop_definitions = char_data.get("prop_definitions", {})
        equipment = resolve_prop_references(equipment, prop_definitions)
        
        # Validate hand assignments (raises ValueError if invalid for non-multi-limbed)
        validate_hand_assignments(equipment, str(character), form, char_data)
        
        # Check if this is a pose library reference
        pose_prompt = ""
        if "pose_library_ref" in first_item and pose_library:
            character_override, pose_prompt = compose_pose_prompt_from_library(
                char_data, first_item, pose_library, json_data, equipment
            )
            # Use character_override for appearance/expression additions
            refinement_prompt = character_override if character_override else ""
        else:
            refinement_prompt = first_item.get("prompt", "")
        
        # Prepend character_base to refinement prompt if present
        # Skip if refinement_prompt uses structured format (starts with "SUBJECT:")
        if character_base and refinement_prompt and not refinement_prompt.startswith("SUBJECT:"):
            final_prompt = f"{character_base}, {refinement_prompt}"
        elif character_base:
            final_prompt = character_base
        else:
            final_prompt = refinement_prompt

        return final_prompt, thematic, gender, proportions, equipment, pose_prompt
    
    # Find the item (pose or refinement)
    item = find_refinement_by_id_or_name(items_to_search, form)
    
    if not item:
        item_type = "poses" if poses else "refinements"
        available = [f"{r.get('id')}:{r.get('name')}" for r in items_to_search]
        raise PromptNotFoundError(
            f"Pose/refinement '{form}' not found for character '{character}'.\n"
            f"Available {item_type}: {', '.join(available)}"
        )
    
    # Collect thematic snippet from this item
    thematic = []
    if "thematic_snippet" in item:
        snippet_val = item["thematic_snippet"]
        if isinstance(snippet_val, list):
            # List of references - resolve each one
            for ref in snippet_val:
                if ref in thematic_forms and thematic_forms[ref]:
                    thematic.append(thematic_forms[ref])
                else:
                    # Not a form reference, use as-is
                    thematic.append(ref)
        else:
            # Legacy: single string value
            thematic.append(snippet_val)
    
    # Use item-level gender if present, else character-level
    gender = item.get("gender", char_gender)
    
    # Extract equipment array - check for pose-level equipment_override first
    equipment = item.get("equipment_override", char_data.get("equipment", []))
    
    # Resolve prop references if prop_definitions exist
    prop_definitions = char_data.get("prop_definitions", {})
    equipment = resolve_prop_references(equipment, prop_definitions)
    
    # Validate hand assignments (raises ValueError if invalid for non-multi-limbed)
    validate_hand_assignments(equipment, str(character), form, char_data)
    
    # Check if this is a pose library reference
    pose_prompt = ""
    if "pose_library_ref" in item and pose_library:
        character_override, pose_prompt = compose_pose_prompt_from_library(
            char_data, item, pose_library, json_data, equipment
        )
        # Use character_override for appearance/expression additions
        refinement_prompt = character_override if character_override else ""
    else:
        refinement_prompt = item.get("prompt", "")
    
    # Prepend character_base to refinement prompt if present
    # Skip if refinement_prompt uses structured format (starts with "SUBJECT:")
    if character_base and refinement_prompt and not refinement_prompt.startswith("SUBJECT:"):
        final_prompt = f"{character_base}, {refinement_prompt}"
    elif character_base:
        final_prompt = character_base
    else:
        final_prompt = refinement_prompt

    return final_prompt, thematic, gender, proportions, equipment, pose_prompt


def build_final_prompt(
    base_prompt: str,
    *,
    gender: Optional[str] = None,
    thematic_snippets: List[str] = None,
    thematic_general: str = "",
    proportions: str = "",
    default_proportions: str = "",
    style_snippet: str = "",
    generic_snippet,  # Can be str or dict of sections
    miniature_snippet: str = "",
    include_generic: bool,
    include_miniature: bool,
    no_base: bool = False,
    equipment: List[str] = None,
    character_id: str = "",
    form_id: str = "",
    pose_prompt: str = "",
) -> str:
    """Build the final prompt from components with structured sections.
    
    Args:
        base_prompt: Character base + pose description
        gender: Character gender
        thematic_snippets: Thematic form snippets
        thematic_general: General thematic prompt
        proportions: Character proportions
        default_proportions: Default proportions if character has none
        style_snippet: Style rules
        generic_snippet: Generic render rules (str or dict of sections)
        miniature_snippet: Miniature-specific rules
        include_generic: Whether to include generic rules
        include_miniature: Whether to include miniature rules
        no_base: Whether to specify no base/stand
        equipment: List of equipment/props with placement descriptions
        character_id: Character ID for asset naming
        form_id: Form/pose ID for asset naming
        pose_prompt: Pose description from pose library
        
    Returns:
        Complete formatted prompt string with structured sections
    """
    sections = []
    
    # ASSET_NAME section (if both IDs provided)
    if character_id and form_id:
        asset_name = f"{character_id}_{form_id}"
        sections.append(f"ASSET_NAME: {asset_name}")
    
    # CHARACTER section
    character_parts = [base_prompt.strip().rstrip(",")]
    
    # Add gender hint if provided and not already explicitly stated
    if gender:
        gender_lower = gender.lower()
        base_lower = base_prompt.lower()
        
        # Check for explicit gender words
        has_gender = any(word in base_lower for word in [
            'female', 'male', 'woman', 'man ', ' man,', 'girl', 'boy',
            'feminine', 'masculine'
        ])
        
        # Add gender to all forms unless already present
        if not has_gender:
            character_parts.append(f"{gender_lower}")
    
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
    
    return "\n\n".join(sections)


def list_available_from_json(json_data: Dict[str, Any]) -> str:
    """Return a human-friendly listing of available characters and refinements."""
    characters = json_data.get("characters", [])
    lines: List[str] = []
    
    total_refinements = sum(len(c.get("refinements", [])) for c in characters)
    lines.append(f"Total characters: {len(characters)}")
    lines.append(f"Total refinements: {total_refinements}")
    lines.append("")
    
    for char in characters:
        char_id = char.get("id", "?")
        char_name = char.get("name", "unknown")
        char_title = char.get("title", "")
        
        lines.append(f"{char_id} ({char_name}): {char_title}")
        
        refinements = char.get("refinements", [])
        for ref in refinements:
            ref_id = ref.get("id", "?")
            ref_name = ref.get("name", "?")
            ref_desc = ref.get("description", "")
            lines.append(f"  {char_id}:{ref_id} or {char_name}:{ref_name} - {ref_desc}")
        
        lines.append("")
    
    return "\n".join(lines)


def resolve_prompt(prompts: Dict[PromptKey, str], character: int, form: str) -> str:
    key = PromptKey(character=character, form=form.lower())
    try:
        return prompts[key]
    except KeyError as e:
        available = sorted(
            (k for k in prompts.keys() if k.character == character),
            key=lambda k: k.form,
        )
        available_forms = ", ".join(k.form for k in available) if available else "(none)"
        raise PromptNotFoundError(
            f"No prompt found for character={character} form={form!r}. "
            f"Available for that character: {available_forms}"
        ) from e


def generate_image_openai(prompt: str, *, model: str, size: str) -> bytes:
    """Call OpenAI Images API and return PNG bytes.

    Uses the official OpenAI Python SDK.
    """
    try:
        from openai import OpenAI  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "Missing dependency 'openai'. Install with: pip install openai"
        ) from e

    client = OpenAI()

    result = client.images.generate(
        model=model,
        prompt=prompt,
        size=size,
    )

    # The SDK can return either base64 or URLs depending on configuration/model.
    # Prefer b64_json when available.
    data0 = result.data[0]

    if getattr(data0, "b64_json", None):
        return base64.b64decode(data0.b64_json)

    url = getattr(data0, "url", None)
    if url:
        # Fall back to downloading the URL.
        # Avoid adding extra dependency; use urllib.
        import urllib.request

        with urllib.request.urlopen(url) as resp:
            return resp.read()

    raise RuntimeError("Unexpected images response format: no b64_json or url")


def build_output_path(
    out_dir: Path, *, character: Union[int, str], form: str
) -> Path:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_form = str(form).lower()
    safe_char = str(character).replace(":", "_")
    filename = f"generated_{safe_char}_{safe_form}_{ts}.png"
    return out_dir / filename


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="create_image",
        description=(
            "Read prompts from a JSON file and generate an image for a given character + form. "
            "Supports nested refinements using path syntax like '1:1' or 'alpha:human'."
        ),
    )
    parser.add_argument(
        "filename",
        type=str,
        help="JSON file containing character definitions (e.g., garou.json, myproject.json)",
    )
    parser.add_argument(
        "character_positional",
        nargs="?",
        type=str,
        help="Character ID (number or name) or full path like '1:1' or 'alpha:human'. Can also use --character flag.",
    )
    parser.add_argument(
        "--character",
        "-c",
        type=str,
        help="Character ID (number or name) or full path like '1:1' or 'alpha:human'. Required unless using --list.",
    )
    parser.add_argument(
        "--form",
        "-f",
        type=str,
        help="Form/refinement name or ID. Not needed if using path syntax in --character.",
    )
    parser.add_argument(
        "--json",
        "-j",
        type=Path,
        help="Alternative way to specify JSON file (overrides positional filename argument)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("out"),
        help="Output directory for images (default: ./out)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-image-1",
        help="OpenAI image model (default: gpt-image-1)",
    )
    parser.add_argument(
        "--size",
        type=str,
        default="1024x1024",
        help="Image size (default: 1024x1024)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the resolved prompt only; do not call the API",
    )

    parser.add_argument(
        "--prompt-only",
        action="store_true",
        help="Print the resolved prompt only (alias of --dry-run).",
    )

    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy prompt-only output to the clipboard (Windows).",
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List available characters/forms found in the JSON and exit.",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate (or print) all forms for all characters. If --character is specified, generate all forms for that character only.",
    )

    parser.add_argument(
        "--no-miniature",
        action="store_true",
        help="Do not append the shared 40mm-miniature snippet to prompts.",
    )

    parser.add_argument(
        "--no-base",
        action="store_true",
        help="Do not include a miniature base in the 40mm snippet (keeps the 40mm look).",
    )

    parser.add_argument(
        "--no-generic",
        action="store_true",
        help="Do not append the shared generic rendering rules snippet to prompts.",
    )

    args = parser.parse_args(argv)

    if args.prompt_only:
        args.dry_run = True

    # Determine JSON file path (--json flag overrides positional filename)
    json_path = args.json if args.json else Path(args.filename)
    if not json_path.suffix:
        json_path = json_path.with_suffix(".json")

    # Load JSON data
    json_data = load_json_data(json_path)
    generic_snippet = extract_generic_snippet(json_data)
    miniature_snippet = extract_miniature_snippet(json_data)
    thematic_general = extract_thematic_snippet(json_data)
    style_snippet = extract_style_snippet(json_data)
    default_proportions = extract_default_proportions(json_data)
    thematic_forms = extract_thematic_forms(json_data)
    
    include_miniature = not args.no_miniature
    include_generic = not args.no_generic

    if include_miniature and args.no_base and miniature_snippet:
        miniature_snippet = remove_base_language(miniature_snippet)

    if args.list:
        print(list_available_from_json(json_data))
        return 0

    # Handle positional or flag-based character argument
    character_arg = args.character_positional or args.character
    
    # If --all is used without a character, generate all characters and all forms
    if args.all and character_arg is None:
        characters = json_data.get("characters", [])
        if not characters:
            raise PromptNotFoundError("No characters found in JSON")
        
        if args.dry_run:
            blocks: list[str] = []
            for char_data in characters:
                character_id = char_data.get("name", "") or char_data.get("id", "")
                char_gender = char_data.get("gender", None)
                char_proportions = char_data.get("proportions", "").strip()
                # Check for both poses and refinements
                poses = char_data.get("poses", [])
                refinements = char_data.get("refinements", [])
                items_to_generate = poses if poses else refinements

                for ref in items_to_generate:
                    ref_name = ref.get("name", "")
                    # Use resolve_prompt_from_json to handle pose library references
                    p0, thematic_snip, gender_for_prompt, ref_proportions, equipment, pose_prompt = resolve_prompt_from_json(
                        json_data, character=character_id, form=ref_name
                    )
                    # Use character proportions if ref doesn't have its own
                    proportions_to_use = ref_proportions if ref_proportions else char_proportions
                    p = build_final_prompt(
                        p0,
                        gender=gender_for_prompt,
                        thematic_snippets=thematic_snip,
                        thematic_general=thematic_general,
                        proportions=proportions_to_use,
                        default_proportions=default_proportions,
                        style_snippet=style_snippet,
                        generic_snippet=generic_snippet,
                        miniature_snippet=miniature_snippet,
                        include_generic=include_generic,
                        include_miniature=include_miniature,
                        no_base=args.no_base,
                        equipment=equipment,
                        character_id=str(character_id),
                        form_id=ref_name,
                        pose_prompt=pose_prompt,
                    )
                    blocks.append(f"[{character_id}:{ref_name}]\n{sanitize_for_ascii(format_for_chat(p))}")
            
            out_text = "\n\n".join(blocks).strip() + "\n"
            if args.copy:
                copy_to_clipboard_windows(out_text)
            print(out_text, end="")
            return 0
        
        # Generate images for all characters and all forms
        args.out.mkdir(parents=True, exist_ok=True)
        for char_data in characters:
            character_id = char_data.get("name", "") or char_data.get("id", "")
            char_gender = char_data.get("gender", None)
            char_proportions = char_data.get("proportions", "").strip()
            # Check for both poses and refinements
            poses = char_data.get("poses", [])
            refinements = char_data.get("refinements", [])
            items_to_generate = poses if poses else refinements

            for ref in items_to_generate:
                ref_name = ref.get("name", "")
                # Use resolve_prompt_from_json to handle pose library references
                p0, thematic_snip, gender_for_prompt, ref_proportions, equipment, pose_prompt = resolve_prompt_from_json(
                    json_data, character=character_id, form=ref_name
                )
                # Use character proportions if ref doesn't have its own
                proportions_to_use = ref_proportions if ref_proportions else char_proportions
                p = build_final_prompt(
                    p0,
                    gender=gender_for_prompt,
                    thematic_snippets=thematic_snip,
                    thematic_general=thematic_general,
                    proportions=proportions_to_use,
                    default_proportions=default_proportions,
                    style_snippet=style_snippet,
                    generic_snippet=generic_snippet,
                    miniature_snippet=miniature_snippet,
                    include_generic=include_generic,
                    include_miniature=include_miniature,
                    no_base=args.no_base,
                    equipment=equipment,
                    character_id=str(character_id),
                    form_id=ref_name,
                    pose_prompt=pose_prompt,
                )
                png_bytes = generate_image_openai(p, model=args.model, size=args.size)
                out_path = build_output_path(
                    args.out, character=character_id, form=ref_name
                )
                out_path.write_bytes(png_bytes)
                print(str(out_path))
        return 0
    
    if character_arg is None:
        parser.error("Character argument is required unless using --list or --all. Use positional argument or --character flag.")

    # Parse character - could be path like "1:1" or "alpha:human"
    character_id = None
    form_id = None
    
    if ":" in character_arg:
        # Path syntax
        parts = parse_refinement_path(character_arg)
        if len(parts) >= 1:
            character_id = parts[0]
        if len(parts) >= 2:
            form_id = parts[1]
        
    else:
        character_id = character_arg
    
    # If form is also specified as argument, it overrides path
    if args.form:
        form_id = args.form

    if args.all and form_id:
        parser.error("Use either --all or specify a form, not both")

    # Basic key check early for nicer UX.
    if not args.dry_run and not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is not set. In PowerShell: $env:OPENAI_API_KEY=\"...\""
        )

    # If no form specified, generate all refinements (--all is now default behavior)
    if not form_id or args.all:
        # Generate (or print) all refinements for this character
        char_data = find_character_by_id_or_name(json_data, character_id)
        if not char_data:
            raise PromptNotFoundError(f"Character not found: {character_id}")
        
        # Extract gender from character data (refinements may override)
        char_gender = char_data.get("gender", None)
        
        # Check for both poses and refinements
        poses = char_data.get("poses", [])
        refinements = char_data.get("refinements", [])
        items_to_generate = poses if poses else refinements
        
        if not items_to_generate:
            raise PromptNotFoundError(
                f"No poses/refinements found for character: {character_id}"
            )

        if args.dry_run:
            blocks: list[str] = []
            for ref in items_to_generate:
                ref_name = ref.get("name", "")
                # Use resolve_prompt_from_json to handle pose library references
                p0, thematic_snip, gender_for_prompt, ref_proportions, equipment, pose_prompt = resolve_prompt_from_json(
                    json_data, character=character_id, form=ref_name
                )
                # Use character proportions if ref doesn't have its own
                proportions_to_use = ref_proportions if ref_proportions else char_proportions
                p = build_final_prompt(
                    p0,
                    gender=gender_for_prompt,
                    thematic_snippets=thematic_snip,
                    thematic_general=thematic_general,
                    proportions=proportions_to_use,
                    default_proportions=default_proportions,
                    style_snippet=style_snippet,
                    generic_snippet=generic_snippet,
                    miniature_snippet=miniature_snippet,
                    include_generic=include_generic,
                    include_miniature=include_miniature,
                    no_base=args.no_base,
                    equipment=equipment,
                    character_id=str(character_id),
                    form_id=ref_name,
                    pose_prompt=pose_prompt,
                )
                blocks.append(f"[{character_id}:{ref_name}]\n{sanitize_for_ascii(format_for_chat(p))}")

            out_text = "\n\n".join(blocks).strip() + "\n"
            if args.copy:
                copy_to_clipboard_windows(out_text)
            print(out_text, end="")
            return 0

        args.out.mkdir(parents=True, exist_ok=True)
        for ref in items_to_generate:
            ref_name = ref.get("name", "")
            # Use resolve_prompt_from_json to handle pose library references
            p0, thematic_snip, gender_for_prompt, ref_proportions, equipment, pose_prompt = resolve_prompt_from_json(
                json_data, character=character_id, form=ref_name
            )
            # Use character proportions if ref doesn't have its own
            proportions_to_use = ref_proportions if ref_proportions else char_proportions
            p = build_final_prompt(
                p0,
                gender=gender_for_prompt,
                thematic_snippets=thematic_snip,
                thematic_general=thematic_general,
                proportions=proportions_to_use,
                default_proportions=default_proportions,
                style_snippet=style_snippet,
                generic_snippet=generic_snippet,
                miniature_snippet=miniature_snippet,
                include_generic=include_generic,
                include_miniature=include_miniature,
                no_base=args.no_base,
                equipment=equipment,
                character_id=str(character_id),
                form_id=ref_name,
                pose_prompt=pose_prompt,
            )
            png_bytes = generate_image_openai(p, model=args.model, size=args.size)
            out_path = build_output_path(
                args.out, character=character_id, form=ref_name
            )
            out_path.write_bytes(png_bytes)
            print(str(out_path))
        return 0

    # Single (character, form) - form_id must be specified to reach here
    prompt0, thematic_snip, gender, char_proportions, equipment, pose_prompt = resolve_prompt_from_json(
        json_data, character=character_id, form=form_id
    )
    
    # Get character name for asset naming
    char_data = find_character_by_id_or_name(json_data, character_id)
    character_name = char_data.get("name", str(character_id)) if char_data else str(character_id)
    
    prompt = build_final_prompt(
        prompt0,
        gender=gender,
        thematic_snippets=thematic_snip,
        thematic_general=thematic_general,
        proportions=char_proportions,
        default_proportions=default_proportions,
        style_snippet=style_snippet,
        generic_snippet=generic_snippet,
        miniature_snippet=miniature_snippet,
        include_generic=include_generic,
        include_miniature=include_miniature,
        no_base=args.no_base,
        equipment=equipment,
        character_id=character_name,
        form_id=str(form_id),
        pose_prompt=pose_prompt,
    )
    
    if args.dry_run:
        out_text = "create image: " + sanitize_for_ascii(format_for_chat(prompt)) + "\n"
        if args.copy:
            copy_to_clipboard_windows(out_text)
        print(out_text, end="")
        return 0

    args.out.mkdir(parents=True, exist_ok=True)
    png_bytes = generate_image_openai(prompt, model=args.model, size=args.size)
    out_path = build_output_path(args.out, character=character_id, form=form_id)
    out_path.write_bytes(png_bytes)
    print(str(out_path))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
