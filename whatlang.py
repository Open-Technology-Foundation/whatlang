#!/usr/bin/env python3
"""
Whatlang - Language detection tool for text files and stdin input.

Identifies the language of text from files or stdin, providing language code,
name, and confidence score. Supports sample size control, language restriction,
multiple output formats, and custom fallback languages.

Usage:
  whatlang [OPTIONS] [FILES...]
  cat file.txt | whatlang [OPTIONS]

Options:
  -n, --sample-size INT  Bytes to examine (default: 420)
  -L, --language-set STR Limit detection to these languages (comma-separated)
  -f, --fallback-langcode STR  Code for failed detection (default: unknown)
  -F, --fallback-langname STR  Name for failed detection (default: Unknown)
  --format FMT          Output format: text, json, csv, bash (default: text)
  -v, --verbose         Show processing details
  -h, --help            Show help message
"""

__version__ = "1.0.0"
import sys
import os
import argparse
from langdetect import DetectorFactory, detect_langs
import pycountry

# Set seed for reproducible results
DetectorFactory.seed = 0

def detect_language(text, lang_set=None, fallback_code="unknown", fallback_name="Unknown"):
  """
  Detect the language of text with optional language restriction.
  
  Args:
      text: Text to analyze
      lang_set: List of language codes to restrict detection to
      fallback_code: Code returned on detection failure
      fallback_name: Name returned on detection failure
      
  Returns:
      (language_code, language_name, confidence_score)
  """
  try:
    if not text or text.strip() == "":
      print("Warning: Empty text provided", file=sys.stderr)
      return fallback_code, fallback_name, 0.0
    
    if len(text.strip()) < 10:
      print("Warning: Text too short for reliable detection", file=sys.stderr)
      return fallback_code, fallback_name, 0.0
    
    # Run detection with potential language restriction
    if lang_set:
      # For language set restriction, we use detect_langs and filter the results
      try:
        # Use standard detection but filter results
        results = detect_langs(text)
        # Filter to only include languages in our set
        filtered_results = [r for r in results if r.lang in lang_set]
        
        if not filtered_results:
          print(f"Warning: No languages in set {lang_set} detected", file=sys.stderr)
          return fallback_code, fallback_name, 0.0
          
        # Get the most likely language from our filtered set
        result = filtered_results[0]  
        lang_code = result.lang
        confidence = result.prob
      except Exception as e:
        print(f"Warning: Failed to detect language within specified set: {e}", file=sys.stderr)
        return fallback_code, fallback_name, 0.0
    else:
      # Standard detection with probabilities
      results = detect_langs(text)
      if not results:
        return fallback_code, fallback_name, 0.0
        
      # Get the most likely language
      result = results[0]
      lang_code = result.lang
      confidence = result.prob
      
    # Get language name
    try:
      lang = pycountry.languages.get(alpha_2=lang_code)
      lang_name = lang.name if lang else lang_code
      return lang_code, lang_name, confidence
    except AttributeError:
      # If we can't get the language name, just use the code
      return lang_code, lang_code, confidence
        
  except Exception as e:
    error_msg = f"Error detecting language: {e}"
    print(error_msg, file=sys.stderr)
    return fallback_code, fallback_name, 0.0

def format_output(filepath, code, name, confidence, output_format):
  """
  Format detection results in the specified output format.
  
  Args:
      filepath: Path to file (None for stdin)
      code: Language code
      name: Language name
      confidence: Detection confidence (0.0-1.0)
      output_format: 'text', 'json', 'csv', or 'bash'
      
  Returns:
      Formatted output string
  """
  if filepath:
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
    # For stdin input
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
  Read a file, detect its language, and output the results.
  
  Args:
      filepath: File to analyze
      sample_size: Maximum bytes to read
      lang_set: Language codes to restrict detection to
      fallback_code: Code for detection failures
      fallback_name: Name for detection failures
      output_format: Output format
      verbose: Enable verbose logging
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
  """
  Command-line entry point for whatlang.
  
  Parses arguments, processes input from files or stdin, and outputs
  language detection results in the specified format.
  """
  parser = argparse.ArgumentParser(
    prog='whatlang',
    description='Detect language of text files or stdin'
  )
  parser.add_argument('files', nargs='*', help='Files to process')
  
  # Performance options
  parser.add_argument('-n', '--sample-size', type=int, default=420,
                    help='Number of bytes to examine (default: 420)')
  
  # Output format options
  parser.add_argument('--format', choices=['text', 'json', 'csv', 'bash'], 
                    default='text', help='Output format (default: text)')
  
  # Language configuration options
  parser.add_argument('-L', '--language-set', type=str,
                    help='Comma-separated list of language codes to restrict detection to (e.g., "en,fr,es")')
  
  # Fallback language options
  parser.add_argument('-f', '--fallback-langcode', type=str, default='unknown',
                    help='Language code to use when detection fails (default: unknown)')
  parser.add_argument('-F', '--fallback-langname', type=str, default='Unknown',
                    help='Language name to use when detection fails (default: Unknown)')
  
  # Verbose mode
  parser.add_argument('--verbose', '-v', action='store_true',
                    help='Display verbose information including detection details')
  
  args = parser.parse_args()
  
  # Process language restriction parameter
  lang_set = args.language_set.split(',') if args.language_set else None
  if lang_set and args.verbose:
    print(f"Restricting detection to languages: {', '.join(lang_set)}", file=sys.stderr)
  
  # Dynamic import of json when needed
  if args.format == 'json':
    global json
    import json
  
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

if __name__ == "__main__":
  main()

#fin
