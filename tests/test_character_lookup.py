"""Tests for character and refinement lookup functions."""
import pytest
import create_image


class TestCharacterLookup:
    """Test finding characters by ID or name."""
    
    @pytest.fixture
    def sample_json_data(self):
        """Sample JSON data with multiple characters."""
        return {
            "characters": [
                {"id": 1, "name": "Alpha"},
                {"id": 2, "name": "Beta"},
                {"id": 3, "name": "Gamma"}
            ]
        }
    
    def test_find_character_by_numeric_id(self, sample_json_data):
        """Test finding character by numeric ID."""
        result = create_image.find_character_by_id_or_name(sample_json_data, 2)
        assert result is not None
        assert result["name"] == "Beta"
    
    def test_find_character_by_string_id(self, sample_json_data):
        """Test finding character by string representation of ID."""
        result = create_image.find_character_by_id_or_name(sample_json_data, "2")
        assert result is not None
        assert result["name"] == "Beta"
    
    def test_find_character_by_name(self, sample_json_data):
        """Test finding character by name (case-insensitive)."""
        result = create_image.find_character_by_id_or_name(sample_json_data, "gamma")
        assert result is not None
        assert result["id"] == 3
    
    def test_find_character_by_name_case_insensitive(self, sample_json_data):
        """Test finding character by name is case-insensitive."""
        result = create_image.find_character_by_id_or_name(sample_json_data, "ALPHA")
        assert result is not None
        assert result["id"] == 1
    
    def test_find_character_not_found(self, sample_json_data):
        """Test that None is returned for non-existent character."""
        result = create_image.find_character_by_id_or_name(sample_json_data, "NonExistent")
        assert result is None
    
    def test_find_character_invalid_id(self, sample_json_data):
        """Test that None is returned for invalid ID."""
        result = create_image.find_character_by_id_or_name(sample_json_data, 99)
        assert result is None


class TestRefinementLookup:
    """Test finding refinements by ID or name."""
    
    @pytest.fixture
    def sample_refinements(self):
        """Sample refinement list."""
        return [
            {"id": 1, "name": "standing"},
            {"id": 2, "name": "running"},
            {"id": 3, "name": "crouching"}
        ]
    
    def test_find_refinement_by_numeric_id(self, sample_refinements):
        """Test finding refinement by numeric ID."""
        result = create_image.find_refinement_by_id_or_name(sample_refinements, 2)
        assert result is not None
        assert result["name"] == "running"
    
    def test_find_refinement_by_string_id(self, sample_refinements):
        """Test finding refinement by string ID."""
        result = create_image.find_refinement_by_id_or_name(sample_refinements, "3")
        assert result is not None
        assert result["name"] == "crouching"
    
    def test_find_refinement_by_name(self, sample_refinements):
        """Test finding refinement by name (case-insensitive)."""
        result = create_image.find_refinement_by_id_or_name(sample_refinements, "standing")
        assert result is not None
        assert result["id"] == 1
    
    def test_find_refinement_not_found(self, sample_refinements):
        """Test that None is returned for non-existent refinement."""
        result = create_image.find_refinement_by_id_or_name(sample_refinements, "flying")
        assert result is None


class TestRefinementPathParsing:
    """Test parsing refinement paths like '1:1' or 'alpha:human'."""
    
    def test_parse_refinement_path_numeric(self):
        """Test parsing numeric path."""
        result = create_image.parse_refinement_path("1:2")
        assert result == ["1", "2"]
    
    def test_parse_refinement_path_names(self):
        """Test parsing name-based path."""
        result = create_image.parse_refinement_path("alpha:human")
        assert result == ["alpha", "human"]
    
    def test_parse_refinement_path_mixed(self):
        """Test parsing mixed numeric/name path."""
        result = create_image.parse_refinement_path("1:human")
        assert result == ["1", "human"]
    
    def test_parse_refinement_path_single(self):
        """Test parsing single element (no colon)."""
        result = create_image.parse_refinement_path("alpha")
        assert result == ["alpha"]
    
    def test_parse_refinement_path_triple(self):
        """Test parsing three-level path."""
        result = create_image.parse_refinement_path("1:2:3")
        assert result == ["1", "2", "3"]
    
    def test_parse_refinement_path_with_spaces(self):
        """Test parsing path with spaces (should be stripped)."""
        result = create_image.parse_refinement_path(" 1 : 2 ")
        assert result == ["1", "2"]
