# PromptSmith

A JSON-based system for organizing and generating AI image prompts with nested refinements. Designed for flexible prompt management with support for multiple characters, variants, poses, and hierarchical rule application.

## Overview

This system organizes character prompts with support for nested refinements. Each character can have multiple forms, and each form can have multiple poses or variations. The system supports flexible addressing syntax that allows you to reference prompts by number, name, or a combination.

## File Structure

- **`template.json`** - Generic template for creating new projects
- **`create_image.py`** - Python script to generate images using OpenAI API
- **`rules/`** - Directory for reusable rule definitions (optional)
  - **`generic_render_rules.json`** - Universal rendering rules
  - **`pose_library.json`** - Reusable pose definitions
- **`readme.md`** - This file

### Example Projects
- **`garou.json`** - Old West Werewolf Pack (9 characters, 45 refinements) - demonstrates the system

## Addressing Syntax

The system supports multiple ways to reference characters and refinements:

- **By number**: `1:1` = character 1, refinement 1 (e.g., first form)
- **By name**: `alpha:human` = character named 'alpha', refinement named 'human'
- **Mixed**: `alpha:1` or `1:human` = mix numbers and names
- **Deep nesting**: `1:1:1` = character:form:pose (or any other levels)

### Examples:

- `1` or `alpha` = entire character (all refinements)
- `1:1` or `alpha:human` = specific form
- `1:1:1` or `alpha:human:standing` = specific pose within form (if implemented)

## JSON Structure

### Required Sections

1. **`metadata`** - Project information (title, version, description, date)
2. **`generic_render_rules`** - Universal rules applied to ALL prompts
3. **`thematic_rules`** - Optional theme-specific rules
4. **`miniature_scale_rules`** - Scale-specific rendering rules (e.g., 40mm tabletop)
5. **`characters`** - Array of character definitions

### Character Structure

Each character has:
- `id` (number) - Numeric identifier
- `name` (string) - Text identifier for name-based addressing
- `title` (string) - Display title
- `description` (string) - Character background
- `visual_notes` (string) - Visual reference notes
- `equipment` (array) - Equipment/props with structured format
- `refinements` or `poses` (array) - Nested refinements (forms, poses, etc.)

### Refinement Structure

Each refinement can have:
- `id` (number) - Numeric identifier within parent
- `name` (string) - Text identifier
- `description` (string) - Description of this refinement
- `pose` (string) - Optional pose description
- `prompt` (string) - The actual prompt text
- `thematic_snippet` (array of strings, optional) - List of thematic rule references or custom snippets
  - Each item can be:
    - A reference to a form name from `thematic_rules.forms` (e.g., `["glabro"]`)
    - A custom snippet string (e.g., `["aggressive stance, prop displayed"]`)
    - Multiple references or combinations (e.g., `["glabro", "combat-ready"]`)
  - The script resolves references and applies all snippets in order
  - If omitted, only global thematic rules are applied
- `refinements` (array) - Optional nested sub-refinements

### Equipment Structure (v5.0.0)

Equipment uses a structured format that separates item details, position, and usage:

**Format:**
```json
"equipment": [
  "item_name (visual_detail) : position : usage_description"
]
```

**Position values:**
- `main_hand` - Primary weapon/tool in dominant hand
- `off_hand` - Secondary weapon/shield in off hand
- `dual_wield` - Paired weapons in both hands
- `holstered_belt`, `holstered_hip`, `holstered_thigh`, `holstered_back` - Storage locations

**Example:**
```json
"equipment": [
  "longsword (straight blade, wrapped leather grip) : main_hand : held at ready",
  "round shield (wood planks, steel rim) : off_hand : held at guard",
  "dagger (simple blade, leather sheath) : holstered_belt : sheathed"
]
```

**Output in prompts:**
```
PROPS:
- longsword (straight blade, wrapped leather grip) [main_hand] held at ready
- round shield (wood planks, steel rim) [off_hand] held at guard
- dagger (simple blade, leather sheath) [holstered_belt] sheathed
```

**Pose-level equipment_override:**

Poses can completely replace character equipment using the same format:

