# Safe Image Prompt Guide
## Guardrail-Safe Prompting for Character Illustration
### Updated: 2026-01-02

---

## Purpose

This guide defines **safe prompt language** for generating stylized character illustrations that look like tabletop miniatures.

**Scope:** Image generation prompts only.

**Out of Scope:** Image-to-3D conversion, 3D printing, STL generation, manufacturing constraints.

---

## System Architecture Overview

The prompt generation system uses a **pose library architecture** that separates weapon definitions from pose descriptions:

1. **Weapon Definitions**: Characters define weapons separately with:
   - `prop_class`: Type classification (none, small, compact, long, flexible, shield_plane, two_hand_frame, bulky)
   - `handedness`: Which hand(s) use the weapon (main_hand, off_hand, holstered)
   - Visual details and descriptions

2. **Pose Library**: Reusable pose templates with:
   - `handedness_mode`: unarmed, single_handed, two_handed, dual_wield
   - `prop_visibility_mode`: "presented" (fully visible, held away) or "carried_attached" (overlap allowed at attachment zones)
   - Placeholders (MAIN_HAND_PROP, OFF_HAND_PROP) for weapon injection

3. **Validation System**: Automatically checks pose compatibility with character weapons and warns about mismatches

4. **Prompt Composition**: Weapons are injected into pose templates at generation time, replacing placeholders with safe descriptive language

**Key Benefit**: Poses are written once generically, weapons are defined separately, and the system ensures compatibility while composing safe prompts.

---

## Critical Understanding

Modern image generation guardrails evaluate prompts in three layers:

1. **Content** - What objects are present (weapons, characters, poses)
2. **Context** - How those objects are described (engineering vs. aesthetic)
3. **Pattern** - Whether repeated attempts suggest bypass behavior

**All three layers must pass.** A single failure in any layer = rejection.

---

## Core Rules - Always Apply

**PASSIVE STATE LANGUAGE ONLY:**

The system uses **passive state descriptors** for weapon positioning, never active handling verbs.

**Forbidden Active Verbs (INSTANT FAIL):**
- holding (as verb: "character is holding"), aiming, pointing, firing, wielding
- gripping, grasping, clutching, brandishing
- carrying (as action: "character carrying weapon")
- drawing, raising (as action verbs), lifting, unsheathing
- resting on, posed with, displayed by hands

**Acceptable Passive State Language:**
- "held firmly" (state descriptor, not active verb)
- "positioned", "kept away", "oriented"
- "visible as silhouette element"
- "slung", "stowed", "sheathed", "holstered"
- "separated with clear negative space"
- Explicit negation: "not held in hands", "not gripped", "not supported by hands"

**Critical Distinction:**
- ❌ "character is holding the sword" (active verb)
- ✅ "sword held firmly, positioned away from torso" (passive state)
- ❌ "gripping the weapon tightly" (active handling)
- ✅ "weapon positioned for silhouette clarity" (passive placement)

**For Slung/Stowed Weapons:**
Always add explicit disclaimer:
- "weapon visible but not held in hands; hands free for pose action"
- "carried by [sling/strap/sheath]; not actively wielded"

**Keep hands empty when required:**
If pose is "unarmed", explicitly state:
- no objects in hands
- open negative space around fists/claws
- hands/fingers clearly visible and separated from body

---

## Instant-Fail Triggers

These patterns trigger immediate guardrail rejection. Learn them, avoid them completely.

### 1. Weapon Engineering Language

**The Problem:** Describing weapon structure or durability = engineering specification, not visual description.

**Poison Words (NEVER use with real weapons):**
- durable / durability
- fragile / fragility  
- spine thickness / wide spine / narrow spine
- reinforced / reinforcement
- structural / structure
- optimized / optimization
- performance / functional
- thick enough / thin profile (in structural context)

**Why this fails:** Guardrails interpret structural language + real weapon = "designing a functional weapon for real use."

**Safe Replacements:**

