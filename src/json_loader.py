"""JSON loading and import resolution for character files.

This module handles loading JSON character files and resolving imports to external
rule files (generic render rules, miniature scale rules, style rules, etc.).
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List


def load_json_data(json_path: Path) -> Dict[str, Any]:
    """Load and parse the JSON file, resolving any imports.
    
    Args:
        json_path: Path to the JSON character file
        
    Returns:
        Loaded and processed JSON data with imports resolved
        
    Raises:
        FileNotFoundError: If the JSON file doesn't exist
        json.JSONDecodeError: If the JSON is malformed
        ValueError: If character IDs are invalid
    """
    if not json_path.exists():
        # Check if there's a similar file nearby
        parent_dir = json_path.parent
        filename = json_path.name
        similar_files = []
        
        if parent_dir.exists():
            # Look for files with similar names
            for file in parent_dir.glob("*.json"):
                if file.stem.lower().replace('_', '').replace('-', '') == filename.lower().replace('.json', '').replace('_', '').replace('-', ''):
                    similar_files.append(file.name)
        
        error_msg = f"JSON file not found: {json_path}"
        if similar_files:
            error_msg += f"\n\nDid you mean one of these?\n  " + "\n  ".join(similar_files)
        elif parent_dir.exists():
            json_files = [f.name for f in parent_dir.glob("*.json")]
            if json_files:
                error_msg += f"\n\nAvailable JSON files in {parent_dir}:\n  " + "\n  ".join(json_files)
            else:
                error_msg += f"\n\nNo JSON files found in {parent_dir}"
        else:
            error_msg += f"\n\nDirectory does not exist: {parent_dir}"
        
        raise FileNotFoundError(error_msg)
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Resolve imports if present.
    # Resolve relative import paths with fallback strategy:
    # 1. Try relative to JSON file's directory (for co-located rules)
    # 2. Fall back to project root (for centralized rules)
    if "imports" in data:
        data = resolve_imports(data, json_path.parent, json_path)
    
    # Validate character IDs are sequential
    if "characters" in data:
        validate_character_ids(data["characters"])
    
    return data


def validate_character_ids(characters: List[Dict[str, Any]]) -> None:
    """Validate that character IDs are sequential with no gaps or duplicates.
    
    Args:
        characters: List of character dictionaries
        
    Raises:
        ValueError: If IDs are duplicated or not sequential
    """
    if not characters:
        return
    
    ids = [char.get("id") for char in characters if "id" in char]
    if not ids:
        return
    
    # Check for duplicates
    duplicates = [x for x in ids if ids.count(x) > 1]
    if duplicates:
        raise ValueError(f"Duplicate character IDs found: {sorted(set(duplicates))}")
    
    # Check for sequential numbering
    expected_ids = list(range(1, len(ids) + 1))
    if sorted(ids) != expected_ids:
        missing = set(expected_ids) - set(ids)
        extra = set(ids) - set(expected_ids)
        errors = []
        if missing:
            errors.append(f"Missing IDs: {sorted(missing)}")
        if extra:
            errors.append(f"Unexpected IDs: {sorted(extra)}")
        raise ValueError(f"Character IDs must be sequential from 1 to {len(ids)}. {' '.join(errors)}")


def find_project_root(json_path: Path = None) -> Path:
    """Find the project root by looking for a rules/ directory.
    
    Searches upward from either the provided JSON file's location or from this module's
    location to find a directory containing a rules/ subdirectory, which indicates the
    project root.
    
    Args:
        json_path: Optional path to start searching from. If None, searches from this module's location.
        
    Returns:
        Path to project root if found, None otherwise
    """
    if json_path:
        start = json_path.parent
    else:
        # Start from this module's location
        start = Path(__file__).parent.parent  # Go up from src/ to project root
    
    current = start
    max_levels = 10  # Prevent infinite loop
    
    for _ in range(max_levels):
        rules_dir = current / "rules"
        if rules_dir.exists() and rules_dir.is_dir():
            return current
        
        parent = current.parent
        if parent == current:  # Reached filesystem root
            break
        current = parent
    
    return None


def resolve_imports(data: Dict[str, Any], base_path: Path, json_path: Path = None) -> Dict[str, Any]:
    """Resolve file references in the imports section and merge them into the data.
    
    This function loads referenced JSON files and merges their content into the main data structure.
    Files are cached to avoid loading the same file multiple times.
    
    Uses a fallback strategy for resolving relative paths:
    1. Try relative to base_path (typically the JSON file's directory)
    2. If not found, try relative to project root (detected by finding rules/ directory)
    
    Args:
        data: The JSON data with potential imports section
        base_path: Base path for resolving relative import paths
        json_path: Optional path to the JSON file being loaded (for project root detection)
        
    Returns:
        Updated data with imports resolved and merged
    """
    imports = data.get("imports", {})
    if not imports:
        return data
    
    # Cache for loaded files to avoid duplicate loads
    file_cache = {}
    
    # Helper function to resolve with fallback
    def resolve_with_fallback(import_path: str) -> Path:
        """Try to resolve import path with fallback to project root and custom rules directory."""
        # First try: relative to base_path (JSON file's directory)
        resolved = resolve_path(import_path, base_path)
        if resolved.exists():
            return resolved
        
        # Second try: custom rules directory from environment variable
        # If import contains "rules/", try using PROMPTSMITH_RULES_DIR
        custom_rules_dir = os.environ.get("PROMPTSMITH_RULES_DIR")
        if custom_rules_dir:
            custom_rules_path = Path(custom_rules_dir)
            if custom_rules_path.exists():
                # Try the import path as-is from custom rules directory
                resolved = resolve_path(import_path, custom_rules_path)
                if resolved.exists():
                    return resolved
                
                # If path contains "rules/", strip it and resolve from custom directory
                import_path_normalized = import_path.lstrip("./").replace("../", "")
                if "rules/" in import_path_normalized:
                    # Remove the "rules/" part since we're already in the rules directory
                    rules_relative = import_path_normalized.split("rules/", 1)[-1]
                    resolved = custom_rules_path / rules_relative
                    if resolved.exists():
                        return resolved
        
        # Third try: relative to project root searched from JSON location
        if json_path:
            project_root = find_project_root(json_path)
            if project_root and project_root != base_path:
                resolved = resolve_path(import_path, project_root)
                if resolved.exists():
                    return resolved
        
        # Fourth try: relative to this module's project root
        # For imports like "../rules/...", try treating as "rules/..." from project root
        module_project_root = find_project_root()
        if module_project_root and module_project_root != base_path:
            # Try the path as-is from project root
            resolved = resolve_path(import_path, module_project_root)
            if resolved.exists():
                return resolved
            
            # Also try stripping leading "../" and resolving from project root
            # This handles imports like "../rules/..." that should be "rules/..." from project root
            import_path_normalized = import_path.lstrip("./").replace("../", "")
            if import_path_normalized != import_path:
                resolved = resolve_path(import_path_normalized, module_project_root)
                if resolved.exists():
                    return resolved
        
        # If nothing worked, return first attempt (will fail with clear error message)
        return resolve_path(import_path, base_path)
    
    # Resolve generic_render_rules
    if "generic_render_rules" in imports:
        rules_path = resolve_with_fallback(imports["generic_render_rules"])
        if rules_path not in file_cache:
            with open(rules_path, "r", encoding="utf-8") as f:
                file_cache[rules_path] = json.load(f)
        data["generic_render_rules"] = file_cache[rules_path].get("generic_render_rules", {})
    
    # Resolve miniature_scale_rules
    if "miniature_scale_rules" in imports:
        rules_path = resolve_with_fallback(imports["miniature_scale_rules"])
        if rules_path not in file_cache:
            with open(rules_path, "r", encoding="utf-8") as f:
                file_cache[rules_path] = json.load(f)
        data["miniature_scale_rules"] = file_cache[rules_path].get("miniature_scale_rules", {})
    
    # Resolve common_thematic_forms
    if "common_thematic_forms" in imports:
        forms_path = resolve_with_fallback(imports["common_thematic_forms"])
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
        style_path = resolve_with_fallback(imports["style_rules"])
        if style_path not in file_cache:
            with open(style_path, "r", encoding="utf-8") as f:
                file_cache[style_path] = json.load(f)
        # Import the entire style file content (it has prompt_snippet at root level)
        data["style_rules"] = file_cache[style_path]
    
    # Resolve pose_library
    if "pose_library" in imports:
        pose_path = resolve_with_fallback(imports["pose_library"])
        if pose_path not in file_cache:
            with open(pose_path, "r", encoding="utf-8") as f:
                file_cache[pose_path] = json.load(f)
        data["pose_library"] = file_cache[pose_path]
    
    return data


def resolve_path(path_str: str, base_path: Path) -> Path:
    """Resolve a path string relative to base_path or as absolute.

    Notes (Windows):
    - Git Bash / MSYS paths like '/d/dev/...' are *not* native Windows absolute paths.
      If passed directly to pathlib on Windows, they are treated as '\\d\\dev\\...' on the
      current drive (e.g. 'D:\\d\\dev\\...').
    - To make JSON `imports` portable for Git Bash users, translate '/<drive>/' to
      '<DRIVE>:/'.
      
    Args:
        path_str: Path string to resolve (may be relative or absolute)
        base_path: Base path for resolving relative paths
        
    Returns:
        Resolved absolute Path object
    """
    # Translate Git Bash / MSYS drive paths (e.g. /d/dev/...) into Windows drive paths.
    # Only do this on Windows; on POSIX systems '/d/...' is a normal absolute path.
    if os.name == "nt":
        msys_drive_match = re.match(r"^/([a-zA-Z])/(.*)$", path_str)
        if msys_drive_match:
            drive_letter = msys_drive_match.group(1).upper()
            remainder = msys_drive_match.group(2)
            path_str = f"{drive_letter}:/{remainder}"

    path = Path(path_str)
    if path.is_absolute():
        return path
    return (base_path / path).resolve()


def extract_generic_snippet(json_data: Dict[str, Any]) -> str:
    """Extract the generic render rules sections from JSON.
    
    Args:
        json_data: Loaded JSON data
        
    Returns:
        Generic render rules sections or prompt snippet
    """
    sections = json_data.get("generic_render_rules", {}).get("sections", {})
    # For backwards compatibility, also check for prompt_snippet
    if not sections:
        return json_data.get("generic_render_rules", {}).get("prompt_snippet", "")
    return sections


def extract_miniature_snippet(json_data: Dict[str, Any]) -> str:
    """Extract the miniature scale rules prompt snippet from JSON.
    
    Args:
        json_data: Loaded JSON data
        
    Returns:
        Miniature scale rules prompt snippet
    """
    return json_data.get("miniature_scale_rules", {}).get("prompt_snippet", "")


def extract_thematic_snippet(json_data: Dict[str, Any]) -> str:
    """Extract the general thematic rules prompt snippet from JSON.
    
    Args:
        json_data: Loaded JSON data
        
    Returns:
        Thematic rules prompt snippet
    """
    return json_data.get("thematic_rules", {}).get("prompt_snippet", "")


def extract_style_snippet(json_data: Dict[str, Any]) -> str:
    """Extract the style rules prompt snippet from JSON.
    
    Args:
        json_data: Loaded JSON data
        
    Returns:
        Style rules prompt snippet
    """
    return json_data.get("style_rules", {}).get("prompt_snippet", "")


def extract_default_proportions(json_data: Dict[str, Any]) -> str:
    """Extract default proportions from style rules.
    
    Args:
        json_data: Loaded JSON data
        
    Returns:
        Default proportions string
    """
    return json_data.get("style_rules", {}).get("default_proportions", "")


def extract_thematic_forms(json_data: Dict[str, Any]) -> Dict[str, str]:
    """Extract form definitions from thematic_rules.forms.
    
    Args:
        json_data: Loaded JSON data
        
    Returns:
        Dictionary mapping form names to their prompt snippets
    """
    forms = json_data.get("thematic_rules", {}).get("forms", {})
    result = {}
    for name, form in forms.items():
        # Skip non-dict entries (like _comment)
        if not isinstance(form, dict):
            continue
        result[name] = form.get("prompt_snippet", "")
    return result
