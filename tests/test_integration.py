"""Integration tests comparing actual prompt outputs to golden reference files.

These tests validate that changes to create_image.py don't alter the generated prompts.
They use real character files and compare against pre-generated golden outputs.
"""
import pytest
from pathlib import Path
import json
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import create_image
from prompt_builder import build_final_prompt


class TestPlayerDenizenIntegration:
    """Integration tests for player_denizen_standees.json."""
    
    @pytest.fixture
    def player_json_path(self, standees_path):
        """Path to player denizen JSON."""
        return standees_path / "player_denizen_standees.json"
    
    @pytest.fixture
    def player_json_data(self, player_json_path):
        """Loaded player denizen JSON data."""
        return create_image.load_json_data(player_json_path)
    
    def test_player_denizen_1_1(self, player_json_data):
        """Test character 1, pose 1 matches golden output."""
        golden_path = Path(__file__).parent / "golden_outputs" / "player_denizen_1_1.txt"
        if not golden_path.exists():
            pytest.skip(f"Golden output not found: {golden_path}")
        
        # Generate prompt
        prompt0, thematic, gender, proportions, age, equipment, pose_prompt, camera_rotation, visual_notes = \
            create_image.resolve_prompt_from_json(player_json_data, character=1, form=1)
        
        # Build full prompt
        generic_snippet = create_image.extract_generic_snippet(player_json_data)
        miniature_snippet = create_image.extract_miniature_snippet(player_json_data)
        thematic_general = create_image.extract_thematic_snippet(player_json_data)
        style_snippet = create_image.extract_style_snippet(player_json_data)
        default_proportions = create_image.extract_default_proportions(player_json_data)
        
        # Get character data for naming
        char_data = create_image.find_character_by_id_or_name(player_json_data, 1)
        character_name = char_data.get("name", "1") if char_data else "1"
        character_archetype = char_data.get("archetype", "") if char_data else ""
        
        prompt = build_final_prompt(
            prompt0,
            gender=gender,
            thematic_snippets=thematic,
            thematic_general=thematic_general,
            proportions=proportions,
            age=age,
            default_proportions=default_proportions,
            style_snippet=style_snippet,
            generic_snippet=generic_snippet,
            miniature_snippet=miniature_snippet,
            include_generic=True,
            include_miniature=False,  # --no-base flag
            no_base=True,
            equipment=equipment,
            character_id=character_name,
            character_name=character_archetype,
            form_id="1",
            pose_prompt=pose_prompt,
            camera_rotation=camera_rotation,
            visual_notes=visual_notes,
        )
        
        # Format like command-line output
        formatted_prompt = "create image: " + create_image.sanitize_for_ascii(create_image.format_for_chat(prompt))
        
        # Load golden output
        expected = golden_path.read_text(encoding='utf-8').strip()
        actual = formatted_prompt.strip()
        
        # Compare
        assert actual == expected, f"Output differs from golden file {golden_path}"
    
    def test_player_denizen_all_characters(self, player_json_data):
        """Test all player denizen characters/poses match golden output."""
        golden_path = Path(__file__).parent / "golden_outputs" / "player_denizens_all.txt"
        if not golden_path.exists():
            pytest.skip(f"Golden output not found: {golden_path}")
        
        # Get shared snippets
        generic_snippet = create_image.extract_generic_snippet(player_json_data)
        miniature_snippet = create_image.extract_miniature_snippet(player_json_data)
        thematic_general = create_image.extract_thematic_snippet(player_json_data)
        style_snippet = create_image.extract_style_snippet(player_json_data)
        default_proportions = create_image.extract_default_proportions(player_json_data)
        
        # Generate all prompts
        blocks = []
        characters = player_json_data.get("characters", [])
        
        for char_data in characters:
            character_id = char_data.get("name", "") or char_data.get("id", "")
            character_archetype = char_data.get("archetype", "")
            
            poses = char_data.get("poses", [])
            for pose in poses:
                pose_name = pose.get("name", "")
                
                # Resolve prompt
                p0, thematic_snip, gender_for_prompt, ref_proportions, age, equipment, pose_prompt, camera_rotation, visual_notes = \
                    create_image.resolve_prompt_from_json(player_json_data, character=character_id, form=pose_name)
                
                proportions_to_use = ref_proportions if ref_proportions else char_data.get("proportions", "").strip()
                
                p = build_final_prompt(
                    p0,
                    gender=gender_for_prompt,
                    thematic_snippets=thematic_snip,
                    thematic_general=thematic_general,
                    proportions=proportions_to_use,
                    age=age,
                    default_proportions=default_proportions,
                    style_snippet=style_snippet,
                    generic_snippet=generic_snippet,
                    miniature_snippet=miniature_snippet,
                    include_generic=True,
                    include_miniature=False,
                    no_base=True,
                    equipment=equipment,
                    character_id=str(character_id),
                    character_name=character_archetype,
                    form_id=pose_name,
                    pose_prompt=pose_prompt,
                    camera_rotation=camera_rotation,
                    visual_notes=visual_notes,
                )
                
                blocks.append(f"[{character_id}:{pose_name}]\n{create_image.sanitize_for_ascii(create_image.format_for_chat(p))}")
        
        actual = "\n\n".join(blocks).strip() + "\n"
        expected = golden_path.read_text(encoding='utf-8')
        
        assert actual == expected, f"Output differs from golden file {golden_path}"


