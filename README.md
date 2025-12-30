# Garou Character Prompt System

A JSON-based system for organizing and generating AI image prompts for tabletop miniatures with nested refinements.

## Overview

This system organizes character prompts with support for nested refinements. Each character can have multiple forms, and each form can have multiple poses or variations. The system supports flexible addressing syntax that allows you to reference prompts by number, name, or a combination.

## File Structure

- **`template.json`** - Generic template for creating new character databases
- **`garou.json`** - Old West Werewolf Pack character database (9 characters, 45 refinements)
- **`create_image.py`** - Python script to generate images using OpenAI API
- **`readme.md`** - This file

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
- `refinements` (array) - Nested refinements (forms, poses, etc.)

### Refinement Structure

Each refinement can have:
- `id` (number) - Numeric identifier within parent
- `name` (string) - Text identifier
- `description` (string) - Description of this refinement
- `pose` (string) - Optional pose description
- `prompt` (string) - The actual prompt text
- `thematic_snippet` (string) - Optional refinement-specific thematic rules (e.g., form anatomy, style)
- `refinements` (array) - Optional nested sub-refinements

### Thematic Rules

The `thematic_rules` section supports project-wide theming:
- `prompt_snippet` (string) - General thematic snippet applied to ALL prompts
- Each refinement can optionally include a `thematic_snippet` that adds refinement-specific theming
- Thematic snippets are accumulated as you descend through nested refinements

**Example workflow:**
1. Character prompt defines unique features
2. Refinement's `thematic_snippet` adds form/variant-specific details (e.g., "fully human form" vs "massive werewolf war form")
3. Global `thematic_rules.prompt_snippet` adds overall theme (e.g., "Old West horror")
4. Generic and miniature rules add technical requirements

## Usage

### Script Usage

```powershell
# Activate conda environment (if needed)
conda activate sc

# List all available characters and refinements
python create_image.py garou.json --list

# Generate prompt only (no API call)
python create_image.py garou.json 1:3 --dry-run
python create_image.py garou.json alpha:crinos --dry-run

# Generate actual image (requires OpenAI API key)
$env:OPENAI_API_KEY = "your-key-here"
python create_image.py garou.json 1:3
python create_image.py garou.json alpha:human

# Generate all forms for a character
python create_image.py garou.json 1 --all
python create_image.py garou.json alpha --all --dry-run

# Copy prompt to clipboard (Windows)
python create_image.py garou.json 1:1 --dry-run --copy

# Remove miniature base from prompt
python create_image.py garou.json 1:1 --no-base

# Exclude generic or miniature rules
python create_image.py garou.json 1:1 --no-generic
python create_image.py garou.json 1:1 --no-miniature

# Use a different JSON file
python create_image.py myproject.json 1:1 --dry-run
python create_image.py template.json --list
```

### Command-Line Options

- **`filename`** - JSON file to use (required, first argument)
- `--character, -c` - Character ID or path (e.g., `1`, `alpha`, `1:3`)
- `--form, -f` - Refinement/form (e.g., `human`, `crinos`)
- `--json, -j` - Alternative way to specify JSON file (overrides positional argument)
- `--out` - Output directory (default: `./out`)
- `--out` - Output directory (default: `./out`)
- `--model` - OpenAI model (default: `gpt-image-1`)
- `--size` - Image size (default: `1024x1024`)
- `--dry-run` - Print prompt only, don't call API
- `--prompt-only` - Alias for `--dry-run`
- `--copy` - Copy prompt to clipboard (Windows)
- `--list` - List all available characters/refinements
- `--all` - Generate all refinements for a character
- `--no-miniature` - Don't append miniature scale rules
- `--no-base` - Remove base/stand from miniature rules
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
- **Character prompts**: Focus on unique identifying features
- **Refinement prompts**: Add specific pose, action, or variation details
- **Test combination**: Ensure prompts combine well at each nesting level

### Naming Conventions

- Use clear, descriptive names for characters and refinements
- Use underscores for multi-word names (`crow_eyed_one`, `powder_burn`)
- Keep IDs sequential for easy reference
- Document poses in the description field

### Prompt Construction

The final prompt is constructed in this order:
1. Character/refinement specific prompt
2. Refinement `thematic_snippet` (if present)
3. Global thematic rules `prompt_snippet`
4. Generic render rules (if not excluded with `--no-generic`)
5. Miniature scale rules (if not excluded with `--no-miniature`)
6. Additional flags (e.g., `--no-base` adds "no base, no stand...")

This layering ensures consistent theming across all variants while allowing refinement-specific details.

## Examples from Garou Pack

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
- **Human** - Fully human appearance
- **Glabro** - Near-human but wrong
- **Crinos** - The war form (towering bipedal wolf-man)
- **Hispo** - Massive dire-wolf form
- **Wolf** - Near-natural wolf

### Example Commands

```powershell
# Alpha in Crinos form (by number)
python create_image.py garou.json 1:3 --dry-run

# Alpha in human form (by name)
python create_image.py garou.json alpha:human --dry-run

# All forms for the Lost Cub
python create_image.py garou.json 9 --all --dry-run

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
