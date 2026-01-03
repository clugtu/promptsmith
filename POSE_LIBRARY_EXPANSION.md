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

### Complete Pose Library (39 Poses)

**Naming Convention:**
- Handedness codes: `un` (unarmed), `oh` (one-hand), `th` (two-hand), `dh` (dual-hand), `quad` (quadrupedal), `fbp` (facultatively bipedal)
- Type qualifiers: `_melee` (melee-only), `_ranged` (ranged-only), `_object` (gesture/display), none (universal)
- Format: `{handedness}{_type}_{description}`

| Pose ID | Handedness | Main Hand Props | Off Hand Props | Style | Type | Figure Type |
|---------|-----------|-----------------|----------------|-------|------|-------------|
| **Unarmed Bipedal (4)** |
| un_fighter_ready | unarmed | none | none | ready | - | bipedal_humanoid |
| un_aggressive_charge | unarmed | none | none | dynamic | - | bipedal_humanoid |
| un_defensive_crouch | unarmed | none | none | crouch | - | bipedal_humanoid |
| un_victory_roar | unarmed | none | none | victory | - | bipedal_humanoid |
| **One-Handed Bipedal (9)** |
| oh_melee_guarded_low_ready | single_handed | compact, long, small | none | ready | melee | bipedal_humanoid |
| oh_over_shoulder_carry | single_handed | long, compact | none | static | universal | bipedal_humanoid |
| oh_melee_forward_lunge_action | single_handed | compact, long, flexible | none | dynamic | melee | bipedal_humanoid |
| oh_triumph_raise | single_handed | compact, long, small | none | victory | universal | bipedal_humanoid |
| oh_melee_defensive_crouch | single_handed | compact, long | none | crouch | melee | bipedal_humanoid |
| oh_sprint_carry | single_handed | long | none | dynamic | universal | bipedal_humanoid |
| oh_melee_overhead_strike | single_handed | compact, long | none | dynamic | melee | bipedal_humanoid |
| oh_melee_side_guard_low | single_handed | compact, long | none | ready | melee | bipedal_humanoid |
| oh_melee_shield_bash | single_handed | shield_plane | none | dynamic | melee | bipedal_humanoid |
| **Two-Handed (7)** |
| th_ranged_standing_aim_wide | two_handed | two_hand_frame, long, bulky | two_hand_frame, long, bulky | ready | ranged | bipedal_humanoid |
| th_ranged_kneel_aim | two_handed | two_hand_frame, long, bulky | two_hand_frame, long, bulky | kneel | ranged | bipedal_humanoid |
| th_ranged_dynamic_step_aim | two_handed | two_hand_frame, long, bulky | two_hand_frame, long, bulky | dynamic | ranged | bipedal_humanoid |
| th_melee_low_sweep | two_handed | long, two_hand_frame | long, two_hand_frame | dynamic | melee | bipedal_humanoid |
| th_melee_overhead_chop | two_handed | long, two_hand_frame | long, two_hand_frame | dynamic | melee | bipedal_humanoid |
| th_march_carry | two_handed | long, two_hand_frame | long, two_hand_frame | static | universal | bipedal_humanoid |
| th_melee_defensive_brace | two_handed | long, shield_plane, two_hand_frame | long, shield_plane, two_hand_frame | ready | melee | bipedal_humanoid |
| **Dual-Wield (10)** |
| dh_ranged_dual_aim_spread | dual_wield | compact, small | compact, small | dynamic | ranged | bipedal_humanoid |
| dh_melee_long_short_charge | dual_wield | long | compact, small, shield_plane | dynamic | melee | bipedal_humanoid |
| dh_ranged_aim_and_cover | dual_wield | compact, small | shield_plane, long | dynamic | ranged | bipedal_humanoid |
| dh_ranged_cqb_forward | dual_wield | compact, small | compact, small | ready | ranged | bipedal_humanoid |
| dh_melee_guardian_vigil | dual_wield | long, compact | small, compact | static | melee | bipedal_humanoid |
| dh_melee_spinning_strike | dual_wield | compact, small | compact, small | dynamic | melee | bipedal_humanoid |
| dh_melee_crossed_defense | dual_wield | long, compact | shield_plane, long | ready | melee | bipedal_humanoid |
| dh_ranged_asymmetric_ready | dual_wield | compact, small | long, compact | ready | ranged | bipedal_humanoid |
| dh_transition_stance | dual_wield | long, compact | compact, small | ready | universal | bipedal_humanoid |
| **Quadrupedal (6)** |
| quad_stalking | unarmed | none | none | dynamic | - | quadrupedal |
| quad_charging | unarmed | none | none | dynamic | - | quadrupedal |
| quad_howling | unarmed | none | none | static | - | quadrupedal |
| quad_seated_watch | unarmed | none | none | static | - | quadrupedal |
| quad_circling | unarmed | none | none | dynamic | - | quadrupedal |
| quad_loping | unarmed | none | none | dynamic | - | quadrupedal |
| **Facultatively Bipedal (4)** |
| fbp_melee_overhead_display | single_handed | long, compact, two_hand_frame | none | static | melee | facultatively_bipedal |
| fbp_howling | single_handed | long, compact, two_hand_frame | none | victory | universal | facultatively_bipedal |
| fbp_melee_low_sweep | single_handed | long, compact, flexible | none | dynamic | melee | facultatively_bipedal |
| fbp_menacing_advance | single_handed | long, compact, two_hand_frame | none | ready | melee | facultatively_bipedal |

