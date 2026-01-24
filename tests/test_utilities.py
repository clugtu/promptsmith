"""Tests for utility functions."""
import pytest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import create_image
from reference_sheet import parse_page_spec, deduplicate_figure_sections


class TestSanitization:
    """Test ASCII sanitization for terminal output."""
    
    def test_sanitize_for_ascii_degree_symbol(self):
        """Test converting degree symbol."""
        text = "45° angle"
        result = create_image.sanitize_for_ascii(text)
        assert result == "45 degrees angle"
    
    def test_sanitize_for_ascii_quotes(self):
        """Test converting smart quotes."""
        text = "\u2018single\u2019 and \u201cdouble\u201d quotes"
        result = create_image.sanitize_for_ascii(text)
        assert result == "'single' and \"double\" quotes"
    
    def test_sanitize_for_ascii_dashes(self):
        """Test converting en-dash and em-dash."""
        text = "en–dash and em—dash"
        result = create_image.sanitize_for_ascii(text)
        assert result == "en-dash and em--dash"
    
    def test_sanitize_for_ascii_ellipsis(self):
        """Test converting ellipsis."""
        text = "wait…"
        result = create_image.sanitize_for_ascii(text)
        assert result == "wait..."
    
    def test_sanitize_for_ascii_no_change(self):
        """Test that plain ASCII is unchanged."""
        text = "plain ASCII text"
        result = create_image.sanitize_for_ascii(text)
        assert result == text


class TestFormatting:
    """Test prompt formatting."""
    
    def test_format_for_chat_strips_whitespace(self):
        """Test that format_for_chat strips leading/trailing whitespace."""
        prompt = "  test prompt  \n"
        result = create_image.format_for_chat(prompt)
        assert result == "test prompt"
    
    def test_format_for_chat_preserves_internal_whitespace(self):
        """Test that internal whitespace is preserved."""
        prompt = "line one\n\nline two"
        result = create_image.format_for_chat(prompt)
        assert result == prompt.strip()


class TestRemoveBaseLanguage:
    """Test removing base/plinth language from miniature snippet."""
    
    def test_remove_base_language_mounted_on_base(self):
        """Test removing 'mounted on a round gaming base' phrase."""
        snippet = "40mm miniature, mounted on a round gaming base (about 32mm), detailed painting"
        result = create_image.remove_base_language(snippet)
        assert "mounted" not in result.lower()
        assert "base" not in result.lower()
        assert "40mm miniature" in result
        assert "detailed painting" in result
    
    def test_remove_base_language_on_base(self):
        """Test removing 'on a base' phrase."""
        snippet = "miniature figure, on a base, painted"
        result = create_image.remove_base_language(snippet)
        assert "base" not in result.lower()
        assert "miniature figure" in result
        assert "painted" in result
    
    def test_remove_base_language_multiple_patterns(self):
        """Test removing various base-related phrases."""
        snippet = "figure, mounted on a gaming base, display base visible"
        result = create_image.remove_base_language(snippet)
        assert "base" not in result.lower()
        assert "mounted" not in result.lower()
    
    def test_remove_base_language_no_base(self):
        """Test that snippet without base language is unchanged."""
        snippet = "miniature figure, detailed sculpt, dynamic pose"
        result = create_image.remove_base_language(snippet)
        # Should be mostly unchanged (may have spacing normalization)
        assert "miniature figure" in result
        assert "detailed sculpt" in result
        assert "dynamic pose" in result
    
    def test_remove_base_language_plinth(self):
        """Test removing 'plinth' references."""
        snippet = "figure on plinth, painted"
        result = create_image.remove_base_language(snippet)
        assert "plinth" not in result.lower()


