"""Additional unit tests for equipment_handler module to ensure complete coverage."""
import pytest
import equipment_handler


class TestResolvePropReferencesEdgeCases:
    """Additional edge case tests for prop reference resolution."""
    
    def test_resolve_prop_references_empty_list(self):
        """Test resolving empty equipment list."""
        equipment = []
        prop_definitions = {"sword": "steel sword"}
        result = equipment_handler.resolve_prop_references(equipment, prop_definitions)
        assert result == []
    
    def test_resolve_prop_references_empty_prop_definitions(self):
        """Test resolving with empty prop definitions."""
        equipment = ["sword : main_hand : gripped"]
        prop_definitions = {}
        result = equipment_handler.resolve_prop_references(equipment, prop_definitions)
        assert result == equipment  # Should pass through unchanged
    
    def test_resolve_prop_references_no_colons(self):
        """Test resolving legacy format with no colons."""
        equipment = ["simple sword"]
        prop_definitions = {"sword": "steel sword"}
        result = equipment_handler.resolve_prop_references(equipment, prop_definitions)
        assert result == ["simple sword"]  # Should pass through unchanged
    
    def test_resolve_prop_references_single_colon(self):
        """Test resolving format with only one colon."""
        equipment = ["sword : main_hand"]
        prop_definitions = {"sword": "steel sword (sharp)"}
        result = equipment_handler.resolve_prop_references(equipment, prop_definitions)
        assert result == ["steel sword (sharp) : main_hand"]
    
    def test_resolve_prop_references_prop_id_with_parentheses(self):
        """Test that items with parentheses are not treated as prop IDs."""
        equipment = ["sword (rusty) : main_hand : gripped"]
        prop_definitions = {"sword (rusty)": "iron sword (very rusty)"}
        result = equipment_handler.resolve_prop_references(equipment, prop_definitions)
        # Should not resolve because first part has parentheses
        assert result == equipment
    
    def test_resolve_prop_references_prop_id_with_brackets(self):
        """Test that items with brackets are not treated as prop IDs."""
        equipment = ["sword [enchanted] : main_hand : glowing"]
        prop_definitions = {"sword [enchanted]": "magic sword [powerful]"}
        result = equipment_handler.resolve_prop_references(equipment, prop_definitions)
        # Should not resolve because first part has brackets
        assert result == equipment
    
    def test_resolve_prop_references_multiple_colons(self):
        """Test resolving with extra colons in description."""
        equipment = ["sword : main_hand : gripped firmly : at ready"]
        prop_definitions = {"sword": "steel sword (sharp)"}
        result = equipment_handler.resolve_prop_references(equipment, prop_definitions)
        assert result == ["steel sword (sharp) : main_hand : gripped firmly : at ready"]
    
    def test_resolve_prop_references_whitespace_handling(self):
        """Test that whitespace around colons is handled correctly."""
        equipment = ["  sword  :  main_hand  :  gripped  "]
        prop_definitions = {"sword": "steel sword"}
        result = equipment_handler.resolve_prop_references(equipment, prop_definitions)
        assert result == ["steel sword :  main_hand  :  gripped  "]
    
    def test_resolve_prop_references_prop_def_with_complex_description(self):
        """Test resolving prop with complex description including special chars."""
        equipment = ["holy_symbol : worn : around neck"]
        prop_definitions = {
            "holy_symbol": "silver holy symbol (sun motif, blessed by priest)"
        }
        result = equipment_handler.resolve_prop_references(equipment, prop_definitions)
        assert result == ["silver holy symbol (sun motif, blessed by priest) : worn : around neck"]


