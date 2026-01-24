"""Additional unit tests for pose_library module to ensure complete coverage."""
import pytest
import pose_library


class TestExtractPoseLibrary:
    """Test extracting pose library from JSON data."""
    
    def test_extract_pose_library_present(self):
        """Test extracting pose library when present."""
        json_data = {
            "pose_library": {
                "poses": [
                    {"pose_id": "test_pose", "pose_prompt": "Test"}
                ]
            }
        }
        result = pose_library.extract_pose_library(json_data)
        assert result == json_data["pose_library"]
    
    def test_extract_pose_library_missing(self):
        """Test extracting pose library when not present."""
        json_data = {"characters": []}
        result = pose_library.extract_pose_library(json_data)
        assert result == {}
    
    def test_extract_pose_library_empty(self):
        """Test extracting empty pose library."""
        json_data = {"pose_library": {}}
        result = pose_library.extract_pose_library(json_data)
        assert result == {}


class TestFindPoseEdgeCases:
    """Additional edge cases for finding poses."""
    
    def test_find_pose_with_no_poses_key(self):
        """Test finding pose when 'poses' key doesn't exist."""
        pose_library_data = {}
        result = pose_library.find_pose_in_library(pose_library_data, "any_pose")
        assert result is None
    
    def test_find_pose_with_none_pose_library(self):
        """Test finding pose with invalid library data."""
        # Should handle gracefully
        result = pose_library.find_pose_in_library({}, "test_pose")
        assert result is None
    
    def test_find_pose_case_sensitive(self):
        """Test that pose_id matching is case-sensitive."""
        pose_library_data = {
            "poses": [
                {"pose_id": "TestPose", "pose_prompt": "Correct"}
            ]
        }
        result = pose_library.find_pose_in_library(pose_library_data, "testpose")
        assert result is None  # Should not match
        
        result = pose_library.find_pose_in_library(pose_library_data, "TestPose")
        assert result is not None  # Should match
    
    def test_find_pose_multiple_poses(self):
        """Test finding specific pose among multiple."""
        pose_library_data = {
            "poses": [
                {"pose_id": "pose1", "pose_prompt": "First"},
                {"pose_id": "pose2", "pose_prompt": "Second"},
                {"pose_id": "pose3", "pose_prompt": "Third"}
            ]
        }
        result = pose_library.find_pose_in_library(pose_library_data, "pose2")
        assert result is not None
        assert result["pose_prompt"] == "Second"


