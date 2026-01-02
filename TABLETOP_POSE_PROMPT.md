# Tabletop Miniature Pose Review & Creation Prompt
**Purpose:** Use this prompt to *create*, *review*, or *iterate on poses* for tabletop-scale miniatures with high sculpt fidelity and print-readability.

---

## ARCHITECTURE NOTE

This system uses a **pose library architecture**:

- **Poses are defined generically** in a reusable library with placeholders (MAIN_HAND_PROP, OFF_HAND_PROP)
- **Weapons are defined separately** on characters with prop_class, handedness, and visual details
- **Composition happens at generation time**: Weapon descriptions replace placeholders in pose templates
- **Validation checks compatibility**: System warns if character weapons don't match pose requirements

**Handedness Modes:**
- `unarmed`: No weapons in hands
- `single_handed`: One weapon in main hand
- `two_handed`: Both hands on same weapon
- `dual_wield`: Different weapon in each hand

**Prop Visibility Modes:**
- `presented`: Fully visible with clear negative space, held away from torso (most poses)
- `carried_attached`: Overlap allowed at attachment zones (slung/stowed weapons)

When creating new poses, use placeholder syntax and specify handedness_mode, prop_visibility_mode, and expected prop_class arrays.

---

## 1. SUBJECT DEFINITION (AUTHORITATIVE)
- **Character:** [Describe the character succinctly]
- **Theme / Setting:** [e.g., Weird West, Gothic Horror, Feudal]
- **Scale Intent:** Tabletop miniature (28–32mm equivalent)
- **Mood / Role:** [e.g., vigilant protector, grim hero]

> **Rule:** This section defines WHAT the figure is. It overrides later stylistic interpretation.

---

## 2. MATERIAL & RENDERING CONSTRAINTS (NON-NEGOTIABLE)
- **Material:** Unpainted cast plastic/resin
- **Color:** Grayscale only (black–white range used strictly for depth)
- **Surface:** Smooth planar surfaces, hard/crisp edges
- **Detail Style:** Sculpt-readable; no photoreal textures
- **Forbidden:** wood grain, metal shine, fabric weave, color accents

> Shading represents *form depth only*, not material realism.

---

## 3. CAMERA & FRAMING (HARD CONSTRAINTS)
- **View:** Three-quarter sculpt view (~45° turntable rotation)
- **Lens:** Neutral / orthographic-leaning (no cinematic distortion)
- **Framing:** Full body visible, head-to-feet
- **Negative Space:** Generous; no limb or prop touching frame edges
- **Presentation:** Figure-only (no base, stand, plinth, ground plane)

> Treat the model as a **physical resin miniature rotated on a turntable**.

---

## 4. LIGHTING
- Overhead key light + subtle rim light
- Neutral illumination
- Emphasize plane breaks and silhouette readability
- No dramatic spotlights or film lighting

---

## 5. POSE DEFINITION (CORE)
Describe the pose clearly and calmly.

- **Stance:** [e.g., feet shoulder-width, weight balanced]
- **Torso:** [upright, slight lean, squared shoulders]
- **Arms:** [relaxed, braced, extended—but never ambiguous]
- **Expression:** [neutral, determined, restrained]

> **Rule:** Prioritize anatomical clarity over drama.

---

## 6. PROP SAFETY BLOCK (CRITICAL)

**Pose Library System Approach:**

Props (weapons) are defined separately from poses using this structure:

### Weapon Definition (on Character)
```json
"weapons": {
  "main_hand": {
    "name": "double-barrel coach gun",
    "description": "Old West double-barrel shotgun (period-appropriate 1880s style)",
    "prop_class": "long",
    "visual_detail": "chunky double barrels, exposed hammers, weathered wood stock"
  },
  "off_hand": {
    "name": "silver crucifix",
    "prop_class": "small",
    "visual_detail": "ornate silver cross, visible chain"
  }
}
```

### Pose Template (in Pose Library)
```json
"pose_prompt": "Protective vigil stance: feet planted wide; MAIN_HAND_PROP held low and angled outward from body; OFF_HAND_PROP raised at chest/shoulder level in warding gesture; clear negative space between props and torso",
"handedness_mode": "dual_wield",
"prop_visibility_mode": "presented",
"main_hand": {
  "prop_slot": "MAIN_HAND_PROP",
  "prop_class": ["long", "compact"],
  "action": "guard",
  "orientation": "forward_offset"
}
```

### At Generation Time
- System validates weapon compatibility with pose (handedness_mode, prop_class)
- Placeholders get replaced: `MAIN_HAND_PROP` → "double-barrel coach gun (Old West double-barrel shotgun...) held firmly, angled low ready"
- Result uses safe passive language automatically

### Prop Placement Rules
- **State:** Non-operational, non-wielded display/support posture
- **Hand Contact:** Passive language only ("held firmly", "positioned", "kept away")
- **Orientation:** Specified by pose template (forward_offset, side_out, high_overhead, etc.)
- **Spacing:** Enforced by prop_visibility_mode (presented = clear negative space)

**Forbidden:**
- Active handling verbs (gripping, aiming, wielding)
- Extreme diagonals or foreshortening
- Occlusion by cloth or anatomy
- Combat action language ("preparing to strike", "ready to attack")

> If constraints conflict, **geometric correctness overrides dramatic pose**.

---

## 7. SILHOUETTE & READABILITY CHECK
Before finalizing, confirm:
- Limbs are clearly separated
- Props are identifiable in silhouette
- No tangents between prop and body
- Pose reads clearly at small scale

---

## 8. REVIEW QUESTIONS (USE FOR ITERATION)
Use these to critique or request revisions:
1. Does the pose survive a 360° turntable view?
2. Are all rigid objects straight and undistorted?
3. Would this print cleanly without fragile overhangs?
4. Is anything being implied instead of clearly shown?
5. Is drama coming from *shape*, not *angle*?
6. **Pose Library Checks:**
   - Does handedness_mode match the character's weapon setup?
   - Are prop_class arrays appropriate for the weapon types?
   - Is prop_visibility_mode correct (presented for most poses, carried_attached for slung weapons)?
   - Do placeholder positions (MAIN_HAND_PROP, OFF_HAND_PROP) maintain clear negative space?
   - Are action/orientation values appropriate for the pose intent?

---

## 9. FAILURE PREVENTION CLAUSE (OPTIONAL BUT RECOMMENDED)
> Do not mirror, flip, or reinterpret anatomy.  
> Do not redesign unseen areas.  
> This is a pose refinement, not a new concept.

---

**End of Prompt**
