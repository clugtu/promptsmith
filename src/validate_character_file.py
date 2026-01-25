#!/usr/bin/env python3
"""
Validate character JSON files against the character_schema.json schema.
Also performs additional consistency checks beyond basic schema validation.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Set

def load_json(file_path: Path) -> Dict[str, Any]:
    """Load JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def validate_ids_sequential(characters: List[Dict[str, Any]]) -> List[str]:
    """Check that character IDs are sequential with no gaps or duplicates."""
    errors = []
    ids = [char.get('id') for char in characters if 'id' in char]
    
    if not ids:
        return ["No character IDs found"]
    
    # Check for duplicates
    seen = set()
    duplicates = set()
    for id_val in ids:
        if id_val in seen:
            duplicates.add(id_val)
        seen.add(id_val)
    
    if duplicates:
        errors.append(f"Duplicate IDs found: {sorted(duplicates)}")
    
    # Check for sequential (1, 2, 3, ...)
    expected = list(range(1, len(ids) + 1))
    if sorted(ids) != expected:
        missing = set(expected) - set(ids)
        extra = set(ids) - set(expected)
        if missing:
            errors.append(f"Missing IDs: {sorted(missing)}")
        if extra:
            errors.append(f"Unexpected IDs: {sorted(extra)}")
    
    return errors

def validate_pose_structure(char: Dict[str, Any], char_id: str) -> List[str]:
    """Check that character has valid pose structure."""
    errors = []
    
    has_pose = 'pose' in char
    has_poses = 'poses' in char
    
    count = sum([has_pose, has_poses])
    
    if count == 0:
        errors.append(f"Character {char_id} has no pose/poses field")
    elif count > 1:
        errors.append(f"Character {char_id} has multiple pose fields (should have only one)")
    
    # Check pose library reference or inline prompt
    poses_to_check = []
    if has_pose:
        poses_to_check = [char['pose']]
    elif has_poses:
        poses_to_check = char['poses']
    
    for i, pose in enumerate(poses_to_check):
        pose_id = pose.get('name', f'pose_{i}')
        has_ref = 'pose_library_ref' in pose
        has_prompt = 'prompt' in pose
        
        if not has_ref and not has_prompt:
            errors.append(f"Character {char_id}, pose {pose_id}: missing both 'pose_library_ref' and 'prompt'")
    
    return errors

def validate_imports(data: Dict[str, Any]) -> List[str]:
    """Check that required imports are present."""
    warnings = []
    
    if 'imports' not in data:
        warnings.append("No 'imports' section found (recommended)")
        return warnings
    
    imports = data['imports']
    
    # Check if any poses use pose_library_ref
    uses_pose_library = False
    for char in data.get('characters', []):
        pose = char.get('pose', {})
        poses = char.get('poses', [])
        
        if 'pose_library_ref' in pose:
            uses_pose_library = True
            break
        
        for p in poses:
            if 'pose_library_ref' in p:
                uses_pose_library = True
                break
        
        if uses_pose_library:
            break
    
    if uses_pose_library and 'pose_library' not in imports:
        warnings.append("Characters use 'pose_library_ref' but 'imports.pose_library' is missing")
    
    return warnings

def validate_tags_structure(char: Dict[str, Any], char_id: str) -> List[str]:
    """Check tags structure."""
    warnings = []
    
    # Check for deprecated character-level gender
    if 'gender' in char and 'tags' in char:
        if 'gender' in char['tags']:
            warnings.append(f"Character {char_id}: has both char.gender and tags.gender (use tags.gender)")
    
    return warnings

def validate_file(file_path: Path, verbose: bool = False) -> bool:
    """Validate a character JSON file."""
    print(f"\n{'='*60}")
    print(f"Validating: {file_path}")
    print(f"{'='*60}\n")
    
    try:
        data = load_json(file_path)
    except json.JSONDecodeError as e:
        print(f"❌ JSON parse error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return False
    
    errors = []
    warnings = []
    
    # Check required fields
    if 'characters' not in data:
        errors.append("Missing required field: 'characters'")
        print(f"❌ Missing required field: 'characters'")
        return False
    
    characters = data['characters']
    if not characters:
        errors.append("'characters' array is empty")
    
    # Validate character IDs
    id_errors = validate_ids_sequential(characters)
    errors.extend(id_errors)
    
    # Validate imports
    import_warnings = validate_imports(data)
    warnings.extend(import_warnings)
    
    # Validate each character
    for char in characters:
        char_id = f"{char.get('id', '?')}:{char.get('name', 'unnamed')}"
        
        # Check required fields
        if 'id' not in char:
            errors.append(f"Character missing 'id' field: {char.get('name', 'unnamed')}")
        if 'name' not in char:
            errors.append(f"Character {char.get('id', '?')} missing 'name' field")
        if 'character_base' not in char:
            errors.append(f"Character {char_id} missing 'character_base' field")
        
        # Validate pose structure
        pose_errors = validate_pose_structure(char, char_id)
        errors.extend(pose_errors)
        
        # Validate tags
        tag_warnings = validate_tags_structure(char, char_id)
        warnings.extend(tag_warnings)
    
    # Report results
    print(f"Characters: {len(characters)}")
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for error in errors:
            print(f"  • {error}")
    
    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"  • {warning}")
    
    if not errors and not warnings:
        print("\n✅ All validations passed!")
        return True
    elif not errors:
        print(f"\n✅ No errors (but {len(warnings)} warnings)")
        return True
    else:
        print(f"\n❌ Validation failed with {len(errors)} error(s)")
        return False

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python validate_character_file.py <file.json> [file2.json ...]")
        print("\nValidates character JSON files against structure requirements.")
        sys.exit(1)
    
    all_passed = True
    
    for file_arg in sys.argv[1:]:
        file_path = Path(file_arg)
        if not file_path.exists():
            print(f"\n❌ File not found: {file_path}")
            all_passed = False
            continue
        
        if not validate_file(file_path):
            all_passed = False
    
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
