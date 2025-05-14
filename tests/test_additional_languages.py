#!/usr/bin/env python3
"""
Tests for additional languages in whatlang.
"""

import pytest
from whatlang import detect_language
import contextlib
import sys
from io import StringIO
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

# --- Hindi ---
def test_detect_hindi(sample_texts):
    """Test detection of Hindi text."""
    code, name, confidence = detect_language(sample_texts['hi'])
    assert code == 'hi'
    assert name == 'Hindi'
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.5  # Should have high confidence

def test_process_hindi_file(sample_filepath):
    """Test processing a Hindi file."""
    filepath = sample_filepath('hi')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, output_format='text')
        
    stdout_content = stdout.getvalue().strip()
    assert "hi" in stdout_content
    assert "Hindi" in stdout_content

# --- Portuguese ---
def test_detect_portuguese(sample_texts):
    """Test detection of Portuguese text."""
    code, name, confidence = detect_language(sample_texts['pt'])
    assert code == 'pt'
    assert name == 'Portuguese'
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.5  # Should have high confidence

def test_process_portuguese_file(sample_filepath):
    """Test processing a Portuguese file."""
    filepath = sample_filepath('pt')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, output_format='text')
        
    stdout_content = stdout.getvalue().strip()
    assert "pt" in stdout_content
    assert "Portuguese" in stdout_content

# --- Bengali ---
def test_detect_bengali(sample_texts):
    """Test detection of Bengali text."""
    code, name, confidence = detect_language(sample_texts['bn'])
    assert code == 'bn'
    assert name == 'Bengali'
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.5  # Should have high confidence

def test_process_bengali_file(sample_filepath):
    """Test processing a Bengali file."""
    filepath = sample_filepath('bn')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, output_format='text')
        
    stdout_content = stdout.getvalue().strip()
    assert "bn" in stdout_content
    assert "Bengali" in stdout_content

# --- Japanese ---
def test_detect_japanese(sample_texts):
    """Test detection of Japanese text."""
    code, name, confidence = detect_language(sample_texts['ja'])
    assert code == 'ja'
    assert name == 'Japanese'
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.5  # Should have high confidence

def test_process_japanese_file(sample_filepath):
    """Test processing a Japanese file."""
    filepath = sample_filepath('ja')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, output_format='text')
        
    stdout_content = stdout.getvalue().strip()
    assert "ja" in stdout_content
    assert "Japanese" in stdout_content

# --- German ---
def test_detect_german(sample_texts):
    """Test detection of German text."""
    code, name, confidence = detect_language(sample_texts['de'])
    assert code == 'de'
    assert name == 'German'
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.5  # Should have high confidence

def test_process_german_file(sample_filepath):
    """Test processing a German file."""
    filepath = sample_filepath('de')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, output_format='text')
        
    stdout_content = stdout.getvalue().strip()
    assert "de" in stdout_content
    assert "German" in stdout_content

# --- Turkish ---
def test_detect_turkish(sample_texts):
    """Test detection of Turkish text."""
    code, name, confidence = detect_language(sample_texts['tr'])
    assert code == 'tr'
    assert name == 'Turkish'
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.5  # Should have high confidence

def test_process_turkish_file(sample_filepath):
    """Test processing a Turkish file."""
    filepath = sample_filepath('tr')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, output_format='text')
        
    stdout_content = stdout.getvalue().strip()
    assert "tr" in stdout_content
    assert "Turkish" in stdout_content

# --- Vietnamese ---
def test_detect_vietnamese(sample_texts):
    """Test detection of Vietnamese text."""
    code, name, confidence = detect_language(sample_texts['vi'])
    assert code == 'vi'
    assert name == 'Vietnamese'
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.5  # Should have high confidence

def test_process_vietnamese_file(sample_filepath):
    """Test processing a Vietnamese file."""
    filepath = sample_filepath('vi')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, output_format='text')
        
    stdout_content = stdout.getvalue().strip()
    assert "vi" in stdout_content
    assert "Vietnamese" in stdout_content

# --- Korean ---
def test_detect_korean(sample_texts):
    """Test detection of Korean text."""
    code, name, confidence = detect_language(sample_texts['ko'])
    assert code == 'ko'
    assert name == 'Korean'
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.5  # Should have high confidence

