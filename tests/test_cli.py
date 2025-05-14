#!/usr/bin/env python3
"""
Integration tests for the whatlang CLI.

These tests verify that the command-line interface works correctly
by running the main() function with various arguments.
"""

import sys
import os
import pytest
from io import StringIO
import json
from unittest.mock import patch

# Import the main function from whatlang.py
from whatlang import main

def test_cli_with_file(sample_filepath, monkeypatch):
    """Test CLI with a file argument."""
    filepath = sample_filepath('en')
    
    # Set up command line arguments
    monkeypatch.setattr('sys.argv', ['whatlang', filepath])
    
    # Capture stdout
    stdout_capture = StringIO()
    monkeypatch.setattr('sys.stdout', stdout_capture)
    
    # Run the main function
    main()
    
    # Check the output
    output = stdout_capture.getvalue().strip()
    assert os.path.basename(filepath) in output
    assert "en" in output
    assert "English" in output

def test_cli_with_multiple_files(sample_filepath, monkeypatch):
    """Test CLI with multiple file arguments."""
    filepath_en = sample_filepath('en')
    filepath_es = sample_filepath('es')
    
    # Set up command line arguments
    monkeypatch.setattr('sys.argv', ['whatlang', filepath_en, filepath_es])
    
    # Capture stdout
    stdout_capture = StringIO()
    monkeypatch.setattr('sys.stdout', stdout_capture)
    
    # Run the main function
    main()
    
    # Check the output
    output = stdout_capture.getvalue().strip()
    lines = output.split('\n')
    
    assert len(lines) == 2
    assert os.path.basename(filepath_en) in lines[0]
    assert "en" in lines[0]
    assert "English" in lines[0]
    
    assert os.path.basename(filepath_es) in lines[1]
    assert "es" in lines[1]
    assert "Spanish" in lines[1]

def test_cli_with_stdin(stdin_redirect, monkeypatch):
    """Test CLI with stdin input."""
    # Set up stdin with English text
    stdin_redirect("This is English text for testing stdin input.")
    
    # Set up command line arguments
    monkeypatch.setattr('sys.argv', ['whatlang'])
    
    # Capture stdout
    stdout_capture = StringIO()
    monkeypatch.setattr('sys.stdout', stdout_capture)
    
    # Run the main function
    main()
    
    # Check the output
    output = stdout_capture.getvalue().strip()
    assert "en" in output
    assert "English" in output

def test_cli_with_sample_size(sample_filepath, monkeypatch):
    """Test CLI with sample size option."""
    filepath = sample_filepath('en')
    
    # Set up command line arguments
    monkeypatch.setattr('sys.argv', ['whatlang', '--sample-size', '10', filepath])
    
    # Capture stdout and stderr
    stdout_capture = StringIO()
    stderr_capture = StringIO()
    monkeypatch.setattr('sys.stdout', stdout_capture)
    monkeypatch.setattr('sys.stderr', stderr_capture)
    
    # Run the main function
    main()
    
    # We should still get a result, but it might be less accurate
    output = stdout_capture.getvalue().strip()
    assert os.path.basename(filepath) in output

def test_cli_with_json_format(sample_filepath, monkeypatch):
    """Test CLI with JSON output format."""
    filepath = sample_filepath('en')
    
    # Set up command line arguments
    monkeypatch.setattr('sys.argv', ['whatlang', '--format', 'json', filepath])
    
    # Capture stdout
    stdout_capture = StringIO()
    monkeypatch.setattr('sys.stdout', stdout_capture)
    
    # Run the main function
    main()
    
    # Check the output is valid JSON
    output = stdout_capture.getvalue().strip()
    data = json.loads(output)
    
    assert data["file"] == os.path.basename(filepath)
    assert data["language_code"] == "en"
    assert data["language_name"] == "English"
    assert 0 <= data["confidence"] <= 1

def test_cli_with_csv_format(sample_filepath, monkeypatch):
    """Test CLI with CSV output format."""
    filepath = sample_filepath('en')
    
    # Set up command line arguments
    monkeypatch.setattr('sys.argv', ['whatlang', '--format', 'csv', filepath])
    
    # Capture stdout
    stdout_capture = StringIO()
    monkeypatch.setattr('sys.stdout', stdout_capture)
    
    # Run the main function
    main()
    
    # Check the output format
    output = stdout_capture.getvalue().strip()
    assert os.path.basename(filepath) in output
    assert "en,English" in output