| ❌ Fails | ✅ Passes |
|---------|----------|
| wide spine, durable tip; avoid thin fragile profile | oversized ceremonial blade with bold silhouette |
| reinforced structural design | heroic stylized blade shape |
| optimized for durability | chunky exaggerated proportions |
| thick spine to prevent breakage | dramatic blade with strong visual presence |

**Rule:** Describe visual appearance and artistic style only. Never physical properties or structural requirements.

---

### 2. Weapon Interaction Must Be Passive State, Not Active Handling

**Critical Rule:** Weapons are described using **passive state language** that positions them in space without active handling verbs.

**Pose Library System Approach:**
The system uses **prop visibility modes** and **prop_state values**:

1. **Visibility Modes:**
   - **"presented"**: Fully visible with clear negative space (default)
   - **"carried_attached"**: Overlap allowed at attachment zones (slung weapons)

2. **Prop State Values (passive descriptors):**
   - "held firmly" - passive state descriptor
   - "positioned [orientation]" - spatial placement
   - "slung_side_visible" - carried by equipment, not hands
   - "set_aside_visible" - visible but not in use

3. **Explicit Disclaimers (added by system):**
   - "not held in hands"
   - "not gripped"
   - "not supported by hands"
   - "weapon visible but not held in hands; hands free for pose action"

**Safe Composition Pattern:**
```
[weapon name] ([description]) [passive state], [orientation]; [visual details]; 
not held in hands; not gripped; not supported by hands
```

**Example from actual system:**
```
double-barrel coach gun (Old West double-barrel shotgun) held firmly, angled low ready; 
chunky double barrels, exposed hammers, weathered wood stock; 
not held in hands; not gripped
```

**Enforcement:** Passive state language + explicit negation = safe

**Validation Layer:** System checks weapon/pose compatibility and warns about mismatches.

---

#### Explicitly Forbidden Phrases (Known Failure Triggers)

**Active Handling Verbs (INSTANT FAIL):**
- holding (as verb: "is holding", "are holding")
- gripping / gripped (as action)
- supporting / one hand supporting / other hand supporting
- carried in hand / carried in hands (as active carrying)
- presented with hands / presented with both hands visible
- hands on / both hands on / hands positioned on
- two-handed grip / one-handed grip (implies grasping action)

**Note:** "held firmly" as a STATE (not verb) is acceptable when followed by explicit negation ("not held in hands")

**SPECIFIC HIGH-RISK PATTERNS:**
- ❌ "one hand supporting the barrels" (firearm handling)
- ❌ "other hand supporting the barrel"
- ❌ "hands on grip"
- ❌ "weapon presented with both hands visible"
- ❌ "character is holding the weapon"
- ❌ "gripping the handle"

**Safe Alternatives:**
- ✅ "weapon held firmly, positioned away; not held in hands; not gripped"
- ✅ "weapon visible at the side; not actively wielded"
- ✅ "weapon positioned for silhouette clarity"

**Activation Verbs (INSTANT FAIL with weapons):**
- drawn / drawing (e.g., "Bowie knife drawn")
- unsheathed / unsheathing
- raising (as action: "character raising weapon")
- lifted / lifting
- brandished / brandishing

**Note:** "raised" as POSITION is acceptable: "weapon raised overhead as symbolic element"

**Combat Posture Phrases (FAIL when weapon is drawn/visible):**
- combat ready (with visible weapon)
- guard stance (with drawn weapon in view)
- ready position / ready stance (with weapon)

**Subtle Handling Implications (ALSO FAIL):**
- posed away from / posed (implies character is actively posing/handling the weapon)
- displayed / displaying (biases toward "held/brandished" in practice)
- resting across / resting on (implies weight-bearing = physical contact)
- port-arms / port arms (explicit military carry/handling position)
- carried in / carried on (any "carrying" language, even "on a strap")
- tucked / wedged / secured by hand (implies active placement)
- visible overhead (reads like "held overhead" without explicit "not held" disclaimer)

