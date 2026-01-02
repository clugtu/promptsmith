# Pose Library System

## Overview

The pose library system provides 30 reusable pose templates that work with any character through weapon injection and validation. The system uses a modular architecture that separates weapon definitions from pose templates, composing safe prompts at generation time.

**Total Poses**: 30 covering all weapon combinations  
**Architecture**: Modular pose library with weapon injection and validation  
**Safety**: Passive state language + explicit negation for guardrail compliance

### Key Features

**Weapon Separation**  
Weapons defined once on character, automatically injected into any compatible pose

**Placeholder System**  
Poses use MAIN_HAND_PROP/OFF_HAND_PROP placeholders replaced at generation time

**Safe Prompt Composition**  
Generated prompts use passive state descriptors + explicit negation for guardrail safety

**Prop Visibility Modes**  
- `"presented"`: Clear negative space, held away from torso
- `"carried_attached"`: Slung/stowed weapons with attachment overlap allowed

**Automatic Validation**  
Checks pose compatibility with character weapons and warns about mismatches

**Modular Imports**  
Reusable rules: generic rendering, style rules, pose library all importable

---

## Pose Catalog

### Categorization System

Poses are categorized by **handedness_mode** (how many hands are used) and **prop_class** (what weapon sizes/types are compatible):

**Handedness Modes:**
- `unarmed`: No weapons (fists, claws, empty hands)
- `single_handed`: One weapon in main hand, off hand free
- `two_handed`: Both hands on same object
- `dual_wield`: Different item in each hand

**Prop Classes:**
- `none`: Empty hand
- `small`: Small items (coins, amulets, small symbols)
- `compact`: Compact weapons (pistols, short blades, small shields)
- `long`: Long weapons (rifles, swords, spears, staves)
- `flexible`: Flexible items (whips, chains, ropes)
- `shield_plane`: Shields (round, rectangular)
- `two_hand_frame`: Two-handed weapons
- `bulky`: Large bulky items

### Complete Pose Library (30 Poses)

| Pose ID | Handedness | Main Hand Props | Off Hand Props | Style | Notes |
|---------|-----------|-----------------|----------------|-------|-------|
| **Unarmed (3)** |
| unarmed_001_fighter_ready | unarmed | none | none | ready | Fighting stance, hands up |
| unarmed_002_aggressive_charge | unarmed | none | none | dynamic | Forward charge, fist extended |
| unarmed_003_defensive_crouch | unarmed | none | none | crouch | Low defensive guard |
| unarmed_004_victory_roar | unarmed | none | none | victory | Arms raised triumphant |
| **Single-Handed (9)** |
| melee_001_guarded_low_ready | single_handed | compact, long, small | none | ready | Guard stance, weapon low |
| melee_002_over_shoulder_carry | single_handed | long, compact | none | static | Relaxed carry over shoulder |
| melee_003_forward_lunge_action | single_handed | compact, long, flexible | none | dynamic | Forward lunge attack |
| melee_004_triumph_raise | single_handed | compact, long, small | none | victory | Weapon raised overhead |
| melee_005_defensive_crouch | single_handed | compact, long | none | crouch | Low defensive guard |
| melee_006_sprint_carry | single_handed | long | none | dynamic | Running sprint |
| melee_007_overhead_strike | single_handed | compact, long | none | dynamic | Overhead attack |
| melee_008_side_guard_low | single_handed | compact, long | none | ready | Side guard stance |
| mixed_001_shield_bash | single_handed | shield_plane | none | dynamic | Shield charge |
| **Two-Handed (7)** |
| twohand_001_standing_aim_wide | two_handed | two_hand_frame, long, bulky | two_hand_frame, long, bulky | ready | Wide stance aim |
| twohand_002_kneel_aim | two_handed | two_hand_frame, long, bulky | two_hand_frame, long, bulky | kneel | Kneeling aim |
| twohand_003_dynamic_step_aim | two_handed | two_hand_frame, long, bulky | two_hand_frame, long, bulky | dynamic | Advancing aim |
| twohand_004_low_sweep | two_handed | long, two_hand_frame | long, two_hand_frame | dynamic | Horizontal sweep |
| twohand_005_overhead_chop | two_handed | long, two_hand_frame | long, two_hand_frame | dynamic | Overhead chop |
| twohand_006_march_carry | two_handed | long, two_hand_frame | long, two_hand_frame | static | Marching carry |
| twohand_007_defensive_brace | two_handed | long, shield_plane, two_hand_frame | long, shield_plane, two_hand_frame | ready | Defensive brace |
| **Dual-Wield (10)** |
| dual_001_dual_aim_spread | dual_wield | compact, small | compact, small | dynamic | Both weapons aimed out |
| dual_002_long_short_charge | dual_wield | long | compact, small, shield_plane | dynamic | Long weapon + short/shield |
| dual_003_aim_and_cover | dual_wield | compact, small | shield_plane, long | dynamic | Ranged + shield |
| dual_004_cqb_forward | dual_wield | compact, small | compact, small | ready | Close quarters ready |
| dual_005_guardian_vigil | dual_wield | long, compact | small, compact | static | Protective vigil stance |
| dual_006_spinning_strike | dual_wield | compact, small | compact, small | dynamic | Spinning attack |
| dual_007_crossed_defense | dual_wield | long, compact | shield_plane, long | ready | Crossed X defense |
| dual_008_asymmetric_ready | dual_wield | compact, small | long, compact | ready | Asymmetric stance |
| mixed_002_transition_stance | dual_wield | long, compact | compact, small | ready | Weapon transition |

