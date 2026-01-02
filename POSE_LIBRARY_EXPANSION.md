# Pose Library Expansion

## Overview
The pose library has been expanded from 14 to 30 poses, covering a comprehensive range of weapon combinations and dynamic stances. The system now includes automatic validation to check pose compatibility with character weapons.

## New Poses Added

### Single-Handed (4 new poses)
- **melee_005_defensive_crouch**: Low defensive crouch with guard position
- **melee_006_sprint_carry**: Dynamic sprint with weapon carried at side
- **melee_007_overhead_strike**: Overhead strike with weapon raised high
- **melee_008_side_guard_low**: Side guard stance with weapon at low side

### Two-Handed (4 new poses)
- **twohand_004_low_sweep**: Horizontal sweeping strike at waist/hip level
- **twohand_005_overhead_chop**: Powerful overhead chopping attack
- **twohand_006_march_carry**: Casual marching carry over shoulder
- **twohand_007_defensive_brace**: Defensive ready with weapon braced diagonally

### Unarmed (3 new poses)
- **unarmed_002_aggressive_charge**: Forward charging strike with fists/claws
- **unarmed_003_defensive_crouch**: Low defensive crouch with guarding hands
- **unarmed_004_victory_roar**: Triumphant victory pose with arms raised

### Dual-Wield (3 new poses)
- **dual_006_spinning_strike**: Dynamic spinning attack with both weapons extended
- **dual_007_crossed_defense**: Defensive X-formation with both weapons
- **dual_008_asymmetric_ready**: Asymmetric ready stance (one weapon forward, one low)

### Mixed/Versatile (2 new poses)
- **mixed_001_shield_bash**: Shield charge with ramming position
- **mixed_002_transition_stance**: Mid-transition between weapon stances

## Validation System

### Automatic Compatibility Checking
The system now automatically validates that a character's equipped weapons are compatible with the selected pose. Validation runs when composing pose prompts and prints warnings to stderr (not included in the prompt output).

### Validation Rules

**Handedness Mode Checks:**
- `unarmed`: Warns if character has weapons equipped (weapons will be ignored)
- `single_handed`: 
  - Warns if no main hand weapon when pose requires one
  - Checks main hand prop_class matches pose requirements
  - Warns if off hand weapon is equipped (will be ignored)
- `two_handed`: 
  - Warns if no main hand weapon
  - Checks main hand prop_class matches pose requirements
  - Warns if off hand weapon is equipped (both hands on main weapon)
- `dual_wield`:
  - Warns if main hand weapon missing
  - Warns if off hand weapon missing
  - Checks both prop_classes match pose requirements

**Prop Class Compatibility:**
The system verifies that weapon `prop_class` values (compact, long, shield_plane, etc.) are compatible with the pose's expected `prop_class` arrays.

### Example Validation Output

```
⚠️  Pose Compatibility Warnings:
   Pose 'unarmed_002_aggressive_charge' is unarmed, but character has weapons equipped. Weapons will be ignored in this pose.
   
⚠️  Pose Compatibility Warnings:
   Pose 'dual_006_spinning_strike' expects main hand prop_class ['compact', 'small'], but character has 'long'. May not render optimally.
```

## Using the Expanded Library

### Character Weapon Configuration
Ensure your character has proper weapon definitions:

```json
"weapons": {
  "main_hand": {
    "name": "katana",
    "description": "Oversized katana",
    "prop_class": "long",
    "attachment": "two-hand grip",
    "visual_detail": "extra-wide blade, wrapped handle"
  },
  "off_hand": null,
  "holstered": [...]
}
```

### Referencing Poses
Reference poses from the library using `pose_library_ref`:

```json
"poses": [
  {
    "id": 1,
    "name": "aggressive_stance",
    "description": "Charging attack",
    "pose_library_ref": "twohand_004_low_sweep",
    "character_override": "intense expression; forward momentum"
  }
]
```

### Prop Class Values
- `none`: No weapon/empty hand
- `small`: Small items (coins, small religious symbols)
- `compact`: Compact weapons (pistols, short blades, compact shields)
- `long`: Long weapons (rifles, swords, spears, long staves)
- `flexible`: Flexible items (whips, chains, rope)
- `shield_plane`: Shield objects (round shields, rectangular shields)
- `two_hand_frame`: Two-handed weapons requiring both hands on the same object
- `bulky`: Large bulky items

## Design Principles

All new poses follow these principles:
1. **Generic & Reusable**: Work across different character types and settings
2. **Dynamic & Visually Interesting**: Strong silhouettes and clear action reads
3. **Clear Negative Space**: Weapons/props kept away from torso for 3D readability
4. **Varied Stances**: Different foot positions, heights, and orientations
5. **Explicit Requirements**: Clear `prop_class` arrays define compatibility

## Testing Validation

To see validation warnings, redirect stderr:
```bash
python create_image.py character_file.json --prompt-only character:pose 2>&1 | head -30
```

Warnings appear before the prompt output but are not copied to clipboard with `--copy` flag.

## Future Enhancements

Potential additions:
- Flight/airborne poses
- Mounted/riding poses
- Grappling/wrestling poses
- Kneeling/prone poses
- Climbing/acrobatic poses
- Injured/wounded poses