def test_cli_with_language_set(sample_filepath, monkeypatch):
    """Test CLI with language set restriction."""
    filepath = sample_filepath('en')
    
    # Set up command line arguments for matching language set
    monkeypatch.setattr('sys.argv', ['whatlang', '--language-set', 'en,fr', filepath])
    
    # Capture stdout
    stdout_capture = StringIO()
    monkeypatch.setattr('sys.stdout', stdout_capture)
    
    # Run the main function
    main()
    
    # Check the output
    output = stdout_capture.getvalue().strip()
    assert "en" in output
    assert "English" in output
    
    # Set up command line arguments for non-matching language set
    monkeypatch.setattr('sys.argv', ['whatlang', '--language-set', 'es,fr', filepath])
    
    # Reset stdout capture
    stdout_capture = StringIO()
    monkeypatch.setattr('sys.stdout', stdout_capture)
    
    # Run the main function
    main()
    
    # Check the output falls back to unknown
    output = stdout_capture.getvalue().strip()
    assert "unknown" in output.lower()
    assert "Unknown" in output

def test_cli_with_fallback(empty_file, monkeypatch):
    """Test CLI with custom fallback options."""
    # Set up command line arguments
    monkeypatch.setattr('sys.argv', [
        'whatlang', 
        '--fallback-langcode', 'xx', 
        '--fallback-langname', 'Custom', 
        empty_file
    ])
    
    # Capture stdout
    stdout_capture = StringIO()
    monkeypatch.setattr('sys.stdout', stdout_capture)
    
    # Run the main function
    main()
    
    # Check the output uses custom fallback
    output = stdout_capture.getvalue().strip()
    assert "xx" in output
    assert "Custom" in output

def test_cli_with_verbose(sample_filepath, monkeypatch):
    """Test CLI with verbose mode."""
    filepath = sample_filepath('en')
    
    # Set up command line arguments
    monkeypatch.setattr('sys.argv', ['whatlang', '--verbose', filepath])
    
    # Capture stdout and stderr
    stdout_capture = StringIO()
    stderr_capture = StringIO()
    monkeypatch.setattr('sys.stdout', stdout_capture)
    monkeypatch.setattr('sys.stderr', stderr_capture)
    
    # Run the main function
    main()
    
    # Check stderr contains verbose information
    stderr_output = stderr_capture.getvalue().strip()
    assert "Processing" in stderr_output
    assert "Detection result:" in stderr_output
    
    # Check stdout contains the normal output
    stdout_output = stdout_capture.getvalue().strip()
    assert "en" in stdout_output
    assert "English" in stdout_output

def test_cli_help(monkeypatch):
    """Test CLI with help option."""
    # Set up command line arguments
    monkeypatch.setattr('sys.argv', ['whatlang', '--help'])
    
    # Capture stdout
    stdout_capture = StringIO()
    monkeypatch.setattr('sys.stdout', stdout_capture)
    
    # Run the main function with exit caught
    with pytest.raises(SystemExit) as exit_info:
        main()
    
    # Check exit code is 0 (success)
    assert exit_info.value.code == 0
    
    # Check help output
    help_output = stdout_capture.getvalue().strip()
    assert "usage:" in help_output
    assert "Detect language of text files or stdin" in help_output

def test_cli_no_input(monkeypatch):
    """Test CLI with no input (should show help and exit)."""
    # Set up command line arguments
    monkeypatch.setattr('sys.argv', ['whatlang'])
    
    # Make sys.stdin.isatty() return True (no piped input)
    monkeypatch.setattr('sys.stdin.isatty', lambda: True)
    
    # Capture stdout
    stdout_capture = StringIO()
    monkeypatch.setattr('sys.stdout', stdout_capture)
    
    # Run the main function with exit caught
    with pytest.raises(SystemExit) as exit_info:
        main()
    
    # Check exit code is 1 (error)
    assert exit_info.value.code == 1
    
    # Check help output
    help_output = stdout_capture.getvalue().strip()
    assert "usage:" in help_output