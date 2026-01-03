# Prop Definitions System

## Overview
The prop definitions system separates prop descriptions from pose-specific positioning, eliminating duplication across poses.

## Structure

### Character Level
```json
{
  "id": 1,
  "name": "character_name",
  "character_base": "...",
  "prop_definitions": {
    "prop_id": "full description (with details)",
    "another_prop": "another description (with more details)"
  },
  "equipment": [
    "prop_id : position : pose_description",
    "another_prop : position : pose_description"
  ]
}
```

### Pose Level (Optional Override)
```json
{
  "id": 1,
  "name": "pose_name",
  "equipment_override": [
    "prop_id : different_position : different_pose_description"
  ]
}
```

## Benefits

1. **No Duplication**: Prop descriptions defined once at character level
2. **Easy Updates**: Change prop description in one place
3. **Cleaner Poses**: Poses only specify positioning and state
4. **Backwards Compatible**: Legacy full-description format still works

## Conversion

Use `convert_to_prop_definitions.py` to automatically convert existing files:

```bash
python convert_to_prop_definitions.py input.json output.json
```

The script:
- Extracts unique prop descriptions from equipment arrays
- Creates prop_definitions dict with snake_case IDs
- Converts equipment arrays to use references
- Preserves all pose-specific positioning info

## Examples

### Before (Duplicated)
```json
{
  "equipment": [
    "coach gun (double-barreled shotgun with full stock) : main_hand : held at ready"
  ],
  "poses": [
    {
      "equipment_override": [
        "coach gun (double-barreled shotgun with full stock) : main_hand : raised overhead"
      ]
    }
  ]
}
```

### After (Referenced)
```json
{
  "prop_definitions": {
    "coach_gun": "coach gun (double-barreled shotgun with full stock)"
  },
  "equipment": [
    "coach_gun : main_hand : held at ready"
  ],
  "poses": [
    {
      "equipment_override": [
        "coach_gun : main_hand : raised overhead"
      ]
    }
  ]
}
```

## Implementation

The `resolve_prop_references()` function in `create_image.py`:
1. Checks if first part of equipment string is a prop_id (no parentheses/brackets)
2. Looks up prop_id in character's prop_definitions
3. Substitutes full description and preserves position/pose info
4. Falls back to legacy format if not found

This happens automatically during prompt generation, so both formats work seamlessly.