class TestPageSpecParsing:
    """Test parsing page specifications for reference sheets."""
    
    def test_parse_page_spec_all(self):
        """Test parsing 'all' pages."""
        page_spec, subrefs = parse_page_spec("all")
        assert page_spec == "all"
        assert subrefs is None
    
    def test_parse_page_spec_single_page(self):
        """Test parsing single page number."""
        page_spec, subrefs = parse_page_spec("1")
        assert page_spec == 1
        assert subrefs is None
    
    def test_parse_page_spec_with_single_subref(self):
        """Test parsing page with single subrefinement."""
        page_spec, subrefs = parse_page_spec("1:1")
        assert page_spec == 1
        assert subrefs == [1]
    
    def test_parse_page_spec_with_subref_range(self):
        """Test parsing page with subrefinement range."""
        page_spec, subrefs = parse_page_spec("1:{1:3}")
        assert page_spec == 1
        assert subrefs == [1, 2, 3]
    
    def test_parse_page_spec_with_subref_list(self):
        """Test parsing page with subrefinement list."""
        page_spec, subrefs = parse_page_spec("1:{1,4,5}")
        assert page_spec == 1
        assert subrefs == [1, 4, 5]
    
    def test_parse_page_spec_invalid_page_number(self):
        """Test error for invalid page number."""
        with pytest.raises(ValueError, match="Invalid page"):
            parse_page_spec("abc")
    
    def test_parse_page_spec_zero_page(self):
        """Test error for page number less than 1."""
        with pytest.raises(ValueError, match="Invalid page specification|Page number must be 1 or greater"):
            parse_page_spec("0")


