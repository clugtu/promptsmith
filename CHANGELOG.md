# Changelog

All notable changes to the PromptSmith pose library system.

## [3.0.0] - 2026-01-02

### Added
- Pose library system with weapon separation and placeholder injection
- 16 new poses expanding library from 14 to 30 total poses
- Prop visibility modes: `"presented"` and `"carried_attached"`
- Automatic validation system with compatibility warnings
- Modular rule imports (generic_render_rules, style_rules, pose_library)
- Passive state + explicit negation composition pattern for guardrail safety
- Prop override system (prop_state and orientation customization)
- `validate_pose_compatibility()` function in create_image.py
- Comprehensive system documentation in template.json

### Changed
- Character structure: flat poses array replacing nested refinements
- Weapons now defined in separate `weapons` object with handedness
- Poses reference library templates via `pose_library_ref`
- Prompt composition happens at generation time (not pre-written)
- Updated template.json to v3.0.0 architecture
- Updated all documentation (SAFE_IMAGE_GUIDE_PROMPT.md, tabletop_pose_prompt.md, POSE_LIBRARY_EXPANSION.md)

### Removed
- Nested refinements structure (replaced by flat pose arrays)
- Direct prompt definitions in character files (replaced by pose_library_ref)
- Old template structure with thematic_snippet arrays

## [2.0.0] - 2025-12-31

### Added
- Initial pose expansion: 16 new poses
  - 4 single-handed poses (defensive_crouch, sprint_carry, overhead_strike, side_guard_low)
  - 4 two-handed poses (low_sweep, overhead_chop, march_carry, defensive_brace)
  - 3 unarmed poses (aggressive_charge, defensive_crouch, victory_roar)
  - 3 dual-wield poses (spinning_strike, crossed_defense, asymmetric_ready)
  - 2 mixed poses (shield_bash, transition_stance)
- Prop class system (none, small, compact, long, flexible, shield_plane, two_hand_frame, bulky)
- Handedness mode categorization (unarmed, single_handed, two_handed, dual_wield)
- Basic validation system

### Changed
- Expanded pose library coverage for all weapon combinations
- Improved error messages with available character/pose listings

## [1.0.0] - 2025-12-29

### Added
- Initial release with 14 base poses
- Character/refinement nested structure
- Direct prompt definitions
- Basic thematic rules system
- Generic render rules
- Miniature scale rules
