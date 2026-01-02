# Structured Prompt Format Guide

## Overview
This document describes the structured format for `character_override` entries that produce clean, organized prompts optimized for image-to-3D conversion.

## When to Use Structured Format
Use structured format for poses where:
- You need explicit geometry rules for hard objects (weapons, props)
- The pose requires detailed spatial relationships
- You want to override generic rules with character-specific details
- The prompt benefits from clear sectioning for readability

## Format Structure

When `character_override` starts with `"SUBJECT:"`, the system recognizes it as structured and:
- Skips prepending `character_base` (to avoid redundancy)
- Skips appending holstered weapons (they should be in SUBJECT section)
- Preserves the structured sections with newlines

### Required Sections

```
SUBJECT:
[Character description]
[Equipment and gear with simplified geometry notes]
[Each major piece of equipment on its own line]

POSE (CLEAR SEPARATION, 3D-SAFE):
[Basic stance description]
[Foot position]
[Torso orientation]

[PROP_NAME] (PRIMARY/SECONDARY HARD OBJECT):
[Which hand holds it and general position]

PRIMARY OBJECT OWNERSHIP:
[Prop] is rigidly owned by the [HAND].
[Hand] grips the [prop] [location] with full finger wrap.
[Prop] must visually originate from the [hand] grip point.
[Other hand] must NOT touch or support the [prop] in any way.

GRIP LOCATION ANCHOR:
[Hand] grips the [prop] at the [specific location on prop].
Fingers fully wrapped; palm contact visible.
Grip point clearly readable.

NO SUPPORT CLAUSE:
[Prop] is NOT braced against [body parts that should not support it].
No secondary support points.

[Prop name] geometry rules:
- [Specific geometric constraint 1]
- [Specific geometric constraint 2]
- [etc.]

CLOTHING & SILHOUETTE:
[Cloth flow direction]
[Intersection prevention rules]
[Edge simplification notes]
```

### Optional Sections
These are typically handled by `generic_render_rules.json` but can be overridden if needed:
- `FACE (LOW-RELIEF, 3D-SAFE):` - Usually skip, let generic rules handle it
- `STRICT EXCLUSIONS:` - Usually skip, let generic rules handle it

## Example: Vampire Nun with Shotgun and Crucifix

```
SUBJECT:
Vampire nun of the Old West.
Black habit worn as a weathered cloak, parted to reveal frontier clothing underneath (vest, shirt, belt, trousers, boots).
Habit adorned with simplified crosses and religious symbols.
Silver cross necklace simplified and thickened.
Bandolier with shotgun shells modeled as thick cylinders.
Belt with simplified containers.
Western Bowie knife sheathed on thigh, blocky simplified shape.

POSE (CLEAR SEPARATION, 3D-SAFE):
Side guard stance.
Feet shoulder-width.
Torso rotated approximately 45 degrees.

SHOTGUN (PRIMARY HARD OBJECT):
Main hand holds a double-barrel shotgun low at the side.

PRIMARY OBJECT OWNERSHIP:
Shotgun is rigidly owned by the MAIN HAND.
Main hand grips the shotgun stock with full finger wrap.
Shotgun must visually originate from the main hand grip point.
Off hand must NOT touch or support the shotgun in any way.

GRIP LOCATION ANCHOR:
Main hand grips the shotgun at the stock/wrist directly behind the trigger guard.
Fingers fully wrapped; palm contact visible.
Grip point clearly readable.

NO SUPPORT CLAUSE:
Shotgun is NOT braced against shoulder, torso, arm, or cloak.
No secondary support points.

Shotgun geometry rules:
- Stock clearly visible at hip level
- Barrels angled sharply upward (approximately 35-45 degrees)
- Muzzle clearly higher than the stock and visibly higher than the shoulder line in screen space
- Strong upward foreshortening visible
- Entire weapon visible from stock to muzzle
- Shotgun separated from thigh and cloak by a clear air gap
- Shotgun modeled as simple solids (two cylinders + blocky stock)
- No straps, slings, cords, or flexible attachments

CRUCIFIX (SECONDARY HARD OBJECT):
Off hand holds a crucifix near the chest in a guarded defensive position.
Crucifix geometry rules:
- Thickened cross shape with rectangular arms
- Simplified, rounded edges
- Rotated slightly outward from the torso
- Offset from the body with clear negative space around the entire silhouette
- Increased thickness for miniature readability
- Crucifix does not touch torso, cloak, or arm

CLOTHING & SILHOUETTE:
Habit cloak flows backward only.
Cloak does NOT intersect arms, shotgun, crucifix, or torso.
Cloak edges thick and simplified.
No thin folds or dangling cloth elements.
Strong negative space maintained around all props.
```

## Geometry Rules Best Practices

### For Long Props (Weapons, Staffs, etc.)

**PRIMARY OBJECT OWNERSHIP** - Establish what cannot change:
- State which hand rigidly owns the prop
- Specify full finger wrap or grip type
- Declare visual origin from grip point
- Explicitly forbid other hand from touching/supporting

**GRIP LOCATION ANCHOR** - Prevent reinterpretation:
- Specify exact grip location on the prop (e.g., "at the stock/wrist directly behind trigger guard")
- State finger wrap and palm contact visibility
- Note grip point readability

**NO SUPPORT CLAUSE** - Prevent shoulder/body bracing:
- List all body parts prop is NOT braced against (shoulder, torso, arm, cloak, etc.)
- State "No secondary support points"

**Geometry rules** - Spatial constraints:
- Specify angle relative to body (30-45 degrees from camera plane)
- Describe foreshortening visibility (muzzle higher than stock, tip higher than grip)
- State separation from body parts and cloth (clear air gaps)
- Simplify to primitive shapes (cylinders, blocks)
- Explicitly forbid straps, slings, cords

### For Small Props (Amulets, Crosses, etc.)
- Increase thickness beyond realistic proportions
- Rotate outward from body for visibility
- Offset from torso with negative space
- Simplify edges and forms
- State non-intersection rules

### For Cloth
- One clear flow direction only (behind, beside, never touching props/limbs)
- Thick simplified edges
- No thin folds or dangling elements
- Explicit non-intersection statements

## Final Prompt Assembly

The system assembles the final prompt as:
1. `character_override` (your structured sections) - OR - `character_base + character_override` (for legacy format)
2. Holstered weapons (only for legacy format)
3. Thematic snippets
4. Proportions
5. Style snippet (thematic style)
6. Generic render rules (STYLE, 3D-SAFE GEOMETRY, POSE CLARITY, FACE, FRAMING, LIGHTING)
7. No-base clause (if --no-base flag used)

## Migration from Legacy Format

Legacy format:
```json
"character_override": "calm determined expression with fangs visible; habit parted to show belt and gear"
```

Structured format:
```json
"character_override": "SUBJECT:\n[Full character description]\n\nPOSE (CLEAR SEPARATION, 3D-SAFE):\n[Detailed pose]\n\n[PROP] (HARD OBJECT):\n[Prop details with geometry rules]"
```

The legacy format still works and will have `character_base` prepended. The structured format is self-contained and more explicit about geometry constraints.
