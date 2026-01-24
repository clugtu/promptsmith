"""Tests for JSON loading, validation, and import resolution."""
import pytest
from pathlib import Path
import json
import tempfile
from src import json_loader
from src import create_image  # Keep for backwards compatibility in some tests


class TestJSONLoading:
    """Test JSON file loading and parsing."""
    
    def test_load_json_data_basic(self, tmp_path):
        """Test loading a basic JSON file."""
        json_file = tmp_path / "test.json"
        data = {"characters": [{"id": 1, "name": "Test"}]}
        json_file.write_text(json.dumps(data))
        
        result = json_loader.load_json_data(json_file)
        assert result == data
    
    def test_load_json_data_file_not_found(self, tmp_path):
        """Test that FileNotFoundError is raised for missing file."""
        json_file = tmp_path / "nonexistent.json"
        with pytest.raises(FileNotFoundError):
            json_loader.load_json_data(json_file)
    
    def test_load_json_data_invalid_json(self, tmp_path):
        """Test that invalid JSON raises an error."""
        json_file = tmp_path / "invalid.json"
        json_file.write_text("{invalid json")
        
        with pytest.raises(json.JSONDecodeError):
            json_loader.load_json_data(json_file)


class TestCharacterIDValidation:
    """Test character ID validation."""
    
    def test_validate_character_ids_sequential(self):
        """Test validation passes for sequential IDs."""
        characters = [
            {"id": 1, "name": "First"},
            {"id": 2, "name": "Second"},
            {"id": 3, "name": "Third"}
        ]
        # Should not raise
        json_loader.validate_character_ids(characters)
    
    def test_validate_character_ids_empty_list(self):
        """Test validation passes for empty list."""
        json_loader.validate_character_ids([])
    
    def test_validate_character_ids_no_ids(self):
        """Test validation passes when characters have no IDs."""
        characters = [{"name": "Test"}]
        json_loader.validate_character_ids(characters)
    
    def test_validate_character_ids_duplicate(self):
        """Test validation fails for duplicate IDs."""
        characters = [
            {"id": 1, "name": "First"},
            {"id": 2, "name": "Second"},
            {"id": 2, "name": "Duplicate"}
        ]
        with pytest.raises(ValueError, match="Duplicate character IDs"):
            json_loader.validate_character_ids(characters)
    
    def test_validate_character_ids_gap(self):
        """Test validation fails for non-sequential IDs."""
        characters = [
            {"id": 1, "name": "First"},
            {"id": 3, "name": "Third"}  # Missing ID 2
        ]
        with pytest.raises(ValueError, match="Missing IDs"):
            json_loader.validate_character_ids(characters)
    
    def test_validate_character_ids_wrong_start(self):
        """Test validation fails if IDs don't start at 1."""
        characters = [
            {"id": 0, "name": "Zero"},
            {"id": 1, "name": "One"}
        ]
        with pytest.raises(ValueError, match="Unexpected IDs"):
            json_loader.validate_character_ids(characters)


class TestPathResolution:
    """Test path resolution for imports."""
    
    def test_resolve_path_absolute(self, tmp_path):
        """Test resolving absolute paths."""
        absolute = tmp_path / "test.json"
        absolute.touch()
        result = json_loader.resolve_path(str(absolute), Path.cwd())
        assert result == absolute
    
    def test_resolve_path_relative(self, tmp_path):
        """Test resolving relative paths."""
        base_dir = tmp_path / "base"
        base_dir.mkdir()
        
        target_file = tmp_path / "target.json"
        target_file.touch()
        
        # Relative path from base_dir to target_file
        result = json_loader.resolve_path("../target.json", base_dir)
        assert result == target_file
    
    def test_resolve_path_git_bash_drive(self):
        """Test resolving Git Bash style paths on Windows (e.g., /c/Users)."""
        import os
        if os.name != "nt":
            pytest.skip("Windows-only test")
        
        # Git Bash path: /c/dev/test.json -> C:/dev/test.json
        result = json_loader.resolve_path("/c/dev/test.json", Path.cwd())
        assert str(result).startswith("C:")


