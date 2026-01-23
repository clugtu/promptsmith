# Test Infrastructure

This directory contains the test suite for `create_image.py`.

## Structure

```
tests/
├── __init__.py                    # Package marker
├── conftest.py                    # Pytest fixtures and configuration
├── test_json_loading.py          # JSON parsing, validation, imports
├── test_character_lookup.py      # Character/pose lookup functions
├── test_equipment.py             # Equipment and hand validation
├── test_pose_library.py          # Pose library integration
├── test_utilities.py             # Utility functions
├── test_integration.py           # End-to-end integration tests (TODO)
├── generate_golden_outputs.py    # Script to generate baseline outputs
├── run_tests.sh                  # Convenience script to run tests
├── golden_outputs/               # Expected prompt outputs
│   ├── player_denizens_all.txt
│   ├── garou_all.txt
│   └── reference_sheets/
└── test_character_catalog.md     # Catalog of test character files
```

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
# Simple run
pytest tests/

# With verbose output
pytest tests/ -v

# With coverage
pytest tests/ --cov=create_image --cov-report=term-missing

# Or use the convenience script
./tests/run_tests.sh
```

### Run Specific Test Files

```bash
pytest tests/test_equipment.py -v
pytest tests/test_pose_library.py -v
```

### Run Specific Test Functions

```bash
pytest tests/test_equipment.py::TestHandValidation::test_validate_hand_assignments_valid -v
```

## Generating Golden Outputs

Golden outputs are baseline prompt generations used for regression testing.
They capture the current behavior before refactoring begins.

```bash
# Generate all golden outputs (requires character files)
python tests/generate_golden_outputs.py

# Specify custom OneDrive path
python tests/generate_golden_outputs.py --custom-path "C:/Users/YOUR_NAME/OneDrive/3D Printing/SoB/Custom"
```

## Path Resolution for Tests

Tests need to locate character JSON files in different locations:

### Git-Tracked Files (Standees)
- Located in `../shattered_citadel/assets/standees/`
- Use relative paths from promptsmith repo
- Should work on any machine with both repos checked out

### OneDrive Files (Custom)
- Located in user's OneDrive directory
- Path varies by machine and user
- Use `PROMPTSMITH_CUSTOM_PATH` environment variable:

```bash
# Set environment variable (bash)
export PROMPTSMITH_CUSTOM_PATH="/path/to/Custom"

# Set environment variable (PowerShell)
$env:PROMPTSMITH_CUSTOM_PATH = "C:\Users\clugtu\OneDrive\3D Printing\SoB\Custom"

# Then run tests
pytest tests/
```

- Tests will skip if OneDrive files are not found

## Test Fixtures

See [conftest.py](conftest.py) for available fixtures:

### Path Fixtures
- `promptsmith_root` - Repository root directory
- `standees_path` - Path to standees directory (git)
- `custom_path` - Path to Custom directory (OneDrive)

### File Fixtures
- `player_denizens_json` - player_denizen_standees.json
- `enemy_denizens_json` - enemy_denizens_standees.json
- `garou_json` - garou.json

### Sample Data Fixtures
- `minimal_character_json` - Minimal valid character
- `character_with_poses_json` - Character with multiple poses
- `character_with_equipment_json` - Character with props
- `character_with_pose_library_json` - Character using pose library
- `multi_limbed_character_json` - Multi-armed character
- `character_with_forms_json` - Character with thematic forms

## Writing New Tests

### Unit Tests

```python
import pytest
import create_image

def test_my_function():
    """Test description."""
    result = create_image.my_function(input_data)
    assert result == expected_output
```

### Integration Tests (with Golden Outputs)

```python
def test_prompt_generation(player_denizens_json):
    """Test that prompt generation matches golden output."""
    prompt, *_ = create_image.resolve_prompt_from_json(
        json_data, character=1, form=1
    )
    
    # Load golden output
    golden_file = Path("tests/golden_outputs/player_denizen_1_1.txt")
    expected = golden_file.read_text()
    
    # Compare (may need normalization)
    assert prompt.strip() == expected.strip()
```

## Test Coverage Goals

- **Unit tests**: >80% coverage of core functions
- **Integration tests**: All major character files and features
- **Edge cases**: Error handling, invalid inputs, conflicts

## Current Status

✅ Phase 1.3 - Test framework structure created
✅ Phase 1.4 - Unit tests for core functions written
⬜ Phase 1.5 - Integration tests (need golden outputs)
⬜ Phase 1.6 - Regression test script
⬜ Phase 1.7 - Validate all tests pass

## Next Steps

1. Generate golden outputs: `python tests/generate_golden_outputs.py`
2. Write integration tests in `test_integration.py`
3. Run full test suite: `pytest tests/ -v`
4. Fix any failing tests
5. Achieve >80% coverage
6. Ready for refactoring!