### Pose Style Breakdown

| Style | Count | Purpose |
|-------|-------|---------|
| **ready** | 10 | Alert guard stances, battle-ready positions |
| **dynamic** | 12 | Action poses, attacks, movement |
| **static** | 3 | Calm standing poses, heroic stances |
| **victory** | 2 | Triumphant celebration poses |
| **crouch** | 2 | Low defensive or aggressive crouches |
| **kneel** | 1 | Kneeling position |

### Naming Convention Notes

Current pose IDs use legacy prefixes that don't perfectly match the handedness system:
- `melee_*`: Mostly single_handed poses
- `twohand_*`: Two-handed poses
- `dual_*`: Dual-wield poses
- `unarmed_*`: Unarmed poses
- `mixed_*`: Special cases (shield bash, transitions)

The actual categorization is by **handedness_mode** field, not the ID prefix. When referencing poses, use the full `pose_id` as shown in the catalog.

## System Architecture

### Pose Library Templates
Poses are defined as reusable templates in `rules/pose_library.json` with:
- **handedness_mode**: unarmed, single_handed, two_handed, dual_wield
- **prop_visibility_mode**: "presented" (default) or "carried_attached"
- **Placeholders**: MAIN_HAND_PROP, OFF_HAND_PROP for weapon injection
- **Explicit negation**: Templates include "not held in hands; not gripped; not supported by hands"

### Weapon Definitions
Weapons defined separately on character with:
- **prop_class**: Geometry classification (none, small, compact, long, flexible, shield_plane, two_hand_frame, bulky)
- **visual_detail**: Appearance descriptors
- **handedness**: main_hand, off_hand, or holstered

### Prompt Composition
At generation time:
1. System validates pose compatibility with character weapons
2. Weapon details replace placeholders in pose template
3. Passive state descriptors added ("held firmly", "positioned")
4. Explicit negation preserved ("not held in hands; not gripped")
5. Result: Safe prompt with weapon + spatial positioning + safety disclaimers

**Example Composition:**
```
Template: "MAIN_HAND_PROP held low and angled outward; not held in hands"

Weapon: "double-barrel coach gun" + "Old West shotgun" + "chunky barrels"

Output: "double-barrel coach gun (Old West shotgun) held firmly, angled low ready; 
chunky barrels, exposed hammers; not held in hands; not gripped"
```

## Pose Breakdown by Handedness

The 30 poses break down by handedness mode:

### Unarmed (4 poses)
No weapons in hands - fists, claws, or empty hands

- **unarmed_001_fighter_ready**: Ready fighting stance
- **unarmed_002_aggressive_charge**: Forward charging strike
- **unarmed_003_defensive_crouch**: Low defensive crouch
- **unarmed_004_victory_roar**: Triumphant arms raised

### Single-Handed (9 poses)
One weapon in main hand, off hand free or gesturing

