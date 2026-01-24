"""Tests for utility functions."""
import pytest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import create_image
from reference_sheet import parse_page_spec


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
