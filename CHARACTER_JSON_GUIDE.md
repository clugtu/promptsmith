# Character JSON Structure Guide

## Overview
This document describes the standardized structure for character JSON files used with create_image.py.

## Three Supported Pose Patterns

The script supports three different ways to define character poses:

### Pattern 1: Single Pose Object (Recommended for simple characters)
```json
{
  "id": 1,
  "name": "Simple Character",
  "character_base": "description",
  "pose": {
    "name": "Standing Ready",
    "pose_library_ref": "oh_melee_guarded_low_ready",
    "character_override": "optional overrides",
    "camera_rotation": 45
  }
}
```

### Pattern 2: Multiple Poses Array (Recommended for reference sheets)
```json
{
  "id": 1,
  "name": "Multi-Pose Character",
  "character_base": "description",
  "poses": [
    {
      "id": 1,
      "name": "Attack Pose",
      "pose_library_ref": "oh_melee_overhead_chop",
      "character_override": "optional overrides",
      "camera_rotation": 45
    },
    {
      "id": 2,
      "name": "Defense Pose",
      "pose_library_ref": "oh_melee_guarded_low_ready",
      "camera_rotation": 90
    }
  ]
}
```

### Pattern 3: Refinements Array (Legacy - inline prompts)
```json
{
  "id": 1,
  "name": "Custom Character",
  "character_base": "description",
  "refinements": [
    {
      "id": 1,
      "name": "Custom Pose",
      "prompt": "full inline pose prompt text"
    }
  ]
}
```

## Pose Definition Options

Each pose MUST have either:
- `pose_library_ref`: Reference to a pose in pose_library.json (recommended)
- `prompt`: Inline pose description (legacy, less reusable)

Optional pose fields:
- `character_override`: Additional character details specific to this pose
- `camera_rotation`: Integer 0-360 degrees for camera angle

## Equipment Format

### Recommended: Simple String Array
```json
"equipment": [
  "longsword (steel blade with leather-wrapped hilt) : right hand : held ready for combat",
  "wooden shield (round, iron rim) : left forearm : strapped and raised defensively"
]
```

Format: `"item (details) : position : usage_description"`

### Deprecated: Weapons Object
The old `weapons` structure is deprecated. Use simple equipment array instead.

## Character Metadata

### Required Fields
- `id`: Integer, must be sequential (1, 2, 3, ...) with no gaps or duplicates
- `name`: String, human-readable character name
- `character_base`: String, core character description

### Recommended Fields
- `tags`: Object containing:
  - `gender`: "male" | "female" | "other"
  - `age`: "child" | "teen" | "adult" | "older" | "elder" | "ancient"
  - `trope`: String describing character archetype (optional)

### Optional Fields
- `description`: Detailed character background
- `visual_notes`: Physical appearance details
- `proportions`: Body proportions adjustments
- `equipment`: Array of equipment strings

### Legacy Fields
- `gender`: Character-level gender (deprecated, use tags.gender instead)

## File Structure

### Required Sections
```json
{
  "imports": {
    "generic_render_rules": "rules/generic_render_rules.json",
    "style_rules": "rules/realistic_weird_west_style.json",
    "pose_library": "rules/pose_library.json"
  },
  "metadata": {
    "name": "File Name",
    "description": "File description",
    "version": "1.0.0"
  },
  "characters": []
}
```

### Optional Sections
- `thematic_rules`: Theme-specific rendering rules
- `system_documentation`: Documentation and notes

## Validation Requirements

1. **Sequential IDs**: Character IDs must be sequential (1, 2, 3, ...) with no gaps or duplicates
2. **Pose Structure**: Each character must have ONE of: `pose`, `poses`, or `refinements`
3. **Pose Library Import**: If using `pose_library_ref`, must have `imports.pose_library`
4. **Pose Definition**: Each pose must have either `pose_library_ref` OR `prompt`

## Usage with create_image.py

### Generate Single Character
```bash
python create_image.py characters.json 5
# Generates prompt for character ID 5
```

### Generate Reference Sheet
```bash
python create_image.py characters.json --reference-sheet 3
# Generates reference sheet for character ID 3

python create_image.py characters.json --reference-sheet 3 --page 2
# Generates page 2 (poses 10-18) of reference sheet

python create_image.py characters.json --reference-sheet 3 --page all
# Generates all poses on one page
```

### Validation
```bash
python validate_character_file.py characters.json
# Validates structure and reports errors/warnings
```

## See Also
- [character_schema.json](character_schema.json): JSON Schema Draft 07 validation schema
- [template.json](template.json): Reference template with example characters
- [pose_library.json](rules/pose_library.json): Reusable pose definitions

## Migration from Old Structure

### Update Equipment
Old:
```json
"weapons": {
  "main_hand": "longsword",
  "off_hand": "shield"
}
```

New:
```json
"equipment": [
  "longsword : right hand : held ready",
  "shield : left forearm : raised defensively"
]
```

### Update Gender/Age
Old:
```json
{
  "gender": "male"
}
```

New:
```json
{
  "tags": {
    "gender": "male",
    "age": "adult"
  }
}
```

### Add Pose Library References
Old:
```json
"poses": [
  {
    "id": 1,
    "name": "Attack",
    "prompt": "full inline prompt..."
  }
]
```

New:
```json
"poses": [
  {
    "id": 1,
    "name": "Attack",
    "pose_library_ref": "oh_melee_overhead_chop",
    "camera_rotation": 45
  }
]
```
