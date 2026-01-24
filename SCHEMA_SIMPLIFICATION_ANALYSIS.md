# JSON Schema Simplification Analysis

## Executive Summary

After analyzing the character JSON schema, golden outputs, and prompt builder, I've identified several opportunities to simplify the schema by consolidating redundant sections. The schema has accumulated complexity as features were added, and some sections serve overlapping purposes.

## Current Schema Sections (Per Character)

### Top-Level Character Fields:
1. **`description`** - Short character description
2. **`visual_notes`** - Visual details and appearance notes
3. **`character_base`** - Main character description used as base prompt
4. **`proportions`** - Body proportions and build description

### Pose-Level Fields:
5. **`character_override`** - Character-specific additions to library pose
6. **`prompt`** - Inline full pose prompt (alternative to pose_library_ref)

### Output Sections:
The prompt builder generates these sections in the final output:
- ASSET_NAME
- VISUAL (from `visual_notes`)
- CHARACTER (from `character_base` + demographics)
- PROPS (from `equipment`)
- POSE (from pose library or `prompt`)
- THEME
- PROPORTIONS (from `proportions`)
- STYLE
- [Various render rules sections]

## Analysis: Overlapping/Redundant Sections

### Issue 1: `description` vs `character_base`

**Problem:** Both fields describe the character, creating confusion about which to use.

**Current Usage:**
- `description`: "Skilled explorer and marksman who ventures into dangerous ruins..."
- `character_base`: "Skilled explorer and marksman who ventures into dangerous ruins in search of pre-Fall technology and dimensional artifacts. Confident but wary survivor who knows the Citadel's depths hide both treasure and terrible danger."

**Impact:** The `description` field is NOT used in the final prompt output. Only `character_base` appears in the CHARACTER section.

**Recommendation:** ✅ **ELIMINATE `description` field** - It's unused metadata. All character description should go in `character_base`.

**Migration:** Simply remove `description` from all character definitions. No output changes.

---

### Issue 2: `visual_notes` in Wrong Position

**Problem:** `visual_notes` creates a separate VISUAL section that appears BEFORE the CHARACTER section in output, but contains information that could logically be part of character_base.

**Current Output:**
```
VISUAL:
Masculine presentation; sturdy build; readable silhouette. Medium brown skin...

CHARACTER:
Skilled explorer and marksman who ventures into dangerous ruins...
```

**Analysis:** 
- The VISUAL section contains appearance details
- The CHARACTER section contains role/personality
- These are artificially separated but could be combined

**However:** Looking at actual usage in player_denizen_standees.json, `visual_notes` contains very detailed appearance specifications that are intentionally kept separate for reference sheet generation and character design clarity.

**Recommendation:** ⚠️ **KEEP SEPARATE** - The separation is intentional for:
1. Character reference sheets (artists need visual specs separate from backstory)
2. Pose reuse across multiple visual variants
3. Clear design documentation

---

### Issue 3: `character_base` vs `character_override`

**Problem:** Similar names, different scopes, easy to confuse.

**Current Usage:**
- `character_base`: Top-level character description (shared across all poses)
- `character_override`: Pose-specific additive details

**Analysis:** These serve different purposes but the naming is confusing. One is "base" (foundation), the other is "override" (modification), but both are additive in the prompt building.

**Recommendation:** ⚠️ **RENAME for clarity**:
- Keep `character_base` as-is
- Rename `character_override` → `pose_character_details` or `pose_specific_notes`

This makes it clearer that it's pose-specific additions, not an override.

---

### Issue 4: Pose `prompt` vs `pose_library_ref` + `character_override`

**Problem:** Two completely different approaches to defining poses:
1. Inline: `"prompt": "full pose description here"`
2. Library: `"pose_library_ref": "stance_name"` + `"character_override": "character-specific details"`

**Analysis:** This is intentional flexibility, not redundancy. Different use cases:
- Inline `prompt`: For unique one-off poses (standees with front/back views)
- Library ref: For reusable pose templates (garou pack with standardized stances)

**Recommendation:** ✅ **KEEP BOTH** - Different tools for different needs. Well-documented in schema.

---

### Issue 5: Multiple Demographic Fields

**Problem:** Character demographics are split across multiple places:
- `tags.gender`
- `tags.age`
- Embedded in `visual_notes` ("Masculine presentation")
- Embedded in `character_base` ("adult female")

**Current Behavior:** The prompt builder:
1. Reads `tags.gender` and `tags.age`
2. Appends them to CHARACTER section: ", adult female"
3. Checks if gender words already exist in `character_base` to avoid duplication

**Analysis:** 
- `tags` are used for programmatic access
- Visual/base descriptions contain natural language
- The prompt builder deduplicates automatically

**Recommendation:** ✅ **KEEP AS-IS** - The tags provide structured data, while natural language provides context. The deduplication logic handles overlaps.

---

## Concrete Simplification Proposals

### Proposal 1: Remove unused `description` field ✅ HIGH IMPACT

**Change:**
```json
// BEFORE
{
  "id": 1,
  "name": "character_name",
  "description": "Short description here",  // ❌ Remove this
  "character_base": "Detailed character description..."
}

// AFTER
{
  "id": 1,
  "name": "character_name",
  "character_base": "Detailed character description..."
}
```

