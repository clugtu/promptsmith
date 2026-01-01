# Safe Image Prompt Guide
## Guardrail-Safe Prompting for Character Illustration
### Updated: 2025-12-31

---

## Purpose

This guide defines **safe prompt language** for generating stylized character illustrations that look like tabletop miniatures.

**Scope:** Image generation prompts only.

**Out of Scope:** Image-to-3D conversion, 3D printing, STL generation, manufacturing constraints.

---

## Critical Understanding

Modern image generation guardrails evaluate prompts in three layers:

1. **Content** - What objects are present (weapons, characters, poses)
2. **Context** - How those objects are described (engineering vs. aesthetic)
3. **Pattern** - Whether repeated attempts suggest bypass behavior

**All three layers must pass.** A single failure in any layer = rejection.

---

## Core Rules - Always Apply

**NO ACTIVE HANDLING / NO GRIP LANGUAGE:**

Avoid verbs implying the character is holding/operating/aiming a weapon or prop.

**Do NOT use:**
- holding, aiming, pointing, firing, wielding, gripping
- carrying, resting on shoulders, across chest, port-arms, posed
- brandishing, drawing, raising, lifted, unsheathed

**Use passive visibility language instead:**
- visible as a silhouette element
- stowed, slung, sheathed, holstered
- kept away from torso, not held in hands
- separated with clear negative space

**Keep hands empty when required:**
If pose is "unarmed/combat-ready," explicitly say:
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

### 2. Weapon Interaction Must Be Symbolic, Not Handled

**Critical Rule:** If a real-world weapon is present (firearm, blade, spear, axe, etc.), the prompt must NOT describe any hand–weapon interaction or operational handling.

**Weapons may ONLY be described as:**
- Symbolic / ceremonial silhouette elements
- Visible and positioned away from the torso
- Oriented for silhouette clarity

**Enforcement:** `weapon_present == true` → forbid ALL handling language

---

#### Explicitly Forbidden Phrases (Known Failure Triggers)

**Handling Verbs (INSTANT FAIL):**
- held / holding
- gripped / gripping
- supporting / one hand supporting / other hand supporting
- carried in hand / carried in hands
- presented with hands / presented with both hands visible
- hands on / both hands on / hands positioned on
- two-handed / one-handed (in handling context)

**SPECIFIC HIGH-RISK PATTERNS:**
- ❌ "one hand supporting the barrels" (firearm handling)
- ❌ "other hand supporting the barrel"
- ❌ "hands on grip"
- ❌ "weapon presented with both hands visible"

**Activation Verbs (INSTANT FAIL with weapons):**
- drawn / drawing (e.g., "Bowie knife drawn")
- unsheathed / unsheathing
- raised / raising (e.g., "revolver raised high", "katana raised overhead", "katana raised vertically")
- lifted / lifting
- brandished / brandishing

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

#### Required Replacement Pattern

When a weapon is present, use ONLY these generic safe patterns:

**Pattern 1 (Preferred):**
```
ceremonial [weapon] visible as a symbolic silhouette element, positioned away from the torso
```

**Pattern 2:**
```
[weapon] oriented for silhouette clarity, not actively wielded
```

**Pattern 3:**
```
[weapon] visible to the side / overhead as a symbolic element, kept clear of the torso outline
```

**Examples:**

| ❌ Fails | ✅ Passes |
|---------|----------|
| katana held in two-handed grip | ceremonial katana visible as symbolic silhouette element, positioned to the side |
| revolver raised high in victorious salute | ceremonial revolver visible overhead as symbolic element, not actively wielded |
| Bowie knife drawn and held away from torso | ceremonial Bowie knife visible to the side as symbolic element, positioned away from torso |
| one hand supporting the barrels | ceremonial coach gun visible as silhouette element, oriented for clarity |
| katana raised vertically with blade pointing skyward | ceremonial katana oriented vertically as dramatic silhouette element, positioned away from torso |
| weapon presented with both hands visible | oversized ceremonial weapon visible to the side, not actively wielded |

**Core Principle:** Describe weapon position and symbolic purpose ONLY. Never describe how hands/arms interact with the weapon.

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

| ❌ Fails | ✅ Passes |
|---------|----------|
| preparing to strike | weapon positioned for display |
| sweeping strike motion | dynamic weapon presentation |
| combat ready stance | battle-ready presence / heroic stance |
| overhead attack | weapon raised dramatically overhead |
| aggressive forward stance with blade | forward stance with blade visible |
| coiled to explode into motion | powerful coiled stance |
| poised to strike | weapon framed for silhouette |

---

## Safe Action Pose Language

When describing dynamic poses with weapons, focus exclusively on:

### Visual Framing (Always Safe - NO hand-weapon references)
- "weapon positioned away from body"
- "blade visible with clear negative space"
- "ceremonial weapon displayed to the side as symbolic silhouette element"
- "oversized weapon visible to the side, not actively wielded"
- "weapon positioned away from body as symbolic visual element"

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
- Where they are: "overhead", "to the side", "across body", "away from torso"
- How they look: "dramatic", "bold", "exaggerated", "stylized", "ceremonial", "oversized"
- Visual purpose: "symbolic element", "silhouette element", "visual element"
- Visibility: "fully visible", "clearly visible", "strong silhouette"
- NOT actively used: "not actively wielded", "ceremonial display", "symbolic"

### What You CANNOT Say About Weapons:
- Hand-weapon relationships: "hands on weapon", "both hands visible on weapon", "weapon presented with hands"
- What they're about to do: "ready to strike", "preparing to hit"
- How they're being used: "in grip", "attack position", "wielding"
- Combat context: "battle technique", "striking motion"
- Mechanical function: "angled for strike", "positioned to hit"

**Core Principle:** Describe weapon position and body position SEPARATELY. Never link hands/arms to weapon interaction.

**Enforcement Rule:** `weapon_present == true` → forbid any hand–weapon relationship language

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
