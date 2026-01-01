# Pose Guidance for Image-to-3D Conversion (Meshy.ai)
## Optimized for Miniatures, Action Poses, and Equipment
### Updated: 2025-12-30 - Surgical Improvements Applied

## Critical Rules (Must-Not-Break Constraints)

### 1. **Anti-Occlusion Weapon Rule (CRITICAL)**
Any weapon must be fully visible from grip to tip, not crossing or overlapping the torso, limbs, or silhouette of the body. Weapon shaft and head must be unobstructed, with clear negative space between weapon and figure. No motion blur, no depth-of-field blur, no foreshortening that hides length.

**Why this matters:** Every recent failure with weapon poses has been weapon occlusion, not anatomy issues. This rule must be universal and explicitly enforced.

### 2. **Action Pose Constraint**
Attack poses must be readable from a single 3/4 camera angle without limb or weapon overlap. Weapon thrusts and swings must project away from the torso at 20–30° with visible negative space.

**Why this matters:** Dynamic poses are the hardest and most failure-prone. This constraint prevents drift and ensures consistent quality.

### 3. **No Environmental Geometry (Hard Ban)**
Do not add rocks, terrain, debris, perches, platforms, or scenic elements unless explicitly requested. Character must exist in isolation.

**Why this matters:** Models keep inventing rocks and terrain even when "no background" is specified. This explicit ban prevents environmental geometry from sneaking in.

### 4. **Value Contrast for Depth (CRITICAL for Printing)**
Use deliberate value contrast to define depth. Deep recesses must render significantly darker than primary planes; major forms must separate clearly in value. Avoid flat mid-grey renders. Lighting and shading should simulate zenithal priming for resin readability.

**Why this matters:** "Color should signify depth" - value separation is essential for print readability but was never codified until now.

### 5. **Conditional Base Contact**
- **If a base is requested:** at least one point of contact must exist
- **If "no base" or "no ground plane" is specified:** the figure must be posed as a free-standing sculpt with all weight-bearing limbs visible and no environmental geometry added

**Why this matters:** The contradiction between "base contact required" and "no base/no ground plane" was causing models to invent rocks. This resolves the ambiguity.

### 6. **Fur Hierarchy (For Any Furred Creatures)**
Prioritize primary silhouette clumps > secondary mass breaks > minimal tertiary texture. If detail competes with silhouette readability at 40mm, remove it.

**Why this matters:** Prevents regression to photorealistic fur rendering that doesn't print well at miniature scale.

## Understanding Occlusion Limitations

Image-to-3D software like Meshy.ai uses AI models trained on visible features to reconstruct 3D geometry. When parts of the subject are hidden (occluded), the model must "hallucinate" or infer what's behind, often resulting in artifacts, missing geometry, or incorrect topology. This is especially critical for miniatures in action poses with weapons and equipment, where dynamic positioning creates more occlusion challenges.

## Core Principles for Optimal Poses

### 1. **Maximize Visible Surface Area**
- Show as much of the subject as possible in a single view
- Avoid poses where limbs cross in front of the body
- Keep arms away from torso to prevent occlusion
- Spread fingers to ensure each digit is visible

### 2. **Action Pose Principles**
- **Dynamic poses are preferred** for miniatures that will be used as-is
- Action poses should still follow occlusion-avoidance principles
- Think in terms of "readable silhouette" - the pose should be clear from multiple angles

#### Key Guidelines for Action Poses:
- **Limb Separation**: Even in dynamic poses, keep limbs away from body core
- **Asymmetry**: Use asymmetrical poses for more dynamic appearance
- **Gesture Lines**: Follow natural action lines (sword swings, running strides)
- **Weight Distribution**: Show clear weight shift for realistic action
- **Camera Angle**: Choose angle that shows maximum action while minimizing occlusion

### 3. **Optimal Camera Angles for Action Poses**
- **¾ View (30-45° angle)**: Often best for action poses
  - Shows depth and dimensionality
  - Reveals both front and side details
  - Creates more dynamic composition
  
- **Avoid Pure Profile (90°)**: Hides half the character
- **Slight Elevation**: Camera 5-15° above eye level shows more of the miniature base
- **Consider Final Display Angle**: Match camera to how miniature will be viewed on table

### 4. **Avoid Self-Occlusion**

#### Critical Areas to Keep Visible:
- **Hands**: Don't hide behind body, in pockets, or crossed
- **Feet**: Both feet should be visible and separated
- **Face**: Keep hair away from face, no hands near face
- **Joints**: Elbows, knees, shoulders should be clearly visible
- **Fingers/Toes**: Spread them to show individual digits