**Impact:**
- ✅ Zero output changes (field is not used)
- ✅ Simpler schema
- ✅ No migration complexity
- ✅ Clearer which field to use

**Effort:** Low - just remove field from schema and existing JSON files

---

### Proposal 2: Rename `character_override` → `pose_details` ⚠️ MEDIUM IMPACT

**Change:**
```json
// BEFORE
{
  "pose_library_ref": "stance",
  "character_override": "character-specific details"
}

// AFTER
{
  "pose_library_ref": "stance",
  "pose_details": "character-specific details"
}
```

**Impact:**
- ✅ Clearer naming
- ⚠️ Requires updating all JSON files using this field
- ⚠️ Requires updating code that reads this field
- ✅ Zero output changes (just internal field rename)

**Effort:** Medium - need to update:
1. Schema definition
2. All character JSON files
3. `character_resolver.py` or wherever this is read
4. Documentation

---

### Proposal 3: Consolidate visual + character_base (REJECTED)

**Considered Change:**
```json
// Combine visual_notes into character_base
{
  "character_base": "Visual details first. Then character personality and role."
}
```

**Decision:** ❌ **DO NOT DO THIS**

**Reasons:**
1. Visual notes are used for reference sheets and art direction
2. Separation allows reusing the same character description with different visual presentations
3. The VISUAL section in output serves a clear purpose
4. Artists expect visual specs separate from character backstory

---

## Actual Complexity Source

After analyzing the schema and outputs, the **real complexity** isn't in redundant character fields—it's in the **proliferation of render rule sections**:

### Current Render Sections in Output:
1. BACKGROUND TRANSPARENCY (CRITICAL)
2. SILHOUETTE LOCK (CRITICAL)
3. HAND & GRIP MIRRORING (CRITICAL)
4. SUBREFINEMENT PAIRING (CRITICAL)
5. RENDER SCOPE (CRITICAL)
6. WEAPON CONSTRAINT (CRITICAL)
7. WEAPON ORIENTATION & CAMERA CONSISTENCY (CRITICAL)
8. CAMERA DISCIPLINE (CRITICAL)
9. MATERIAL & APPEARANCE
10. 3D-SAFE GEOMETRY
11. FACE (3D-SAFE)
12. POSE CLARITY
13. FRAMING
14. RENDERING

**These 14 sections** make up the bulk of the prompt! Each is labeled (CRITICAL) or contains specific technical requirements.

### Observation:
Many of these sections could potentially be consolidated:
- WEAPON CONSTRAINT + WEAPON ORIENTATION + CAMERA DISCIPLINE → **WEAPON RULES**
- SILHOUETTE LOCK + HAND & GRIP MIRRORING + SUBREFINEMENT PAIRING → **SILHOUETTE RULES**
- MATERIAL & APPEARANCE + RENDERING + FACE → **MINIATURE RENDERING**
- 3D-SAFE GEOMETRY + POSE CLARITY → **3D GEOMETRY RULES**

**But:** These sections were added incrementally to solve specific AI generation problems. Each addresses a different failure mode.

---

## Recommendations Summary

### ✅ Implement Now (Low Risk):
1. **Remove `description` field** - Unused, creates confusion, zero output impact
   - Update schema
   - Remove from all character JSON files
   - Update documentation

### ⚠️ Consider (Medium Effort):
2. **Rename `character_override` → `pose_details`** - Clearer, but requires updates across codebase
   - Wait for a larger refactor cycle
   - Can be done alongside other changes

### ❌ Do Not Do:
3. **Do NOT combine visual_notes with character_base** - Separation is intentional and valuable
4. **Do NOT consolidate render rule sections** - Each addresses specific AI failure modes, consolidation would reduce clarity

### 📊 Metrics:
- **Current character fields:** 10+ fields per character
- **After removing description:** 9 fields (10% reduction)
- **Output impact:** Zero (description not used)
- **Codebase impact:** Minimal (just remove field access)

---

## Implementation Status - Proposal 1 ✅ COMPLETED

**Date:** January 24, 2026

### Changes Made:
1. ✅ Updated [character_schema.json](character_schema.json) - Removed `description` field from schema
2. ✅ Updated [template.json](template.json) - Removed `description` from all three example characters
3. ✅ Updated [CHARACTER_JSON_GUIDE.md](CHARACTER_JSON_GUIDE.md) - Removed description from Optional Fields section
4. ✅ Updated [src/create_image.py](src/create_image.py) - Modified comments to indicate fallback is for backward compatibility
5. ✅ All 260 tests pass

### Backward Compatibility:
- Code retains `character_base or char_data.get("description", "")` fallback for external files that haven't been updated yet
- This ensures the schema simplification doesn't break existing character files in other repositories
- New files should use only `character_base` (as required by schema)

### Impact:
- **New projects:** Will use simplified schema without `description` field
- **Existing projects:** Continue to work via fallback mechanism
- **Migration path:** Clear - just move description content to character_base
- **Test results:** All 260 tests pass, including integration tests with external character files

---

## Next Steps (Future Proposals)

### Proposal 2: Rename `character_override` → `pose_details` (Not Yet Implemented)
This would improve clarity but requires updates across all character JSON files and code. Can be considered for a future refactoring cycle.

Estimated time: 30 minutes
Risk level: Low (just a rename, no logic changes)

