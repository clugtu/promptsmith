"""Additional unit tests for character_resolver module to ensure complete coverage."""
import pytest
import character_resolver


class TestFindCharacterEdgeCases:
    """Additional edge case tests for character lookup."""
    
    def test_find_character_with_empty_characters_list(self):
        """Test finding character when characters list is empty."""
        json_data = {"characters": []}
        result = character_resolver.find_character_by_id_or_name(json_data, 1)
        assert result is None
    
    def test_find_character_with_no_characters_key(self):
        """Test finding character when 'characters' key doesn't exist."""
        json_data = {}
        result = character_resolver.find_character_by_id_or_name(json_data, 1)
        assert result is None
    
    def test_find_character_by_mixed_case_name(self):
        """Test that name matching is case-insensitive."""
        json_data = {
            "characters": [
                {"id": 1, "name": "AlPhA"},
                {"id": 2, "name": "BETA"}
            ]
        }
        result = character_resolver.find_character_by_id_or_name(json_data, "alpha")
        assert result is not None
        assert result["name"] == "AlPhA"
        
        result = character_resolver.find_character_by_id_or_name(json_data, "Beta")
        assert result is not None
        assert result["name"] == "BETA"
    
    def test_find_character_string_id_vs_name_priority(self):
        """Test that numeric string IDs are tried before name matching."""
        json_data = {
            "characters": [
                {"id": 1, "name": "2"},  # Name is "2"
                {"id": 2, "name": "Second"}
            ]
        }
        # Should find ID 2, not the character with name "2"
        result = character_resolver.find_character_by_id_or_name(json_data, "2")
        assert result is not None
        assert result["name"] == "Second"
    
    def test_find_character_with_none_identifier(self):
        """Test handling of None as identifier."""
        json_data = {
            "characters": [{"id": 1, "name": "Test"}]
        }
        result = character_resolver.find_character_by_id_or_name(json_data, None)
        assert result is None
    
    def test_find_character_with_empty_string(self):
        """Test handling of empty string identifier."""
        json_data = {
            "characters": [{"id": 1, "name": "Test"}]
        }
        result = character_resolver.find_character_by_id_or_name(json_data, "")
        assert result is None
    
    def test_find_character_with_zero_id(self):
        """Test finding character with ID 0."""
        json_data = {
            "characters": [
                {"id": 0, "name": "Zero"},
                {"id": 1, "name": "One"}
            ]
        }
        result = character_resolver.find_character_by_id_or_name(json_data, 0)
        assert result is not None
        assert result["name"] == "Zero"
    
    def test_find_character_negative_id(self):
        """Test finding character with negative ID."""
        json_data = {
            "characters": [
                {"id": -1, "name": "Negative"},
                {"id": 1, "name": "Positive"}
            ]
        }
        result = character_resolver.find_character_by_id_or_name(json_data, -1)
        assert result is not None
        assert result["name"] == "Negative"


class TestFindRefinementEdgeCases:
    """Additional edge case tests for refinement lookup."""
    
    def test_find_refinement_empty_list(self):
        """Test finding refinement in empty list."""
        result = character_resolver.find_refinement_by_id_or_name([], 1)
        assert result is None
    
    def test_find_refinement_by_mixed_case_name(self):
        """Test that refinement name matching is case-insensitive."""
        refinements = [
            {"id": 1, "name": "HuMaN"},
            {"id": 2, "name": "WEREWOLF"}
        ]
        result = character_resolver.find_refinement_by_id_or_name(refinements, "human")
        assert result is not None
        assert result["name"] == "HuMaN"
    
    def test_find_refinement_string_id_vs_name_priority(self):
        """Test that numeric string IDs are tried before name matching."""
        refinements = [
            {"id": 1, "name": "2"},
            {"id": 2, "name": "Second"}
        ]
        # Should find ID 2, not the refinement with name "2"
        result = character_resolver.find_refinement_by_id_or_name(refinements, "2")
        assert result is not None
        assert result["name"] == "Second"
    
    def test_find_refinement_with_none_identifier(self):
        """Test handling of None as identifier."""
        refinements = [{"id": 1, "name": "Test"}]
        result = character_resolver.find_refinement_by_id_or_name(refinements, None)
        assert result is None
    
    def test_find_refinement_with_empty_string(self):
        """Test handling of empty string identifier."""
        refinements = [{"id": 1, "name": "Test"}]
        result = character_resolver.find_refinement_by_id_or_name(refinements, "")
        assert result is None
    
    def test_find_refinement_with_zero_id(self):
        """Test finding refinement with ID 0."""
        refinements = [
            {"id": 0, "name": "Zero"},
            {"id": 1, "name": "One"}
        ]
        result = character_resolver.find_refinement_by_id_or_name(refinements, 0)
        assert result is not None
        assert result["name"] == "Zero"
    
    def test_find_refinement_with_float_id(self):
        """Test handling of float as identifier."""
        refinements = [
            {"id": 1, "name": "One"},
            {"id": 2, "name": "Two"}
        ]
        # Float should be converted to int
        result = character_resolver.find_refinement_by_id_or_name(refinements, 1.0)
        assert result is not None
        assert result["name"] == "One"
    
    def test_find_refinement_missing_name_field(self):
        """Test handling refinements without name field."""
        refinements = [
            {"id": 1},  # No name field
            {"id": 2, "name": "Second"}
        ]
        result = character_resolver.find_refinement_by_id_or_name(refinements, "first")
        assert result is None


