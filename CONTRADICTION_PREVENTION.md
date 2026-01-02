# Contradiction Prevention Guide

## The Problem

Image generation models struggle when prompts contain **mutually exclusive spatial constraints**. Even if each constraint is technically valid, too many overlapping requirements cause the model to produce uncanny results by "cheating" physics or anatomy.

## Common Contradiction Patterns

### 1. Slung Weapon + Active Pose Physics
**Symptoms:** Floating weapons, impossible strap physics, hands appearing to touch despite "no contact" language

**Example:**
```
❌ BAD: "weapon suspended by strap under full tension + diagonal orientation + hands positioned with visible air gap + torso turned + arms extended"
```

**Solution:** Simplify slung weapon constraints
```
✅ GOOD: "weapon carried by strap; visible but not held in hands; hands free for pose action"
```

### 2. Pose Handedness Mismatch
**Symptoms:** Awkward hand positions, weapons appearing in wrong locations

**Example:**
```
❌ BAD: Using `slung_side_visible` with a two-handed combat pose
```

**Solution:** Match weapon state to pose handedness mode
```
✅ GOOD: Two-handed poses should use held weapons, not slung
```

### 3. Character Override Contradicting Pose Mechanics
**Symptoms:** Anatomy warping, impossible positions

**Example:**
```
❌ BAD: Pose says "feet planted wide" but override says "dynamic leaping motion"
```

**Solution:** Character overrides should only add characterization (expression, clothing details), not change pose mechanics

### 4. Constraint Density Overload
**Symptoms:** Model ignores some constraints, produces unpredictable results

**Example:**
```
❌ BAD: Stacking pose rules + sculpt rules + print rules + physics rules + camera rules + framing rules + lighting rules + aesthetic rules + proportion rules + clothing rules all with equal weight
```

**Solution:** Rely on pose library for mechanics; use overrides sparingly for characterization only

## Best Practices

### For Slung Weapons
1. Only use slung weapons with poses designed for them (check `pose_prompt` for "No hands on" language)
2. Keep slung weapon constraints simple - state what IS happening, not exhaustive physics
3. Let the pose library handle spatial arrangement

**Poses designed for slung weapons:**
- `melee_001_guarded_low_ready` - Weapon at side, hands free
- `melee_003_forward_lunge_action` - Weapon visible but not wielded
- `melee_004_triumph_raise` - Weapon overhead as symbolic element
- `dual_005_guardian_vigil` - Weapon visible as presence element

### For Character Overrides
**GOOD Override Content:**
- Facial expression details
- Clothing arrangement (flowing cloak, parted habit)
- Emotional tone
- Gear visibility (belt, straps, accessories)
- Proportions at character level (not pose level)

**BAD Override Content:**
- Contradicting pose mechanics ("feet planted" vs "dynamic leap")
- Redefining weapon handling that conflicts with pose
- Adding new spatial constraints that compete with pose library
- Changing handedness mode

### For Prop Overrides
**Use `prop_override` to:**
- Change weapon state (held vs slung)
- Adjust orientation within pose expectations
- Specify alternative weapons for a pose

**Don't use `prop_override` to:**
- Add new physics constraints
- Override fundamental pose mechanics
- Create spatial requirements the pose wasn't designed for

## Validation System

The code includes validation warnings for common contradictions:

```python
validate_pose_compatibility(character_data, pose_def, pose_library)
```

Warnings indicate:
- Handedness mismatches (dual-wield pose with slung weapon)
- Prop class incompatibilities (shield pose with long weapon)
- Slung weapons in poses expecting active wielding

**Take these warnings seriously** - they indicate mechanical contradictions that will produce uncanny results.

## How Contradictions Manifest

When spatial constraints conflict, the model "solves" it by:
1. Subtly letting prohibited contact happen (hand appears to touch slung weapon)
2. Making physics wrong (strap hangs impossibly)
3. Warping anatomy (arms at wrong angles to satisfy all constraints)
4. Ignoring some constraints entirely (weapon not where specified)

The result feels "off" even if you can't identify exactly why - it's because the model had to break physics or anatomy to satisfy mutually exclusive requirements.

## The Solution: Simplicity + Hierarchy

1. **Pose library = spatial mechanics** (trusted source of truth)
2. **Character overrides = characterization only** (expression, clothing, tone)
3. **Prop overrides = weapon selection** (which weapon, held or slung)
4. **Weapon details = minimal** (name, attachment method, visibility)

Keep each layer focused on its job. Don't make character overrides redefine spatial relationships - that's the pose library's job.
