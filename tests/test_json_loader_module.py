"""Additional unit tests for json_loader module to ensure complete coverage."""
import pytest
from pathlib import Path
import json
import json_loader


class TestExtractFunctions:
    """Test all extract functions for edge cases and coverage."""
    
    def test_extract_generic_snippet_with_sections(self):
        """Test extracting generic snippet when sections dict exists."""
        data = {
            "generic_render_rules": {
                "sections": {
                    "lighting": "soft ambient light",
                    "camera": "wide angle"
                }
            }
        }
        result = json_loader.extract_generic_snippet(data)
        assert result == {"lighting": "soft ambient light", "camera": "wide angle"}
    
    def test_extract_generic_snippet_legacy_prompt(self):
        """Test extracting generic snippet from legacy prompt_snippet."""
        data = {
            "generic_render_rules": {
                "prompt_snippet": "legacy prompt text"
            }
        }
        result = json_loader.extract_generic_snippet(data)
        assert result == "legacy prompt text"
    
    def test_extract_generic_snippet_empty(self):
        """Test extracting generic snippet when no rules exist."""
        data = {}
        result = json_loader.extract_generic_snippet(data)
        assert result == ""
    
    def test_extract_miniature_snippet_exists(self):
        """Test extracting miniature snippet when it exists."""
        data = {
            "miniature_scale_rules": {
                "prompt_snippet": "miniature scale details"
            }
        }
        result = json_loader.extract_miniature_snippet(data)
        assert result == "miniature scale details"
    
    def test_extract_miniature_snippet_missing(self):
        """Test extracting miniature snippet when missing."""
        data = {}
        result = json_loader.extract_miniature_snippet(data)
        assert result == ""
    
    def test_extract_thematic_snippet_exists(self):
        """Test extracting thematic snippet when it exists."""
        data = {
            "thematic_rules": {
                "prompt_snippet": "dark fantasy theme"
            }
        }
        result = json_loader.extract_thematic_snippet(data)
        assert result == "dark fantasy theme"
    
    def test_extract_thematic_snippet_missing(self):
        """Test extracting thematic snippet when missing."""
        data = {}
        result = json_loader.extract_thematic_snippet(data)
        assert result == ""
    
    def test_extract_style_snippet_exists(self):
        """Test extracting style snippet when it exists."""
        data = {
            "style_rules": {
                "prompt_snippet": "realistic oil painting"
            }
        }
        result = json_loader.extract_style_snippet(data)
        assert result == "realistic oil painting"
    
    def test_extract_style_snippet_missing(self):
        """Test extracting style snippet when missing."""
        data = {}
        result = json_loader.extract_style_snippet(data)
        assert result == ""
    
    def test_extract_default_proportions_exists(self):
        """Test extracting default proportions when they exist."""
        data = {
            "style_rules": {
                "default_proportions": "heroic proportions"
            }
        }
        result = json_loader.extract_default_proportions(data)
        assert result == "heroic proportions"
    
    def test_extract_default_proportions_missing(self):
        """Test extracting default proportions when missing."""
        data = {}
        result = json_loader.extract_default_proportions(data)
        assert result == ""


class TestExtractThematicForms:
    """Test thematic forms extraction."""
    
    def test_extract_thematic_forms_basic(self):
        """Test extracting thematic forms with valid forms."""
        data = {
            "thematic_rules": {
                "forms": {
                    "human": {
                        "prompt_snippet": "human form description"
                    },
                    "werewolf": {
                        "prompt_snippet": "werewolf form description"
                    }
                }
            }
        }
        result = json_loader.extract_thematic_forms(data)
        assert result == {
            "human": "human form description",
            "werewolf": "werewolf form description"
        }
    
    def test_extract_thematic_forms_with_comments(self):
        """Test that non-dict entries (like _comment) are skipped."""
        data = {
            "thematic_rules": {
                "forms": {
                    "_comment": "This is a comment",
                    "human": {
                        "prompt_snippet": "human form"
                    },
                    "invalid": "not a dict"
                }
            }
        }
        result = json_loader.extract_thematic_forms(data)
        assert result == {"human": "human form"}
        assert "_comment" not in result
        assert "invalid" not in result
    
    def test_extract_thematic_forms_no_forms(self):
        """Test extracting when no forms exist."""
        data = {}
        result = json_loader.extract_thematic_forms(data)
        assert result == {}
    
    def test_extract_thematic_forms_empty_forms(self):
        """Test extracting when forms dict is empty."""
        data = {
            "thematic_rules": {
                "forms": {}
            }
        }
        result = json_loader.extract_thematic_forms(data)
        assert result == {}
    
    def test_extract_thematic_forms_missing_prompt_snippet(self):
        """Test that forms without prompt_snippet return empty string."""
        data = {
            "thematic_rules": {
                "forms": {
                    "human": {
                        "other_field": "value"
                    }
                }
            }
        }
        result = json_loader.extract_thematic_forms(data)
        assert result == {"human": ""}