class TestComposePoseEdgeCases:
    """Additional edge cases for pose prompt composition."""
    
    def test_compose_with_equipment_no_colons(self):
        """Test compose with equipment in legacy format (no colons)."""
        character_data = {}
        pose_def = {"pose_library_ref": "test_pose"}
        pose_library_data = {
            "poses": [
                {"pose_id": "test_pose", "pose_prompt": "MAIN_HAND_PROP held high"}
            ]
        }
        json_data = {}
        equipment = ["simple sword"]  # No colons
        
        char_override, pose_prompt, camera_rotation = pose_library.compose_pose_prompt_from_library(
            character_data, pose_def, pose_library_data, json_data, equipment
        )
        
        # MAIN_HAND_PROP should not be replaced (no valid equipment format)
        assert "MAIN_HAND_PROP" in pose_prompt
    
    def test_compose_with_both_hand_props(self):
        """Test compose with both main_hand and off_hand props."""
        character_data = {}
        pose_def = {"pose_library_ref": "dual_wield"}
        pose_library_data = {
            "poses": [
                {"pose_id": "dual_wield", "pose_prompt": "MAIN_HAND_PROP in right, OFF_HAND_PROP in left"}
            ]
        }
        json_data = {}
        equipment = [
            "steel sword : main_hand : gripped",
            "wooden shield : off_hand : held"
        ]
        
        char_override, pose_prompt, camera_rotation = pose_library.compose_pose_prompt_from_library(
            character_data, pose_def, pose_library_data, json_data, equipment
        )
        
        assert "steel sword" in pose_prompt
        assert "wooden shield" in pose_prompt
        assert "MAIN_HAND_PROP" not in pose_prompt
        assert "OFF_HAND_PROP" not in pose_prompt
    
    def test_compose_with_prop_complex_description(self):
        """Test compose with prop that has complex description."""
        character_data = {}
        pose_def = {"pose_library_ref": "test_pose"}
        pose_library_data = {
            "poses": [
                {"pose_id": "test_pose", "pose_prompt": "Wielding MAIN_HAND_PROP"}
            ]
        }
        json_data = {}
        equipment = ["ornate longsword (enchanted, glowing) : main_hand : held firmly"]
        
        char_override, pose_prompt, camera_rotation = pose_library.compose_pose_prompt_from_library(
            character_data, pose_def, pose_library_data, json_data, equipment
        )
        
        # Should extract just "ornate longsword" before parentheses
        assert "ornate longsword" in pose_prompt
        assert "MAIN_HAND_PROP" not in pose_prompt
    
    def test_compose_with_grip_cluster_enhancement(self):
        """Test GRIP CLUSTER section enhancement with props."""
        character_data = {}
        pose_def = {"pose_library_ref": "test_pose"}
        pose_library_data = {
            "poses": [
                {
                    "pose_id": "test_pose",
                    "pose_prompt": "GRIP CLUSTER (MANDATORY): Hands are spatially locked together"
                }
            ]
        }
        json_data = {}
        equipment = ["sword : main_hand : gripped"]
        
        char_override, pose_prompt, camera_rotation = pose_library.compose_pose_prompt_from_library(
            character_data, pose_def, pose_library_data, json_data, equipment
        )
        
        assert "actively grips sword" in pose_prompt
        assert "hands are spatially locked together" in pose_prompt
    
    def test_compose_with_grip_cluster_dual_wield(self):
        """Test GRIP CLUSTER with both hands."""
        character_data = {}
        pose_def = {"pose_library_ref": "test_pose"}
        pose_library_data = {
            "poses": [
                {
                    "pose_id": "test_pose",
                    "pose_prompt": "GRIP CLUSTER (MANDATORY): Hands are spatially locked together"
                }
            ]
        }
        json_data = {}
        equipment = [
            "sword : main_hand : gripped",
            "dagger : off_hand : held"
        ]
        
        char_override, pose_prompt, camera_rotation = pose_library.compose_pose_prompt_from_library(
            character_data, pose_def, pose_library_data, json_data, equipment
        )
        
        assert "actively grips sword" in pose_prompt
        assert "actively grips dagger" in pose_prompt
    
    def test_compose_figure_type_mismatch_warning(self, capsys):
        """Test that figure type mismatch generates warning."""
        character_data = {}
        pose_def = {
            "pose_library_ref": "test_pose",
            "figure_type": "bipedal_humanoid"
        }
        pose_library_data = {
            "poses": [
                {
                    "pose_id": "test_pose",
                    "pose_prompt": "Standing",
                    "figure_type": "quadrupedal"
                }
            ]
        }
        json_data = {}
        equipment = []
        
        pose_library.compose_pose_prompt_from_library(
            character_data, pose_def, pose_library_data, json_data, equipment
        )
        
        captured = capsys.readouterr()
        assert "Warning" in captured.err or "warning" in captured.err.lower()
        assert "figure_type" in captured.err.lower() or "Figure type" in captured.err
    
    def test_compose_figure_type_compatible_mismatch(self):
        """Test compatible figure type mismatches (no warning)."""
        character_data = {}
        pose_def = {
            "pose_library_ref": "test_pose",
            "figure_type": "facultatively_bipedal"
        }
        pose_library_data = {
            "poses": [
                {
                    "pose_id": "test_pose",
                    "pose_prompt": "Standing",
                    "figure_type": "bipedal_humanoid"
                }
            ]
        }
        json_data = {}
        equipment = []
        
        # Should not raise or warn (compatible mismatch)
        char_override, pose_prompt, camera_rotation = pose_library.compose_pose_prompt_from_library(
            character_data, pose_def, pose_library_data, json_data, equipment
        )
        
        assert pose_prompt == "Standing"
    
    def test_compose_with_character_override_and_camera_rotation(self):
        """Test compose extracting both override and camera rotation."""
        character_data = {}
        pose_def = {
            "pose_library_ref": "test_pose",
            "character_override": "grinning menacingly"
        }
        pose_library_data = {
            "poses": [
                {
                    "pose_id": "test_pose",
                    "pose_prompt": "Standing ready",
                    "camera_rotation": 90
                }
            ]
        }
        json_data = {}
        equipment = []
        
        char_override, pose_prompt, camera_rotation = pose_library.compose_pose_prompt_from_library(
            character_data, pose_def, pose_library_data, json_data, equipment
        )
        
        assert char_override == "grinning menacingly"
        assert pose_prompt == "Standing ready"
        assert camera_rotation == 90