**Safe Alternatives:**
- ❌ "posed away from the chest" → ✅ "kept away from the chest"
- ❌ "displayed away from torso" → ✅ "clearly visible, kept away from torso"
- ❌ "visible horizontally overhead" → ✅ "visible overhead, not held in hands"
- ❌ "resting across shoulders" → ✅ "visible behind shoulders, not held"
- ❌ "port-arms display" → ✅ "visible at the side as symbolic element"
- ❌ "carried on a strap" → ✅ "slung at the side" (sling = passive equipment)
- ❌ "positioned low in hands" → ✅ "positioned low at the side"

**Core Insight:** If the phrase describes what the CHARACTER is doing TO the weapon (posing it, resting it, carrying it), it fails. Only describe where the weapon IS, as a passive element.

---

#### System Composition Pattern (How It Actually Works)

The system composes weapon descriptions using this safe pattern:

**Composition Formula:**
```
[weapon name] ([description]) [passive state], [orientation]; [visual details]; 
[explicit negation]
```

**Pattern 1 (Presented Weapons):**
```
double-barrel coach gun (Old West double-barrel shotgun) held firmly, angled low ready; 
chunky double barrels, exposed hammers, weathered wood stock; 
not held in hands; not gripped
```

**Pattern 2 (Slung Weapons):**
```
oversized katana (Mighty oversized katana): slung side visible; 
carried by sling; weapon visible but not held in hands; hands free for pose action; 
chunky stylized blade profile
```

**Pattern 3 (Ceremonial Display - External Prompts):**
```
ceremonial [weapon] visible as symbolic silhouette element, positioned away from torso; 
not actively wielded
```

**Key Components:**
1. **Weapon identity**: name + brief description in parentheses
2. **Passive state**: "held firmly", "positioned", "slung"
3. **Orientation**: spatial placement ("angled low", "overhead", "at side")
4. **Visual details**: appearance descriptors
5. **Explicit negation**: "not held in hands; not gripped; not supported by hands"

**Examples:**

| ❌ Fails | ✅ System Output |
|---------|----------|
| katana held in two-handed grip | katana (oversized katana) held firmly, vertical; not held in hands; not gripped by hands |
| character raising revolver high | revolver (six-shooter) positioned overhead; visible as symbolic element; not actively wielded |
| Bowie knife drawn and gripped | Bowie knife (large blade) held firmly, at side; not held in hands; hands free |
| one hand supporting the barrels | coach gun (double-barrel shotgun) positioned low; not held in hands; not supported by hands |
| both hands on weapon | weapon held firmly, positioned away from torso; not held in hands; not gripped |

**Core Principle:** Use passive state descriptors + explicit negation. The "held firmly" state + "not held in hands" negation creates a safe contradiction that signals display/positioning rather than active use.

---

### 3. Crouching + Armed + Attack Intent = INSTANT FAIL

**Hard Rule:** ANY combination of these three elements triggers immediate rejection:
1. Low/crouching/bent stance
2. Weapon actively in hands (not sheathed/stowed)
3. Attack/strike/aggressive language

**Why this fails:** Guardrails pattern-match this as "attack preparation" regardless of disclaimers.

**The Triple Threat Pattern:**
- "crouching" + "weapon held" + "preparing to strike" = BLOCKED
- "low stance" + "blade ready" + "sweeping motion" = BLOCKED
- "bent pose" + "armed" + "ready to attack" = BLOCKED

**Safe alternatives (remove at least ONE element):**
- ✅ Crouching unarmed (fists, claws, empty hands)
- ✅ Standing with weapon displayed (upright pose)
- ✅ Crouching with weapon stowed/sheathed on body
- ✅ Low stance with weapon in DISPLAY posture (no attack language)
- ✅ Dynamic standing pose with weapon presentation (no crouching)