#### Problem Poses to Avoid:
- ❌ Weapon directly in front of face or chest (blocks torso)
- ❌ Both arms close together in front of body
- ❌ Shield completely covering one side of body
- ❌ Crouching with legs tucked under (creates complex occlusions)
- ❌ Hair or cape covering shoulders and back
- ❌ Equipment straps crossing in front of important details
- ❌ Hands gripping weapons so tight that fingers are hidden

#### Good Action Pose Patterns:
- ✅ **Attacking Stance**: Weapon arm extended, off-hand visible for balance
- ✅ **Running/Charging**: Front leg forward, back leg extended and visible
- ✅ **Defensive Pose**: Shield to side, weapon visible, body stance clear
- ✅ **Spellcasting**: Arms in gesture with fingers spread, energy effect away from body
- ✅ **Aiming**: Weapon angled to show both weapon and shooter's form

### 5. **Weapons and Equipment Handling**

#### Weapon Positioning:
- **Swords/Melee**: Blade away from body, grip clearly visible
- **Guns/Ranged**: Stock against shoulder but not covering chest
- **Two-Handed Weapons**: Stagger hand positions, show both grips
- **Dual Wielding**: Weapons at different heights/angles, not crossed
- **Polearms/Staves**: Angle to avoid blocking body, show full length

#### Equipment Best Practices:
- **Shields**: Hold to side (30-45° from center), show arm and body behind
- **Backpacks/Quivers**: Visible from ¾ rear angle, not completely covering back
- **Capes/Cloaks**: Flow away from body, not wrapped around
- **Belts/Straps**: Don't bunch up, keep flat against form
- **Accessories**: Hang naturally, separated from body mass

#### Depth and Layering:
- Weapon in foreground, character mid-ground creates depth
- Stagger equipment at different Z-depths (sword, shield, cape at different distances)
- Leave 4-6 inches of air between weapon and torso when possible
- Show negative space between equipment and body

## Specific Recommendations for Meshy.ai

### Image Quality Guidelines
- **Resolution**: Minimum 1024x1024, preferably 2048x2048 or higher
- **Lighting**: Even, diffused lighting from front
- **Background**: Solid, contrasting color (prefer white or light gray)
- **Focus**: Sharp focus on entire subject, avoid depth of field blur

### Composition Best Practices
- Subject should occupy 60-80% of frame height
- Leave some margin around the subject (10-15%)
- Avoid cropping any visible body parts at edges
- Keep the ground/base clearly visible

### Character-Specific Tips

#### Miniature Characters in Combat
- **Sword & Board**: Sword arm extended in strike, shield at 45° angle showing body
- **Archer**: Draw arm back, bow arm extended, torso twisted to show both sides
- **Mage**: One hand forward casting, other hand visible at side or raised
- **Dual Wielder**: Weapons at high/low split, one forward one back
- **Heavy Weapon**: Two-handed grip with hands separated, weapon to side not center
- **Mounted**: Rider clearly separated from mount, weapon angled out

#### Creatures/Animals
- Quadrupeds: Side view with all four legs visible
- Show underside details if important (belly, paws)
- Tails should curve away from body, not wrap around

#### Objects & Props
- Show all functional parts (handles, openings, mechanisms)
- Rotate to most informative angle (¾ view often best)
- If asymmetric, consider multiple reference angles

### Common Meshy.ai Failure Points for Action Miniatures

**These are the primary failure modes that the Critical Rules (above) were designed to prevent:**

1. **Weapon Occlusion (MOST COMMON)**
   - Weapon directly in front of chest → missing torso detail
   - Sword blade along arm → merged weapon-arm geometry
   - **Solution:** Anti-occlusion weapon rule - weapons must project 20-30° away from body parts with clear negative space

2. **Environmental Geometry Invention**
   - Model invents rocks/terrain even when "no background" specified
   - "Perched" language triggers physical rock geometry
   - **Solution:** Hard ban on environmental geometry; conditional base contact rule

3. **Flat Mid-Grey Renders**
   - Lack of value contrast makes details unreadable at print scale
   - Recesses and primary planes have same value
   - **Solution:** Value hierarchy rule - deliberate contrast simulating zenithal priming

4. **Shield Over-Coverage**
   - Shield flat against body → entire side undefined
   - Shield rim touching shoulder/head → merged geometry
   - **Solution:** Action pose constraint - shields must show clear gap and body visibility

