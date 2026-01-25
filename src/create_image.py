#!/usr/bin/env python
"""create_image.py

Generate an image from prompts stored in a JSON file (garou.json).

Usage examples (PowerShell):
  python create_image.py garou.json 1:1
  python create_image.py myproject.json alpha:human --dry-run
  python create_image.py garou.json 1 --all
  python create_image.py garou.json --list
  python create_image.py garou.json --page 1 --copy
  python create_image.py garou.json --page 2 --copy
  python create_image.py garou.json --page all --copy
  python create_image.py garou.json --page 1:1 --copy
  python create_image.py garou.json --page 1:{1:3} --copy
  python create_image.py garou.json --page 1:{1,4,5} --copy

Notes:
- First argument is the JSON filename (required)
- API calls require an OpenAI API key in the environment:
        $env:OPENAI_API_KEY = "..."
- If you only want a copy/paste prompt for ChatGPT, use --prompt-only (no API key needed).
- Supports nested refinements: use 1:1 or alpha:human or mixed (1:human, alpha:1)
- Reference sheets combine up to 9 poses with shared rules for efficient prompt generation
- Page specification supports subrefinement filtering: --page 1:1 (first subrefinement only), 
  --page 1:{1:3} (subrefinements 1-3), --page 1:{1,4,5} (subrefinements 1, 4, and 5)
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

# Handle imports for both direct script execution and module import
if __name__ == "__main__" and __package__ is None:
    # Running as a script - add parent dir to path and use absolute imports
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.json_loader import (
        load_json_data,
        validate_character_ids,
        resolve_imports,
        resolve_path,
        extract_generic_snippet,
        extract_miniature_snippet,
        extract_thematic_snippet,
        extract_style_snippet,
        extract_default_proportions,
        extract_thematic_forms,
    )
    from src.character_resolver import (
        find_character_by_id_or_name,
        find_refinement_by_id_or_name,
        parse_refinement_path,
    )
    from src.equipment_handler import (
        resolve_prop_references,
        validate_hand_assignments,
    )
    from src.pose_library import (
        extract_pose_library,
        find_pose_in_library,
        compose_pose_prompt_from_library,
        validate_pose_compatibility,
        remove_base_language,
        PromptNotFoundError,
    )
    from src.prompt_builder import (
        format_for_chat,
        build_final_prompt,
    )
    from src.reference_sheet import (
        deduplicate_figure_sections,
        parse_page_spec,
    )
else:
    # Running as a module - use relative imports
    from .json_loader import (
        load_json_data,
        validate_character_ids,
        resolve_imports,
        resolve_path,
        extract_generic_snippet,
        extract_miniature_snippet,
        extract_thematic_snippet,
        extract_style_snippet,
        extract_default_proportions,
        extract_thematic_forms,
    )
    from .character_resolver import (
        find_character_by_id_or_name,
        find_refinement_by_id_or_name,
        parse_refinement_path,
    )
    from .equipment_handler import (
        resolve_prop_references,
        validate_hand_assignments,
    )
    from .pose_library import (
        extract_pose_library,
        find_pose_in_library,
        compose_pose_prompt_from_library,
        validate_pose_compatibility,
        remove_base_language,
        PromptNotFoundError,
    )
    from .prompt_builder import (
        format_for_chat,
        build_final_prompt,
    )
    from .reference_sheet import (
        deduplicate_figure_sections,
        parse_page_spec,
    )


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




def resolve_prompt_from_json(
    json_data: Dict[str, Any], 
    character: Optional[Union[int, str]] = None,
    form: Optional[str] = None,
    refinement_path: Optional[str] = None
) -> Tuple[str, List[str], Optional[str], str, str, List[str], str, Optional[int], str]:
    """Resolve a prompt from JSON using various addressing methods.
    
    Args:
        json_data: The loaded JSON data
        character: Character ID (int) or name (str)
        form: Form/refinement name (or pose name in v2 structure)
        refinement_path: Full path like '1:1' or 'alpha:human'
    
    Returns:
        Tuple of (prompt string, list of thematic snippets, gender or None, proportions string, age string, equipment list, pose_prompt, camera_rotation, visual_notes)
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
    
    # Get visual_notes if present
    visual_notes = char_data.get("visual_notes", "").strip()
    
    # Get proportions from character data
    proportions = char_data.get("proportions", "").strip()
    
    # Get age from character tags
    tags = char_data.get("tags", {})
    age = tags.get("age", "") if isinstance(tags, dict) else ""
    
    # Get gender from character data (poses may override)
    char_gender = char_data.get("gender", None)
    
    # Get poses array
    poses = char_data.get("poses", [])
    
    # If no form specified, return character description or first item
    if form is None:
        if not poses:
            # No poses array - check for single 'pose' object
            single_pose = char_data.get("pose", None)
            
            thematic = []
            gender = char_gender
            equipment = char_data.get("equipment", [])
            
            # Resolve prop references if prop_definitions exist
            prop_definitions = char_data.get("prop_definitions", {})
            equipment = resolve_prop_references(equipment, prop_definitions)
            
            # Validate hand assignments
            validate_hand_assignments(equipment, str(character), None, char_data)
            
            # Check if this is a pose library reference
            pose_prompt = ""
            camera_rotation = None
            if single_pose and "pose_library_ref" in single_pose and pose_library:
                pose_details, library_pose_prompt, camera_rotation = compose_pose_prompt_from_library(
                    char_data, single_pose, pose_library, json_data, equipment
                )
                # Combine library pose with pose-specific details (additive)
                if pose_details:
                    pose_prompt = f"{library_pose_prompt}. {pose_details}" if library_pose_prompt else pose_details
                else:
                    pose_prompt = library_pose_prompt
            
            # Use character_base as the character prompt
            final_prompt = character_base
            
            return final_prompt, thematic, gender, proportions, age, equipment, pose_prompt, camera_rotation, visual_notes
        
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
        
        # Use character-level gender (no pose-level override)
        gender = char_gender
        
        # Extract equipment array - check for pose-level equipment_override first
        equipment = first_item.get("equipment_override", char_data.get("equipment", []))
        
        # Resolve prop references if prop_definitions exist
        prop_definitions = char_data.get("prop_definitions", {})
        equipment = resolve_prop_references(equipment, prop_definitions)
        
        # Validate hand assignments (raises ValueError if invalid for non-multi-limbed)
        validate_hand_assignments(equipment, str(character), form, char_data)
        
        # Check if this is a pose library reference
        pose_prompt = ""
        camera_rotation = None
        if "pose_library_ref" in first_item and pose_library:
            pose_details, library_pose_prompt, camera_rotation = compose_pose_prompt_from_library(
                char_data, first_item, pose_library, json_data, equipment
            )
            # Combine library pose with pose-specific details (additive)
            if pose_details:
                pose_prompt = f"{library_pose_prompt}. {pose_details}" if library_pose_prompt else pose_details
            else:
                pose_prompt = library_pose_prompt
        else:
            # No pose library, check for inline prompt
            inline_prompt = first_item.get("prompt", "")
            if inline_prompt and not inline_prompt.startswith("SUBJECT:"):
                # This is a pose-specific addition, add it to pose_prompt
                pose_prompt = inline_prompt
        
        # Use character_base as the character prompt
        final_prompt = character_base

        return final_prompt, thematic, gender, proportions, age, equipment, pose_prompt, camera_rotation, visual_notes
    
    # Find the specific pose
    item = find_refinement_by_id_or_name(poses, form)
    
    if not item:
        available = [f"{r.get('id')}:{r.get('name')}" for r in poses]
        raise PromptNotFoundError(
            f"Pose '{form}' not found for character '{character}'.\n"
            f"Available poses: {', '.join(available)}"
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
    
    # Use character-level gender (no pose-level override)
    gender = char_gender
    
    # Extract equipment array - check for pose-level equipment_override first
    equipment = item.get("equipment_override", char_data.get("equipment", []))
    
    # Resolve prop references if prop_definitions exist
    prop_definitions = char_data.get("prop_definitions", {})
    equipment = resolve_prop_references(equipment, prop_definitions)
    
    # Validate hand assignments (raises ValueError if invalid for non-multi-limbed)
    validate_hand_assignments(equipment, str(character), form, char_data)
    
    # Check if this is a pose library reference
    pose_prompt = ""
    camera_rotation = None
    if "pose_library_ref" in item and pose_library:
        pose_details, library_pose_prompt, camera_rotation = compose_pose_prompt_from_library(
            char_data, item, pose_library, json_data, equipment
        )
        # Combine library pose with pose-specific details (additive)
        if pose_details:
            pose_prompt = f"{library_pose_prompt}. {pose_details}" if library_pose_prompt else pose_details
        else:
            pose_prompt = library_pose_prompt
    else:
        # No pose library, check for inline prompt
        inline_prompt = item.get("prompt", "")
        if inline_prompt and not inline_prompt.startswith("SUBJECT:"):
            # This is a pose-specific addition, add it to pose_prompt
            pose_prompt = inline_prompt
    
    # Use character_base as the character prompt
    final_prompt = character_base

    return final_prompt, thematic, gender, proportions, age, equipment, pose_prompt, camera_rotation, visual_notes


def generate_image_openai(prompt: str, *, model: str, size: str) -> bytes:
    """Generate image using OpenAI API and return PNG bytes.

    Args:
        prompt: Text description of image to generate
        model: OpenAI model name (e.g., 'dall-e-3')
        size: Image size string (e.g., '1024x1024')
        
    Returns:
        PNG image data as bytes
        
    Raises:
        RuntimeError: If openai package is not installed
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
    """Build timestamped output path for generated image.
    
    Args:
        out_dir: Directory where image will be saved
        character: Character ID or name
        form: Form/refinement name
        
    Returns:
        Full path with format: generated_{character}_{form}_{timestamp}.png
    """
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_form = str(form).lower()
    safe_char = str(character).replace(":", "_")
    filename = f"generated_{safe_char}_{safe_form}_{ts}.png"
    return out_dir / filename


def list_available_from_json(json_data: Dict[str, Any]) -> str:
    """Return a human-friendly listing of available characters and poses."""
    characters = json_data.get("characters", [])
    lines: List[str] = []
    
    total_poses = sum(len(c.get("poses", [])) for c in characters)
    lines.append(f"Total characters: {len(characters)}")
    lines.append(f"Total poses: {total_poses}")
    lines.append("")
    
    for char in characters:
        char_id = char.get("id", "?")
        char_name = char.get("name", "unknown")
        char_title = char.get("title", "")
        
        lines.append(f"{char_id} ({char_name}): {char_title}")
        
        poses = char.get("poses", [])
        for pose in poses:
            pose_id = pose.get("id", "?")
            pose_name = pose.get("name", "?")
            pose_desc = pose.get("description", "")
            lines.append(f"  {char_id}:{pose_id} or {char_name}:{pose_name} - {pose_desc}")
        
        lines.append("")
    
    return "\n".join(lines)


def handle_reference_sheet(
    *,
    json_data: dict,
    spec: str,
    generic_snippet: str,
    miniature_snippet: str,
    thematic_general: str,
    style_snippet: str,
    default_proportions: str,
    thematic_forms: dict,
    include_generic: bool,
    include_miniature: bool,
    no_base: bool,
    copy: bool,
) -> int:
    """Generate a combined reference sheet prompt for multiple poses.
    
    Args:
        spec: Page specification string. Can be:
            - 'all' for all pages
            - '1' - page 1, all subrefinements  
            - '1:1' - page 1, only subrefinement 1
            - '1:{1:3}' - page 1, subrefinements 1-3
            - '1:{1,4,5}' - page 1, subrefinements 1, 4, and 5
        
    Returns:
        0 on success
    """
    characters = json_data.get("characters", [])
    if not characters:
        raise PromptNotFoundError("No characters found in JSON")
    
    # Parse the page specification
    page_spec, subrefinement_indices = parse_page_spec(spec)
    
    # Collect all available poses from all characters grouped by character: 1:1, 1:2, ..., 2:1, 2:2, ...
    all_pose_specs = []
    for char_data in characters:
        character_id = char_data.get("name", "") or char_data.get("id", "")
        poses = char_data.get("poses", [])
        refinements = char_data.get("refinements", [])
        single_pose = char_data.get("pose", None)
        if poses:
            for pose_idx in range(1, len(poses) + 1):
                # If subrefinement filtering is specified, only include matching subrefinements
                if subrefinement_indices is None or pose_idx in subrefinement_indices:
                    all_pose_specs.append((character_id, pose_idx))
        elif refinements:
            for pose_idx in range(1, len(refinements) + 1):
                # If subrefinement filtering is specified, only include matching subrefinements
                if subrefinement_indices is None or pose_idx in subrefinement_indices:
                    all_pose_specs.append((character_id, pose_idx))
        elif single_pose:
            all_pose_specs.append((character_id, None))
        else:
            all_pose_specs.append((character_id, None))

    if not all_pose_specs:
        if subrefinement_indices:
            raise PromptNotFoundError(f"No poses found matching subrefinement filter: {subrefinement_indices}")
        else:
            raise PromptNotFoundError("No poses found for reference sheet")
    
    # Parse page specification
    if page_spec == "all":
        # Generate all pages
        batches = []
        for i in range(0, len(all_pose_specs), 9):
            batches.append(all_pose_specs[i:i+9])
    else:
        # Parse page number (already validated by parse_page_spec)
        page_num = page_spec
        
        # Calculate start and end indices for this page
        start_idx = (page_num - 1) * 9
        end_idx = start_idx + 9
        
        if start_idx >= len(all_pose_specs):
            total_pages = (len(all_pose_specs) + 8) // 9  # Round up
            raise PromptNotFoundError(f"Page {page_num} is out of range. Total poses: {len(all_pose_specs)}, total pages: {total_pages}")
        
        # Extract the poses for this page
        pose_specs = all_pose_specs[start_idx:end_idx]
        batches = [pose_specs]
    
    # Generate a prompt for each batch
    all_prompts = []
    
    for batch_num, batch in enumerate(batches, 1):
        # Collect all character-specific prompts for this batch
        character_descriptions = []
        
        for idx, (char_id, form_id) in enumerate(batch, 1):
            try:
                # If form_id is None, it means single-pose character without refinements
                if form_id is None:
                    prompt0, thematic_snip, gender, char_proportions, age, equipment, pose_prompt, camera_rotation, visual_notes = resolve_prompt_from_json(
                        json_data=json_data,
                        character=char_id,
                        form=None,
                    )
                    pose_label = f"{char_id}"
                else:
                    prompt0, thematic_snip, gender, char_proportions, age, equipment, pose_prompt, camera_rotation, visual_notes = resolve_prompt_from_json(
                        json_data=json_data,
                        character=char_id,
                        form=form_id,
                    )
                    pose_label = f"{char_id}:{form_id}"

                # Build character description using same logic as single image generation
                desc_parts = []

                # CHARACTER section with age/gender (pose_label will be outside)
                char_parts = [prompt0.strip().rstrip(",")]

                # Add age and gender as demographic descriptors
                demographic_parts = []
                if age:
                    demographic_parts.append(age.lower())
                if gender:
                    gender_lower = gender.lower()
                    base_lower = prompt0.lower()
                    # Check for explicit gender words
                    has_gender = any(word in base_lower for word in [
                        'female', 'male', 'woman', 'man ', ' man,', 'girl', 'boy',
                        'feminine', 'masculine'
                    ])
                    if not has_gender:
                        demographic_parts.append(gender_lower)

                if demographic_parts:
                    char_parts.append(" ".join(demographic_parts))

                character_desc = ", ".join(p.strip().rstrip(",") for p in char_parts if p.strip())
                
                # VISUAL NOTES section if present (before CHARACTER)
                if visual_notes:
                    desc_parts.append(f"VISUAL: {visual_notes}")
                
                desc_parts.append(f"CHARACTER: {character_desc}")
                
                # PROPS section if present
                if equipment:
                    props_list = []
                    for item in equipment:
                        # Parse structured format: "item (details) : position : description"
                        if " : " in item:
                            parts = item.split(" : ", 2)
                            if len(parts) == 3:
                                item_with_details = parts[0].strip()
                                position = parts[1].strip()
                                description = parts[2].strip()
                                props_list.append(f"{item_with_details} [{position}] {description}")
                            else:
                                props_list.append(item)
                        else:
                            props_list.append(item)
                    if props_list:
                        desc_parts.append(f"PROPS: {'; '.join(props_list)}")
                
                # POSE section if present
                if pose_prompt:
                    desc_parts.append(f"POSE: {pose_prompt}")
                
                # PROPORTIONS section if present
                if char_proportions:
                    desc_parts.append(f"PROPORTIONS: {char_proportions}")
                
                full_description = ". ".join(desc_parts)
                character_descriptions.append(f"Figure {idx} [{pose_label}]: {full_description}")
                
            except Exception as e:
                raise PromptNotFoundError(f"Could not resolve character '{char_id}' (pose {form_id}): {e}")
        
        if not character_descriptions:
            continue
        
        # Deduplicate common sections from figure descriptions
        deduplicated_descriptions, common_sections = deduplicate_figure_sections(character_descriptions)
        
        # Build the combined prompt as a natural image generation prompt
        parts = []
        
        # Opening instruction with aspect ratio specification
        if len(batches) > 1:
            parts.append(f"create image\n\nCreate a reference sheet image showing {len(character_descriptions)} tabletop miniature figures arranged in a 3x3 grid layout (page {batch_num} of {len(batches)}).")
        else:
            parts.append(f"create image\n\nCreate a reference sheet image showing {len(character_descriptions)} tabletop miniature figures arranged in a 3x3 grid layout.")
        
        parts.append("Image format: 3:4 aspect ratio (portrait orientation).")
        parts.append("Each figure is a separate miniature sculpt with full body visible, clearly separated with white space between them.")
        parts.append("CRITICAL: All figures must be completely in frame from head to toe with no clipping at any edges. Full body visibility is mandatory for every figure.")
        parts.append("IMPORTANT: Arrange figures in the EXACT ORDER specified below. Do NOT reorder, group by character, or rearrange in any way. The figure numbers (Figure 1, Figure 2, etc.) indicate the precise grid position from left to right, top to bottom.")
        parts.append("")
        
        # Add deduplicated character descriptions as numbered list
        parts.extend(deduplicated_descriptions)
        parts.append("")
        
        # Add common sections that were extracted
        if common_sections:
            parts.append("COMMON TO ALL FIGURES:")
            if 'RENDER_SCOPE' in common_sections:
                parts.append(f"  {common_sections['RENDER_SCOPE']}")
            if 'PROPORTIONS' in common_sections:
                parts.append(f"  PROPORTIONS: {common_sections['PROPORTIONS']}")
            parts.append("")
        
        # Add shared thematic and style rules
        if thematic_general:
            parts.append(f"THEME: {thematic_general}")
        
        if style_snippet:
            parts.append(f"STYLE: {style_snippet}")
        
        # Add technical rendering rules
        if include_generic and generic_snippet:
            # Format generic snippet if it's a dict
            if isinstance(generic_snippet, dict):
                parts.append("RENDERING:")
                for section_key, section_data in generic_snippet.items():
                    if isinstance(section_data, dict) and 'content' in section_data:
                        parts.append(f"  {section_data.get('title', section_key)}: {section_data['content']}")
            else:
                parts.append(f"RENDERING: {generic_snippet}")
        
        if include_miniature and miniature_snippet:
            parts.append(f"MINIATURE SCALE: {miniature_snippet}")
        
        combined_prompt = "\n".join(parts)
        all_prompts.append(combined_prompt)
    
    if not all_prompts:
        raise PromptNotFoundError("No valid poses resolved for reference sheet")
    
    # Join multiple prompts with clear separators
    if len(all_prompts) > 1:
        final_output = "\n\n" + ("\n\n" + "="*80 + "\n\n").join(all_prompts)
    else:
        final_output = all_prompts[0]
    
    # Sanitize unicode before output
    final_output = sanitize_for_ascii(final_output)
    
    # Output
    if copy:
        copy_to_clipboard_windows(final_output)
    
    print(format_for_chat(final_output))
    
    return 0


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

    parser.add_argument(
        "--page",
        "-p",
        type=str,
        help="Generate a reference sheet for a specific page or subrefinements. Use 'all' to generate all pages. Examples: '1' (page 1, all subrefinements), '1:1' (page 1, subrefinement 1 only), '1:{1:3}' (page 1, subrefinements 1-3), '1:{1,4,5}' (page 1, subrefinements 1, 4, and 5). Each page shows up to 9 poses.",
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

    # Handle --page
    if args.page:
        return handle_reference_sheet(
            json_data=json_data,
            spec=args.page,
            generic_snippet=generic_snippet,
            miniature_snippet=miniature_snippet,
            thematic_general=thematic_general,
            style_snippet=style_snippet,
            default_proportions=default_proportions,
            thematic_forms=thematic_forms,
            include_generic=include_generic,
            include_miniature=include_miniature,
            no_base=args.no_base,
            copy=args.copy,
        )

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
                character_archetype = char_data.get("archetype", "")
                char_gender = char_data.get("gender", None) or char_data.get("tags", {}).get("gender", None)
                char_proportions = char_data.get("proportions", "").strip()
                
                # Support poses (array), refinements (legacy array), or pose (single object)
                poses = char_data.get("poses", [])
                refinements = char_data.get("refinements", [])
                single_pose = char_data.get("pose", None)
                
                if single_pose and not poses and not refinements:
                    items_to_process = [single_pose]
                else:
                    items_to_process = poses if poses else refinements

                for ref in items_to_process:
                    ref_name = ref.get("name", "")
                    # Use resolve_prompt_from_json to handle pose library references
                    p0, thematic_snip, gender_for_prompt, ref_proportions, age, equipment, pose_prompt, camera_rotation, visual_notes = resolve_prompt_from_json(
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
                        age=age,
                        default_proportions=default_proportions,
                        style_snippet=style_snippet,
                        generic_snippet=generic_snippet,
                        miniature_snippet=miniature_snippet,
                        include_generic=include_generic,
                        include_miniature=include_miniature,
                        no_base=args.no_base,
                        equipment=equipment,
                        character_id=str(character_id),
                        character_name=character_archetype,
                        form_id=ref_name,
                        pose_prompt=pose_prompt,
                        camera_rotation=camera_rotation,
                        visual_notes=visual_notes,
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
            character_archetype = char_data.get("archetype", "")
            char_gender = char_data.get("gender", None) or char_data.get("tags", {}).get("gender", None)
            char_proportions = char_data.get("proportions", "").strip()
            
            # Support poses (array), refinements (legacy array), or pose (single object)
            poses = char_data.get("poses", [])
            refinements = char_data.get("refinements", [])
            single_pose = char_data.get("pose", None)
            
            if single_pose and not poses and not refinements:
                items_to_process = [single_pose]
            else:
                items_to_process = poses if poses else refinements

            for ref in items_to_process:
                ref_name = ref.get("name", "")
                # Use resolve_prompt_from_json to handle pose library references
                p0, thematic_snip, gender_for_prompt, ref_proportions, age, equipment, pose_prompt, camera_rotation, visual_notes = resolve_prompt_from_json(
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
                    age=age,
                    default_proportions=default_proportions,
                    style_snippet=style_snippet,
                    generic_snippet=generic_snippet,
                    miniature_snippet=miniature_snippet,
                    include_generic=include_generic,
                    include_miniature=include_miniature,
                    no_base=args.no_base,
                    equipment=equipment,
                    character_id=str(character_id),
                    character_name=character_archetype,
                    form_id=ref_name,
                    pose_prompt=pose_prompt,
                    camera_rotation=camera_rotation,
                    visual_notes=visual_notes,
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
        
        # Extract gender and archetype from character data (refinements/poses may override)
        character_archetype = char_data.get("archetype", "")
        char_gender = char_data.get("gender", None) or char_data.get("tags", {}).get("gender", None)
        char_proportions = char_data.get("proportions", "").strip()
        
        # Check for both 'poses' (new format), 'refinements' (legacy), or single 'pose' object
        poses = char_data.get("poses", [])
        refinements = char_data.get("refinements", [])
        single_pose = char_data.get("pose", None)
        
        # If there's a single pose object, wrap it in a list for uniform processing
        if single_pose and not poses and not refinements:
            items_to_process = [single_pose]
        else:
            items_to_process = poses if poses else refinements
        
        if not items_to_process:
            raise PromptNotFoundError(
                f"No pose/poses/refinements found for character: {character_id}"
            )

        if args.dry_run:
            blocks: list[str] = []
            for ref in items_to_process:
                ref_name = ref.get("name", "")
                # Use resolve_prompt_from_json to handle pose library references
                # For single-pose characters, pass form=None to use the pose object directly
                form_to_pass = None if (single_pose and not poses and not refinements) else ref_name
                p0, thematic_snip, gender_for_prompt, ref_proportions, age, equipment, pose_prompt, camera_rotation, visual_notes = resolve_prompt_from_json(
                    json_data, character=character_id, form=form_to_pass
                )
                # Use character proportions if ref doesn't have its own
                proportions_to_use = ref_proportions if ref_proportions else char_proportions
                # Use char_gender if pose doesn't override it
                gender_to_use = gender_for_prompt if gender_for_prompt else char_gender
                p = build_final_prompt(
                    p0,
                    gender=gender_to_use,
                    thematic_snippets=thematic_snip,
                    thematic_general=thematic_general,
                    proportions=proportions_to_use,
                    age=age,
                    default_proportions=default_proportions,
                    style_snippet=style_snippet,
                    generic_snippet=generic_snippet,
                    miniature_snippet=miniature_snippet,
                    include_generic=include_generic,
                    include_miniature=include_miniature,
                    no_base=args.no_base,
                    equipment=equipment,
                    character_id=str(character_id),
                    character_name=character_archetype,
                    form_id=ref_name,
                    pose_prompt=pose_prompt,
                    camera_rotation=camera_rotation,
                    visual_notes=visual_notes,
                )
                blocks.append(f"[{character_id}:{ref_name}]\n{sanitize_for_ascii(format_for_chat(p))}")

            out_text = "\n\n".join(blocks).strip() + "\n"
            if args.copy:
                copy_to_clipboard_windows(out_text)
            print(out_text, end="")
            return 0

        args.out.mkdir(parents=True, exist_ok=True)
        for ref in items_to_process:
            ref_name = ref.get("name", "")
            # Use resolve_prompt_from_json to handle pose library references
            # For single-pose characters, pass form=None to use the pose object directly
            form_to_pass = None if (single_pose and not poses and not refinements) else ref_name
            p0, thematic_snip, gender_for_prompt, ref_proportions, age, equipment, pose_prompt, camera_rotation, visual_notes = resolve_prompt_from_json(
                json_data, character=character_id, form=form_to_pass
            )
            # Use character proportions if ref doesn't have its own
            proportions_to_use = ref_proportions if ref_proportions else char_proportions
            # Use char_gender if pose doesn't override it
            gender_to_use = gender_for_prompt if gender_for_prompt else char_gender
            p = build_final_prompt(
                p0,
                gender=gender_to_use,
                thematic_snippets=thematic_snip,
                thematic_general=thematic_general,
                proportions=proportions_to_use,
                age=age,
                default_proportions=default_proportions,
                style_snippet=style_snippet,
                generic_snippet=generic_snippet,
                miniature_snippet=miniature_snippet,
                include_generic=include_generic,
                include_miniature=include_miniature,
                no_base=args.no_base,
                equipment=equipment,
                character_id=str(character_id),
                character_name=character_archetype,
                form_id=ref_name,
                pose_prompt=pose_prompt,
                camera_rotation=camera_rotation,
                visual_notes=visual_notes,
            )
            png_bytes = generate_image_openai(p, model=args.model, size=args.size)
            out_path = build_output_path(
                args.out, character=character_id, form=ref_name
            )
            out_path.write_bytes(png_bytes)
            print(str(out_path))
        return 0

    # Single (character, form) - form_id must be specified to reach here
    prompt0, thematic_snip, gender, char_proportions, age, equipment, pose_prompt, camera_rotation, visual_notes = resolve_prompt_from_json(
        json_data, character=character_id, form=form_id
    )
    
    # Get character archetype for asset naming
    char_data = find_character_by_id_or_name(json_data, character_id)
    character_archetype = char_data.get("archetype", "") if char_data else ""
    character_name = char_data.get("name", str(character_id)) if char_data else str(character_id)
    
    prompt = build_final_prompt(
        prompt0,
        gender=gender,
        thematic_snippets=thematic_snip,
        thematic_general=thematic_general,
        proportions=char_proportions,
        age=age,
        default_proportions=default_proportions,
        style_snippet=style_snippet,
        generic_snippet=generic_snippet,
        miniature_snippet=miniature_snippet,
        include_generic=include_generic,
        include_miniature=include_miniature,
        no_base=args.no_base,
        equipment=equipment,
        character_id=character_name,
        character_name=character_archetype,
        form_id=form_id,
        pose_prompt=pose_prompt,
        camera_rotation=camera_rotation,
        visual_notes=visual_notes,
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