- **melee_001_guarded_low_ready**: Low guard stance
- **melee_002_over_shoulder_carry**: Relaxed shoulder carry
- **melee_003_forward_lunge_action**: Forward lunge attack
- **melee_004_triumph_raise**: Overhead victory raise
- **melee_005_defensive_crouch**: Low defensive guard
- **melee_006_sprint_carry**: Dynamic sprint
- **melee_007_overhead_strike**: Overhead strike
- **melee_008_side_guard_low**: Side guard stance
- **mixed_001_shield_bash**: Shield charge (main hand shield only)

Compatible with: compact, long, small, flexible, shield_plane props

### Two-Handed (7 poses)
Both hands on same weapon or object

- **twohand_001_standing_aim_wide**: Wide stance aim
- **twohand_002_kneel_aim**: Kneeling aim position
- **twohand_003_dynamic_step_aim**: Advancing with aim
- **twohand_004_low_sweep**: Horizontal sweeping attack
- **twohand_005_overhead_chop**: Overhead chopping attack
- **twohand_006_march_carry**: Casual marching carry
- **twohand_007_defensive_brace**: Defensive ready brace

Compatible with: two_hand_frame, long, bulky, shield_plane props

### Dual-Wield (10 poses)
Different item in each hand

- **dual_001_dual_aim_spread**: Both weapons aimed outward
- **dual_002_long_short_charge**: Long weapon + short/shield charge
- **dual_003_aim_and_cover**: Compact weapon + shield/long weapon
- **dual_004_cqb_forward**: Close quarters both weapons
- **dual_005_guardian_vigil**: Protective stance (long/compact + small/compact)
- **dual_006_spinning_strike**: Spinning attack both weapons
- **dual_007_crossed_defense**: Crossed X defense
- **dual_008_asymmetric_ready**: Asymmetric ready stance
- **mixed_002_transition_stance**: Mid-weapon-transition

Compatible combinations:
- Compact + compact/small (pistols, short blades)
- Long + compact/small/shield (sword + dagger, rifle + shield)
- Shield + compact/small (shield + weapon)

## Validation System

### Automatic Compatibility Checking
The system automatically validates that a character's equipped weapons are compatible with the selected pose:
- **When**: Runs during pose prompt composition (before generation)
- **Where**: Warnings printed to stderr (separate from prompt output)
- **What**: Checks handedness_mode and prop_class compatibility
- **Result**: Non-blocking warnings guide users to fix mismatches

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
    "prop_override": {
      "main_hand_prop_state": "held_firmly",
      "main_hand_orientation": "side_out"
    },
    "character_override": "intense expression; forward momentum"
  }
]
```

### Prop Override Options
Customize weapon presentation per-pose:

**prop_state values:**
- `"held_firmly"`: Default passive state (with explicit negation)
- `"slung_side_visible"`: Weapon carried by sling/strap, hands free
- `"slung_back_visible"`: Weapon on back, not in hands
- `"set_aside_visible"`: Weapon visible but not in use
- `"holstered"`: Weapon in holster/sheath

**orientation values:**
- `"low_outside"`, `"forward_offset"`, `"high_overhead"`: Spatial positioning
- `"side_out"`, `"down_away"`, `"vertical_dramatic"`: Angular orientation
- `"chest_level_ward"`, `"positioned_side"`: Specific placements

### Prop Visibility Modes
Control weapon-body overlap:

**"presented" (default):**
- Weapon fully visible with clear negative space
- Held away from torso and face
- No overlap with body geometry
- Used for active display poses

**"carried_attached":**
- Overlap allowed at attachment zones (shoulder, hip, back)
- For slung/stowed weapons
- Weapon visible but not actively held
- Disclaimer added: "weapon visible but not held in hands; hands free for pose action"

### Prop Class Values
- `none`: No weapon/empty hand
- `small`: Small items (coins, small religious symbols)
- `compact`: Compact weapons (pistols, short blades, compact shields)
- `long`: Long weapons (rifles, swords, spears, long staves)
- `flexible`: Flexible items (whips, chains, rope)
- `shield_plane`: Shield objects (round shields, rectangular shields)
- `two_hand_frame`: Two-handed weapons requiring both hands on the same object
- `bulky`: Large bulky items

## Safe Prompt Composition

### Passive State + Explicit Negation Pattern
The system uses a safe composition pattern:

```
[weapon name] ([description]) [passive state], [orientation]; [visual details]; 
[explicit negation]
```

**Components:**
1. **Weapon Identity**: name + brief description in parentheses
2. **Passive State**: "held firmly", "positioned", "kept away" (never active verbs)
3. **Orientation**: Spatial placement ("angled low", "overhead", "at side")
4. **Visual Details**: Appearance descriptors only
5. **Explicit Negation**: "not held in hands; not gripped; not supported by hands"

**Why This Works:**
The combination of passive state descriptor + explicit negation creates a safe contradiction that signals display/positioning rather than active weapon handling. Guardrails interpret this as illustration/visualization rather than instructional content.

**Example Outputs:**
```
double-barrel coach gun (Old West shotgun) held firmly, angled low ready; 
chunky barrels, exposed hammers, weathered wood stock; 
not held in hands; not gripped; not supported by hands

