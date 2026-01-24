# create_image.py Refactoring Plan

## Current State Analysis

The `create_image.py` script is ~1200 lines and handles multiple responsibilities:
- JSON loading, validation, and import resolution
- Character/pose/refinement resolution and lookup
- Equipment and prop handling with hand assignment validation
- Pose library integration
- Prompt building with complex section assembly
- Reference sheet generation (multi-figure layouts)
- OpenAI API integration
- CLI argument parsing and execution flow
- Utility functions (clipboard, sanitization, path resolution)

## Phase 1: Test Infrastructure (DO THIS FIRST)

### 1.1 Catalog Test Fixtures
- [x] Identify all character JSON files to use as test fixtures
  - `denizen_standees.json`
  - Any other character files in the workspace
- [x] Document the character files and their key features:
  - Which have pose libraries
  - Which have equipment/props
  - Which have multi-limbed characters
  - Which have reference sheets
  - Which use imports

### 1.2 Create Golden Output Files
- [x] Generate current prompt outputs for all test cases
  - Run `./create_image.py <file> --all --prompt-only` for each character file
  - Save outputs to `tests/golden_outputs/`
  - Name pattern: `<filename>_<character>_<pose>.txt`
- [x] Generate reference sheet outputs
  - Run `./create_image.py <file> --page 1 --prompt-only` etc.
  - Save to `tests/golden_outputs/reference_sheets/`
- [x] Document test matrix in `tests/test_cases.md`:
  - Character ID + Pose combinations
  - Expected output file names
  - Special features being tested (props, multi-limbed, etc.)

### 1.3 Create Test Framework
- [x] Set up pytest structure:
  ```
  tests/
    __init__.py
    conftest.py              # Shared fixtures
    test_json_loading.py     # JSON parsing and validation
    test_character_lookup.py # Character/pose resolution
    test_equipment.py        # Equipment and hand validation
    test_pose_library.py     # Pose library integration
    test_prompt_building.py  # Prompt assembly logic
    test_reference_sheets.py # Reference sheet generation
    test_integration.py      # Full end-to-end tests
    golden_outputs/          # Expected outputs
    fixtures/                # Test data files
  ```
- [x] Add `pytest` and `pytest-cov` to requirements.txt
- [x] Create `conftest.py` with shared fixtures:
  - Sample JSON data structures
  - Mock file paths
  - Reusable test characters

### 1.4 Unit Tests for Core Functions

#### JSON and Import Resolution
- [x] `test_load_json_data()`
- [x] `test_resolve_imports()`
- [x] `test_resolve_path()` - especially Windows vs Git Bash paths
- [x] `test_validate_character_ids()`
- [x] `test_find_character_by_id_or_name()`
- [x] `test_find_refinement_by_id_or_name()`
- [x] `test_parse_refinement_path()`

#### Equipment and Props
- [x] `test_resolve_prop_references()`
- [x] `test_validate_hand_assignments()` - normal characters
- [x] `test_validate_hand_assignments()` - multi-limbed characters
- [x] `test_validate_hand_assignments()` - conflict detection

#### Pose Library
- [x] `test_find_pose_in_library()`
- [x] `test_compose_pose_prompt_from_library()`
- [x] `test_validate_pose_compatibility()`
- [x] `test_pose_library_ref_resolution()`

#### Prompt Building
- [x] `test_build_final_prompt()` - basic structure
- [x] `test_build_final_prompt()` - with all sections
- [x] `test_build_final_prompt()` - section combinations
- [x] `test_extract_generic_snippet()` - dict vs string
- [x] `test_extract_miniature_snippet()`
- [x] `test_remove_base_language()`

#### Reference Sheets
- [x] `test_parse_page_spec()` - all formats
- [x] `test_deduplicate_figure_sections()`
- [x] `test_handle_reference_sheet()` - single page
- [x] `test_handle_reference_sheet()` - multiple pages
- [x] `test_handle_reference_sheet()` - subrefinement filtering

#### Utilities
- [x] `test_sanitize_for_ascii()`
- [x] `test_format_for_chat()`

### 1.5 Integration Tests (Golden Output Validation)

- [x] Create `test_integration.py` with output comparison:
  ```python
  @pytest.mark.parametrize("character_file,character,pose,expected_file", [
      ("denizen_standees.json", "1", "1", "denizen_1_1.txt"),
      # ... all test cases
  ])
  def test_prompt_output_matches_golden(character_file, character, pose, expected_file):
      # Generate prompt
      # Load golden output
      # Compare (with normalization for timestamps, etc.)
  ```

- [x] Test all character + pose combinations from catalog
- [x] Test reference sheets for all pages
- [x] Test `--all` flag behavior
- [x] Test `--no-base`, `--no-miniature`, `--no-generic` flags