class TestValidatePoseCompatibilityEdgeCases:
    """Additional edge cases for pose compatibility validation."""
    
    def test_validate_with_missing_figure_type(self):
        """Test validation when character has no figure_type."""
        character_data = {}  # No figure_type
        character_pose_def = {}
        library_pose_def = {"figure_type": "bipedal_humanoid"}
        json_data = {}
        
        warnings = pose_library.validate_pose_compatibility(
            character_data, character_pose_def, library_pose_def, "test_pose", json_data
        )
        
        # Should not generate warnings when character figure_type is missing
        assert len([w for w in warnings if "figure_type" in w.lower()]) == 0
    
    def test_validate_figure_type_from_thematic_forms(self):
        """Test extracting figure_type from thematic forms."""
        character_data = {}
        character_pose_def = {"thematic_snippet": ["wolf_form"]}
        library_pose_def = {"figure_type": "quadrupedal"}
        json_data = {
            "thematic_rules": {
                "forms": {
                    "wolf_form": {
                        "figure_type": "quadrupedal",
                        "prompt_snippet": "wolf-like form"
                    }
                }
            }
        }
        
        warnings = pose_library.validate_pose_compatibility(
            character_data, character_pose_def, library_pose_def, "test_pose", json_data
        )
        
        # Should match figure types and not warn
        figure_type_warnings = [w for w in warnings if "mismatch" in w.lower()]
        assert len(figure_type_warnings) == 0
    
    def test_validate_invalid_pose_figure_type(self):
        """Test validation with invalid pose figure_type."""
        character_data = {"figure_type": "bipedal_humanoid"}
        character_pose_def = {}
        library_pose_def = {"figure_type": "invalid_type"}
        json_data = {}
        
        warnings = pose_library.validate_pose_compatibility(
            character_data, character_pose_def, library_pose_def, "test_pose", json_data
        )
        
        # Should warn about invalid pose figure_type
        assert len(warnings) > 0
        assert any("invalid" in w.lower() for w in warnings)
    
    def test_validate_invalid_character_figure_type(self):
        """Test validation with invalid character figure_type."""
        character_data = {"figure_type": "invalid_char_type"}
        character_pose_def = {}
        library_pose_def = {"figure_type": "bipedal_humanoid"}
        json_data = {}
        
        warnings = pose_library.validate_pose_compatibility(
            character_data, character_pose_def, library_pose_def, "test_pose", json_data
        )
        
        # Should warn about invalid character figure_type
        assert len(warnings) > 0
        assert any("invalid" in w.lower() for w in warnings)
    
    def test_validate_all_compatible_mismatches(self):
        """Test all defined compatible mismatch combinations."""
        compatible_pairs = [
            ("facultatively_bipedal", "bipedal_humanoid"),
            ("winged_bipedal", "bipedal_humanoid"),
            ("winged_centauroid", "centauroid"),
            ("multi_limbed_bipedal", "bipedal_humanoid"),
            ("multi_limbed_centauroid", "centauroid"),
        ]
        
        for char_type, pose_type in compatible_pairs:
            character_data = {"figure_type": char_type}
            character_pose_def = {}
            library_pose_def = {"figure_type": pose_type}
            json_data = {}
            
            warnings = pose_library.validate_pose_compatibility(
                character_data, character_pose_def, library_pose_def, "test_pose", json_data
            )
            
            # Should not generate mismatch warnings
            mismatch_warnings = [w for w in warnings if "mismatch" in w.lower()]
            assert len(mismatch_warnings) == 0, f"Unexpected warning for {char_type} + {pose_type}"