### Type Categories

**Melee (`_melee`):** Combat actions with striking/guarding weapons
- Actions: `strike`, `guard`, `brace`
- Examples: `oh_melee_overhead_strike`, `th_melee_low_sweep`, `dh_melee_spinning_strike`

**Ranged (`_ranged`):** Aiming actions with ranged weapons
- Actions: `aim`
- Examples: `th_ranged_standing_aim_wide`, `dh_ranged_dual_aim_spread`

**Object (`_object`):** Gesture/display actions with objects
- Actions: `gesture`
- Examples: None currently in library (unarmed poses use gesture without qualifier)

**Universal (no qualifier):** Carry/present actions compatible with any weapon type
- Actions: `carry`, `present`, `hold_object`, `reach`
- Examples: `oh_over_shoulder_carry`, `oh_triumph_raise`, `th_march_carry`

**Unarmed (no qualifier):** No weapon, hands free
- Handedness: `unarmed`
- All unarmed poses have no type qualifier regardless of action
- Examples: `un_fighter_ready`, `un_victory_roar`

### Figure Types

**Understanding Body Types**

The pose library supports three different body types based on how creatures move:

**Bipedal (Two-Legged)**
- Walks upright on two legs like humans, elves, dwarves
- Can use weapons with hands
- Standard humanoid proportions
- Technical term: `bipedal_humanoid`
- 29 poses covering all weapon combinations

**Quadrupedal (Four-Legged)**
- Walks on all four legs like wolves, cats, bears, horses
- Cannot use hand-held weapons (no hands)
- Animal body structure with four legs
- Technical term: `quadrupedal`
- 6 poses for stalking, running, howling, watching

**Facultatively Bipedal**
- Can walk upright on two legs OR drop to all fours
- Real-world examples: gorillas, bears, some large lizards
- When upright: can use weapons like bipeds
- When on all fours: moves like quadrupeds (not yet implemented)
- Used for werewolf war-form (crinos), werebears, large shapeshifters
- Technical term: `facultatively_bipedal` (means "optional two-legged")
- 4 poses showing upright weapon combat

**Serpentine (Snake Body)**
- Humanoid upper body with snake/serpent lower body instead of legs
- Moves by slithering, coiling, or raising up on tail
- Can use weapons with arms like bipeds
- Real-world mythology: nagas, lamias, yuan-ti, merfolk
- Technical term: `serpentine` or `naga_form`
- No poses yet (future expansion)

**Centauroid (Half-Human, Half-Beast)**
- Humanoid torso mounted on four-legged animal body
- Always has four legs (unlike facultatively bipedal)
- Can use weapons like bipedal humanoids
- Real-world mythology: centaurs (horse), driders (spider), sagittari
- Technical term: `centauroid`
- No poses yet (future expansion)

**Multi-Limbed**
- More than two arms (4, 6, or more)
- Can be bipedal or centauroid base with extra arms
- Special weapon combinations (triple-wield, quad-wield)
- Examples: thri-kreen (4 arms), marilith demons (6 arms), aliens
- Technical term: `multi_limbed_bipedal` or `multi_limbed_centauroid`
- No poses yet (future expansion)

**Winged**
- Has wings that affect balance and silhouette
- Usually bipedal base with wings added
- Wing position matters for pose composition
- Examples: angels, demons, aarakocra, dragonborn with wings
- Technical term: `winged_bipedal` or `winged_centauroid`
- No poses yet (uses modified bipedal poses)

**Amorphous/Floating**
- No ground contact, hovers or floats
- No legs or feet
- Examples: ghosts, specters, beholders, floating jellyfish creatures
- Technical term: `amorphous` or `floating`
- No poses yet (future expansion)

**Arachnoid (Spider Body)**
- Eight legs in spider configuration
- Similar to centauroid but spider anatomy
- Examples: giant spiders, phase spiders, ettercaps
- Technical term: `arachnoid`
- No poses yet (future expansion)

