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
    """Extract the generic render rules prompt snippet from JSON."""
    return json_data.get("generic_render_rules", {}).get("prompt_snippet", "")


def extract_miniature_snippet(json_data: Dict[str, Any]) -> str:
    """Extract the miniature scale rules prompt snippet from JSON."""
    return json_data.get("miniature_scale_rules", {}).get("prompt_snippet", "")


def extract_thematic_snippet(json_data: Dict[str, Any]) -> str:
    """Extract the general thematic rules prompt snippet from JSON."""
    return json_data.get("thematic_rules", {}).get("prompt_snippet", "")


def extract_style_snippet(json_data: Dict[str, Any]) -> str:
    """Extract the style rules prompt snippet from JSON."""
    return json_data.get("style_rules", {}).get("prompt_snippet", "")


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
    pose_library: Dict[str, Any]
) -> str:
    """Compose a complete pose prompt from library reference + weapon definitions.
    
    Args:
        character_data: The character definition containing weapons and character_base
        pose_def: The pose definition with pose_library_ref and overrides
        pose_library: The loaded pose library data
    
    Returns:
        Composed prompt string with weapons injected and overrides applied
    """
    # Get the library pose reference
    library_ref = pose_def.get("pose_library_ref")
    if not library_ref:
        # Fallback to old-style direct prompt if no library reference
        return pose_def.get("prompt", "")
    
    # Find the pose in the library
    library_pose = find_pose_in_library(pose_library, library_ref)
    if not library_pose:
        return f"[ERROR: Pose {library_ref} not found in library]"
    
    # Validate pose compatibility and print warnings
    warnings = validate_pose_compatibility(character_data, library_pose, library_ref)
    if warnings:
        import sys
        print("\n⚠️  Pose Compatibility Warnings:", file=sys.stderr)
        for warning in warnings:
            print(f"   {warning}", file=sys.stderr)
        print(file=sys.stderr)
    
    # Get the base pose prompt from library
    pose_prompt = library_pose.get("pose_prompt", "")
    
    # Get weapon definitions
    weapons = character_data.get("weapons", {})
    main_hand_weapon = weapons.get("main_hand")
    off_hand_weapon = weapons.get("off_hand")
    
    # Check if pose has custom weapons_for_pose (for dual-wield scenarios)
    weapons_for_pose = pose_def.get("weapons_for_pose", {})
    if weapons_for_pose:
        # Use custom weapon assignment for this pose
        main_hand_name = weapons_for_pose.get("main_hand")
        off_hand_name = weapons_for_pose.get("off_hand")
        
        # Find weapons in holstered list if needed
        holstered = weapons.get("holstered", [])
        if main_hand_name and main_hand_name != weapons.get("main_hand", {}).get("name"):
            for h_weapon in holstered:
                if h_weapon.get("name") == main_hand_name:
                    main_hand_weapon = h_weapon.copy()
                    break
        if off_hand_name:
            for h_weapon in holstered:
                if h_weapon.get("name") == off_hand_name:
                    off_hand_weapon = h_weapon.copy()
                    break
    
    # Build weapon detail strings
    main_hand_detail = ""
    if main_hand_weapon:
        name = main_hand_weapon.get("name", "prop")
        desc = main_hand_weapon.get("description", "")
        visual = main_hand_weapon.get("visual_detail", "")
        attachment = main_hand_weapon.get("attachment", "")
        
        # Check for prop state override
        prop_override = pose_def.get("prop_override", {})
        state = prop_override.get("main_hand_prop_state", "held_firmly")
        orientation = prop_override.get("main_hand_orientation", "")
        
        if "slung" in state:
            main_hand_detail = f"{name} ({desc}) supported by {attachment}, {state.replace('_', ' ')}"
        else:
            main_hand_detail = f"{name} ({desc}) {state.replace('_', ' ')}"
        
        if orientation:
            main_hand_detail += f", {orientation.replace('_', ' ')}"
        if visual:
            main_hand_detail += f"; {visual}"
    
    off_hand_detail = ""
    if off_hand_weapon:
        name = off_hand_weapon.get("name", "prop")
        desc = off_hand_weapon.get("description", "")
        visual = off_hand_weapon.get("visual_detail", "")
        
        prop_override = pose_def.get("prop_override", {})
        state = prop_override.get("off_hand_prop_state", "held_firmly")
        orientation = prop_override.get("off_hand_orientation", "")
        
        off_hand_detail = f"{name} ({desc}) {state.replace('_', ' ')}"
        if orientation:
            off_hand_detail += f", {orientation.replace('_', ' ')}"
        if visual:
            off_hand_detail += f"; {visual}"
    
    # Replace placeholders in pose prompt
    if main_hand_detail:
        pose_prompt = pose_prompt.replace("MAIN_HAND_PROP", main_hand_detail)
    else:
        pose_prompt = pose_prompt.replace("MAIN_HAND_PROP", "[empty hand]")
    
    if off_hand_detail:
        pose_prompt = pose_prompt.replace("OFF_HAND_PROP", off_hand_detail)
    else:
        # Remove OFF_HAND_PROP references for unarmed off-hand
        pose_prompt = re.sub(r"OFF_HAND_PROP[^;.]*[;.]", "", pose_prompt)
    
    # Add character-specific override text if present
    character_override = pose_def.get("character_override", "")
    if character_override:
        pose_prompt += f" {character_override}"
    
    # Add holstered weapons visibility
    holstered = weapons.get("holstered", [])
    if holstered:
        holstered_names = []
        for h in holstered:
            h_name = h.get("name", "item")
            h_loc = h.get("location", "on belt")
            holstered_names.append(f"{h_name} {h_loc}")
        if holstered_names:
            pose_prompt += f"; {', '.join(holstered_names)}"
    
    return pose_prompt


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
    pose_def: Dict[str, Any],
    pose_id: str
) -> List[str]:
    """Check if character weapons match pose requirements.
    
    Args:
        character_data: Character definition with weapons
        pose_def: Pose definition from pose library
        pose_id: Pose ID for error messages
        
    Returns:
        List of warning messages (empty if no issues)
    """
    warnings = []
    
    # Get character weapon config
    weapons = character_data.get("weapons", {})
    main_hand_weapon = weapons.get("main_hand")
    off_hand_weapon = weapons.get("off_hand")
    holstered_items = weapons.get("holstered", [])
    
    # Get pose requirements
    handedness_mode = pose_def.get("handedness_mode", "unarmed")
    main_hand_slot = pose_def.get("main_hand", {})
    off_hand_slot = pose_def.get("off_hand", {})
    
    main_prop_classes = main_hand_slot.get("prop_class", [])
    off_prop_classes = off_hand_slot.get("prop_class", [])
    
    # Check handedness compatibility
    if handedness_mode == "unarmed":
        if main_hand_weapon or off_hand_weapon:
            warnings.append(
                f"Pose '{pose_id}' is unarmed, but character has weapons equipped. "
                f"Weapons will be ignored in this pose."
            )
    
    elif handedness_mode == "single_handed":
        if not main_hand_weapon:
            if "none" not in main_prop_classes:
                warnings.append(
                    f"Pose '{pose_id}' requires a main hand weapon, but character has none equipped."
                )
        else:
            # Check if main hand weapon prop_class matches pose requirements
            weapon_prop_class = main_hand_weapon.get("prop_class", "compact")
            if weapon_prop_class not in main_prop_classes and "none" not in main_prop_classes:
                warnings.append(
                    f"Pose '{pose_id}' expects main hand prop_class {main_prop_classes}, "
                    f"but character has '{weapon_prop_class}'. May not render optimally."
                )
        
        if off_hand_weapon:
            warnings.append(
                f"Pose '{pose_id}' is single-handed, but character has off hand weapon. "
                f"Off hand weapon will be ignored."
            )
    
    elif handedness_mode == "two_handed":
        if not main_hand_weapon:
            warnings.append(
                f"Pose '{pose_id}' requires a two-handed weapon in main hand, but character has none equipped."
            )
        else:
            weapon_prop_class = main_hand_weapon.get("prop_class", "compact")
            if weapon_prop_class not in main_prop_classes:
                warnings.append(
                    f"Pose '{pose_id}' expects two-handed prop_class {main_prop_classes}, "
                    f"but character has '{weapon_prop_class}'. May not render optimally."
                )
        
        if off_hand_weapon:
            warnings.append(
                f"Pose '{pose_id}' is two-handed, but character has separate off hand weapon. "
                f"Off hand weapon will be ignored (both hands on main weapon)."
            )
    
    elif handedness_mode == "dual_wield":
        if not main_hand_weapon:
            warnings.append(
                f"Pose '{pose_id}' requires a main hand weapon, but character has none equipped."
            )
        if not off_hand_weapon:
            warnings.append(
                f"Pose '{pose_id}' requires an off hand weapon, but character has none equipped."
            )
        
        if main_hand_weapon:
            weapon_prop_class = main_hand_weapon.get("prop_class", "compact")
            if weapon_prop_class not in main_prop_classes and "none" not in main_prop_classes:
                warnings.append(
                    f"Pose '{pose_id}' expects main hand prop_class {main_prop_classes}, "
                    f"but character has '{weapon_prop_class}'. May not render optimally."
                )
        
        if off_hand_weapon:
            weapon_prop_class = off_hand_weapon.get("prop_class", "compact")
            if weapon_prop_class not in off_prop_classes and "none" not in off_prop_classes:
                warnings.append(
                    f"Pose '{pose_id}' expects off hand prop_class {off_prop_classes}, "
                    f"but character has '{weapon_prop_class}'. May not render optimally."
                )
    
    return warnings


