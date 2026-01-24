"""Pytest configuration and shared fixtures."""
import os
import sys
from pathlib import Path
import pytest

# Add parent directory to path so we can import create_image
sys.path.insert(0, str(Path(__file__).parent.parent))

import create_image


# ==============================================================================
# Path Resolution Fixtures
# ==============================================================================

@pytest.fixture
def promptsmith_root():
    """Return the promptsmith repository root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def standees_path(promptsmith_root):
    """Return path to standees directory (git-tracked, relative path)."""
    path = promptsmith_root.parent / "shattered_citadel" / "assets" / "standees"
    if not path.exists():
        pytest.skip(f"Standees directory not found: {path}")
    return path


@pytest.fixture
def custom_path():
    """Return path to Custom character files (OneDrive, dynamic resolution).
    
    Tries multiple strategies:
    1. PROMPTSMITH_CUSTOM_PATH environment variable
    2. Common OneDrive locations
    3. Skip if not found
    """
    # Try environment variable first
    env_path = os.getenv("PROMPTSMITH_CUSTOM_PATH")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path
    
    # Try common OneDrive locations
    candidates = [
        Path.home() / "OneDrive" / "3D Printing" / "SoB" / "Custom",
        Path("C:/Users/clugtu/OneDrive/3D Printing/SoB/Custom"),
        Path("D:/OneDrive/3D Printing/SoB/Custom"),
    ]
    
    for path in candidates:
        if path.exists():
            return path
    
    pytest.skip("Custom character files not found (OneDrive). Set PROMPTSMITH_CUSTOM_PATH environment variable.")


# ==============================================================================
# Character File Fixtures
# ==============================================================================

@pytest.fixture
def player_denizens_json(standees_path):
    """Return path to player_denizen_standees.json."""
    return standees_path / "player_denizen_standees.json"


@pytest.fixture
def enemy_denizens_json(standees_path):
    """Return path to enemy_denizens_standees.json."""
    return standees_path / "enemy_denizens_standees.json"


@pytest.fixture
def garou_json(custom_path):
    """Return path to garou.json."""
    return custom_path / "Garou" / "garou.json"


# ==============================================================================
# Sample JSON Data Fixtures
# ==============================================================================

@pytest.fixture
def minimal_character_json():
    """Minimal valid character JSON for testing."""
    return {
        "characters": [
            {
                "id": 1,
                "name": "Test Character",
                "character_base": "A test character",
                "pose": {
                    "name": "test_pose",
                    "prompt": "standing upright"
                }
            }
        ]
    }


@pytest.fixture
def character_with_poses_json():
    """Character with multiple poses."""
    return {
        "characters": [
            {
                "id": 1,
                "name": "Test Character",
                "character_base": "A test character",
                "poses": [
                    {
                        "id": 1,
                        "name": "standing",
                        "prompt": "standing upright"
                    },
                    {
                        "id": 2,
                        "name": "running",
                        "prompt": "running forward"
                    }
                ]
            }
        ]
    }


@pytest.fixture
def character_with_equipment_json():
    """Character with equipment and props."""
    return {
        "characters": [
            {
                "id": 1,
                "name": "Test Character",
                "character_base": "A warrior",
                "prop_definitions": {
                    "longsword": "steel longsword (double-edged blade, leather-wrapped hilt)",
                    "shield": "round wooden shield (iron boss, painted heraldry)"
                },
                "equipment": [
                    "longsword : main_hand : gripped firmly",
                    "shield : off_hand : held defensively"
                ],
                "pose": {
                    "name": "combat_ready",
                    "prompt": "ready stance"
                }
            }
        ]
    }


@pytest.fixture
def character_with_pose_library_json():
    """Character using pose library references."""
    return {
        "pose_library": {
            "poses": [
                {
                    "pose_id": "stand_relaxed",
                    "figure_type": "bipedal_humanoid",
                    "pose_prompt": "Standing with relaxed posture"
                }
            ]
        },
        "characters": [
            {
                "id": 1,
                "name": "Test Character",
                "character_base": "A person",
                "equipment": [],
                "pose": {
                    "name": "relaxed",
                    "pose_library_ref": "stand_relaxed"
                }
            }
        ]
    }


@pytest.fixture
def multi_limbed_character_json():
    """Character with more than 2 arms."""
    return {
        "characters": [
            {
                "id": 1,
                "name": "Four-Armed Warrior",
                "character_base": "A multi-armed fighter",
                "figure_type": "multi_limbed_bipedal",
                "prop_definitions": {
                    "sword": "curved sword",
                    "dagger": "curved dagger",
                    "shield": "small buckler"
                },
                "equipment": [
                    "sword : main_hand : gripped firmly",
                    "dagger : off_hand : held ready",
                    "shield : main_hand : strapped to forearm"  # Conflict for 2-armed, ok for 4-armed
                ],
                "pose": {
                    "name": "combat",
                    "prompt": "ready for battle"
                }
            }
        ]
    }


@pytest.fixture
def character_with_forms_json():
    """Character with thematic forms (like werewolf)."""
    return {
        "thematic_rules": {
            "forms": {
                "human": {
                    "figure_type": "bipedal_humanoid",
                    "prompt_snippet": "fully human form"
                },
                "beast": {
                    "figure_type": "quadrupedal",
                    "prompt_snippet": "bestial wolf form, four-legged"
                }
            }
        },
        "characters": [
            {
                "id": 1,
                "name": "Shapeshifter",
                "character_base": "A cursed warrior",
                "poses": [
                    {
                        "id": 1,
                        "name": "human",
                        "thematic_snippet": ["human"],
                        "prompt": "standing upright"
                    },
                    {
                        "id": 2,
                        "name": "beast",
                        "thematic_snippet": ["beast"],
                        "prompt": "crouched on all fours"
                    }
                ]
            }
        ]
    }