class TestValidateHandAssignmentsEdgeCases:
    """Additional edge case tests for hand assignment validation."""
    
    def test_validate_hand_assignments_none_form_id(self):
        """Test validation with None as form_id."""
        equipment = ["sword : main_hand : gripped"]
        char_data = {"figure_type": "bipedal_humanoid"}
        # Should not raise
        equipment_handler.validate_hand_assignments(equipment, "1", None, char_data)
    
    def test_validate_hand_assignments_missing_figure_type(self):
        """Test validation when figure_type is not specified."""
        equipment = ["sword : main_hand : gripped"]
        char_data = {}  # No figure_type
        # Should default to bipedal_humanoid (2 hands)
        equipment_handler.validate_hand_assignments(equipment, "1", "test", char_data)
    
    def test_validate_hand_assignments_only_spaces_in_position(self):
        """Test validation with whitespace-only position."""
        equipment = ["sword :   : gripped"]
        char_data = {"figure_type": "bipedal_humanoid"}
        # Should not raise (position is just whitespace, not a hand)
        equipment_handler.validate_hand_assignments(equipment, "1", "test", char_data)
    
    def test_validate_hand_assignments_case_sensitive_positions(self):
        """Test that position matching is case-sensitive."""
        equipment = [
            "sword : Main_Hand : gripped",  # Capital M - should not match
            "shield : off_hand : held"
        ]
        char_data = {"figure_type": "bipedal_humanoid"}
        # Should not raise (Main_Hand doesn't match main_hand)
        equipment_handler.validate_hand_assignments(equipment, "1", "test", char_data)
    
    def test_validate_hand_assignments_multi_limbed_with_exact_limit(self):
        """Test multi-limbed character using exactly 4 hands."""
        equipment = [
            "sword1 : main_hand : gripped",
            "sword2 : main_hand : gripped",
            "shield1 : off_hand : held",
            "shield2 : off_hand : held"
        ]
        char_data = {"figure_type": "multi_limbed_bipedal"}
        # Should not raise (4 hands is the limit for multi-limbed)
        equipment_handler.validate_hand_assignments(equipment, "1", "test", char_data)
    
    def test_validate_hand_assignments_multi_limbed_exceeds_limit(self, capsys):
        """Test multi-limbed character exceeding 4 hands generates warning."""
        equipment = [
            "sword1 : main_hand : gripped",
            "sword2 : main_hand : gripped",
            "sword3 : main_hand : gripped",
            "shield1 : off_hand : held",
            "shield2 : off_hand : held"
        ]
        char_data = {"figure_type": "multi_limbed_quadruped"}
        # Should not raise but should print warning
        equipment_handler.validate_hand_assignments(equipment, "1", "test", char_data)
        captured = capsys.readouterr()
        assert "WARNING" in captured.err
        assert "HAND CONFLICT" in captured.err
    
    def test_validate_hand_assignments_both_hands_on_multi_limbed(self, capsys):
        """Test both_hands assignment on multi-limbed character."""
        equipment = [
            "greatsword : both_hands : gripped",
            "sword : main_hand : held"
        ]
        char_data = {"figure_type": "multi_limbed_humanoid"}
        # Should print warning but not raise
        equipment_handler.validate_hand_assignments(equipment, "1", "test", char_data)
        captured = capsys.readouterr()
        assert "WARNING" in captured.err
    
    def test_validate_hand_assignments_special_positions(self):
        """Test that special positions like 'wielded', 'held', 'carried' are not counted."""
        equipment = [
            "sword : main_hand : gripped",
            "shield : off_hand : held",
            "torch : wielded : in left hand",  # 'wielded' not counted
            "bag : carried : over shoulder"     # 'carried' not counted
        ]
        char_data = {"figure_type": "bipedal_humanoid"}
        # Should not raise (wielded and carried are not hand positions)
        equipment_handler.validate_hand_assignments(equipment, "1", "test", char_data)
    
    def test_validate_hand_assignments_multiple_both_hands(self):
        """Test multiple both_hands assignments."""
        equipment = [
            "greatsword : both_hands : gripped",
            "staff : both_hands : held"
        ]
        char_data = {"figure_type": "bipedal_humanoid"}
        with pytest.raises(ValueError, match="HAND CONFLICT"):
            equipment_handler.validate_hand_assignments(equipment, "1", "test", char_data)
    
    def test_validate_hand_assignments_character_id_in_error(self):
        """Test that character and form IDs appear in error messages."""
        equipment = [
            "sword : main_hand : gripped",
            "axe : main_hand : held"
        ]
        char_data = {"figure_type": "bipedal_humanoid"}
        
        with pytest.raises(ValueError) as exc_info:
            equipment_handler.validate_hand_assignments(equipment, "alpha", "crinos", char_data)
        
        error_msg = str(exc_info.value)
        assert "alpha" in error_msg
        assert "crinos" in error_msg


class TestMultiLimbedCharacters:
    """Tests specifically for multi-limbed character handling."""
    
    def test_multi_limbed_detection_exact_string(self):
        """Test that 'multi_limbed' substring is detected."""
        test_cases = [
            "multi_limbed",
            "multi_limbed_humanoid",
            "multi_limbed_bipedal",
            "spider_multi_limbed",
        ]
        
        for figure_type in test_cases:
            equipment = [
                "sword1 : main_hand : gripped",
                "sword2 : main_hand : gripped"
            ]
            char_data = {"figure_type": figure_type}
            # Should not raise (multi-limbed allows warnings)
            equipment_handler.validate_hand_assignments(equipment, "1", "test", char_data)
    
    def test_non_multi_limbed_detection(self):
        """Test that similar strings without 'multi_limbed' are not detected."""
        test_cases = [
            "bipedal_humanoid",
            "quadruped",
            "limbed_creature",  # 'limbed' without 'multi_'
            "multiple_arms",    # 'multiple' not 'multi_limbed'
        ]
        
        for figure_type in test_cases:
            equipment = [
                "sword1 : main_hand : gripped",
                "sword2 : main_hand : gripped"
            ]
            char_data = {"figure_type": figure_type}
            # Should raise (not multi-limbed)
            with pytest.raises(ValueError, match="HAND CONFLICT"):
                equipment_handler.validate_hand_assignments(equipment, "1", "test", char_data)


class TestModuleInterface:
    """Test that the module can be imported and used independently."""
    
    def test_module_has_all_expected_functions(self):
        """Test that all expected functions are available."""
        assert hasattr(equipment_handler, 'resolve_prop_references')
        assert hasattr(equipment_handler, 'validate_hand_assignments')
    
    def test_functions_are_callable(self):
        """Test that all functions are callable."""
        assert callable(equipment_handler.resolve_prop_references)
        assert callable(equipment_handler.validate_hand_assignments)
    
    def test_module_docstring_exists(self):
        """Test that module has documentation."""
        assert equipment_handler.__doc__ is not None
        assert len(equipment_handler.__doc__) > 0
    
    def test_function_docstrings_exist(self):
        """Test that functions have documentation."""
        assert equipment_handler.resolve_prop_references.__doc__ is not None
        assert equipment_handler.validate_hand_assignments.__doc__ is not None
    
    def test_module_imports_required_dependencies(self):
        """Test that module has required imports."""
        import inspect
        source = inspect.getsource(equipment_handler)
        assert 'import sys' in source
        assert 'from typing import' in source