**Key insight:** You cannot have all three. Pick two maximum:
- Armed + Standing + Display language ✅
- Crouching + Unarmed + Any language ✅
- Armed + Crouching + ONLY visual framing language ✅
- Armed + Any pose + Attack language ❌ NEVER

---

### 4. Attack Intent Language (Universal Ban with Weapons)

**NEVER combine these phrases with any weapon present:**
- preparing to strike / about to strike / ready to strike
- attack angle / strike angle / sweeping strike
- sweeping blow / overhead strike / downward strike
- combat technique / fighting stance / battle stance
- execution stance / killing blow
- ready to attack / poised to strike
- coiled to explode into motion
- aggressive forward stance (when armed)

**Safe substitutions (focus on display, not intent):**

| ❌ Fails | ✅ System Output |
|---------|----------|
| preparing to strike | weapon positioned for display; not actively wielded |
| sweeping strike motion | dynamic stance; weapon visible at side; not held in hands |
| combat ready stance | battle-ready presence; weapon held firmly, positioned away; not gripped |
| overhead attack | weapon positioned overhead; visible as symbolic element; not actively wielded |
| aggressive forward stance with blade | forward stance; blade held firmly, visible; not held in hands; not gripped |
| coiled to explode into motion | powerful coiled stance; weapon positioned away from torso |
| poised to strike | weapon held firmly, positioned for silhouette; not held in hands |

---

## Handedness Modes & Weapon Compatibility

The pose library system categorizes poses by **handedness_mode**:

- **unarmed**: No weapons in hands (fists, claws, empty hands)
- **single_handed**: One weapon in main hand, off hand empty or gesturing
- **two_handed**: Both hands on same weapon (rifles, two-handed swords, staffs)
- **dual_wield**: Different weapon in each hand (pistol + knife, sword + shield)

**Prop Class System:**
Weapons are classified by visual bulk and geometry:
- `none`: Empty hand
- `small`: Small items (coins, amulets, small religious symbols)
- `compact`: Compact weapons (pistols, short blades, small shields)
- `long`: Long weapons (rifles, swords, spears, staves)
- `flexible`: Flexible items (whips, chains, ropes, lasso)
- `shield_plane`: Shield objects (round/rectangular shields)
- `two_hand_frame`: Two-handed weapons requiring both hands
- `bulky`: Large bulky items

**Automatic Validation:**
The system checks:
- Does character's weapon handedness match pose requirements?
- Does weapon prop_class fit pose expectations?
- Are required weapons missing or extra weapons present?

Validation warnings guide users to fix compatibility issues before generation.

---

## Safe Action Pose Language

When describing dynamic poses with weapons, focus exclusively on:

### Visual Framing (System Composition Approach)

**Pose Library Approach:**
Poses use placeholders (MAIN_HAND_PROP, OFF_HAND_PROP) that get replaced at generation time.

**Pose Template (in library):**
```
"pose_prompt": "Protective stance: feet wide; MAIN_HAND_PROP held low and angled 
outward from body; OFF_HAND_PROP raised at chest level; clear negative space; 
not held in hands; not gripped; not supported by hands"
```

**After Weapon Injection (actual output):**
```
Protective stance: feet wide; double-barrel coach gun (Old West shotgun) held firmly, 
angled low ready; chunky barrels, exposed hammers held low and angled outward from body; 
silver crucifix (Large silver crucifix) positioned at chest, visible chain raised at 
chest level; clear negative space; not held in hands; not gripped; not supported by hands
```

**Pattern Breakdown:**
1. Pose template has placeholders and explicit negation
2. System injects weapon: `[name] ([description]) [passive state]`
3. Pose orientation language preserved
4. Explicit negation remains at end
5. Result: passive state + negation = safe

**Generated Safe Language Examples:**
- "weapon positioned away from body; not actively wielded"
- "blade held firmly, visible with clear negative space; not held in hands"
- "ceremonial weapon visible to the side as symbolic element; not gripped"
- "oversized weapon positioned overhead; not supported by hands; hands free"
- "weapon held firmly, kept away from torso; not held in hands; not gripped"