class TestEnemyDenizenIntegration:
    """Integration tests for enemy_denizens_standees.json."""
    
    @pytest.fixture
    def enemy_json_path(self, standees_path):
        """Path to enemy denizen JSON."""
        return standees_path / "enemy_denizens_standees.json"
    
    @pytest.fixture
    def enemy_json_data(self, enemy_json_path):
        """Loaded enemy denizen JSON data."""
        return create_image.load_json_data(enemy_json_path)
    
    @pytest.mark.parametrize("char_id,pose_id", [
        (1, 1),
        (1, 2),
        (2, 1),
    ])
    def test_enemy_denizen_sample_poses(self, enemy_json_data, char_id, pose_id):
        """Test sample enemy poses match golden outputs."""
        golden_path = Path(__file__).parent / "golden_outputs" / f"enemy_denizen_{char_id}_{pose_id}.txt"
        if not golden_path.exists():
            pytest.skip(f"Golden output not found: {golden_path}")
        
        # Generate prompt
        prompt0, thematic, gender, proportions, age, equipment, pose_prompt, camera_rotation, visual_notes = \
            create_image.resolve_prompt_from_json(enemy_json_data, character=char_id, form=pose_id)
        
        # Build full prompt
        generic_snippet = create_image.extract_generic_snippet(enemy_json_data)
        miniature_snippet = create_image.extract_miniature_snippet(enemy_json_data)
        thematic_general = create_image.extract_thematic_snippet(enemy_json_data)
        style_snippet = create_image.extract_style_snippet(enemy_json_data)
        default_proportions = create_image.extract_default_proportions(enemy_json_data)
        
        # Get character data
        char_data = create_image.find_character_by_id_or_name(enemy_json_data, char_id)
        character_name = char_data.get("name", str(char_id)) if char_data else str(char_id)
        character_archetype = char_data.get("archetype", "") if char_data else ""
        
        prompt = build_final_prompt(
            prompt0,
            gender=gender,
            thematic_snippets=thematic,
            thematic_general=thematic_general,
            proportions=proportions,
            age=age,
            default_proportions=default_proportions,
            style_snippet=style_snippet,
            generic_snippet=generic_snippet,
            miniature_snippet=miniature_snippet,
            include_generic=True,
            include_miniature=False,
            no_base=True,
            equipment=equipment,
            character_id=character_name,
            character_name=character_archetype,
            form_id=str(pose_id),
            pose_prompt=pose_prompt,
            camera_rotation=camera_rotation,
            visual_notes=visual_notes,
        )
        
        # Format like command-line output
        formatted_prompt = "create image: " + create_image.sanitize_for_ascii(create_image.format_for_chat(prompt))
        
        # Load golden output
        expected = golden_path.read_text(encoding='utf-8').strip()
        actual = formatted_prompt.strip()
        
        # Compare
        assert actual == expected, f"Output differs from golden file {golden_path}"