def resolve_prompt_from_json(
    json_data: Dict[str, Any], 
    character: Optional[Union[int, str]] = None,
    form: Optional[str] = None,
    refinement_path: Optional[str] = None
) -> Tuple[str, List[str], Optional[str]]:
    """Resolve a prompt from JSON using various addressing methods.
    
    Args:
        json_data: The loaded JSON data
        character: Character ID (int) or name (str)
        form: Form/refinement name (or pose name in v2 structure)
        refinement_path: Full path like '1:1' or 'alpha:human'
    
    Returns:
        Tuple of (prompt string, list of thematic snippets from refinement path, gender or None)
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
        
        # Check if this is a pose library reference
        if "pose_library_ref" in first_item and pose_library:
            refinement_prompt = compose_pose_prompt_from_library(
                char_data, first_item, pose_library
            )
        else:
            refinement_prompt = first_item.get("prompt", "")
        
        # Prepend character_base to refinement prompt if present
        if character_base:
            final_prompt = f"{character_base}, {refinement_prompt}"
        else:
            final_prompt = refinement_prompt

        # Use item-level gender if present, else character-level
        gender = first_item.get("gender", char_gender)

        return final_prompt, thematic, gender
    
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
    
    # Check if this is a pose library reference
    if "pose_library_ref" in item and pose_library:
        refinement_prompt = compose_pose_prompt_from_library(
            char_data, item, pose_library
        )
    else:
        refinement_prompt = item.get("prompt", "")
    
    # Prepend character_base to refinement prompt if present
    if character_base:
        final_prompt = f"{character_base}, {refinement_prompt}"
    else:
        final_prompt = refinement_prompt

    # Use item-level gender if present, else character-level
    gender = item.get("gender", char_gender)

    return final_prompt, thematic, gender


def build_final_prompt(
    base_prompt: str,
    *,
    gender: Optional[str] = None,
    thematic_snippets: List[str] = None,
    thematic_general: str = "",
    style_snippet: str = "",
    generic_snippet: str,
    miniature_snippet: str,
    include_generic: bool,
    include_miniature: bool,
    no_base: bool = False,
) -> str:
    base_prompt = base_prompt.strip().rstrip(",")

    parts = [base_prompt]
    
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
            parts.append(f"{gender_lower}")
    
    # Add thematic snippets from refinements
    if thematic_snippets:
        parts.extend(thematic_snippets)
    
    # Add general thematic snippet
    if thematic_general:
        parts.append(thematic_general)
    
    # Add style snippet
    if style_snippet:
        parts.append(style_snippet)
    
    if include_generic and generic_snippet:
        parts.append(generic_snippet)
    if include_miniature and miniature_snippet:
        parts.append(miniature_snippet)

    if no_base:
        parts.append(
            "no base, no stand, not mounted, no plinth, no pedestal, no ground plane"
        )

    return ", ".join(p.strip().rstrip(",") for p in parts if p.strip())


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
                refinements = char_data.get("refinements", [])

                for ref in refinements:
                    ref_name = ref.get("name", "")
                    p0 = ref.get("prompt", "")
                    # Prefer refinement-level gender when present
                    gender_for_prompt = ref.get("gender", char_gender)
                    thematic_snip = []
                    if "thematic_snippet" in ref:
                        snippet_val = ref["thematic_snippet"]
                        if isinstance(snippet_val, list):
                            for ref_item in snippet_val:
                                if ref_item in thematic_forms and thematic_forms[ref_item]:
                                    thematic_snip.append(thematic_forms[ref_item])
                                else:
                                    thematic_snip.append(ref_item)
                        else:
                            thematic_snip.append(snippet_val)
                    p = build_final_prompt(
                        p0,
                        gender=gender_for_prompt,
                        thematic_snippets=thematic_snip,
                        thematic_general=thematic_general,
                        style_snippet=style_snippet,
                        generic_snippet=generic_snippet,
                        miniature_snippet=miniature_snippet,
                        include_generic=include_generic,
                        include_miniature=include_miniature,
                        no_base=args.no_base,
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
            refinements = char_data.get("refinements", [])

            for ref in refinements:
                ref_name = ref.get("name", "")
                p0 = ref.get("prompt", "")
                # Prefer refinement-level gender when present
                gender_for_prompt = ref.get("gender", char_gender)
                thematic_snip = []
                if "thematic_snippet" in ref:
                    snippet_val = ref["thematic_snippet"]
                    if isinstance(snippet_val, list):
                        for ref_item in snippet_val:
                            if ref_item in thematic_forms and thematic_forms[ref_item]:
                                thematic_snip.append(thematic_forms[ref_item])
                            else:
                                thematic_snip.append(ref_item)
                    else:
                        thematic_snip.append(snippet_val)
                p = build_final_prompt(
                    p0,
                    gender=gender_for_prompt,
                    thematic_snippets=thematic_snip,
                    thematic_general=thematic_general,
                    style_snippet=style_snippet,
                    generic_snippet=generic_snippet,
                    miniature_snippet=miniature_snippet,
                    include_generic=include_generic,
                    include_miniature=include_miniature,
                    no_base=args.no_base,
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
        
        refinements = char_data.get("refinements", [])
        if not refinements:
            raise PromptNotFoundError(
                f"No refinements found for character: {character_id}"
            )

        if args.dry_run:
            blocks: list[str] = []
            for ref in refinements:
                ref_name = ref.get("name", "")
                p0 = ref.get("prompt", "")
                # Prefer refinement-level gender when present
                gender_for_prompt = ref.get("gender", char_gender)
                thematic_snip = []
                if "thematic_snippet" in ref:
                    snippet_val = ref["thematic_snippet"]
                    if isinstance(snippet_val, list):
                        # List of references - resolve each one
                        for ref_item in snippet_val:
                            if ref_item in thematic_forms and thematic_forms[ref_item]:
                                thematic_snip.append(thematic_forms[ref_item])
                            else:
                                # Not a form reference, use as-is
                                thematic_snip.append(ref_item)
                    else:
                        # Legacy: single string value
                        thematic_snip.append(snippet_val)
                p = build_final_prompt(
                    p0,
                    gender=gender_for_prompt,
                    thematic_snippets=thematic_snip,
                    thematic_general=thematic_general,
                    style_snippet=style_snippet,
                    generic_snippet=generic_snippet,
                    miniature_snippet=miniature_snippet,
                    include_generic=include_generic,
                    include_miniature=include_miniature,
                    no_base=args.no_base,
                )
                blocks.append(f"[{character_id}:{ref_name}]\n{sanitize_for_ascii(format_for_chat(p))}")

            out_text = "\n\n".join(blocks).strip() + "\n"
            if args.copy:
                copy_to_clipboard_windows(out_text)
            print(out_text, end="")
            return 0

        args.out.mkdir(parents=True, exist_ok=True)
        for ref in refinements:
            ref_name = ref.get("name", "")
            p0 = ref.get("prompt", "")
            # Prefer refinement-level gender when present
            gender_for_prompt = ref.get("gender", char_gender)
            thematic_snip = []
            if "thematic_snippet" in ref:
                snippet_val = ref["thematic_snippet"]
                if isinstance(snippet_val, list):
                    # List of references - resolve each one
                    for ref_item in snippet_val:
                        if ref_item in thematic_forms and thematic_forms[ref_item]:
                            thematic_snip.append(thematic_forms[ref_item])
                        else:
                            # Not a form reference, use as-is
                            thematic_snip.append(ref_item)
                else:
                    # Legacy: single string value
                    thematic_snip.append(snippet_val)
            p = build_final_prompt(
                p0,
                gender=gender_for_prompt,
                thematic_snippets=thematic_snip,
                thematic_general=thematic_general,
                style_snippet=style_snippet,
                generic_snippet=generic_snippet,
                miniature_snippet=miniature_snippet,
                include_generic=include_generic,
                include_miniature=include_miniature,
                no_base=args.no_base,
            )
            png_bytes = generate_image_openai(p, model=args.model, size=args.size)
            out_path = build_output_path(
                args.out, character=character_id, form=ref_name
            )
            out_path.write_bytes(png_bytes)
            print(str(out_path))
        return 0

    # Single (character, form) - form_id must be specified to reach here
    prompt0, thematic_snip, gender = resolve_prompt_from_json(
        json_data, character=character_id, form=form_id
    )
    prompt = build_final_prompt(
        prompt0,
        gender=gender,
        thematic_snippets=thematic_snip,
        thematic_general=thematic_general,
        style_snippet=style_snippet,
        generic_snippet=generic_snippet,
        miniature_snippet=miniature_snippet,
        include_generic=include_generic,
        include_miniature=include_miniature,
        no_base=args.no_base,
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
