#!/usr/bin/env python3
"""
Tests for edge cases in whatlang.
"""

import pytest
import sys
from io import StringIO
import contextlib
from whatlang import detect_language, process_file, main

@contextlib.contextmanager
def capture_output():
    """
    Context manager to capture stdout and stderr.
    
    Returns:
        tuple: Captured stdout and stderr as strings
    """
    stdout, stderr = StringIO(), StringIO()
    old_stdout, old_stderr = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = stdout, stderr
        yield stdout, stderr
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr

def test_very_long_text():
    """Test with very long text (should use sample size internally)."""
    # Create a text that's longer than the max sample size (4096)
    long_text = "This is English. " * 1000  # ~17000 chars
    
    code, name, confidence = detect_language(long_text)
    
    assert code == "en"
    assert name == "English"
    assert confidence > 0.5

def test_mixed_language_text():
    """Test with text containing multiple languages."""
    mixed_text = (
        "This is English text. "
        "Esto es texto en español. "
        "Ceci est du texte en français."
    )
    
    code, name, confidence = detect_language(mixed_text)
    
    # We don't assert which language is detected, as it may vary
    # Just check that we get a result without error
    assert isinstance(code, str)
    assert isinstance(name, str)
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.0  # Should have some confidence

def test_unusual_characters():
    """Test with text containing unusual/special characters."""
    special_text = "✨🌟 This text has emojis and special characters! ®©™ ¥€$£"
    
    code, name, confidence = detect_language(special_text)
    
    # Should still detect as English despite special chars
    assert code == "en"
    assert name == "English"
    assert confidence > 0.0

def test_invalid_language_set():
    """Test with invalid language codes in the language set."""
    text = "This is English text."
    
    # Invalid language code that doesn't exist
    code, name, confidence = detect_language(text, lang_set=["xx", "yy"])
    
    # Should fall back to unknown since no valid languages in set
    assert code == "unknown"
    assert name == "Unknown"
    assert confidence == 0.0
    
    # Mix of valid and invalid
    code, name, confidence = detect_language(text, lang_set=["en", "xx"])
    
    # Should still match English since it's in the set
    assert code == "en"
    assert name == "English"
    assert confidence > 0.0

def test_all_whitespace():
    """Test with text that's all whitespace."""
    whitespace_text = "   \n\t   \r\n"
    
    code, name, confidence = detect_language(whitespace_text)
    
    # Should fall back to unknown
    assert code == "unknown"
    assert name == "Unknown"
    assert confidence == 0.0

def test_unexpected_encoding(tmp_path):
    """Test with file that has unexpected encoding."""
    # Create a binary file with non-UTF-8 content
    binary_file = tmp_path / "binary.dat"
    with open(binary_file, 'wb') as f:
        f.write(b'\x80\x81\x82\x83\x84binary data that is not valid utf-8')
    
    with capture_output() as (stdout, stderr):
        process_file(str(binary_file))
    
    stderr_content = stderr.getvalue().strip()
    assert "Error" in stderr_content

def test_max_sample_size_enforcement(monkeypatch, sample_filepath):
    """Test that sample size is enforced to max of 4096."""
    filepath = sample_filepath('en')
    
    # Set up command line arguments with sample size > 4096
    monkeypatch.setattr('sys.argv', ['whatlang', '--sample-size', '10000', '--verbose', filepath])
    
    # Capture stderr
    stdout_capture = StringIO()
    stderr_capture = StringIO()
    monkeypatch.setattr('sys.stdout', stdout_capture)
    monkeypatch.setattr('sys.stderr', stderr_capture)
    
    # Run the main function
    main()
    
    # Check that sample size was capped at 4096
    stderr_output = stderr_capture.getvalue().strip()
    # Either 4096 explicitly mentioned or we see a sample size ≤ 4096
    assert "4096" in stderr_output or not any(
        str(size) in stderr_output 
        for size in range(4097, 10001)
    )

def test_unicode_filenames(tmp_path, monkeypatch):
    """Test with filenames containing Unicode characters."""
    # Create a file with Unicode in the name
    unicode_file = tmp_path / "üñîçøðé_file.txt"
    with open(unicode_file, 'w', encoding='utf-8') as f:
        f.write("This is English text in a file with Unicode filename.")
    
    # Set up command line arguments
    monkeypatch.setattr('sys.argv', ['whatlang', str(unicode_file)])
    
    # Capture stdout
    stdout_capture = StringIO()
    monkeypatch.setattr('sys.stdout', stdout_capture)
    
    # Run the main function
    main()
    
    # Check the output
    output = stdout_capture.getvalue().strip()
    assert "en" in output
    assert "English" in output
    assert "üñîçøðé_file.txt" in output