def test_process_korean_file(sample_filepath):
    """Test processing a Korean file."""
    filepath = sample_filepath('ko')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, output_format='text')
        
    stdout_content = stdout.getvalue().strip()
    assert "ko" in stdout_content
    assert "Korean" in stdout_content

# --- Italian ---
def test_detect_italian(sample_texts):
    """Test detection of Italian text."""
    code, name, confidence = detect_language(sample_texts['it'])
    assert code == 'it'
    assert name == 'Italian'
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.5  # Should have high confidence

def test_process_italian_file(sample_filepath):
    """Test processing an Italian file."""
    filepath = sample_filepath('it')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, output_format='text')
        
    stdout_content = stdout.getvalue().strip()
    assert "it" in stdout_content
    assert "Italian" in stdout_content

# --- Thai ---
def test_detect_thai(sample_texts):
    """Test detection of Thai text."""
    code, name, confidence = detect_language(sample_texts['th'])
    assert code == 'th'
    assert name == 'Thai'
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.5  # Should have high confidence

def test_process_thai_file(sample_filepath):
    """Test processing a Thai file."""
    filepath = sample_filepath('th')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, output_format='text')
        
    stdout_content = stdout.getvalue().strip()
    assert "th" in stdout_content
    assert "Thai" in stdout_content

# --- Persian/Farsi ---
def test_detect_persian(sample_texts):
    """Test detection of Persian/Farsi text."""
    code, name, confidence = detect_language(sample_texts['fa'])
    assert code == 'fa'
    assert name == 'Persian'
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.5  # Should have high confidence

def test_process_persian_file(sample_filepath):
    """Test processing a Persian/Farsi file."""
    filepath = sample_filepath('fa')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, output_format='text')
        
    stdout_content = stdout.getvalue().strip()
    assert "fa" in stdout_content
    assert "Persian" in stdout_content

# --- Hebrew ---
def test_detect_hebrew(sample_texts):
    """Test detection of Hebrew text."""
    code, name, confidence = detect_language(sample_texts['he'])
    assert code == 'he'
    assert name == 'Hebrew'
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.5  # Should have high confidence

def test_process_hebrew_file(sample_filepath):
    """Test processing a Hebrew file."""
    filepath = sample_filepath('he')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, output_format='text')
        
    stdout_content = stdout.getvalue().strip()
    assert "he" in stdout_content
    assert "Hebrew" in stdout_content

# --- Greek ---
def test_detect_greek(sample_texts):
    """Test detection of Greek text."""
    code, name, confidence = detect_language(sample_texts['el'])
    assert code == 'el'
    assert name == 'Modern Greek (1453-)'
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.5  # Should have high confidence

def test_process_greek_file(sample_filepath):
    """Test processing a Greek file."""
    filepath = sample_filepath('el')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, output_format='text')
        
    stdout_content = stdout.getvalue().strip()
    assert "el" in stdout_content
    assert "Modern Greek" in stdout_content  # Only check for part of the full name

# --- Malay ---
def test_detect_malay(sample_texts):
    """Test detection of Malay text."""
    code, name, confidence = detect_language(sample_texts['ms'])
    # Malay is consistently detected as Indonesian due to similarity of languages
    assert code == 'id'  
    assert name == 'Indonesian'
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.5  # Should have high confidence

def test_process_malay_file(sample_filepath):
    """Test processing a Malay file."""
    filepath = sample_filepath('ms')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, output_format='text')
        
    stdout_content = stdout.getvalue().strip()
    # Malay is detected as Indonesian
    assert "id" in stdout_content
    assert "Indonesian" in stdout_content

# --- Tamil ---
def test_detect_tamil(sample_texts):
    """Test detection of Tamil text."""
    code, name, confidence = detect_language(sample_texts['ta'])
    assert code == 'ta'
    assert name == 'Tamil'
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.5  # Should have high confidence

def test_process_tamil_file(sample_filepath):
    """Test processing a Tamil file."""
    filepath = sample_filepath('ta')
    
    with capture_output() as (stdout, stderr):
        process_file(filepath, output_format='text')
        
    stdout_content = stdout.getvalue().strip()
    assert "ta" in stdout_content
    assert "Tamil" in stdout_content