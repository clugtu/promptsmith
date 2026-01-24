"""Tests for equipment and prop handling."""
import pytest
import create_image
import equipment_handler


class TestPropResolution:
    """Test resolving prop references to full descriptions."""
    
    def test_resolve_prop_references_new_format(self):
        """Test resolving new format with prop IDs."""
        equipment = [
            "longsword : main_hand : gripped firmly"
        ]
        prop_definitions = {
            "longsword": "steel longsword (double-edged blade)"
        }
        
        result = equipment_handler.resolve_prop_references(equipment, prop_definitions)
        assert result == ["steel longsword (double-edged blade) : main_hand : gripped firmly"]
    
    def test_resolve_prop_references_legacy_format(self):
        """Test that legacy format (full descriptions) pass through unchanged."""
        equipment = [
            "steel longsword (double-edged blade) : main_hand : gripped firmly"
        ]
        prop_definitions = {}
        
        result = equipment_handler.resolve_prop_references(equipment, prop_definitions)
        assert result == equipment
    
    def test_resolve_prop_references_no_definition(self):
        """Test that unknown prop IDs are left as-is."""
        equipment = [
            "unknown_prop : main_hand : held"
        ]
        prop_definitions = {}
        
        result = equipment_handler.resolve_prop_references(equipment, prop_definitions)
        assert result == equipment
    
    def test_resolve_prop_references_multiple_items(self):
        """Test resolving multiple equipment items."""
        equipment = [
            "sword : main_hand : gripped",
            "shield : off_hand : held defensively"
        ]
        prop_definitions = {
            "sword": "iron sword (simple crossguard)",
            "shield": "wooden shield (round, painted)"
        }
        
        result = equipment_handler.resolve_prop_references(equipment, prop_definitions)
        assert len(result) == 2
        assert result[0] == "iron sword (simple crossguard) : main_hand : gripped"
        assert result[1] == "wooden shield (round, painted) : off_hand : held defensively"
    
    def test_resolve_prop_references_mixed_formats(self):
        """Test resolving mix of new format (refs) and legacy format (full desc)."""
        equipment = [
            "sword : main_hand : gripped",
            "leather armor (studded) : worn : on torso"
        ]
        prop_definitions = {
            "sword": "steel sword (sharp blade)"
        }
        
        result = equipment_handler.resolve_prop_references(equipment, prop_definitions)
        assert result[0] == "steel sword (sharp blade) : main_hand : gripped"
        assert result[1] == "leather armor (studded) : worn : on torso"  # Unchanged


class TestHandValidation:
    """Test hand assignment validation."""
    
    def test_validate_hand_assignments_valid(self):
        """Test validation passes for valid assignments."""
        equipment = [
            "sword (steel) : main_hand : gripped",
            "shield (wooden) : off_hand : held"
        ]
        char_data = {"figure_type": "bipedal_humanoid"}
        
        # Should not raise
        equipment_handler.validate_hand_assignments(equipment, "1", "test", char_data)
    
    def test_validate_hand_assignments_both_hands(self):
        """Test validation passes for both_hands assignment."""
        equipment = [
            "greatsword (two-handed) : both_hands : gripped with both hands"
        ]
        char_data = {"figure_type": "bipedal_humanoid"}
        
        # Should not raise
        equipment_handler.validate_hand_assignments(equipment, "1", "test", char_data)
    
    def test_validate_hand_assignments_conflict_both_and_main(self):
        """Test validation fails when both_hands conflicts with main_hand."""
        equipment = [
            "greatsword : both_hands : gripped",
            "dagger : main_hand : held"
        ]
        char_data = {"figure_type": "bipedal_humanoid"}
        
        with pytest.raises(ValueError, match="HAND CONFLICT"):
            equipment_handler.validate_hand_assignments(equipment, "1", "test", char_data)
    
    def test_validate_hand_assignments_too_many_items(self):
        """Test validation fails when too many items for available hands."""
        equipment = [
            "sword : main_hand : gripped",
            "shield : off_hand : held",
            "dagger : main_hand : tucked in belt"  # Conflict - main_hand already used
        ]
        char_data = {"figure_type": "bipedal_humanoid"}
        
        with pytest.raises(ValueError, match="HAND CONFLICT"):
            equipment_handler.validate_hand_assignments(equipment, "1", "test", char_data)
    
    def test_validate_hand_assignments_multiple_main_hand(self):
        """Test validation fails with multiple main_hand assignments."""
        equipment = [
            "sword : main_hand : gripped",
            "axe : main_hand : held"
        ]
        char_data = {"figure_type": "bipedal_humanoid"}
        
        with pytest.raises(ValueError, match="HAND CONFLICT"):
            equipment_handler.validate_hand_assignments(equipment, "1", "test", char_data)
    
    def test_validate_hand_assignments_multi_limbed_allows_conflict(self):
        """Test that multi-limbed characters allow hand conflicts (as warnings)."""
        equipment = [
            "sword1 : main_hand : gripped",
            "sword2 : main_hand : gripped",
            "shield1 : off_hand : held",
            "shield2 : off_hand : held"
        ]
        char_data = {"figure_type": "multi_limbed_bipedal"}
        
        # Should not raise (multi-limbed characters get warnings instead)
        equipment_handler.validate_hand_assignments(equipment, "1", "test", char_data)
    
    def test_validate_hand_assignments_empty_equipment(self):
        """Test validation passes with no equipment."""
        equipment = []
        char_data = {"figure_type": "bipedal_humanoid"}
        
        # Should not raise
        equipment_handler.validate_hand_assignments(equipment, "1", "test", char_data)
    
    def test_validate_hand_assignments_non_hand_positions(self):
        """Test validation ignores non-hand positions like 'worn' or 'holstered'."""
        equipment = [
            "sword : main_hand : gripped",
            "armor : worn : on torso",
            "pistol : holstered : on hip"
        ]
        char_data = {"figure_type": "bipedal_humanoid"}
        
        # Should not raise
        equipment_handler.validate_hand_assignments(equipment, "1", "test", char_data)