class TestGarouIntegration:
    """Integration tests for garou.json (OneDrive)."""
    
    @pytest.fixture
    def garou_json_path(self, custom_path):
        """Path to garou JSON."""
        return custom_path / "Garou" / "garou.json"
    
    @pytest.fixture
    def garou_json_data(self, garou_json_path):
        """Loaded garou JSON data."""
        return create_image.load_json_data(garou_json_path)
    
    @pytest.mark.parametrize("char_name,form_name", [
        ("alpha", "human"),
        ("alpha", "crinos"),
        ("breaker", "human"),
    ])
    def test_garou_character_forms(self, garou_json_data, char_name, form_name):
        """Test garou character forms match golden outputs."""
        safe_char = char_name.lower().replace(" ", "_")
        golden_path = Path(__file__).parent / "golden_outputs" / f"garou_{safe_char}_{form_name}.txt"
        if not golden_path.exists():
            pytest.skip(f"Golden output not found: {golden_path}")
        
        # Generate prompt
        prompt0, thematic, gender, proportions, age, equipment, pose_prompt, camera_rotation, visual_notes = \
            create_image.resolve_prompt_from_json(garou_json_data, character=char_name, form=form_name)
        
        # Build full prompt
        generic_snippet = create_image.extract_generic_snippet(garou_json_data)
        miniature_snippet = create_image.extract_miniature_snippet(garou_json_data)
        thematic_general = create_image.extract_thematic_snippet(garou_json_data)
        style_snippet = create_image.extract_style_snippet(garou_json_data)
        default_proportions = create_image.extract_default_proportions(garou_json_data)
        
        # Get character data
        char_data = create_image.find_character_by_id_or_name(garou_json_data, char_name)
        character_archetype = char_data.get("archetype", "") if char_data else ""
        
        prompt = build_final_prompt(
            prompt0,
            gender=gender,
            thematic_snippets=thematic,
            thematic_general=thematic_general,
            proportions=proportions,
            age=age,
            default_proportions=default_proportions,
            style_snippet=style_snippet,
            generic_snippet=generic_snippet,
            miniature_snippet=miniature_snippet,
            include_generic=True,
            include_miniature=True,
            no_base=False,
            equipment=equipment,
            character_id=char_name,
            character_name=character_archetype,
            form_id=form_name,
            pose_prompt=pose_prompt,
            camera_rotation=camera_rotation,
            visual_notes=visual_notes,
        )
        
        # Format like command-line output
        formatted_prompt = "create image: " + create_image.sanitize_for_ascii(create_image.format_for_chat(prompt))
        
        # Load golden output
        expected = golden_path.read_text(encoding='utf-8').strip()
        actual = formatted_prompt.strip()
        
        # Compare
        assert actual == expected, f"Output differs from golden file {golden_path}"
    
    def test_garou_all_characters(self, garou_json_data):
        """Test all garou characters/forms match golden output."""
        golden_path = Path(__file__).parent / "golden_outputs" / "garou_all.txt"
        if not golden_path.exists():
            pytest.skip(f"Golden output not found: {golden_path}")
        
        # Get shared snippets
        generic_snippet = create_image.extract_generic_snippet(garou_json_data)
        miniature_snippet = create_image.extract_miniature_snippet(garou_json_data)
        thematic_general = create_image.extract_thematic_snippet(garou_json_data)
        style_snippet = create_image.extract_style_snippet(garou_json_data)
        default_proportions = create_image.extract_default_proportions(garou_json_data)
        
        # Generate all prompts
        blocks = []
        characters = garou_json_data.get("characters", [])
        
        for char_data in characters:
            character_id = char_data.get("name", "") or char_data.get("id", "")
            character_archetype = char_data.get("archetype", "")
            char_gender = char_data.get("gender", None)
            char_proportions = char_data.get("proportions", "").strip()
            
            poses = char_data.get("poses", [])
            for pose in poses:
                pose_name = pose.get("name", "")
                
                # Resolve prompt
                p0, thematic_snip, gender_for_prompt, ref_proportions, age, equipment, pose_prompt, camera_rotation, visual_notes = \
                    create_image.resolve_prompt_from_json(garou_json_data, character=character_id, form=pose_name)
                
                proportions_to_use = ref_proportions if ref_proportions else char_proportions
                gender_to_use = gender_for_prompt if gender_for_prompt else char_gender
                
                p = build_final_prompt(
                    p0,
                    gender=gender_to_use,
                    thematic_snippets=thematic_snip,
                    thematic_general=thematic_general,
                    proportions=proportions_to_use,
                    age=age,
                    default_proportions=default_proportions,
                    style_snippet=style_snippet,
                    generic_snippet=generic_snippet,
                    miniature_snippet=miniature_snippet,
                    include_generic=True,
                    include_miniature=True,
                    no_base=False,
                    equipment=equipment,
                    character_id=str(character_id),
                    character_name=character_archetype,
                    form_id=pose_name,
                    pose_prompt=pose_prompt,
                    camera_rotation=camera_rotation,
                    visual_notes=visual_notes,
                )
                
                blocks.append(f"[{character_id}:{pose_name}]\n{create_image.sanitize_for_ascii(create_image.format_for_chat(p))}")
        
        actual = "\n\n".join(blocks).strip() + "\n"
        expected = golden_path.read_text(encoding='utf-8')
        
        assert actual == expected, f"Output differs from golden file {golden_path}"