```json
{
  "id": 5,
  "name": "unarmed_ready",
  "pose_library_ref": "un_fighter_ready",
  "equipment_override": [
    "longsword (straight blade) : holstered_back : slung on back",
    "shield (wood planks) : holstered_back : slung on back"
  ],
  "character_override": "combat ready with hands empty; weapons stowed"
}
```

This completely replaces the character's default equipment for that specific pose, allowing different equipment configurations per pose (e.g., weapons drawn vs weapons stowed).

### Thematic Rules

The `thematic_rules` section supports project-wide theming:
- `prompt_snippet` (string) - General thematic snippet applied to ALL prompts globally
- `forms` (object) - Optional reusable form definitions that can be referenced by refinements
  - Each form has: `description`, `anatomy`, and `prompt_snippet`
  - Useful for standardizing common variants (e.g., werewolf forms, armor types, etc.)
- Refinements reference forms using `thematic_snippet: ["form_name"]`
- Multiple forms or custom snippets can be combined: `thematic_snippet: ["form1", "custom text", "form2"]`

**Example workflow:**
1. Define reusable forms in `thematic_rules.forms` (optional)
2. Character prompt defines unique features
3. Refinement's `thematic_snippet` array references forms or adds custom snippets
4. Global `thematic_rules.prompt_snippet` adds overall theme (applied to ALL prompts)
5. Generic and miniature rules add technical requirements

**Form Definitions Example:**
```json
"thematic_rules": {
  "prompt_snippet": "Old West frontier horror",
  "forms": {
    "human": {
      "description": "Fully human form",
      "anatomy": "human anatomy, human proportions",
      "prompt_snippet": "fully human form, predatory stillness"
    },
    "glabro": {
      "description": "Near-human hybrid",
      "anatomy": "enlarged hands and claws, elongated jaw",
      "prompt_snippet": "near-human hybrid, enlarged hands and claws"
    }
  }
}
```

**Using Form References in Refinements:**
```json
{
  "id": 1,
  "name": "human",
  "thematic_snippet": ["human"],
  "prompt": "Character-specific details..."
},
{
  "id": 2,
  "name": "glabro",
  "thematic_snippet": ["glabro"],
  "prompt": "Character-specific details..."
},
{
  "id": 3,
  "name": "custom",
  "thematic_snippet": ["glabro", "heavily scarred", "aggressive posture"],
  "prompt": "Can combine form refs and custom text..."
}
```

**Snippet Resolution:**
- `thematic_snippet: ["glabro"]` → Looks up "glabro" in `thematic_rules.forms` and uses its `prompt_snippet`
- `thematic_snippet: ["custom text"]` → Uses "custom text" as-is (not a form reference)
- `thematic_snippet: ["form1", "form2"]` → Resolves multiple forms and combines them
- No `thematic_snippet` → Only global thematic rules are applied

## Usage

### Script Usage

```powershell
# List all available characters and refinements
python create_image.py myproject.json --list

# Generate prompts for all refinements of a character (default behavior)
python create_image.py myproject.json 1 --dry-run
python create_image.py myproject.json hero_name --prompt-only

# Generate prompt for a specific refinement
python create_image.py myproject.json 1:3 --dry-run
python create_image.py myproject.json hero_name:variant --dry-run

# Generate actual images (requires OpenAI API key)
$env:OPENAI_API_KEY = "your-key-here"
python create_image.py myproject.json 1              # All refinements for character 1
python create_image.py myproject.json hero_name:variant  # Specific variant

# Copy prompt to clipboard (Windows)
python create_image.py myproject.json 1:1 --dry-run --copy

# Remove miniature base from prompt
python create_image.py myproject.json 1:1 --no-base

# Exclude generic or miniature rules
python create_image.py myproject.json 1:1 --no-generic
python create_image.py myproject.json 1:1 --no-miniature

# Generate reference sheets (multiple poses in one prompt)
python create_image.py myproject.json --page 1 --prompt-only --copy  # First 9 poses
python create_image.py myproject.json --page 2 --prompt-only --copy  # Poses 10-18
python create_image.py myproject.json --page all --prompt-only       # All pages

# Example using the garou.json demo project
python create_image.py garou.json alpha:human --dry-run
python create_image.py garou.json --list
```

### Command-Line Options

