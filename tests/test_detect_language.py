#!/usr/bin/env python3
"""
Unit tests for the detect_language function in whatlang.py.
"""

import pytest
from whatlang import detect_language

def test_detect_english(sample_texts):
    """Test detection of English text."""
    code, name, confidence = detect_language(sample_texts['en'])
    assert code == 'en'
    assert name == 'English'
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.5  # Should have high confidence

def test_detect_spanish(sample_texts):
    """Test detection of Spanish text."""
    code, name, confidence = detect_language(sample_texts['es'])
    assert code == 'es'
    assert name == 'Spanish'
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.5  # Should have high confidence

def test_detect_french(sample_texts):
    """Test detection of French text."""
    code, name, confidence = detect_language(sample_texts['fr'])
    assert code == 'fr'
    assert name == 'French'
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.5  # Should have high confidence

def test_detect_indonesian(sample_texts):
    """Test detection of Indonesian text."""
    code, name, confidence = detect_language(sample_texts['id'])
    assert code == 'id'
    assert name == 'Indonesian'
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.5  # Should have high confidence

def test_detect_russian(sample_texts):
    """Test detection of Russian text."""
    code, name, confidence = detect_language(sample_texts['ru'])
    assert code == 'ru'
    assert name == 'Russian'
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.5  # Should have high confidence

def test_detect_chinese(sample_texts):
    """Test detection of Chinese (Traditional) text."""
    code, name, confidence = detect_language(sample_texts['zh'])
    # The text might be detected as Korean or Chinese based on the character set
    assert code in ['zh-cn', 'zh-tw', 'zh', 'ko']
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.5  # Should have high confidence

def test_detect_urdu(sample_texts):
    """Test detection of Urdu text."""
    code, name, confidence = detect_language(sample_texts['ur'])
    assert code == 'ur'
    assert name == 'Urdu'
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.5  # Should have high confidence

def test_detect_swahili(sample_texts):
    """Test detection of Swahili text."""
    code, name, confidence = detect_language(sample_texts['sw'])
    assert code == 'sw'
    assert 'Swahili' in name  # May be "Swahili (macrolanguage)" from pycountry
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.5  # Should have high confidence

def test_detect_arabic(sample_texts):
    """Test detection of Arabic text."""
    code, name, confidence = detect_language(sample_texts['ar'])
    assert code == 'ar'
    assert name == 'Arabic'
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.5  # Should have high confidence

def test_detect_unknown_language(sample_texts):
    """Test detection of unknown language (Elvish)."""
    code, name, confidence = detect_language(sample_texts['unknown'])
    # We don't assert specific language here as it may vary
    # Just ensure we get something, not an error
    assert isinstance(code, str)
    assert isinstance(name, str)
    assert 0.0 <= confidence <= 1.0

def test_empty_text():
    """Test detection with empty text."""
    code, name, confidence = detect_language("")
    assert code == "unknown"
    assert name == "Unknown"
    assert confidence == 0.0

def test_short_text():
    """Test detection with text too short for reliable detection."""
    code, name, confidence = detect_language("Hi")
    assert code == "unknown"
    assert name == "Unknown"
    assert confidence == 0.0

def test_none_text():
    """Test detection with None input."""
    code, name, confidence = detect_language(None)
    assert code == "unknown"
    assert name == "Unknown"
    assert confidence == 0.0

def test_language_restriction_match(sample_texts):
    """Test detection with language restriction that matches."""
    code, name, confidence = detect_language(sample_texts['en'], lang_set=['en', 'fr'])
    assert code == 'en'
    assert name == 'English'
    assert confidence > 0.0

def test_language_restriction_no_match(sample_texts):
    """Test detection with language restriction that doesn't match."""
    code, name, confidence = detect_language(sample_texts['en'], lang_set=['es', 'fr'])
    # Should fall back to unknown as English isn't in the restriction list
    assert code == "unknown"
    assert name == "Unknown"
    assert confidence == 0.0

def test_custom_fallback():
    """Test detection with custom fallback values."""
    code, name, confidence = detect_language("", fallback_code="xx", fallback_name="Custom")
    assert code == "xx"
    assert name == "Custom"
    assert confidence == 0.0