class TestDeduplicateFigureSections:
    """Test cases for deduplicate_figure_sections function."""
    
    def test_empty_list(self):
        """Empty list should return empty results."""
        result, common = deduplicate_figure_sections([])
        assert result == []
        assert common == {}
    
    def test_single_figure(self):
        """Single figure should not be deduplicated."""
        figures = ["Figure 1 [char1:1]: CHARACTER: warrior. PROPORTIONS: heroic"]
        result, common = deduplicate_figure_sections(figures)
        assert result == figures
        assert common == {}
    
    def test_identical_proportions(self):
        """Identical PROPORTIONS across all figures should be extracted."""
        figures = [
            "Figure 1 [char1:1]: CHARACTER: warrior. PROPORTIONS: heroic",
            "Figure 2 [char1:2]: CHARACTER: mage. PROPORTIONS: heroic",
            "Figure 3 [char1:3]: CHARACTER: rogue. PROPORTIONS: heroic"
        ]
        result, common = deduplicate_figure_sections(figures)
        
        assert 'PROPORTIONS' in common
        assert common['PROPORTIONS'] == 'heroic'
        
        # Each deduplicated result should not contain PROPORTIONS
        for desc in result:
            assert 'PROPORTIONS' not in desc
        
        # But should still have the character info
        assert 'CHARACTER: warrior' in result[0]
        assert 'CHARACTER: mage' in result[1]
        assert 'CHARACTER: rogue' in result[2]
    
    def test_different_proportions(self):
        """Different PROPORTIONS should not be extracted."""
        figures = [
            "Figure 1 [char1:1]: CHARACTER: warrior. PROPORTIONS: heroic",
            "Figure 2 [char1:2]: CHARACTER: mage. PROPORTIONS: slender"
        ]
        result, common = deduplicate_figure_sections(figures)
        
        assert 'PROPORTIONS' not in common
        assert result == figures  # No changes
    
    def test_identical_render_scope(self):
        """Identical RENDER SCOPE across all figures should be extracted."""
        figures = [
            "Figure 1 [char1:1]: POSE: RENDER SCOPE (CRITICAL): full body view only. Standing pose. PROPORTIONS: heroic",
            "Figure 2 [char1:2]: POSE: RENDER SCOPE (CRITICAL): full body view only. Sitting pose. PROPORTIONS: heroic"
        ]
        result, common = deduplicate_figure_sections(figures)
        
        assert 'RENDER_SCOPE' in common
        assert common['RENDER_SCOPE'] == 'RENDER SCOPE (CRITICAL): full body view only.'
        
        # Deduplicated results should not contain RENDER SCOPE
        for desc in result:
            assert 'RENDER SCOPE (CRITICAL)' not in desc
        
        # But should still have pose descriptions
        assert 'Standing pose' in result[0]
        assert 'Sitting pose' in result[1]
    
    def test_both_proportions_and_render_scope(self):
        """Both PROPORTIONS and RENDER SCOPE should be extracted when identical."""
        figures = [
            "Figure 1 [1:1]: POSE: RENDER SCOPE (CRITICAL): full body view only. Action pose. PROPORTIONS: heroic",
            "Figure 2 [1:2]: POSE: RENDER SCOPE (CRITICAL): full body view only. Idle pose. PROPORTIONS: heroic"
        ]
        result, common = deduplicate_figure_sections(figures)
        
        assert 'PROPORTIONS' in common
        assert 'RENDER_SCOPE' in common
        assert common['PROPORTIONS'] == 'heroic'
        assert 'full body view only' in common['RENDER_SCOPE']
        
        # Deduplicated should have neither
        for desc in result:
            assert 'PROPORTIONS' not in desc
            assert 'RENDER SCOPE' not in desc
    
    def test_partial_render_scope_match(self):
        """If only some figures have RENDER SCOPE, it should not be extracted."""
        figures = [
            "Figure 1 [1:1]: POSE: RENDER SCOPE (CRITICAL): full body view only. Action. PROPORTIONS: heroic",
            "Figure 2 [1:2]: POSE: Action pose. PROPORTIONS: heroic"  # No RENDER SCOPE
        ]
        result, common = deduplicate_figure_sections(figures)
        
        # PROPORTIONS should be extracted (both have it)
        assert 'PROPORTIONS' in common
        # RENDER_SCOPE should NOT be extracted (only one has it)
        assert 'RENDER_SCOPE' not in common
    
    def test_figure_prefix_preserved(self):
        """Figure prefix 'Figure N [label]:' should be preserved."""
        figures = [
            "Figure 1 [alpha:human]: CHARACTER: warrior. PROPORTIONS: heroic",
            "Figure 2 [alpha:crinos]: CHARACTER: werewolf. PROPORTIONS: heroic"
        ]
        result, common = deduplicate_figure_sections(figures)
        
        assert result[0].startswith("Figure 1 [alpha:human]:")
        assert result[1].startswith("Figure 2 [alpha:crinos]:")
    
    def test_whitespace_cleanup(self):
        """Extra whitespace should be cleaned up after deduplication."""
        figures = [
            "Figure 1 [1:1]: CHARACTER: test.  PROPORTIONS: heroic",  # Double space
            "Figure 2 [1:2]: CHARACTER: test2.  PROPORTIONS: heroic"
        ]
        result, common = deduplicate_figure_sections(figures)
        
        # Should not have double spaces
        for desc in result:
            assert '  ' not in desc
    
    def test_no_figure_prefix(self):
        """Figures without standard prefix should be handled gracefully."""
        figures = [
            "Some description without prefix. PROPORTIONS: heroic",
            "Another description. PROPORTIONS: heroic"
        ]
        result, common = deduplicate_figure_sections(figures)
        
        # Should still extract common PROPORTIONS
        assert 'PROPORTIONS' in common
    
    def test_complex_multi_figure(self):
        """Complex real-world scenario with multiple figures."""
        figures = [
            "Figure 1 [garou:alpha_human]: POSE: RENDER SCOPE (CRITICAL): full body view only. Standing tall, "
            "arms crossed, stern expression. PROPORTIONS: heroic",
            
            "Figure 2 [garou:alpha_crinos]: POSE: RENDER SCOPE (CRITICAL): full body view only. Battle stance, "
            "claws extended, snarling. PROPORTIONS: heroic",
            
            "Figure 3 [garou:breaker_human]: POSE: RENDER SCOPE (CRITICAL): full body view only. Casual stance, "
            "hands in pockets. PROPORTIONS: heroic"
        ]
        result, common = deduplicate_figure_sections(figures)
        
        # Both should be extracted
        assert 'PROPORTIONS' in common
        assert 'RENDER_SCOPE' in common
        assert common['PROPORTIONS'] == 'heroic'
        
        # Each figure should retain unique pose descriptions
        assert 'Standing tall' in result[0]
        assert 'Battle stance' in result[1]
        assert 'Casual stance' in result[2]
        
        # But not the common parts
        for desc in result:
            assert 'PROPORTIONS' not in desc
            assert 'RENDER SCOPE (CRITICAL)' not in desc