class TestImportResolution:
    """Test import resolution."""
    
    def test_resolve_imports_no_imports(self):
        """Test that data without imports is unchanged."""
        data = {"characters": []}
        result = json_loader.resolve_imports(data, Path.cwd())
        assert result == data
    
    def test_resolve_imports_generic_rules(self, tmp_path):
        """Test resolving generic_render_rules import."""
        # Create a rules file
        rules_file = tmp_path / "rules.json"
        rules_file.write_text(json.dumps({
            "generic_render_rules": {
                "sections": {"test": {"title": "Test", "content": "test content"}}
            }
        }))
        
        data = {
            "imports": {
                "generic_render_rules": str(rules_file)
            },
            "characters": []
        }
        
        result = json_loader.resolve_imports(data, tmp_path)
        assert "generic_render_rules" in result
        assert result["generic_render_rules"]["sections"]["test"]["content"] == "test content"
    
    def test_resolve_imports_style_rules(self, tmp_path):
        """Test resolving style_rules import."""
        style_file = tmp_path / "style.json"
        style_file.write_text(json.dumps({
            "prompt_snippet": "realistic style"
        }))
        
        data = {
            "imports": {
                "style_rules": str(style_file)
            },
            "characters": []
        }
        
        result = json_loader.resolve_imports(data, tmp_path)
        assert "style_rules" in result
        assert result["style_rules"]["prompt_snippet"] == "realistic style"
    
    def test_resolve_imports_pose_library(self, tmp_path):
        """Test resolving pose_library import."""
        pose_file = tmp_path / "poses.json"
        pose_file.write_text(json.dumps({
            "poses": [
                {"pose_id": "stand", "pose_prompt": "standing"}
            ]
        }))
        
        data = {
            "imports": {
                "pose_library": str(pose_file)
            },
            "characters": []
        }
        
        result = json_loader.resolve_imports(data, tmp_path)
        assert "pose_library" in result
        assert len(result["pose_library"]["poses"]) == 1
        assert result["pose_library"]["poses"][0]["pose_id"] == "stand"


class TestExtractFunctions:
    """Test extraction functions for snippets."""
    
    def test_extract_generic_snippet_sections(self):
        """Test extracting generic snippet as sections dict."""
        data = {
            "generic_render_rules": {
                "sections": {
                    "geometry": {"title": "Geometry", "content": "3D-safe geometry"}
                }
            }
        }
        result = json_loader.extract_generic_snippet(data)
        assert isinstance(result, dict)
        assert "geometry" in result
    
    def test_extract_generic_snippet_legacy_string(self):
        """Test extracting legacy prompt_snippet string."""
        data = {
            "generic_render_rules": {
                "prompt_snippet": "legacy prompt"
            }
        }
        result = json_loader.extract_generic_snippet(data)
        assert result == "legacy prompt"
    
    def test_extract_generic_snippet_empty(self):
        """Test extracting when no generic rules present."""
        data = {}
        result = json_loader.extract_generic_snippet(data)
        assert result == ""
    
    def test_extract_miniature_snippet(self):
        """Test extracting miniature snippet."""
        data = {
            "miniature_scale_rules": {
                "prompt_snippet": "28mm miniature scale"
            }
        }
        result = json_loader.extract_miniature_snippet(data)
        assert result == "28mm miniature scale"
    
    def test_extract_thematic_snippet(self):
        """Test extracting thematic snippet."""
        data = {
            "thematic_rules": {
                "prompt_snippet": "dark fantasy theme"
            }
        }
        result = json_loader.extract_thematic_snippet(data)
        assert result == "dark fantasy theme"
    
    def test_extract_style_snippet(self):
        """Test extracting style snippet."""
        data = {
            "style_rules": {
                "prompt_snippet": "realistic rendering"
            }
        }
        result = json_loader.extract_style_snippet(data)
        assert result == "realistic rendering"
    
    def test_extract_thematic_forms(self):
        """Test extracting thematic forms."""
        data = {
            "thematic_rules": {
                "forms": {
                    "human": {"prompt_snippet": "human form"},
                    "beast": {"prompt_snippet": "beast form"},
                    "_comment": "This should be ignored"
                }
            }
        }
        result = json_loader.extract_thematic_forms(data)
        assert len(result) == 2
        assert "human" in result
        assert "beast" in result
        assert "_comment" not in result
        assert result["human"] == "human form"
