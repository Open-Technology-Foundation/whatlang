#!/usr/bin/env python3
"""
Mock version of whatlang.py for testing that includes all necessary imports.
"""

import sys
import os
import json
import argparse
from langdetect import DetectorFactory, detect_langs
import pycountry

# Copy the functions from whatlang.py for testing
def detect_language(text, lang_set=None, fallback_code="unknown", fallback_name="Unknown"):
    """
    Detect the primary language of a text sample with optional language restriction.
    
    Args:
        text (str): The text content to analyze for language detection
        lang_set (list, optional): List of language codes to restrict detection to
        fallback_code (str, optional): Language code to return when detection fails
        fallback_name (str, optional): Language name to return when detection fails
        
    Returns:
        tuple: (language_code, language_name, confidence_score)
    """
    try:
        # Check for empty or minimal text
        if not text or text.strip() == "":
            print("Warning: Empty text provided", file=sys.stderr)
            return fallback_code, fallback_name, 0.0
        
        if len(text.strip()) < 10:
            print("Warning: Text too short for reliable detection", file=sys.stderr)
            return fallback_code, fallback_name, 0.0
        
        # Handle language set restriction if specified
        if lang_set:
            try:
                results = detect_langs(text)
                filtered_results = [r for r in results if r.lang in lang_set]
                
                if not filtered_results:
                    print(f"Warning: No languages in set {lang_set} detected", file=sys.stderr)
                    return fallback_code, fallback_name, 0.0
                    
                result = filtered_results[0]  
                lang_code = result.lang
                confidence = result.prob
            except Exception as e:
                print(f"Warning: Language restriction failed: {e}", file=sys.stderr)
                return fallback_code, fallback_name, 0.0
        else:
            # Standard detection without restriction
            results = detect_langs(text)
            if not results:
                return fallback_code, fallback_name, 0.0
                
            result = results[0]
            lang_code = result.lang
            confidence = result.prob
            
        # Map language code to full name using pycountry
        try:
            lang = pycountry.languages.get(alpha_2=lang_code)
            lang_name = lang.name if lang else lang_code
            return lang_code, lang_name, confidence
        except AttributeError:
            # If language name lookup fails, use the code as the name
            return lang_code, lang_code, confidence
                
    except Exception as e:
        error_msg = f"Error detecting language: {e}"
        print(error_msg, file=sys.stderr)
        return fallback_code, fallback_name, 0.0

def format_output(filepath, code, name, confidence, output_format):
    """
    Format language detection results in the specified output format.
    
    Args:
        filepath (str or None): File path that was processed, or None for stdin input
        code (str): Detected language code (e.g., 'en', 'fr')
        name (str): Full language name (e.g., 'English', 'French')
        confidence (float): Detection confidence score (0.0-1.0)
        output_format (str): Format to use: 'text', 'json', 'csv', or 'bash'
        
    Returns:
        str: Formatted output string ready for printing
    """
    if filepath:
        # Format output for file input
        base_name = os.path.basename(filepath)
        
        if output_format == 'text':
            return f"{base_name}: {code}\t{name}\t{confidence:.2f}"
        elif output_format == 'json':
            return json.dumps({
                'file': base_name,
                'language_code': code,
                'language_name': name,
                'confidence': round(confidence, 2)
            })
        elif output_format == 'csv':
            return f"{base_name},{code},{name},{confidence:.2f}"
        elif output_format == 'bash':
            return f'declare -A LANG_INFO=([file]="{base_name}" [code]="{code}" [name]="{name}" [confidence]="{confidence:.2f}")'
    else:
        # Format output for stdin input
        if output_format == 'text':
            return f"{code}\t{name}\t{confidence:.2f}"
        elif output_format == 'json':
            return json.dumps({
                'language_code': code,
                'language_name': name,
                'confidence': round(confidence, 2)
            })
        elif output_format == 'csv':
            return f"{code},{name},{confidence:.2f}"
        elif output_format == 'bash':
            return f'declare -A LANG_INFO=([code]="{code}" [name]="{name}" [confidence]="{confidence:.2f}")'

def process_file(filepath, sample_size=420, lang_set=None, 
                fallback_code="unknown", fallback_name="Unknown", 
                output_format='text', verbose=False):
    """
    Process a file and output its language detection results.
    
    Args:
        filepath (str): Path to the file to process
        sample_size (int): Maximum number of bytes to read from the file
        lang_set (list): List of language codes to restrict detection to
        fallback_code (str): Language code to use when detection fails
        fallback_name (str): Language name to use when detection fails
        output_format (str): Output format ('text', 'json', 'csv', 'bash')
        verbose (bool): Enable verbose output with processing details
    """
    try:
        if verbose:
            print(f"Processing {filepath} (max {sample_size} bytes)...", file=sys.stderr)
            
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read(sample_size)
            
        if verbose:
            print(f"Read {len(text)} bytes from {filepath}", file=sys.stderr)
            
        code, name, confidence = detect_language(
            text, lang_set, fallback_code, fallback_name
        )
        
        if verbose:
            print(f"Detection result: {code} ({name}) with {confidence:.2f} confidence", file=sys.stderr)
            
        print(format_output(filepath, code, name, confidence, output_format))
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)

def main():
    """Command-line entry point for whatlang."""
    parser = argparse.ArgumentParser(
        prog='whatlang',
        description='Detect language of text files or stdin'
    )
    parser.add_argument('files', nargs='*', help='Files to process')
    
    # Options
    parser.add_argument('-n', '--sample-size', type=int, default=420,
                      help='Number of bytes to examine (default: 420, max: 4096)')
    parser.add_argument('--format', choices=['text', 'json', 'csv', 'bash'], 
                      default='text', help='Output format (default: text)')
    parser.add_argument('-L', '--language-set', type=str,
                      help='Comma-separated list of language codes to restrict detection to')
    parser.add_argument('-f', '--fallback-langcode', type=str, default='unknown',
                      help='Language code to use when detection fails (default: unknown)')
    parser.add_argument('-F', '--fallback-langname', type=str, default='Unknown',
                      help='Language name to use when detection fails (default: Unknown)')
    parser.add_argument('--verbose', '-v', action='store_true',
                      help='Display verbose information')
    
    args = parser.parse_args()
    
    # Enforce sample size limit
    args.sample_size = min(args.sample_size, 4096)
    
    # Handle language restriction if specified
    lang_set = args.language_set.split(',') if args.language_set else None
    
    if args.files:
        # Process files specified as arguments
        for filepath in args.files:
            process_file(
                filepath, 
                sample_size=args.sample_size,
                lang_set=lang_set,
                fallback_code=args.fallback_langcode,
                fallback_name=args.fallback_langname,
                output_format=args.format,
                verbose=args.verbose
            )
    elif not sys.stdin.isatty():
        # Process text from stdin, respecting sample_size
        if args.verbose:
            print(f"Reading from stdin (max {args.sample_size} bytes)...", file=sys.stderr)
            
        text = sys.stdin.read(args.sample_size)
        
        if args.verbose:
            print(f"Read {len(text)} bytes from stdin", file=sys.stderr)
            
        code, name, confidence = detect_language(
            text, 
            lang_set=lang_set,
            fallback_code=args.fallback_langcode,
            fallback_name=args.fallback_langname
        )
        
        if args.verbose:
            print(f"Detection result: {code} ({name}) with {confidence:.2f} confidence", file=sys.stderr)
            
        print(format_output(None, code, name, confidence, args.format))
    else:
        # No files and no stdin - print usage
        parser.print_help()
        sys.exit(1)