---

**bipedal_humanoid:** Standard two-legged humanoid characters
- Uses standard handedness modes (unarmed, single_handed, two_handed, dual_wield)
- All original 29 poses

**quadrupedal:** Four-legged creatures (wolves, dire wolves, large cats, etc.)
- Uses `quad` prefix
- No weapon handling (all `unarmed` mode)
- Examples: `quad_stalking`, `quad_charging`, `quad_howling`
- 6 poses total

**facultatively_bipedal:** Creatures that can move bipedally or quadrupedally (werewolf crinos form, werebears, etc.)
- Uses `fbp` prefix when bipedal with weapons
- Can use weapon-handling poses when upright
- Examples: `fbp_melee_overhead_display`, `fbp_howling`, `fbp_menacing_advance`
- 4 poses total

**serpentine / naga_form:** Humanoid upper body, snake lower body (nagas, yuan-ti, lamias, merfolk)
- Uses `serp` or `naga` prefix
- Can use weapons like bipedal humanoids
- Movement via slithering/coiling
- 0 poses (planned future expansion)

**centauroid:** Humanoid torso on four-legged animal body (centaurs, driders, sagittari)
- Uses `cent` prefix
- Can use weapons like bipedal humanoids
- Always four legs (never walks on two)
- 0 poses (planned future expansion)

**multi_limbed_bipedal / multi_limbed_centauroid:** More than two arms (thri-kreen, marilith demons, aliens)
- Uses `ml` prefix with arm count (e.g., `ml4` for 4 arms)
- Special multi-weapon combat combinations
- Can be bipedal or centauroid base
- 0 poses (planned future expansion)

**winged_bipedal / winged_centauroid:** Winged variants (angels, demons, aarakocra, dragonborn)
- Uses base prefix with `w` suffix (e.g., `ohw` for one-handed winged)
- Wings affect balance and silhouette
- Currently uses modified bipedal/centauroid poses
- 0 dedicated poses (uses existing poses with wing annotations)

**amorphous / floating:** No ground contact, hovering creatures (ghosts, beholders, specters)
- Uses `float` or `amor` prefix
- No legs or ground contact
- Hovering/floating poses only
- 0 poses (planned future expansion)

**arachnoid:** Eight-legged spider body (giant spiders, phase spiders, ettercaps)
- Uses `arac` prefix
- Spider anatomy with eight legs
- Similar to centauroid but spider structure
- 0 poses (planned future expansion)

### Pose Style Breakdown

| Style | Count | Purpose |
|-------|-------|---------|
| **ready** | 12 | Alert guard stances, battle-ready positions |
| **dynamic** | 18 | Action poses, attacks, movement, running, charging |
| **static** | 6 | Calm standing poses, heroic stances, seated watch |
| **victory** | 3 | Triumphant celebration poses, howling |
| **crouch** | 2 | Low defensive or aggressive crouches |
| **kneel** | 1 | Kneeling position |

### Pose ID Structure

**Format:** `{handedness_code}{type_qualifier}_{descriptive_name}`

**Handedness Codes:**
- `un`: unarmed (no weapons, bipedal humanoid)
- `oh`: one-hand (single_handed mode, bipedal)
- `th`: two-hand (two_handed mode, bipedal)
- `dh`: dual-hand (dual_wield mode, bipedal)
- `quad`: quadrupedal (four-legged creatures)
- `fbp`: facultatively bipedal (can be bipedal or quadrupedal, shown bipedal with weapons)
- `serp` or `naga`: serpentine/naga form (snake lower body)
- `cent`: centauroid (humanoid torso on four-legged animal body)
- `ml4`, `ml6`: multi-limbed (4 arms, 6 arms, etc.)
- `ohw`, `thw`, `dhw`: winged variants (one-hand winged, two-hand winged, dual-hand winged)
- `float` or `amor`: amorphous/floating (no ground contact)
- `arac`: arachnoid (eight-legged spider body)

**Type Qualifiers** (only when pose is specific to that weapon type):
- `_melee`: Melee combat actions (strike, guard, brace)
- `_ranged`: Ranged aiming actions (aim)
- `_object`: Object gesture/display actions (gesture)
- *(none)*: Universal poses (carry, present) compatible with any weapon type

**Examples:**
- `oh_melee_overhead_strike` → One-hand, melee-only, overhead strike
- `th_ranged_standing_aim_wide` → Two-hand, ranged-only, standing aim
- `oh_triumph_raise` → One-hand, universal (works with any weapon)
- `un_fighter_ready` → Unarmed, no qualifier needed
- `quad_stalking` → Quadrupedal, low stalking pose
- `fbp_melee_overhead_display` → Facultatively bipedal, melee, overhead display

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
