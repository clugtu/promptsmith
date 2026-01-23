# Character File Test Catalog

## Overview
This catalog documents all character JSON files used for testing create_image.py.
Files are organized by location (git-tracked vs OneDrive) for path resolution strategies.

---

## Git-Tracked Files (Relative Paths)
These files are in the shattered_citadel git repo and can use relative paths.

### Location: `../shattered_citadel/assets/standees/`

#### 1. player_denizen_standees.json
- **Path**: `../shattered_citadel/assets/standees/player_denizen_standees.json`
- **Characters**: 4 (2 archetypes × 2 genders)
  - Relic Hunter (male, female)
  - Sawbones (male, female)
- **Poses per character**: 2 (front view, back view)
- **Total test cases**: 8 poses
- **Features**:
  - ✓ Inline poses (no pose library refs)
  - ✓ Equipment arrays with descriptions
  - ✓ Imports (render rules + style)
  - ✓ Standee-specific render (front/back silhouette-locked)
  - ✓ Camera rotation overrides
  - ✗ No pose library
  - ✗ No multi-limbed characters
  - ✗ No prop_definitions
- **Test Priority**: HIGH - Simple structure, good baseline

#### 2. enemy_denizens_standees.json
- **Path**: `../shattered_citadel/assets/standees/enemy_denizens_standees.json`
- **Characters**: 12+ enemy archetypes
- **Poses per character**: 2 (front view, back view)
- **Total test cases**: ~24+ poses
- **Features**:
  - ✓ Inline poses (no pose library refs)
  - ✓ Faction system (enemy_factions)
  - ✓ Mechanics data (threat, vitality, etc.)
  - ✓ Special abilities
  - ✓ Imports (render rules + style)
  - ✗ No pose library
  - ✗ No multi-limbed characters
  - ✗ No prop_definitions
- **Test Priority**: HIGH - Tests enemy/NPC rendering

---

## OneDrive Files (Dynamic Paths)
These files are in OneDrive and need environment-aware path resolution.
**Strategy**: Use environment variable or config file for OneDrive root.

### Location: `$ONEDRIVE_ROOT/3D Printing/SoB/Custom/`

#### 3. Garou/garou.json
- **Path**: `Custom/Garou/garou.json` (relative to OneDrive Custom root)
- **Characters**: 5 pack members
  - The Howling Wind (Alpha)
  - The Iron Fang
  - The Red Claw
  - The Shadow Runner
  - The Bone Breaker
- **Forms per character**: 3-4 (human, glabro, crinos, hispo/wolf)
- **Total test cases**: ~18 character×form combinations
- **Features**:
  - ✓ Pose library references (extensive)
  - ✓ Thematic forms system (human, glabro, crinos, hispo, wolf)
  - ✓ Equipment with hand positions
  - ✓ Prop definitions (weapons, gear)
  - ✓ Figure type specifications
  - ✓ Imports (generic rules, style, pose library)
  - ✓ Character overrides
  - ✗ No multi-limbed (but has different figure types)
- **Test Priority**: CRITICAL - Most complex, tests all major features

#### 4. Vampire_Heroes/vampire_heroes.json
- **Path**: `Custom/Vampire_Heroes/vampire_heroes.json`
- **Characters**: TBD (need to inspect)
- **Test Priority**: MEDIUM

#### 5. Sisters of the crimson veil/sisters_of_the_crimson_veil.json
- **Path**: `Custom/Sisters of the crimson veil/sisters_of_the_crimson_veil.json`
- **Characters**: TBD (need to inspect)
- **Test Priority**: MEDIUM

#### 6. Townsfolk/*.json
Multiple JSON files in townsfolk subdirectories:
- `Chinese Immigrants/chinese_immigrants.json`
- `Down on their luck/down_on_their_luck.json`
- `Drifters and wayfarers/drifters_and_wayfarers.json`
- `Homesteaders and kin/homesteaders_and_kin.json`
- `Main street traders/main_street_trades.json`
- `Saloon and leisure/saloon_and_leisure.json`
- `Street Idlers/street_idlers.json`
- `The Faithful/the_faithful.json`
- `Working Hands/working_hands.json`
- **Test Priority**: LOW - Likely similar structure, pick 1-2 as samples

---

## Shared Rule Files

### Git-Tracked Rules (standees)
- `shattered_citadel_standee_render_rules.json` - Generic render rules for standees
- `shattered_citadel_standee_style.json` - Style rules for Shattered Citadel

### PromptSmith Rules (git-tracked in promptsmith repo)
- `rules/generic_render_rules.json` - Generic 3D-safe rendering rules
- `rules/realistic_weird_west_style.json` - Realistic western horror style
- `rules/pose_library.json` - Extensive pose library

---