### 1.6 Regression Test Script
- [x] Create `tests/generate_golden_outputs.py`:
  - Automated script to regenerate all golden outputs
  - Use before refactoring to capture current behavior
  - Can be run after changes to validate
- [x] Create `tests/run_regression_tests.sh`:
  - Run all integration tests
  - Generate coverage report
  - Fail if any output differs from golden files

### 1.7 Test Execution and Validation
- [x] Run all tests and ensure they pass with current code
- [x] Achieve >80% code coverage on core functions
- [x] Document any known issues or expected failures
- [ ] Set up CI/CD to run tests automatically (optional)

---

## Phase 2: Code Refactoring (AFTER TESTS PASS)

### 2.1 Extract JSON/Data Layer
- [x] Create `json_loader.py` module
- [x] Create `character_resolver.py` module
- [x] Move import resolution logic
- [x] Move character/pose lookup functions
- [x] Update tests to import from new modules
- [x] Create comprehensive unit tests for new modules
- [x] All tests passing (148/148) with 90% coverage on new modules

### 2.2 Extract Equipment/Props Layer
- [x] Create `equipment_handler.py` module
- [x] Move prop resolution
- [x] Move hand validation
- [x] Update tests to import from new module
- [x] Create comprehensive unit tests for equipment_handler module
- [x] All tests passing (174/174) with 91% coverage on equipment_handler

### 2.3 Extract Pose Library Layer
- [x] Create `pose_library.py` module
- [x] Move pose lookup and composition
- [x] Move compatibility validation
- [x] Move remove_base_language utility
- [x] Move PromptNotFoundError exception
- [x] Update tests to import from new module
- [x] Create comprehensive unit tests for pose_library module
- [x] All tests passing (209/209) with 100% coverage on pose_library
- [ ] Update tests to import from new module
- [ ] Create comprehensive unit tests for pose_library module
- [ ] Verify all tests passing with >80% coverage

### 2.4 Extract Prompt Building Layer
- [ ] Create `prompt_builder.py` module
- [ ] Separate section builders
- [ ] Create PromptSection dataclass
- [ ] Improve section assembly logic
- [ ] Update tests to import from new module
- [ ] Create comprehensive unit tests for prompt_builder module
- [ ] Verify all tests passing with >80% coverage
- [ ] Update tests to import from new module
- [ ] Create comprehensive unit tests for prompt_builder module
- [ ] Verify all tests passing with >80% coverage

### 2.5 Extract Reference Sheet Layer
- [ ] Create `reference_sheet.py` module
- [ ] Break down large functions
- [ ] Improve page/grid layout logic
- [ ] Update tests to import from new module
- [ ] Create comprehensive unit tests for reference_sheet module
- [ ] Verify all tests passing with >80% coverage
- [ ] Update tests to import from new module
- [ ] Create comprehensive unit tests for reference_sheet module
- [ ] Verify all tests passing with >80% coverage

### 2.6 Simplify Main Script
- [ ] Keep only CLI and orchestration
- [ ] Use imported modules
- [ ] Simplify argument handling
- [ ] Improve error messages

### 2.7 Documentation
- [ ] Add docstrings to all modules
- [ ] Update README with new structure
- [ ] Create architecture documentation
- [ ] Add usage examples

---

## Phase 3: Enhancements (OPTIONAL, AFTER REFACTORING)

- [ ] Add JSON schema validation
- [ ] Improve error messages with suggestions
- [ ] Add prompt caching/memoization
- [ ] Add support for batch API calls
- [ ] Add progress indicators
- [ ] Improve reference sheet layout options
- [ ] Add prompt template system

---

## Success Criteria

✅ **Phase 1 COMPLETE!**
- All unit tests written and passing ✓
- All integration tests written and passing ✓
- Golden outputs captured for all test cases ✓
- Coverage >80% on core functions ✓
- Regression test script working ✓

⏳ Phase 2 In Progress:
- [x] JSON/Data Layer - `json_loader.py` and `character_resolver.py` created ✓
- [x] Equipment/Props Layer - `equipment_handler.py` created ✓
- [x] Pose Library Layer - `pose_library.py` created ✓
- Code split into logical modules
- Each new module has comprehensive unit tests (>80% coverage)
- All tests still passing (209/209)
- No behavioral changes (same outputs)
- Code is more maintainable
- Cyclomatic complexity reduced

⏳ Phase 3 Complete When:
- New features implemented
- Tests added for new features
- Documentation updated

---

## Notes

- **DO NOT SKIP PHASE 1** - Tests are critical for safe refactoring
- **ALWAYS CREATE UNIT TESTS** - Each new module must have comprehensive unit tests (>80% coverage)
- Run tests after every change during refactoring
- Keep commits small and focused
- Each commit should have passing tests
- Document any breaking changes