### Static Display Posture (Always Safe)
- "ceremonial weapon display"
- "symbolic weapon presentation"
- "weapon as dramatic silhouette element"
- "heroic statue pose"
- "weapon positioned for visual composition"

### Body Position (Safe - describe body/arms WITHOUT linking to weapon)
- "arms extended for dramatic composition" (NOT "arms extended holding weapon")
- "forward step with dynamic pose" (NOT "forward step with weapon")
- "wide stance with dramatic presence" (NOT "wide stance gripping weapon")
- "powerful coiled stance" (NOT "coiled to strike")

### What You CAN Say About Weapons:

**Passive State Descriptors:**
- "held firmly" (as state, with negation)
- "positioned", "oriented", "angled"
- "kept away from", "separated from"

**Spatial Position:**
- "overhead", "to the side", "at hip level", "away from torso"
- "forward offset", "side out", "low outside"

**Visual Description:**
- "dramatic", "bold", "exaggerated", "stylized", "ceremonial", "oversized"
- "chunky barrels", "weathered stock", "ornate details"

**Symbolic Purpose:**
- "symbolic element", "silhouette element", "visual element"
- "fully visible", "clearly visible", "strong silhouette"

**Explicit Negation (CRITICAL):**
- "not held in hands"
- "not gripped"
- "not supported by hands"
- "not actively wielded"
- "weapon visible but not held in hands; hands free for pose action"

### What You CANNOT Say About Weapons:

**Active Handling Verbs:**
- "gripping", "grasping", "clutching"
- "holding" (as action: "character is holding")
- "hands on weapon", "both hands visible on weapon"
- "weapon presented with both hands"

**Combat Intent:**
- "ready to strike", "preparing to hit", "poised to attack"
- "attack position", "striking motion"
- "battle technique", "combat technique"

**Mechanical Function:**
- "angled for strike", "positioned to hit"
- "aimed at target", "targeting"

**WITHOUT Explicit Negation:**
- "held firmly" alone ❌ → "held firmly... not held in hands" ✅
- "positioned overhead" alone ⚠️ → "positioned overhead; not actively wielded" ✅

**Core Principle:** Passive state + explicit negation = safe. Active verbs = instant fail.

**Enforcement Rule:** Every weapon reference must include explicit negation disclaimer.

---

### 6. Manufacturing & Conversion Language

**Absolute ban in image prompts:**
- image-to-3D / AI-to-3D
- print-safe / print-ready / printable
- STL / fabrication / manufacturing
- wall thickness / structural reinforcement
- durability for printing / conversion-ready

**Safe alternatives:**
- clean silhouette / strong silhouette
- tabletop miniature aesthetic
- crisp sculpted details
- high-contrast sculptural lighting
- stylized miniature sculpture

---

### 7. Numeric Scale References

**Avoid:**
- 40mm scale / 28mm scale
- measurements in cm / inches / feet
- percentage ratios (20% larger, 30% oversized)
- degree angles (45-degree angle, 90-degree turn)

**Use instead:**
- miniature scale / tabletop scale
- heroic miniature proportions
- oversized / exaggerated / larger than life
- slight twist / dramatic angle

---

### 8. Escalation State (Anti-Bypass Detection)

**CRITICAL:** After 2-3 failed attempts with similar content, the system enters **escalation mode**.

**What happens in escalation:**
- Thresholds tighten automatically
- Prompts that "should work" now fail immediately
- System infers: "User is trying to bypass restrictions"
- Every additional attempt makes it worse

**Signs you're in escalation:**
- Same character/weapon keeps getting blocked
- Small changes don't help
- Even "safe" wording now fails