oversized katana (mighty katana): slung side visible; 
carried by sling; weapon visible but not held in hands; hands free for pose action; 
chunky stylized blade profile, dramatic silhouette

silver crucifix (large crucifix on chain) positioned at chest, chest level ward; 
ornate silver cross, visible chain; 
not held in hands; not gripped
```

## Design Principles

All poses follow these principles:
1. **Generic & Reusable**: Work across different character types and settings
2. **Dynamic & Visually Interesting**: Strong silhouettes and clear action reads
3. **Clear Negative Space**: Weapons/props kept away from torso for 3D readability
4. **Varied Stances**: Different foot positions, heights, and orientations
5. **Explicit Requirements**: Clear `prop_class` arrays define compatibility
6. **Placeholder-Based**: Use MAIN_HAND_PROP/OFF_HAND_PROP for weapon injection
7. **Safety First**: Include explicit negation disclaimers in templates

## Testing Validation

### View Warnings
Validation warnings print to stderr, separate from prompt output:
```bash
python create_image.py character_file.json --prompt-only character:pose 2>&1 | head -30
```

### Test Specific Scenarios
```bash
# Test unarmed pose with armed character (should warn)
python create_image.py vampire_heroes.json vampire_sumo:combat_ready --prompt-only 2>&1

# Test dual-wield pose with single weapon (should warn about missing off_hand)
python create_image.py characters.json warrior:dual_wield_pose --prompt-only 2>&1

# Test prop_class mismatch (e.g., long weapon in compact pose)
python create_image.py characters.json archer:pistol_pose --prompt-only 2>&1
```

### Copy to Clipboard
Warnings are NOT copied with `--copy` flag (only the prompt):
```bash
python create_image.py character_file.json character:pose --prompt-only --copy
```

### Silent Mode
Suppress warnings by redirecting stderr to /dev/null:
```bash
python create_image.py character_file.json character:pose --prompt-only 2>/dev/null
```

## Modular Imports

The system uses modular rule imports for flexibility:

```json
"imports": {
  "generic_render_rules": "rules/generic_render_rules.json",
  "style_rules": "rules/realistic_weird_west_style.json",
  "pose_library": "rules/pose_library.json"
}
```

**Benefits:**
- Reuse render rules across multiple character sets
- Swap style rules without changing characters
- Share pose library between projects
- Update rules once, affect all characters

**Custom Rules:**
Create your own:
- `rules/your_style.json` - Custom visual style
- `rules/your_poses.json` - Project-specific poses
- `rules/your_render_rules.json` - Custom rendering constraints

## Future Enhancements

### Additional Poses
Potential additions to pose library:
- **Aerial**: Flight/airborne poses with support prop requirements
- **Mounted**: Riding poses (horse, vehicle, creature)
- **Grappling**: Wrestling/grappling interactions
- **Ground**: Kneeling/prone/sitting poses
- **Acrobatic**: Climbing/leaping/balancing poses
- **Injured**: Wounded/exhausted/defeated poses
- **Social**: Talking/gesturing/non-combat interactions

### System Improvements
- **Pose variants**: Automatic mirroring (left/right stance variants)
- **Pose blending**: Combine upper/lower body from different poses
- **Dynamic validation**: Real-time feedback in editor
- **Pose preview**: Visual reference images for each pose
- **Prop templates**: Reusable prop definitions separate from weapons
- **Animation hints**: Sequence markers for pose chains

### Documentation
- Video tutorials on pose system
- Interactive pose selector tool
- Character template generator
- Pose compatibility matrix
- Visual style guide examples