class TestRemoveBaseLanguage:
    """Test removing base language from miniature snippets."""
    
    def test_remove_base_mounted_on_round(self):
        """Test removing 'mounted on a round gaming base'."""
        snippet = "40mm miniature, mounted on a round gaming base (about 32mm), dramatic lighting"
        result = pose_library.remove_base_language(snippet)
        assert "base" not in result.lower()
        assert "40mm miniature" in result
        assert "dramatic lighting" in result
    
    def test_remove_base_on_gaming_base(self):
        """Test removing 'on a gaming base'."""
        snippet = "miniature scale, on a gaming base, painted"
        result = pose_library.remove_base_language(snippet)
        assert "base" not in result.lower()
        assert "miniature scale" in result
        assert "painted" in result
    
    def test_remove_base_plinth(self):
        """Test removing 'plinth'."""
        snippet = "figure, plinth, studio lighting"
        result = pose_library.remove_base_language(snippet)
        assert "plinth" not in result.lower()
        assert "figure" in result
        assert "studio lighting" in result
    
    def test_remove_base_multiple_patterns(self):
        """Test removing multiple base patterns."""
        snippet = "miniature, mounted on a base, round base, display"
        result = pose_library.remove_base_language(snippet)
        assert "base" not in result.lower()
        assert "miniature" in result
        assert "display" in result
    
    def test_remove_base_case_insensitive(self):
        """Test that removal is case-insensitive."""
        snippet = "Figure, Mounted On A Round Gaming BASE, painted"
        result = pose_library.remove_base_language(snippet)
        assert "base" not in result.lower()
        assert "Figure" in result
        assert "painted" in result
    
    def test_remove_base_preserve_non_base_content(self):
        """Test that non-base content is preserved."""
        snippet = "40mm scale, detailed painting, metallic finish, dramatic pose"
        result = pose_library.remove_base_language(snippet)
        assert result == snippet  # Nothing to remove
    
    def test_remove_base_empty_after_removal(self):
        """Test snippet that becomes empty after base removal."""
        snippet = "mounted on a gaming base"
        result = pose_library.remove_base_language(snippet)
        # Should return empty or minimal content
        assert len(result) < len(snippet)


class TestPromptNotFoundError:
    """Test the custom exception class."""
    
    def test_prompt_not_found_error_is_runtime_error(self):
        """Test that PromptNotFoundError is a RuntimeError."""
        assert issubclass(pose_library.PromptNotFoundError, RuntimeError)
    
    def test_prompt_not_found_error_can_be_raised(self):
        """Test raising PromptNotFoundError."""
        with pytest.raises(pose_library.PromptNotFoundError):
            raise pose_library.PromptNotFoundError("Test error")
    
    def test_prompt_not_found_error_message(self):
        """Test error message is preserved."""
        try:
            raise pose_library.PromptNotFoundError("Custom message")
        except pose_library.PromptNotFoundError as e:
            assert str(e) == "Custom message"


class TestModuleInterface:
    """Test that the module can be imported and used independently."""
    
    def test_module_has_all_expected_functions(self):
        """Test that all expected functions are available."""
        assert hasattr(pose_library, 'extract_pose_library')
        assert hasattr(pose_library, 'find_pose_in_library')
        assert hasattr(pose_library, 'compose_pose_prompt_from_library')
        assert hasattr(pose_library, 'validate_pose_compatibility')
        assert hasattr(pose_library, 'remove_base_language')
        assert hasattr(pose_library, 'PromptNotFoundError')
    
    def test_functions_are_callable(self):
        """Test that all functions are callable."""
        assert callable(pose_library.extract_pose_library)
        assert callable(pose_library.find_pose_in_library)
        assert callable(pose_library.compose_pose_prompt_from_library)
        assert callable(pose_library.validate_pose_compatibility)
        assert callable(pose_library.remove_base_language)
    
    def test_module_docstring_exists(self):
        """Test that module has documentation."""
        assert pose_library.__doc__ is not None
        assert len(pose_library.__doc__) > 0
    
    def test_function_docstrings_exist(self):
        """Test that functions have documentation."""
        assert pose_library.extract_pose_library.__doc__ is not None
        assert pose_library.find_pose_in_library.__doc__ is not None
        assert pose_library.compose_pose_prompt_from_library.__doc__ is not None
        assert pose_library.validate_pose_compatibility.__doc__ is not None
        assert pose_library.remove_base_language.__doc__ is not None
    
    def test_module_imports_required_dependencies(self):
        """Test that module has required imports."""
        import inspect
        source = inspect.getsource(pose_library)
        assert 'import re' in source
        assert 'import sys' in source
        assert 'from typing import' in source