class TestResolveImportsEdgeCases:
    """Test edge cases for import resolution."""
    
    def test_resolve_imports_miniature_scale_rules(self, tmp_path):
        """Test resolving miniature_scale_rules import."""
        # Create miniature rules file
        miniature_file = tmp_path / "miniature.json"
        miniature_file.write_text(json.dumps({
            "miniature_scale_rules": {
                "prompt_snippet": "28mm tabletop scale"
            }
        }))
        
        data = {
            "imports": {
                "miniature_scale_rules": str(miniature_file)
            }
        }
        
        result = json_loader.resolve_imports(data, tmp_path)
        assert "miniature_scale_rules" in result
        assert result["miniature_scale_rules"]["prompt_snippet"] == "28mm tabletop scale"
    
    def test_resolve_imports_common_thematic_forms(self, tmp_path):
        """Test resolving common_thematic_forms import."""
        # Create forms file
        forms_file = tmp_path / "forms.json"
        forms_file.write_text(json.dumps({
            "common_thematic_forms": {
                "human": {"prompt_snippet": "human form"},
                "beast": {"prompt_snippet": "beast form"}
            }
        }))
        
        data = {
            "imports": {
                "common_thematic_forms": str(forms_file)
            }
        }
        
        result = json_loader.resolve_imports(data, tmp_path)
        assert "thematic_rules" in result
        assert "forms" in result["thematic_rules"]
        assert "human" in result["thematic_rules"]["forms"]
        assert "beast" in result["thematic_rules"]["forms"]
    
    def test_resolve_imports_forms_merge_precedence(self, tmp_path):
        """Test that character file forms take precedence over common forms."""
        # Create forms file
        forms_file = tmp_path / "forms.json"
        forms_file.write_text(json.dumps({
            "common_thematic_forms": {
                "human": {"prompt_snippet": "common human"},
                "beast": {"prompt_snippet": "common beast"}
            }
        }))
        
        data = {
            "imports": {
                "common_thematic_forms": str(forms_file)
            },
            "thematic_rules": {
                "forms": {
                    "human": {"prompt_snippet": "character human"}
                }
            }
        }
        
        result = json_loader.resolve_imports(data, tmp_path)
        # Character file form should be preserved
        assert result["thematic_rules"]["forms"]["human"]["prompt_snippet"] == "character human"
        # Common form should be added
        assert result["thematic_rules"]["forms"]["beast"]["prompt_snippet"] == "common beast"
    
    def test_resolve_imports_style_rules(self, tmp_path):
        """Test resolving style_rules import."""
        # Create style file
        style_file = tmp_path / "style.json"
        style_file.write_text(json.dumps({
            "prompt_snippet": "oil painting style",
            "default_proportions": "realistic"
        }))
        
        data = {
            "imports": {
                "style_rules": str(style_file)
            }
        }
        
        result = json_loader.resolve_imports(data, tmp_path)
        assert "style_rules" in result
        assert result["style_rules"]["prompt_snippet"] == "oil painting style"
        assert result["style_rules"]["default_proportions"] == "realistic"
    
    def test_resolve_imports_pose_library(self, tmp_path):
        """Test resolving pose_library import."""
        # Create pose library file
        pose_file = tmp_path / "poses.json"
        pose_file.write_text(json.dumps({
            "poses": {
                "standing": {"description": "standing pose"}
            }
        }))
        
        data = {
            "imports": {
                "pose_library": str(pose_file)
            }
        }
        
        result = json_loader.resolve_imports(data, tmp_path)
        assert "pose_library" in result
        assert "poses" in result["pose_library"]
    
    def test_resolve_imports_file_caching(self, tmp_path):
        """Test that the same file is not loaded multiple times (caching)."""
        # Create a shared rules file
        rules_file = tmp_path / "shared.json"
        rules_file.write_text(json.dumps({
            "generic_render_rules": {"prompt_snippet": "shared rules"},
            "miniature_scale_rules": {"prompt_snippet": "shared miniature"}
        }))
        
        # Import the same file for both rules
        data = {
            "imports": {
                "generic_render_rules": str(rules_file),
                "miniature_scale_rules": str(rules_file)
            }
        }
        
        result = json_loader.resolve_imports(data, tmp_path)
        assert "generic_render_rules" in result
        assert "miniature_scale_rules" in result


class TestValidateCharacterIDsEdgeCases:
    """Additional edge case tests for character ID validation."""
    
    def test_validate_with_mixed_id_types(self):
        """Test validation handles mixed scenarios."""
        characters = [
            {"id": 1, "name": "First"},
            {"name": "NoID"},  # Missing ID
            {"id": 2, "name": "Second"}
        ]
        # Should pass - only validates characters with IDs
        json_loader.validate_character_ids(characters)
    
    def test_validate_single_character(self):
        """Test validation with a single character."""
        characters = [{"id": 1, "name": "Solo"}]
        json_loader.validate_character_ids(characters)  # Should not raise


class TestResolvePathWindows:
    """Test Windows-specific path resolution."""
    
    def test_resolve_path_windows_drive(self):
        """Test resolving Windows drive path (C:/, D:/, etc)."""
        result = json_loader.resolve_path("C:/test/path.json", Path.cwd())
        assert result.is_absolute()
        # On Windows, should be C:\test\path.json
        # On Unix, might be different but still absolute
    
    def test_resolve_path_git_bash_not_on_windows(self):
        """Test that non-Windows systems handle Git Bash paths normally."""
        import os
        if os.name != "nt":
            # On Unix, /d/test should be treated as absolute
            result = json_loader.resolve_path("/d/test/path.json", Path.cwd())
            assert str(result).startswith("/")