#### Required Arguments
- **`filename`** - JSON file to use (e.g., `garou.json`, `myproject.json`)
- **`character`** - Character ID or path (positional or `--character/-c`)
  - Format: `1`, `alpha`, `1:2`, or `alpha:human`
  - If only character specified (e.g., `1` or `alpha`), generates all refinements
  - If full path specified (e.g., `1:2`), generates only that specific refinement
  - Not required when using `--list` or `--reference-sheet`

#### Output Options
- `--out` - Output directory (default: `./out`)
- `--model` - OpenAI model (default: `gpt-image-1`)
- `--size` - Image size (default: `1024x1024`)

#### Preview & Clipboard Options
- `--dry-run` - Print prompt only, don't call API
- `--prompt-only` - Alias for `--dry-run`
- `--copy` - Copy prompt to clipboard (Windows only)

#### Selection Options
- `--json, -j` - Alternative way to specify JSON file (overrides positional filename)
- `--list` - List all available characters/refinements and exit
- `--all` - Generate all refinements for specified character (default behavior when no refinement path specified)
- `--page, -p` - Generate reference sheet for a specific page number (each page shows up to 9 poses)
  - Page 1: poses 1-9
  - Page 2: poses 10-18
  - Page 3: poses 19-27, etc.
  - Use `all` to generate all pages
  - Examples: `--page 1`, `--page 2`, `--page all`

#### Rule Modification Options
- `--no-miniature` - Don't append miniature scale rules
- `--no-base` - Remove base/stand from miniature rules (keeps miniature styling)
- `--no-generic` - Don't append generic render rules

## Workflow for Creating New Projects

1. **Copy the template**
   ```powershell
   cp template.json myproject.json
   ```

2. **Fill in generic_render_rules**
   - Add universal rendering requirements that apply to all prompts
   - Keep these concise and focused on technical requirements

3. **Add thematic_rules** (optional)
   - Add project-specific style guidance
   - Theme, mood, or genre-specific rules
   - Optionally define reusable forms in `thematic_rules.forms`
     - Useful for standardizing variants (e.g., werewolf forms, armor types)
     - Each form includes `description`, `anatomy`, and `prompt_snippet`

4. **Define characters**
   - Each character gets an `id` (number) and `name` (string)
   - Add description and visual notes
   - Create refinements array

5. **Add refinements**
   - Each refinement is a variation (form, pose, etc.)
   - Refinements can nest infinitely
   - Each level inherits and extends parent rules

6. **Test prompts**
   ```powershell
   python create_image.py myproject.json --list
   python create_image.py myproject.json 1:1 --dry-run
   ```

## Best Practices

### Prompt Organization

- **Generic rules**: Keep concise and universal (lighting, camera, materials)
- **Thematic rules**: Project-specific style guidance (genre, mood, theme)
  - **Global snippet**: Applied to ALL prompts automatically via `thematic_rules.prompt_snippet`
  - **Form definitions**: Define reusable forms in `thematic_rules.forms` for consistency across characters
  - Example: All werewolf characters share the same 5 forms (human, glabro, crinos, hispo, wolf)
- **Character prompts**: Focus on unique identifying features specific to that character
- **Refinement prompts**: Add specific pose, action, or variation details
- **Refinement thematic_snippet**: Array of form references or custom snippets
  - Use `["form_name"]` to reference a form from `thematic_rules.forms`
  - Use `["custom text"]` for one-off snippets not defined as forms
  - Combine multiple: `["form1", "custom text", "form2"]`
- **Test combination**: Ensure prompts combine well at each nesting level

### Naming Conventions

- Use clear, descriptive names for characters and refinements
- Use underscores for multi-word names (`crow_eyed_one`, `powder_burn`)
- Keep IDs sequential for easy reference
- Document poses in the description field

### Prompt Construction

The final prompt is constructed in this order:
1. Character/refinement specific prompt (from refinement `prompt` field)
2. Refinement thematic snippets (resolved from `thematic_snippet` array references)
3. Global thematic rules `prompt_snippet` (applied to ALL prompts automatically)
4. Generic render rules (if not excluded with `--no-generic`)
5. Miniature scale rules (if not excluded with `--no-miniature`)
6. Additional flags (e.g., `--no-base` adds "no base, no stand...")