class TestReferenceSheetIntegration:
    """Integration tests for reference sheet generation."""
    
    def test_garou_reference_sheet_page_1(self, custom_path, capsys):
        """Test garou reference sheet page 1 matches golden output."""
        golden_path = Path(__file__).parent / "golden_outputs" / "reference_sheets" / "garou_page_1.txt"
        if not golden_path.exists():
            pytest.skip(f"Golden output not found: {golden_path}")
        
        garou_json_path = custom_path / "Garou" / "garou.json"
        json_data = create_image.load_json_data(garou_json_path)
        
        # Extract required snippets
        generic_snippet = create_image.extract_generic_snippet(json_data)
        miniature_snippet = create_image.extract_miniature_snippet(json_data)
        thematic_general = create_image.extract_thematic_snippet(json_data)
        style_snippet = create_image.extract_style_snippet(json_data)
        default_proportions = create_image.extract_default_proportions(json_data)
        thematic_forms = create_image.extract_thematic_forms(json_data)
        
        # Generate reference sheet using the actual function (it prints to stdout)
        result = create_image.handle_reference_sheet(
            json_data=json_data,
            spec="1",  # Page 1
            generic_snippet=generic_snippet,
            miniature_snippet=miniature_snippet,
            thematic_general=thematic_general,
            style_snippet=style_snippet,
            default_proportions=default_proportions,
            thematic_forms=thematic_forms,
            include_generic=True,
            include_miniature=True,
            no_base=False,
            copy=False,
        )
        
        assert result == 0, f"handle_reference_sheet returned {result}, expected 0"
        
        # Capture stdout output (function already includes "create image" prefix)
        captured = capsys.readouterr()
        actual = captured.out
        expected = golden_path.read_text(encoding='utf-8')
        
        assert actual == expected, f"Output differs from golden file {golden_path}"


class TestPromptConsistency:
    """Tests that verify prompt generation consistency across runs."""
    
    def test_same_input_produces_same_output(self, player_denizens_json):
        """Test that running the same prompt twice produces identical output."""
        json_data = create_image.load_json_data(player_denizens_json)
        
        # Generate prompt twice
        result1 = create_image.resolve_prompt_from_json(json_data, character=1, form=1)
        result2 = create_image.resolve_prompt_from_json(json_data, character=1, form=1)
        
        # Should be identical
        assert result1 == result2, "Same input should produce same output (non-deterministic behavior detected)"
    
    def test_character_lookup_by_id_vs_name(self, player_denizens_json):
        """Test that looking up character by ID or name produces same result."""
        json_data = create_image.load_json_data(player_denizens_json)
        
        # Get first character
        characters = json_data.get("characters", [])
        if not characters:
            pytest.skip("No characters in test file")
        
        first_char = characters[0]
        char_id = first_char.get("id")
        char_name = first_char.get("name")
        
        if not char_id or not char_name:
            pytest.skip("Character missing id or name")
        
        # Look up by ID and by name
        result_by_id = create_image.resolve_prompt_from_json(json_data, character=char_id, form=1)
        result_by_name = create_image.resolve_prompt_from_json(json_data, character=char_name, form=1)
        
        # Should be identical
        assert result_by_id == result_by_name, "Lookup by ID and name should produce same result"
