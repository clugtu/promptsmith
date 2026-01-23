"""Tests for pose library integration."""
import pytest
import create_image


class TestPoseLibraryLookup:
    """Test finding poses in the pose library."""
    
    @pytest.fixture
    def sample_pose_library(self):
        """Sample pose library."""
        return {
            "poses": [
                {
                    "pose_id": "stand_relaxed",
                    "figure_type": "bipedal_humanoid",
                    "pose_prompt": "Standing in a relaxed pose"
                },
                {
                    "pose_id": "combat_ready",
                    "figure_type": "bipedal_humanoid",
                    "pose_prompt": "Ready combat stance with weapon raised"
                }
            ]
        }
    
    def test_find_pose_in_library(self, sample_pose_library):
        """Test finding a pose by pose_id."""
        result = create_image.find_pose_in_library(sample_pose_library, "stand_relaxed")
        assert result is not None
        assert result["pose_prompt"] == "Standing in a relaxed pose"
    
    def test_find_pose_in_library_not_found(self, sample_pose_library):
        """Test that None is returned for non-existent pose."""
        result = create_image.find_pose_in_library(sample_pose_library, "nonexistent")
        assert result is None
    
    def test_find_pose_in_library_empty(self):
        """Test searching in empty pose library."""
        empty_library = {"poses": []}
        result = create_image.find_pose_in_library(empty_library, "any_pose")
        assert result is None


class TestPoseComposition:
    """Test composing pose prompts from library."""
    
    @pytest.fixture
    def sample_char_data(self):
        """Sample character data."""
        return {
            "character_base": "A warrior"
        }
    
    @pytest.fixture
    def sample_pose_def(self):
        """Sample pose definition with library ref."""
        return {
            "pose_library_ref": "combat_ready"
        }
    
    @pytest.fixture
    def sample_pose_library(self):
        """Sample pose library."""
        return {
            "poses": [
                {
                    "pose_id": "combat_ready",
                    "figure_type": "bipedal_humanoid",
                    "pose_prompt": "Ready stance with weapon"
                }
            ]
        }
    
    def test_compose_pose_prompt_basic(self, sample_char_data, sample_pose_def, sample_pose_library):
        """Test composing a basic pose prompt."""
        json_data = {}
        equipment = []
        
        char_override, pose_prompt, camera_rotation = create_image.compose_pose_prompt_from_library(
            sample_char_data, sample_pose_def, sample_pose_library, json_data, equipment
        )
        
        assert pose_prompt == "Ready stance with weapon"
        assert char_override == ""
        assert camera_rotation is None
    
    def test_compose_pose_prompt_with_character_override(self, sample_char_data, sample_pose_library):
        """Test composing pose with character_override."""
        pose_def = {
            "pose_library_ref": "combat_ready",
            "character_override": "eyes glowing red"
        }
        json_data = {}
        equipment = []
        
        char_override, pose_prompt, camera_rotation = create_image.compose_pose_prompt_from_library(
            sample_char_data, pose_def, sample_pose_library, json_data, equipment
        )
        
        # Character override is combined with library pose
        assert "Ready stance with weapon" in pose_prompt
        assert "eyes glowing red" in pose_prompt or "eyes glowing red" in char_override
    
    def test_compose_pose_prompt_with_camera_rotation(self, sample_char_data, sample_pose_def):
        """Test extracting camera_rotation from library pose."""
        pose_library = {
            "poses": [
                {
                    "pose_id": "combat_ready",
                    "pose_prompt": "Ready stance",
                    "camera_rotation": 45
                }
            ]
        }
        json_data = {}
        equipment = []
        
        char_override, pose_prompt, camera_rotation = create_image.compose_pose_prompt_from_library(
            sample_char_data, sample_pose_def, pose_library, json_data, equipment
        )
        
        assert camera_rotation == 45
    
    def test_compose_pose_prompt_missing_ref(self, sample_char_data, sample_pose_library):
        """Test error when pose_library_ref is missing."""
        pose_def = {}  # No pose_library_ref
        json_data = {}
        equipment = []
        
        with pytest.raises(create_image.PromptNotFoundError, match="pose_library_ref is missing"):
            create_image.compose_pose_prompt_from_library(
                sample_char_data, pose_def, sample_pose_library, json_data, equipment
            )
    
    def test_compose_pose_prompt_ref_not_found(self, sample_char_data, sample_pose_library):
        """Test error when pose_id not found in library."""
        pose_def = {
            "pose_library_ref": "nonexistent_pose"
        }
        json_data = {}
        equipment = []
        
        with pytest.raises(create_image.PromptNotFoundError, match="not found in pose library"):
            create_image.compose_pose_prompt_from_library(
                sample_char_data, pose_def, sample_pose_library, json_data, equipment
            )
    
    def test_compose_pose_prompt_fallback_to_embedded(self, sample_char_data):
        """Test fallback to embedded pose definition when library ref not found."""
        pose_def = {
            "pose_library_ref": "nonexistent",
            "pose_prompt": "embedded pose description"
        }
        pose_library = {"poses": []}
        json_data = {}
        equipment = []
        
        # Should use embedded pose_prompt as fallback
        char_override, pose_prompt, camera_rotation = create_image.compose_pose_prompt_from_library(
            sample_char_data, pose_def, pose_library, json_data, equipment
        )
        
        assert pose_prompt == "embedded pose description"