class TestParseRefinementPath:
    """Test refinement path parsing."""
    
    def test_parse_simple_numeric_path(self):
        """Test parsing simple numeric path."""
        result = character_resolver.parse_refinement_path("1:1")
        assert result == ["1", "1"]
    
    def test_parse_simple_string_path(self):
        """Test parsing simple string path."""
        result = character_resolver.parse_refinement_path("alpha:human")
        assert result == ["alpha", "human"]
    
    def test_parse_mixed_path(self):
        """Test parsing mixed numeric and string path."""
        result = character_resolver.parse_refinement_path("1:human")
        assert result == ["1", "human"]
    
    def test_parse_path_with_spaces(self):
        """Test that spaces are trimmed from components."""
        result = character_resolver.parse_refinement_path(" alpha : human ")
        assert result == ["alpha", "human"]
    
    def test_parse_path_with_extra_colons(self):
        """Test handling of extra colons."""
        result = character_resolver.parse_refinement_path("alpha::human")
        assert result == ["alpha", "human"]
    
    def test_parse_single_component(self):
        """Test parsing path with single component (no colon)."""
        result = character_resolver.parse_refinement_path("alpha")
        assert result == ["alpha"]
    
    def test_parse_empty_path(self):
        """Test parsing empty path."""
        result = character_resolver.parse_refinement_path("")
        assert result == []
    
    def test_parse_path_only_colons(self):
        """Test parsing path with only colons."""
        result = character_resolver.parse_refinement_path(":::")
        assert result == []
    
    def test_parse_three_component_path(self):
        """Test parsing path with three components."""
        result = character_resolver.parse_refinement_path("char:form:subform")
        assert result == ["char", "form", "subform"]
    
    def test_parse_path_with_numbers_and_special_chars(self):
        """Test parsing path with special characters."""
        result = character_resolver.parse_refinement_path("alpha-1:human_form")
        assert result == ["alpha-1", "human_form"]


class TestModuleInterface:
    """Test that the module can be imported and used independently."""
    
    def test_module_has_all_expected_functions(self):
        """Test that all expected functions are available."""
        assert hasattr(character_resolver, 'find_character_by_id_or_name')
        assert hasattr(character_resolver, 'find_refinement_by_id_or_name')
        assert hasattr(character_resolver, 'parse_refinement_path')
    
    def test_functions_are_callable(self):
        """Test that all functions are callable."""
        assert callable(character_resolver.find_character_by_id_or_name)
        assert callable(character_resolver.find_refinement_by_id_or_name)
        assert callable(character_resolver.parse_refinement_path)
    
    def test_module_docstring_exists(self):
        """Test that module has documentation."""
        assert character_resolver.__doc__ is not None
        assert len(character_resolver.__doc__) > 0
    
    def test_function_docstrings_exist(self):
        """Test that functions have documentation."""
        assert character_resolver.find_character_by_id_or_name.__doc__ is not None
        assert character_resolver.find_refinement_by_id_or_name.__doc__ is not None
        assert character_resolver.parse_refinement_path.__doc__ is not None
