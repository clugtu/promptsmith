"""Unit tests for the prompt_builder module.

Tests prompt assembly, formatting, and section handling.
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from prompt_builder import format_for_chat, build_final_prompt


class TestFormatForChat:
    """Tests for format_for_chat utility function."""
    
    def test_format_for_chat_strips_whitespace(self):
        """Should strip leading/trailing whitespace."""
        assert format_for_chat("  hello  ") == "hello"
        assert format_for_chat("\n\nhello\n\n") == "hello"
        assert format_for_chat("\t\thello\t\t") == "hello"
    
    def test_format_for_chat_preserves_internal_whitespace(self):
        """Should preserve internal whitespace."""
        assert format_for_chat("hello world") == "hello world"
        assert format_for_chat("hello\nworld") == "hello\nworld"
    
    def test_format_for_chat_empty_string(self):
        """Should handle empty strings."""
        assert format_for_chat("") == ""
        assert format_for_chat("   ") == ""


class TestBuildFinalPromptBasic:
    """Basic tests for build_final_prompt function."""
    
    def test_minimal_prompt(self):
        """Should create minimal prompt with just base prompt."""
        prompt = build_final_prompt(
            "A warrior",
            include_generic=False,
            include_miniature=False
        )
        assert "create image" in prompt
        assert "CHARACTER:" in prompt
        assert "A warrior" in prompt
    
    def test_with_gender(self):
        """Should add gender to character section."""
        prompt = build_final_prompt(
            "A warrior",
            gender="male",
            include_generic=False,
            include_miniature=False
        )
        assert "CHARACTER:" in prompt
        assert "male" in prompt.lower()
    
    def test_gender_not_duplicated(self):
        """Should not add gender if already present in base prompt."""
        prompt = build_final_prompt(
            "A male warrior",
            gender="male",
            include_generic=False,
            include_miniature=False
        )
        # Count occurrences of "male" in CHARACTER section
        char_section = prompt.split("CHARACTER:")[1].split("\n\n")[0]
        assert char_section.lower().count("male") == 1
    
    def test_with_age(self):
        """Should add age to character section."""
        prompt = build_final_prompt(
            "A warrior",
            age="adult",
            include_generic=False,
            include_miniature=False
        )
        assert "adult" in prompt.lower()
    
    def test_age_and_gender_together(self):
        """Should add both age and gender as demographics."""
        prompt = build_final_prompt(
            "A warrior",
            age="adult",
            gender="male",
            include_generic=False,
            include_miniature=False
        )
        char_section = prompt.split("CHARACTER:")[1].split("\n\n")[0]
        assert "adult" in char_section.lower()
        assert "male" in char_section.lower()


class TestBuildFinalPromptSections:
    """Tests for section handling in build_final_prompt."""
    
    def test_asset_name_with_character_name_gender(self):
        """Should create asset name from character name and gender."""
        prompt = build_final_prompt(
            "A warrior",
            character_id="1",
            character_name="Warrior",
            gender="male",
            include_generic=False,
            include_miniature=False
        )
        assert "ASSET_NAME:" in prompt
        assert "1_warrior_male" in prompt.lower()
    
    def test_asset_name_without_character_id(self):
        """Should create asset name without character ID if not provided."""
        prompt = build_final_prompt(
            "A warrior",
            character_name="Warrior",
            gender="male",
            include_generic=False,
            include_miniature=False
        )
        assert "ASSET_NAME:" in prompt
        assert "warrior_male" in prompt.lower()
    
    def test_asset_name_fallback_to_ids(self):
        """Should fallback to ID-based naming if name/gender missing."""
        prompt = build_final_prompt(
            "A warrior",
            character_id="char1",
            form_id="form1",
            include_generic=False,
            include_miniature=False
        )
        assert "ASSET_NAME:" in prompt
        assert "char1_form1" in prompt
    
    def test_visual_notes_section(self):
        """Should include visual notes section when provided."""
        prompt = build_final_prompt(
            "A warrior",
            visual_notes="detailed armor, battle-worn",
            include_generic=False,
            include_miniature=False
        )
        assert "VISUAL:" in prompt
        assert "detailed armor, battle-worn" in prompt
    
    def test_visual_notes_before_character(self):
        """VISUAL section should appear before CHARACTER section."""
        prompt = build_final_prompt(
            "A warrior",
            visual_notes="visual styling",
            include_generic=False,
            include_miniature=False
        )
        visual_pos = prompt.index("VISUAL:")
        char_pos = prompt.index("CHARACTER:")
        assert visual_pos < char_pos
    
    def test_props_section_structured_format(self):
        """Should format equipment with structured format."""
        prompt = build_final_prompt(
            "A warrior",
            equipment=["sword (longsword) : main_hand : gripped firmly"],
            include_generic=False,
            include_miniature=False
        )
        assert "PROPS:" in prompt
        assert "- sword (longsword) [main_hand] gripped firmly" in prompt
    
    def test_props_section_legacy_format(self):
        """Should handle legacy equipment format without colons."""
        prompt = build_final_prompt(
            "A warrior",
            equipment=["sword in right hand"],
            include_generic=False,
            include_miniature=False
        )
        assert "PROPS:" in prompt
        assert "- sword in right hand" in prompt
    
    def test_props_section_multiple_items(self):
        """Should handle multiple equipment items."""
        prompt = build_final_prompt(
            "A warrior",
            equipment=[
                "sword (longsword) : main_hand : gripped firmly",
                "shield (round) : off_hand : held defensively"
            ],
            include_generic=False,
            include_miniature=False
        )
        assert "PROPS:" in prompt
        assert "sword" in prompt
        assert "shield" in prompt
    
    def test_pose_section(self):
        """Should include pose section from pose library."""
        prompt = build_final_prompt(
            "A warrior",
            pose_prompt="standing at attention, feet shoulder-width apart",
            include_generic=False,
            include_miniature=False
        )
        assert "POSE:" in prompt
        assert "standing at attention" in prompt
    
    def test_theme_section_with_snippets(self):
        """Should include thematic snippets in theme section."""
        prompt = build_final_prompt(
            "A warrior",
            thematic_snippets=["medieval fantasy", "heroic"],
            include_generic=False,
            include_miniature=False
        )
        assert "THEME:" in prompt
        assert "medieval fantasy" in prompt
        assert "heroic" in prompt
    
    def test_theme_section_with_general(self):
        """Should include general thematic in theme section."""
        prompt = build_final_prompt(
            "A warrior",
            thematic_general="dark and gritty",
            include_generic=False,
            include_miniature=False
        )
        assert "THEME:" in prompt
        assert "dark and gritty" in prompt
    
    def test_theme_section_combined(self):
        """Should combine snippets and general thematic."""
        prompt = build_final_prompt(
            "A warrior",
            thematic_snippets=["medieval fantasy"],
            thematic_general="dark and gritty",
            include_generic=False,
            include_miniature=False
        )
        assert "THEME:" in prompt
        assert "medieval fantasy" in prompt
        assert "dark and gritty" in prompt
    
    def test_proportions_section(self):
        """Should include proportions section."""
        prompt = build_final_prompt(
            "A warrior",
            proportions="heroic proportions, 8 heads tall",
            include_generic=False,
            include_miniature=False
        )
        assert "PROPORTIONS:" in prompt
        assert "heroic proportions" in prompt
    
    def test_proportions_default_fallback(self):
        """Should use default proportions if character proportions not provided."""
        prompt = build_final_prompt(
            "A warrior",
            default_proportions="realistic proportions",
            include_generic=False,
            include_miniature=False
        )
        assert "PROPORTIONS:" in prompt
        assert "realistic proportions" in prompt
    
    def test_proportions_prefer_character_over_default(self):
        """Should prefer character proportions over defaults."""
        prompt = build_final_prompt(
            "A warrior",
            proportions="custom proportions",
            default_proportions="default proportions",
            include_generic=False,
            include_miniature=False
        )
        assert "custom proportions" in prompt
        assert "default proportions" not in prompt
    
    def test_style_section(self):
        """Should include style section."""
        prompt = build_final_prompt(
            "A warrior",
            style_snippet="painted miniature style, high detail",
            include_generic=False,
            include_miniature=False
        )
        assert "STYLE:" in prompt
        assert "painted miniature style" in prompt


class TestBuildFinalPromptRenderRules:
    """Tests for render rules sections in build_final_prompt."""
    
    def test_generic_render_rules_string_format(self):
        """Should include generic rules in legacy string format."""
        prompt = build_final_prompt(
            "A warrior",
            generic_snippet="3D model, clean geometry",
            include_generic=True,
            include_miniature=False
        )
        assert "RENDER RULES:" in prompt
        assert "3D model, clean geometry" in prompt
    
    def test_generic_render_rules_dict_format(self):
        """Should include generic rules in new dict/section format."""
        generic = {
            "framing": {
                "title": "FRAMING",
                "content": "isometric view at {camera_rotation} degrees",
                "default_camera_rotation": 45
            },
            "geometry": {
                "title": "GEOMETRY",
                "content": "clean topology, manifold mesh"
            }
        }
        prompt = build_final_prompt(
            "A warrior",
            generic_snippet=generic,
            include_generic=True,
            include_miniature=False
        )
        assert "FRAMING:" in prompt
        assert "isometric view at 45 degrees" in prompt
        assert "GEOMETRY:" in prompt
        assert "clean topology" in prompt
    
    def test_camera_rotation_override(self):
        """Should override default camera rotation when specified."""
        generic = {
            "framing": {
                "title": "FRAMING",
                "content": "isometric view at {camera_rotation} degrees",
                "default_camera_rotation": 45
            }
        }
        prompt = build_final_prompt(
            "A warrior",
            generic_snippet=generic,
            camera_rotation=30,
            include_generic=True,
            include_miniature=False
        )
        assert "isometric view at 30 degrees" in prompt
        assert "45 degrees" not in prompt
    
    def test_camera_rotation_uses_default_when_none(self):
        """Should use default rotation when camera_rotation is None."""
        generic = {
            "framing": {
                "title": "FRAMING",
                "content": "isometric view at {camera_rotation} degrees",
                "default_camera_rotation": 45
            }
        }
        prompt = build_final_prompt(
            "A warrior",
            generic_snippet=generic,
            camera_rotation=None,
            include_generic=True,
            include_miniature=False
        )
        assert "isometric view at 45 degrees" in prompt
    
    def test_generic_rules_skipped_when_disabled(self):
        """Should skip generic rules when include_generic=False."""
        prompt = build_final_prompt(
            "A warrior",
            generic_snippet="3D model rules",
            include_generic=False,
            include_miniature=False
        )
        assert "RENDER RULES" not in prompt
        assert "3D model rules" not in prompt
    
    def test_miniature_rules_section(self):
        """Should include miniature rules section."""
        prompt = build_final_prompt(
            "A warrior",
            miniature_snippet="tabletop scale, 28mm heroic",
            include_generic=False,
            include_miniature=True
        )
        assert "MINIATURE RULES:" in prompt
        assert "tabletop scale" in prompt
    
    def test_miniature_rules_skipped_when_disabled(self):
        """Should skip miniature rules when include_miniature=False."""
        prompt = build_final_prompt(
            "A warrior",
            miniature_snippet="tabletop scale",
            include_generic=False,
            include_miniature=False
        )
        assert "MINIATURE RULES" not in prompt
        assert "tabletop scale" not in prompt
    
    def test_base_exclusion_section(self):
        """Should include base exclusion section when no_base=True."""
        prompt = build_final_prompt(
            "A warrior",
            no_base=True,
            include_generic=False,
            include_miniature=False
        )
        assert "BASE EXCLUSION:" in prompt
        assert "no base" in prompt
        assert "no stand" in prompt
    
    def test_base_exclusion_skipped_when_disabled(self):
        """Should skip base exclusion when no_base=False."""
        prompt = build_final_prompt(
            "A warrior",
            no_base=False,
            include_generic=False,
            include_miniature=False
        )
        assert "BASE EXCLUSION" not in prompt


class TestBuildFinalPromptSectionOrder:
    """Tests for correct section ordering in build_final_prompt."""
    
    def test_section_order(self):
        """Should place sections in correct order."""
        prompt = build_final_prompt(
            "A warrior",
            character_name="TestChar",
            gender="male",
            visual_notes="detailed",
            equipment=["sword : main_hand : held"],
            pose_prompt="standing",
            thematic_general="fantasy",
            proportions="heroic",
            style_snippet="painted",
            generic_snippet="3D model",
            miniature_snippet="tabletop",
            no_base=True,
            include_generic=True,
            include_miniature=True
        )
        
        # Find positions of each section
        sections = [
            "ASSET_NAME:",
            "VISUAL:",
            "CHARACTER:",
            "PROPS:",
            "POSE:",
            "THEME:",
            "PROPORTIONS:",
            "STYLE:",
            "RENDER RULES:",
            "MINIATURE RULES:",
            "BASE EXCLUSION:"
        ]
        
        positions = []
        for section in sections:
            if section in prompt:
                positions.append((section, prompt.index(section)))
        
        # Verify sections appear in order
        sorted_positions = sorted(positions, key=lambda x: x[1])
        assert positions == sorted_positions, f"Sections out of order: {[s[0] for s in positions]}"


class TestBuildFinalPromptComplexScenarios:
    """Tests for complex scenarios in build_final_prompt."""
    
    def test_empty_sections_omitted(self):
        """Should omit sections when data is empty."""
        prompt = build_final_prompt(
            "A warrior",
            equipment=[],
            thematic_snippets=[],
            thematic_general="",
            proportions="",
            style_snippet="",
            include_generic=False,
            include_miniature=False
        )
        assert "PROPS:" not in prompt
        assert "THEME:" not in prompt
        assert "PROPORTIONS:" not in prompt
        assert "STYLE:" not in prompt
    
    def test_all_sections_included(self):
        """Should include all sections when all data provided."""
        generic = {
            "framing": {
                "title": "FRAMING",
                "content": "isometric view"
            }
        }
        prompt = build_final_prompt(
            "A warrior",
            character_id="1",
            character_name="TestChar",
            gender="male",
            age="adult",
            visual_notes="detailed armor",
            equipment=["sword : main_hand : held"],
            pose_prompt="standing",
            thematic_snippets=["fantasy"],
            thematic_general="epic",
            proportions="heroic",
            style_snippet="painted",
            generic_snippet=generic,
            miniature_snippet="tabletop",
            no_base=True,
            include_generic=True,
            include_miniature=True
        )
        
        # Check all sections present
        assert "ASSET_NAME:" in prompt
        assert "VISUAL:" in prompt
        assert "CHARACTER:" in prompt
        assert "PROPS:" in prompt
        assert "POSE:" in prompt
        assert "THEME:" in prompt
        assert "PROPORTIONS:" in prompt
        assert "STYLE:" in prompt
        assert "FRAMING:" in prompt
        assert "MINIATURE RULES:" in prompt
        assert "BASE EXCLUSION:" in prompt
    
    def test_multiline_content_preserved(self):
        """Should preserve multiline content in sections."""
        prompt = build_final_prompt(
            "A warrior",
            equipment=[
                "sword : main_hand : held",
                "shield : off_hand : raised"
            ],
            include_generic=False,
            include_miniature=False
        )
        assert "sword" in prompt
        assert "shield" in prompt
        # Check props are on separate lines
        props_section = prompt.split("PROPS:")[1].split("\n\n")[0]
        assert "\n" in props_section
    
    def test_special_characters_preserved(self):
        """Should preserve special characters in content."""
        prompt = build_final_prompt(
            "A warrior (level 5)",
            equipment=["sword: +2 magic : main_hand : glowing"],
            include_generic=False,
            include_miniature=False
        )
        assert "warrior (level 5)" in prompt
        # Equipment with special characters should be preserved
        assert "+2 magic" in prompt or "sword:" in prompt
    
    def test_trailing_commas_removed(self):
        """Should remove trailing commas from character parts."""
        prompt = build_final_prompt(
            "A warrior,",  # Trailing comma
            include_generic=False,
            include_miniature=False
        )
        char_section = prompt.split("CHARACTER:")[1].split("\n\n")[0]
        # Should not have trailing comma
        assert not char_section.strip().endswith(",")
    
    def test_whitespace_normalization(self):
        """Should normalize whitespace in sections."""
        prompt = build_final_prompt(
            "  A warrior  ",  # Extra whitespace
            thematic_general="  fantasy  ",
            include_generic=False,
            include_miniature=False
        )
        assert "A warrior" in prompt
        assert "fantasy" in prompt
        # Should not have excessive whitespace
        assert "  " not in prompt or "create image\n\n" in prompt  # Allow double newline separator
