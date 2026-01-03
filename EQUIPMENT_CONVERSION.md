# Equipment Conversion Guide - v5.0.0

## New Structured Format

Replace `weapons` object with `equipment` array using structured format with position and description.

### Format
```json
"equipment": [
  "item_name (visual_detail) : position : usage_description",
  "item_name (visual_detail) : position : usage_description"
]
```

### Position Values
- `main_hand` - Primary weapon/tool held in dominant hand
- `off_hand` - Secondary weapon/tool or shield in off hand
- `dual_wield` - Paired weapons held in both hands
- `holstered_belt` - Weapon/item secured at belt/waist
- `holstered_hip` - Weapon/item secured at hip
- `holstered_thigh` - Weapon/item secured on thigh/leg
- `holstered_back` - Weapon/item carried on back

### Examples
- `"stone-headed war club (stone head bound with sinew, wrapped leather grip) : main_hand : held at ready"`
- `"six shooter (weathered steel, worn wooden grip) : holstered_belt : ready to draw"`
- `"bowie knife (thick blade profile, leather sheath) : holstered_thigh : sheathed"`
- `"cavalry shield (round wooden shield, iron boss) : off_hand : held at guard"`
- `"twin revolvers (weathered steel, worn wooden grips) : dual_wield : held in both hands"`

## Output Format

Equipment is rendered in prompts as:
```
PROPS:
- item_name (visual_detail) [position] usage_description
```

Example:
```
PROPS:
- double-barrel coach gun (chunky double barrels, exposed hammers, weathered wood stock) [main_hand] held at ready or slung over shoulder
- silver crucifix (ornate silver cross, visible chain) [off_hand] warding gesture
- western Bowie knife (thick blade profile, leather sheath) [holstered_thigh] sheathed
```

## Character File Examples

### Garou Character Example
```json
"equipment": [
  "stone-headed war club (stone head bound with sinew, wrapped leather grip, bone beads on thong) : main_hand : held at ready; becomes bone-obsidian war club in crinos",
  "ceremonial knife (flint blade, bone handle, decorative beadwork on sheath) : holstered_belt : sheathed"
]
```

### Vampire Heroes Example
```json
"equipment": [
  "double-barrel coach gun (chunky double barrels, exposed hammers, weathered wood stock) : main_hand : held at ready or slung over shoulder",
  "silver crucifix (ornate silver cross, visible chain) : off_hand : warding gesture",
  "western Bowie knife (thick blade profile, leather sheath) : holstered_thigh : sheathed"
]
```

## How Poses Override Equipment

The character file defines the default equipment state. Poses can completely replace equipment using `equipment_override`:

### equipment_override (Complete Replacement)

Use `equipment_override` at the pose level to completely replace the character's equipment with a different configuration:

```json
{
  "id": 5,
  "name": "unarmed_ready",
  "pose_library_ref": "un_fighter_ready",
  "equipment_override": [
    "longsword (straight blade, wrapped grip) : holstered_back : slung on back",
    "shield (wood planks, steel rim) : holstered_back : slung on back"
  ],
  "character_override": "combat ready with hands empty; weapons stowed on back"
}
```

This uses the exact same format as character-level equipment. The pose-level `equipment_override` completely replaces the character's equipment array for that specific pose.

**Examples:**

Switching from weapons drawn to weapons holstered:
```json
// Character level
"equipment": [
  "sword (straight blade) : main_hand : held at ready",
  "shield (wood planks) : off_hand : held at guard"
]

// Pose level - weapons stowed
"equipment_override": [
  "sword (straight blade) : holstered_back : slung on back",
  "shield (wood planks) : holstered_back : slung on back"
]
```

Switching equipment for different tactical situations:
```json
// Character level - default ranged loadout
"equipment": [
  "longbow (curved wood) : main_hand : held at ready",
  "quiver (leather, arrows visible) : holstered_back : slung on back"
]

// Pose level - switched to melee
"equipment_override": [
  "short sword (simple blade) : main_hand : drawn and ready",
  "longbow (curved wood) : holstered_back : slung across back",
  "quiver (leather, arrows visible) : holstered_back : slung on back"
]
```