**Example for Alpha's Glabro form:**
- Refinement prompt: "Glabro female -- enlarged hands, elongated jaw..."
- Thematic snippet: `["glabro"]` → resolved to "near-human hybrid with distinctly human features..."
- Global thematic: "Old West frontier horror, evil werewolf pack, territorial and predatory"
- Generic rules: "single character, centered composition, full figure..."
- Miniature rules: "40mm scale tabletop miniature, hard plastic/resin model..."

This layering ensures consistent theming across all variants while allowing refinement-specific details.

## Example Project: Garou Pack

The included `garou.json` demonstrates the system's capabilities with a complete Old West werewolf pack project.

### Character List
1. **Alpha** (The Iron Wolf) - Native American war leader
2. **Breaker** (Beta) - European-American executioner
3. **Crow-Eyed One** (Scout) - Silent hunter
4. **Long Shadow** (Scout) - Endurance tracker
5. **Powder Burn** (Hunter) - Gun-fighter outlaw
6. **Undertaker** (Hunter) - Body arranger
7. **Red Howl** (Hunter) - Berserker
8. **Bone-Singer** (Elder) - Ritual keeper
9. **Lost Cub** (Newblood) - Recently turned

### Each Character Has 5 Forms

The Garou pack uses standardized werewolf forms defined in `thematic_rules.forms`:

- **Human** - Fully human form with subtle predatory tells
  - Anatomy: human anatomy, human proportions
  - Snippet: "fully human form, predatory stillness and unnatural gaze"
  
- **Glabro** - Near-human hybrid form (the "almost human but wrong" state)
  - Anatomy: enlarged hands and claws, elongated jaw with visible fangs, hunched posture, human-like feet (larger with clawed toes)
  - Snippet: "near-human hybrid, enlarged hands and claws, elongated jaw with fangs, hunched posture, human-like feet (larger with clawed toes)"
  
- **Crinos** - The war form (massive bipedal werewolf)
  - Anatomy: towering bipedal werewolf, wolf-like head with elongated muzzle and massive fangs, powerful shoulders and chest, digitigrade legs
  - Snippet: "massive bipedal werewolf war form, towering scale, full spiritual transformation"
  
- **Hispo** - Dire-wolf form (massive prehistoric wolf)
  - Anatomy: massive quadruped dire wolf, exaggerated shoulders and spine, oversized paws and jaws
  - Snippet: "dire wolf form, massive quadruped, exaggerated shoulders and spine"
  
- **Wolf** - Wolf form (near-natural but larger and unsettling)
  - Anatomy: large wolf anatomy, slightly oversized compared to natural wolves, intelligent eyes
  - Snippet: "large intelligent wolf, near-natural but larger and uncanny"

Each character's refinements reference these form definitions in their `thematic_snippet` to ensure consistency across all 9 characters.

### Example Commands

```powershell
# Alpha in Crinos form (by number)
python create_image.py garou.json 1:3 --dry-run

# Alpha in human form (by name)
python create_image.py garou.json alpha:human --dry-run

# All forms for the Lost Cub (default behavior when no form specified)
python create_image.py garou.json 9 --dry-run
python create_image.py garou.json lost_cub --dry-run

# Breaker in wolf form with no base
python create_image.py garou.json breaker:wolf --no-base --dry-run
```

## Requirements

- Python 3.10+
- OpenAI Python SDK (`pip install openai`)
- OpenAI API key (for actual image generation)

## Troubleshooting

**Error: "Character not found"**
- Check available characters with `--list`
- Verify spelling of character names
- Character names are case-insensitive

**Error: "Refinement not found"**
- Use `--list` to see available refinements for each character
- Check spelling and ensure the refinement exists

**Error: "OPENAI_API_KEY is not set"**
- Set the environment variable: `$env:OPENAI_API_KEY = "your-key"`
- Use `--dry-run` to test without API key

## Future Enhancements

- Support for deeper nesting (pose level: `1:1:1`)
- Import/export between formats (JSON ↔ Markdown)
- Batch generation with progress tracking
- Template validation and linting
- Multi-view generation (front/side/top)
