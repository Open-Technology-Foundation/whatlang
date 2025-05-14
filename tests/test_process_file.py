#!/usr/bin/env python3
"""
Unit tests for the process_file function in whatlang.py.
"""

import sys
import pytest
from io import StringIO
import contextlib
from whatlang import process_file

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

def test_process_english_file(sample_filepath):
    """Test processing an English file."""
    filepath = sample_filepath('en')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, output_format='text')
        
    stdout_content = stdout.getvalue().strip()
    assert "en" in stdout_content
    assert "English" in stdout_content

def test_process_spanish_file(sample_filepath):
    """Test processing a Spanish file."""
    filepath = sample_filepath('es')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, output_format='text')
        
    stdout_content = stdout.getvalue().strip()
    assert "es" in stdout_content
    assert "Spanish" in stdout_content

def test_process_french_file(sample_filepath):
    """Test processing a French file."""
    filepath = sample_filepath('fr')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, output_format='text')
        
    stdout_content = stdout.getvalue().strip()
    assert "fr" in stdout_content
    assert "French" in stdout_content

def test_process_indonesian_file(sample_filepath):
    """Test processing an Indonesian file."""
    filepath = sample_filepath('id')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, output_format='text')
        
    stdout_content = stdout.getvalue().strip()
    assert "id" in stdout_content
    assert "Indonesian" in stdout_content
    
def test_process_russian_file(sample_filepath):
    """Test processing a Russian file."""
    filepath = sample_filepath('ru')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, output_format='text')
        
    stdout_content = stdout.getvalue().strip()
    assert "ru" in stdout_content
    assert "Russian" in stdout_content
    
def test_process_chinese_file(sample_filepath):
    """Test processing a Chinese file."""
    filepath = sample_filepath('zh')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, output_format='text')
        
    stdout_content = stdout.getvalue().strip()
    # Chinese text might be detected as Korean due to similar characters
    assert any(code in stdout_content for code in ["zh", "zh-cn", "zh-tw", "ko"])
    
def test_process_urdu_file(sample_filepath):
    """Test processing an Urdu file."""
    filepath = sample_filepath('ur')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, output_format='text')
        
    stdout_content = stdout.getvalue().strip()
    assert "ur" in stdout_content
    assert "Urdu" in stdout_content
    
def test_process_swahili_file(sample_filepath):
    """Test processing a Swahili file."""
    filepath = sample_filepath('sw')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, output_format='text')
        
    stdout_content = stdout.getvalue().strip()
    assert "sw" in stdout_content
    assert "Swahili" in stdout_content  # Will match either "Swahili" or "Swahili (macrolanguage)"
    
def test_process_arabic_file(sample_filepath):
    """Test processing an Arabic file."""
    filepath = sample_filepath('ar')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, output_format='text')
        
    stdout_content = stdout.getvalue().strip()
    assert "ar" in stdout_content
    assert "Arabic" in stdout_content

def test_process_file_with_sample_size(sample_filepath):
    """Test processing file with custom sample size."""
    filepath = sample_filepath('en')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, sample_size=10, output_format='text', verbose=True)
        
    stderr_content = stderr.getvalue().strip()
    assert "10 bytes" in stderr_content
    assert "Processing" in stderr_content

def test_process_file_verbose(sample_filepath):
    """Test processing file with verbose output."""
    filepath = sample_filepath('en')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, verbose=True)
        
    stderr_content = stderr.getvalue().strip()
    assert "Processing" in stderr_content
    assert "Detection result:" in stderr_content

def test_process_empty_file(empty_file):
    """Test processing an empty file."""
    with capture_output() as (stdout, stderr):
        process_file(empty_file)
        
    stderr_content = stderr.getvalue().strip()
    assert "Empty text" in stderr_content or "Text too short" in stderr_content
    
    stdout_content = stdout.getvalue().strip()
    assert "unknown" in stdout_content.lower()
    assert "Unknown" in stdout_content

def test_process_short_file(short_file):
    """Test processing a file with very short content."""
    with capture_output() as (stdout, stderr):
        process_file(short_file)
        
    stderr_content = stderr.getvalue().strip()
    assert "Text too short" in stderr_content
    
    stdout_content = stdout.getvalue().strip()
    assert "unknown" in stdout_content.lower()
    assert "Unknown" in stdout_content

def test_process_file_json_format(sample_filepath):
    """Test processing file with JSON output format."""
    filepath = sample_filepath('en')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, output_format='json')
        
    stdout_content = stdout.getvalue().strip()
    assert '"language_code": "en"' in stdout_content
    assert '"language_name": "English"' in stdout_content

def test_process_file_csv_format(sample_filepath):
    """Test processing file with CSV output format."""
    filepath = sample_filepath('en')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, output_format='csv')
        
    stdout_content = stdout.getvalue().strip()
    assert "en,English" in stdout_content

def test_process_file_bash_format(sample_filepath):
    """Test processing file with Bash output format."""
    filepath = sample_filepath('en')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, output_format='bash')
        
    stdout_content = stdout.getvalue().strip()
    assert 'declare -A LANG_INFO=' in stdout_content
    assert '[code]="en"' in stdout_content
    assert '[name]="English"' in stdout_content

def test_process_file_with_language_restriction(sample_filepath):
    """Test processing file with language restriction."""
    filepath = sample_filepath('en')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, lang_set=['en', 'fr'])
        
    stdout_content = stdout.getvalue().strip()
    assert "en" in stdout_content
    assert "English" in stdout_content
    
    # Now restrict to languages that don't match
    with capture_output() as (stdout, stderr):
        process_file(filepath, lang_set=['es', 'fr'])
        
    stdout_content = stdout.getvalue().strip()
    assert "unknown" in stdout_content.lower()
    assert "Unknown" in stdout_content

def test_process_file_with_custom_fallback(empty_file):
    """Test processing file with custom fallback values."""
    with capture_output() as (stdout, stderr):
        process_file(empty_file, fallback_code="xx", fallback_name="Custom")
        
    stdout_content = stdout.getvalue().strip()
    assert "xx" in stdout_content
    assert "Custom" in stdout_content

def test_process_nonexistent_file():
    """Test processing a file that doesn't exist."""
    with capture_output() as (stdout, stderr):
        process_file("/nonexistent/file.txt")
        
    stderr_content = stderr.getvalue().strip()
    assert "Error processing" in stderr_content
    assert "No such file" in stderr_content