5. **Hand-Weapon Grip Issues**
   - Tight grip hiding fingers → malformed hands
   - Both hands overlapping on handle → fused hand geometry
   - **Solution:** Weapon visibility rule - grip must be clearly visible; stagger hands

6. **Cape/Cloth Physics**
   - Cape draped over shoulders → lost shoulder definition
   - Cloth wrapping legs → incomplete leg geometry
   - **Solution:** No environmental geometry rule applies to cloth - must flow away from body

7. **Dynamic Leg Positioning**
   - Crossed legs in action pose → merged/missing geometry
   - One leg completely behind other → single-leg appearance
   - **Solution:** Action pose constraint - both legs visible from chosen 3/4 angle

8. **Equipment Strap Chaos**
   - Multiple straps crossing chest → confused surface detail
   - Straps too tight to body → lost as separate geometry
   - **Solution:** Texture guidance - straps must have visible separation and crisp edges

9. **Photorealistic Fur Regression**
   - Ultra-fine individual hairs instead of sculpted clumps
   - Micro-fuzz and strand-level detail that doesn't print
   - **Solution:** Fur hierarchy rule - primary silhouette clumps > secondary breaks > minimal tertiary

## Multi-View Strategies

While Meshy.ai can work from single images, providing additional reference views dramatically improves results:

### Recommended View Set
1. **Primary**: Front view (A-pose or T-pose)
2. **Secondary**: Side profile (90° rotation)
3. **Tertiary**: Back view (180° rotation)
4. **Optional**: ¾ views for complex details

### Multi-View Rules
- Maintain exact same pose across all views
- Use turntable or rotate camera, not subject
- Keep lighting consistent across views
- Same distance from subject in all views

## Post-Generation Considerations

Even with optimal poses, expect to:
- Clean up minor artifacts in 3D software
- Refine occluded areas (armpits, inner thighs, etc.)
- Add or correct topology in problem zones
- Retopologize if using for animation

## Quick Checklist for Action Miniatures

Before submitting to Meshy.ai, verify:
- [ ] **Weapon anti-occlusion:** Weapons fully visible grip-to-tip with clear negative space (CRITICAL)
- [ ] **Action pose constraint:** Weapons project 20-30° away from torso with visible negative space
- [ ] **No environmental geometry:** NO rocks, terrain, debris, or platforms added (hard ban)
- [ ] **Value contrast:** Deep recesses darker than primary planes; zenithal-like readability
- [ ] **Base handling:** If "no base" specified, figure is free-standing with no ground plane invented
- [ ] Primary limbs clearly separated from torso
- [ ] Face visible (not blocked by weapons, hair, or equipment)
- [ ] Both hands visible with fingers distinguishable
- [ ] Both legs identifiable in the pose
- [ ] Shield/defensive equipment shows body behind it
- [ ] ¾ view angle captures depth and action
- [ ] High resolution (2K+) with even lighting
- [ ] Clean background with good contrast
- [ ] Action pose is "readable" - clear what character is doing
- [ ] Equipment straps/accessories don't cross critical details
- [ ] Negative space visible between equipment and body
- [ ] Weapon grips show hand position clearly
- [ ] Fur/hair rendered as sculpted clumps (if applicable), not photorealistic strands

## Advanced Tips

### For Miniature Production
- **Action Line**: Every pose should have a clear gesture/action line that flows through the figure
- **Dynamic Balance**: Even extreme poses should feel balanced, with weight properly distributed
- **Storytelling**: Pose should suggest what just happened and what's about to happen
- **Scale Considerations**: Details that read well at miniature scale (28mm, 32mm, etc.)
- **Base Integration**: Consider how pose works with intended base (flat, rubble, elevated)

### Multi-Character Scenes
- Generate each character separately, combine in 3D software
- Avoid occlusion between characters in source images
- Match scale and lighting between characters for consistency

### For Product/Object Scanning
- Show all openings, cavities, and internal structures
- Provide scale reference (ruler, coin) in frame
- Multiple angles more critical than for characters

### Lighting Setup
- 3-point lighting prevents shadows that look like occlusion
- Avoid harsh shadows that confuse edge detection
- Rim lighting helps separate subject from background

---

**Remember**: The goal is to give the AI maximum information about the 3D structure. Every hidden surface is a guess the AI must make. Clear, unobstructed poses dramatically improve output quality and reduce post-processing time.
