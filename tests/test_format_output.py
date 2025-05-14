#!/usr/bin/env python3
"""
Unit tests for the format_output function in whatlang.py.
"""

import json
import pytest
from whatlang import format_output

def test_text_format_file():
    """Test text format output for file input."""
    result = format_output("/path/to/file.txt", "en", "English", 0.98, "text")
    assert result == "file.txt: en\tEnglish\t0.98"

def test_text_format_stdin():
    """Test text format output for stdin input."""
    result = format_output(None, "en", "English", 0.98, "text")
    assert result == "en\tEnglish\t0.98"

def test_json_format_file():
    """Test JSON format output for file input."""
    result = format_output("/path/to/file.txt", "en", "English", 0.98, "json")
    # Parse the JSON to ensure it's valid
    data = json.loads(result)
    
    assert data["file"] == "file.txt"
    assert data["language_code"] == "en"
    assert data["language_name"] == "English"
    assert data["confidence"] == 0.98

def test_json_format_stdin():
    """Test JSON format output for stdin input."""
    result = format_output(None, "en", "English", 0.98, "json")
    # Parse the JSON to ensure it's valid
    data = json.loads(result)
    
    assert "file" not in data
    assert data["language_code"] == "en"
    assert data["language_name"] == "English"
    assert data["confidence"] == 0.98

def test_csv_format_file():
    """Test CSV format output for file input."""
    result = format_output("/path/to/file.txt", "en", "English", 0.98, "csv")
    assert result == "file.txt,en,English,0.98"

def test_csv_format_stdin():
    """Test CSV format output for stdin input."""
    result = format_output(None, "en", "English", 0.98, "csv")
    assert result == "en,English,0.98"

def test_bash_format_file():
    """Test Bash format output for file input."""
    result = format_output("/path/to/file.txt", "en", "English", 0.98, "bash")
    expected = 'declare -A LANG_INFO=([file]="file.txt" [code]="en" [name]="English" [confidence]="0.98")'
    assert result == expected

def test_bash_format_stdin():
    """Test Bash format output for stdin input."""
    result = format_output(None, "en", "English", 0.98, "bash")
    expected = 'declare -A LANG_INFO=([code]="en" [name]="English" [confidence]="0.98")'
    assert result == expected

def test_rounding_confidence():
    """Test that confidence scores are properly rounded."""
    result = format_output(None, "en", "English", 0.9876, "text")
    assert result == "en\tEnglish\t0.99"  # Should round to 2 decimal places