**How to escape escalation (in order of effectiveness):**
1. **Switch to completely different character** - resets context entirely
2. **Change weapon type** - sword → staff, gun → shield, blade → ceremonial object
3. **Try unarmed poses temporarily** - breaks the weapon pattern
4. **Strip ALL poison words** - even borderline terms now fail
5. **Simplify drastically** - remove every non-essential descriptor
6. **Wait 15-30 minutes** - temporal spacing may help reset

**Key insight:** In escalation mode, refinement doesn't work. Only reset works.

---

## Visual Clarity Rules (Supporting Constraints)

These improve output quality and reduce occlusion issues, but they don't override the instant-fail triggers above.

### 1. Anti-Occlusion

Weapons and limbs must:
- Be fully visible
- Maintain clear negative space from torso and face
- Avoid crossing the central silhouette

### 2. Action Pose Guidance

Action poses should be:
- Sculptural and illustrative
- Readable from a single ¾ view
- Suggestive of motion, not instructional

### 3. No Environmental Geometry

Do not include:
- rocks / terrain
- debris / platforms
- scenic elements

Character exists in isolation unless explicitly requested.

### 4. Value Contrast

Use strong value contrast to separate major forms.
Lighting should emphasize depth and silhouette clarity.
Avoid flat mid-grey renders.

### 5. Constraint Consolidation

Avoid stacking more than four explicit "NO ___" clauses.

**Prefer:**
> "clean static miniature aesthetic, no visual effects"

Over:
> "no smoke, no flames, no particles, no motion blur, no glowing effects, no sparks"

---

## Safe Style Anchors (Risk Reducers)

These terms help signal "illustration, not instruction" but they **do not override** the instant-fail triggers.

Use liberally:
- stylized / illustrative
- tabletop miniature aesthetic
- heroic statue / sculptural
- NOT photoreal
- cinematic / dramatic
- ceremonial / ornamental

---

## Conceptual Visualization Language (General Guidance)

Prompts must read as conceptual, illustrative art direction — never as real-world documentation or evidence.

- Avoid real-world evidence framing: do not claim or imply the image is a photograph, proof, or documentation.
- Avoid manufactured-object framing: do not reference existing brands, product models, or depict an existing manufactured item.
- Prefer conceptual phrasing: conceptual visualization, illustrative rendering, stylized design intent, imagined character.
- Keep scope artistic: describe visual composition, silhouette, value, and style — not physical properties, specs, or functionality.

Examples:
- ❌ "photograph of a production miniature" → ✅ "stylized conceptual miniature visualization"
- ❌ "depiction of [brand] katana model" → ✅ "oversized ceremonial katana with bold stylized blade"
- ❌ "evidence image of a real artifact" → ✅ "illustrative render of a fictional ceremonial object"

Core Principle: Maintain a clear separation between artistic illustration and real-world manufactured products or photographic evidence.

## Quick Reference Examples

### Weapon Description

| Context | ❌ Fails | ✅ Passes |
|---------|---------|----------|
| Katana | wide spine, durable tip, avoid fragile thin profile | oversized ceremonial katana with chunky stylized blade |
| Axe | reinforced head structure for durability | heroic exaggerated axe with bold blade shape |
| Gun | structurally optimized barrel | dramatic oversized revolver silhouette |

### Weapon Presentation

| Context | ❌ Fails | ✅ Passes |
|---------|---------|----------|
| Two hands | katana held in two-handed grip | katana presented with both hands visible |
| Overhead | blade wielded overhead in ready stance | blade raised dramatically with arms visible |
| To side | weapon gripped and extended to side | weapon displayed away from body |

### Pose Intent

| Context | ❌ Fails | ✅ Passes |
|---------|---------|----------|
| Action | preparing to strike with overhead blow | heroic display stance with weapon raised |
| Dynamic | sweeping strike motion with blade | dynamic weapon presentation |
| Ready | combat-ready stance with grip tightened | battle-ready presence with weapon visible |

---

## Final Rule (Non-Negotiable)

> **If the prompt sounds like instructions for a machine rather than guidance for an artist, rewrite it.**

Prompts should read like art direction, not engineering specifications.