## Path Resolution Strategy

### For Git-Tracked Files (standees)
```python
# Relative to promptsmith repo root
STANDEES_PATH = Path("../shattered_citadel/assets/standees")
```

### For OneDrive Files (Custom)
```python
# Option 1: Environment variable
ONEDRIVE_CUSTOM = os.getenv("PROMPTSMITH_CUSTOM_PATH", 
                             Path.home() / "OneDrive/3D Printing/SoB/Custom")

# Option 2: Config file (tests/test_config.json)
{
  "custom_files_root": "C:/Users/USERNAME/OneDrive/3D Printing/SoB/Custom"
}

# Option 3: Pytest fixture with skip if not found
@pytest.fixture
def custom_path():
    candidates = [
        Path.home() / "OneDrive/3D Printing/SoB/Custom",
        Path("C:/Users/clugtu/OneDrive/3D Printing/SoB/Custom"),
        # Add more candidates as needed
    ]
    for path in candidates:
        if path.exists():
            return path
    pytest.skip("Custom character files not found (OneDrive)")
```

---

## Test Case Priorities

### Phase 1.2 Golden Outputs (Initial Test Suite)

**Tier 1 - Must Have** (Baseline functionality):
- player_denizen_standees.json - All characters, all poses (8 test cases)
- garou.json - 2-3 characters with all forms (~6-9 test cases)

**Tier 2 - Should Have** (Edge cases):
- enemy_denizens_standees.json - Sample 3-4 enemies (6-8 test cases)
- garou.json - Reference sheets (--page 1, --page 2)

**Tier 3 - Nice to Have** (Coverage expansion):
- 1-2 Townsfolk files for variety
- vampire_heroes.json or sisters_of_the_crimson_veil.json

---

## Test Commands to Generate Golden Outputs

### Standees (Git)
```bash
# Player denizens - all characters, all poses
./create_image.py ../shattered_citadel/assets/standees/player_denizen_standees.json --all --prompt-only --no-base > tests/golden_outputs/player_denizens_all.txt

# Individual poses
./create_image.py ../shattered_citadel/assets/standees/player_denizen_standees.json 1:1 --prompt-only --no-base > tests/golden_outputs/player_denizen_1_1.txt
./create_image.py ../shattered_citadel/assets/standees/player_denizen_standees.json 1:2 --prompt-only --no-base > tests/golden_outputs/player_denizen_1_2.txt
# ... repeat for all
```

### Garou (OneDrive)
```bash
# All characters, all forms
./create_image.py "$CUSTOM_PATH/Garou/garou.json" --all --prompt-only --no-base > tests/golden_outputs/garou_all.txt

# Individual character forms
./create_image.py "$CUSTOM_PATH/Garou/garou.json" "The Howling Wind:human" --prompt-only > tests/golden_outputs/garou_howling_wind_human.txt
./create_image.py "$CUSTOM_PATH/Garou/garou.json" "The Howling Wind:crinos" --prompt-only > tests/golden_outputs/garou_howling_wind_crinos.txt
# ... etc

# Reference sheets
./create_image.py "$CUSTOM_PATH/Garou/garou.json" --page 1 --prompt-only > tests/golden_outputs/garou_ref_page1.txt
./create_image.py "$CUSTOM_PATH/Garou/garou.json" --page 2 --prompt-only > tests/golden_outputs/garou_ref_page2.txt
```

---

## Special Test Cases to Cover

### Features to Test
1. **Pose library resolution** - garou.json with pose_library_ref
2. **Inline poses** - player_denizen_standees.json
3. **Equipment arrays** - all files
4. **Prop definitions** - garou.json
5. **Hand validation** - normal 2-handed characters
6. **Multi-limbed validation** - need to find/create test case
7. **Figure types** - garou forms (bipedal, quadrupedal, facultatively_bipedal)
8. **Imports** - all files use imports
9. **Character/pose lookup** - by ID and by name
10. **Reference sheets** - page selection, subrefinement filtering
11. **Camera rotation** - standees use camera_rotation overrides
12. **Character overrides** - garou uses character_override in poses
13. **Gender/age/proportions** - all files

### Edge Cases
- Missing character
- Missing pose
- Invalid page number
- Invalid pose library ref
- Hand assignment conflicts
- Figure type mismatches
- Malformed equipment arrays

---

## Next Steps

1. ✅ Create this catalog
2. ⬜ Inspect remaining OneDrive files (vampire_heroes, sisters, townsfolk samples)
3. ⬜ Set up path resolution strategy
4. ⬜ Create tests/fixtures/ directory structure
5. ⬜ Generate golden outputs for Tier 1 files
6. ⬜ Create generate_golden_outputs.py script
7. ⬜ Document test matrix with expected features
