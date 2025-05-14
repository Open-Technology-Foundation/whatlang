#!/usr/bin/env python3
"""
Whatlang - Language detection for text files and stdin.

A lightweight command-line tool that identifies the language of text content from
files or standard input, providing language code, full name, and confidence score.

Features:
- Language detection with confidence scoring
- Processing of both files and stdin input
- Sample size control for efficient processing of large files
- Language set restriction for targeted detection
- Multiple output formats (text, JSON, CSV, Bash variables)
- Custom fallback language options
- Automatic file encoding detection
- Verbose mode for detailed processing information

Usage:
  whatlang [OPTIONS] [FILES...]
  cat file.txt | whatlang [OPTIONS]
  whatlang < file.txt

Options:
  -n, --sample-size INT  Bytes to examine (default: 512, min: 50, max: 4096)
  -L, --language-set STR Limit to languages (comma-separated, e.g., "en,fr,es")
  -f, --fallback-langcode STR  Code for failed detection (default: unknown)
  -F, --fallback-langname STR  Name for failed detection (default: Unknown)
  --format FMT          Output format: text, json, csv, bash (default: text)
  -v, --verbose         Show processing details
  -h, --help            Show help message

Dependencies:
  - langdetect: Core language detection functionality
  - pycountry: ISO language code to full name mapping
  - chardet: Automatic file encoding detection
"""

__version__ = "1.0.0"
import sys
import os
import argparse
from langdetect import DetectorFactory, detect_langs
import pycountry

# Conditionally import json
try:
  import json
  JSON_AVAILABLE = True
except ImportError:
  JSON_AVAILABLE = False

# Constants
MIN_SAMPLE_SIZE = 50  # Minimum bytes for reliable language detection
MAX_SAMPLE_SIZE = 4096  # Maximum bytes to analyze for performance reasons
DEFAULT_SAMPLE_SIZE = 512  # Default sample size if not specified

# Control warning/error message printing
# When imported as a module, warnings won't be printed by default
PRINT_WARNINGS = __name__ == "__main__"

# Set seed for reproducible results
DetectorFactory.seed = 0

def detect_language(text, lang_set=None, fallback_code="unknown", fallback_name="Unknown"):
  """
  Detect the primary language of a text sample with optional language restriction.
  
  This function analyzes text content to determine its language, with options to
  restrict detection to specific languages and handle detection failures gracefully.
  The function requires minimum text length for reliable detection (approximately 5
  characters, but more is better).
  
  Args:
      text (str): The text content to analyze for language detection
      lang_set (list, optional): List of language codes to restrict detection to 
          (e.g., ['en', 'fr', 'es']). Default is None (no restriction).
      fallback_code (str, optional): Language code to return when detection fails.
          Default is "unknown".
      fallback_name (str, optional): Language name to return when detection fails.
          Default is "Unknown".
      
  Returns:
      tuple: A 3-element tuple containing:
          - language_code (str): ISO 639-1 language code (e.g., 'en', 'fr')
          - language_name (str): Full language name (e.g., 'English', 'French')
          - confidence_score (float): Detection confidence from 0.0 to 1.0
          
  Raises:
      No exceptions are raised; errors are handled internally with fallback values.
      Warnings are printed to stderr for detection issues when PRINT_WARNINGS is True.
      
  Note:
      - Sets fallback values when text is empty, too short, or detection fails
      - Uses langdetect library for core detection functionality
      - Uses pycountry to map language codes to full language names
      - For language-restricted detection, returns fallback if no languages in the
        specified set are detected
  """
  try:
    # Check for empty or minimal text
    if not text or text.strip() == "":
      if PRINT_WARNINGS:
        print("Warning: Empty text provided", file=sys.stderr)
      return fallback_code, fallback_name, 0.0
    
    # Check minimum text length for reliable detection
    if len(text.strip()) < MIN_SAMPLE_SIZE / 10:  # More permissive for in-memory text
      if PRINT_WARNINGS:
        print(f"Warning: Text too short for reliable detection (minimum {MIN_SAMPLE_SIZE / 10} chars recommended)", file=sys.stderr)
      return fallback_code, fallback_name, 0.0
    
    # Handle language set restriction if specified
    if lang_set:
      try:
        results = detect_langs(text)
        filtered_results = [r for r in results if r.lang in lang_set]
        
        if not filtered_results:
          if PRINT_WARNINGS:
            print(f"Warning: No languages in set {lang_set} detected", file=sys.stderr)
          return fallback_code, fallback_name, 0.0
          
        result = filtered_results[0]  
        lang_code = result.lang
        confidence = result.prob
      except Exception as e:
        if PRINT_WARNINGS:
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
    if PRINT_WARNINGS:
      error_msg = f"Error detecting language: {e}"
      print(error_msg, file=sys.stderr)
    return fallback_code, fallback_name, 0.0

def format_output(filepath, code, name, confidence, output_format):
  """
  Format language detection results in the specified output format.
  
  This function takes the language detection results and formats them
  according to the specified output format (text, JSON, CSV, or Bash).
  The output format varies slightly depending on whether the input was
  from a file or stdin.
  
  Args:
      filepath (str or None): File path that was processed, or None for stdin input
      code (str): Detected language code (e.g., 'en', 'fr')
      name (str): Full language name (e.g., 'English', 'French')
      confidence (float): Detection confidence score (0.0-1.0)
      output_format (str): Format to use: 'text', 'json', 'csv', or 'bash'
      
  Returns:
      str: Formatted output string ready for printing
      
  Note:
      For file input, the output includes the basename of the file.
      For stdin input, only the language information is included.
      
      The specific format for each output type is:
      - text: "file.txt: en  English  0.99" or "en  English  0.99" (stdin)
      - json: {"file":"file.txt","language_code":"en","language_name":"English","confidence":0.99}
        or {"language_code":"en","language_name":"English","confidence":0.99} (stdin)
      - csv: "file.txt,en,English,0.99" or "en,English,0.99" (stdin)
      - bash: 'declare -A LANG_INFO=([file]="file.txt" [code]="en" [name]="English" [confidence]="0.99")'
        or 'declare -A LANG_INFO=([code]="en" [name]="English" [confidence]="0.99")' (stdin)
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

def process_file(filepath, sample_size=DEFAULT_SAMPLE_SIZE, lang_set=None, 
               fallback_code="unknown", fallback_name="Unknown", 
               output_format='text', verbose=False):
  """
  Process a file and output its language detection results.
  
  This function handles opening a text file, reading a sample of its content,
  detecting the language, and outputting the results in the specified format.
  
  Args:
      filepath (str): Absolute or relative path to the file to process
      sample_size (int, optional): Maximum number of bytes to read from the file.
          Default is 512. Larger values may improve accuracy but reduce performance.
      lang_set (list, optional): List of language codes to restrict detection to.
          Default is None (no restriction).
      fallback_code (str, optional): Language code to use when detection fails.
          Default is "unknown".
      fallback_name (str, optional): Language name to use when detection fails.
          Default is "Unknown".
      output_format (str, optional): Output format: 'text', 'json', 'csv', or 'bash'.
          Default is 'text'.
      verbose (bool, optional): Enable verbose output with processing details.
          Default is False.
          
  Returns:
      None: Results are printed directly to stdout; errors to stderr
      
  Raises:
      No exceptions are raised; errors are handled internally and printed to stderr.
      
  Note:
      - The actual sample size is constrained between MIN_SAMPLE_SIZE (50) and
        MAX_SAMPLE_SIZE (4096) bytes
      - Verbose mode outputs additional information to stderr during processing
      - Files smaller than MIN_SAMPLE_SIZE will still be processed, but with a
        warning about potential reduced accuracy
      - The function automatically detects file encoding and falls back to UTF-8
        or latin-1 if detection fails
  """
  try:
    # Enforce minimum and maximum sample size
    sample_size = max(MIN_SAMPLE_SIZE, min(sample_size, MAX_SAMPLE_SIZE))
    
    if verbose and PRINT_WARNINGS:
      print(f"Processing {filepath} (min {MIN_SAMPLE_SIZE}, max {sample_size} bytes)...", file=sys.stderr)
      
    # Detect encoding first
    encoding = 'utf-8'  # Default
    try:
      import chardet
      # Read a small sample to detect encoding
      with open(filepath, 'rb') as rawf:
        raw_bytes = rawf.read(min(1024, sample_size))
      detect_result = chardet.detect(raw_bytes)
      if detect_result['confidence'] > 0.7:
        encoding = detect_result['encoding']
        if verbose and PRINT_WARNINGS:
          print(f"Detected encoding: {encoding} (confidence: {detect_result['confidence']:.2f})", file=sys.stderr)
    except ImportError:
      if verbose and PRINT_WARNINGS:
        print("Warning: chardet not installed; using UTF-8 encoding", file=sys.stderr)
    except Exception as e:
      if verbose and PRINT_WARNINGS:
        print(f"Warning: encoding detection failed: {e}; using UTF-8", file=sys.stderr)
        
    # Now try to open with detected encoding
    try:
      with open(filepath, 'r', encoding=encoding) as f:
        text = f.read(sample_size)
    except UnicodeDecodeError:
      # Fallback to utf-8 if detected encoding fails
      if encoding != 'utf-8' and verbose and PRINT_WARNINGS:
        print(f"Warning: Failed with {encoding}, falling back to UTF-8", file=sys.stderr)
      try:
        with open(filepath, 'r', encoding='utf-8') as f:
          text = f.read(sample_size)
      except UnicodeDecodeError:
        # Last resort: try latin-1 which should always work
        if verbose and PRINT_WARNINGS:
          print("Warning: UTF-8 failed, using latin-1 as last resort", file=sys.stderr)
        with open(filepath, 'r', encoding='latin-1') as f:
          text = f.read(sample_size)
      
    actual_bytes = len(text)
    
    if verbose and PRINT_WARNINGS:
      print(f"Read {actual_bytes} bytes from {filepath} using {encoding} encoding", file=sys.stderr)
      
    if actual_bytes < MIN_SAMPLE_SIZE and PRINT_WARNINGS:
      print(f"Warning: File {filepath} is smaller than recommended minimum ({actual_bytes} < {MIN_SAMPLE_SIZE} bytes)", file=sys.stderr)
      
    code, name, confidence = detect_language(
      text, lang_set, fallback_code, fallback_name
    )
    
    if verbose and PRINT_WARNINGS:
      print(f"Detection result: {code} ({name}) with {confidence:.2f} confidence", file=sys.stderr)
      
    print(format_output(filepath, code, name, confidence, output_format))
  except Exception as e:
    if PRINT_WARNINGS:
      print(f"Error processing {filepath}: {e}", file=sys.stderr)

def set_warning_output(enabled=True):
  """
  Enable or disable warning messages when used as a module.
  
  By default, warnings are disabled when imported as a module.
  This function allows you to explicitly enable or disable warning output
  when using whatlang programmatically.
  
  Args:
      enabled (bool): True to enable warnings, False to disable
      
  Returns:
      None
      
  Example:
      >>> import whatlang
      >>> whatlang.set_warning_output(True)  # Enable warnings
      >>> code, name, confidence = whatlang.detect_language(text)
      >>> whatlang.set_warning_output(False)  # Disable warnings
      
  Note:
      This function modifies the global PRINT_WARNINGS flag which controls
      whether warning messages are output to stderr during processing.
      When whatlang is run directly as a script, warnings are enabled by default.
      When imported as a module, warnings are disabled by default unless 
      explicitly enabled with this function.
  """
  global PRINT_WARNINGS
  PRINT_WARNINGS = enabled

def main():
  """
  Command-line entry point for whatlang.
  
  This function parses command-line arguments and handles the main program flow,
  processing input from either files or stdin. It configures the language detection
  options based on user input and dispatches the processing to the appropriate
  functions.
  
  The function supports two primary modes of operation:
  1. File processing: when file paths are provided as arguments
  2. Stdin processing: when text is piped or redirected to the program
  
  If neither files nor stdin input is provided, it displays the help message.
  
  Args:
      None: Arguments are parsed from sys.argv
      
  Returns:
      None: Results are printed directly to stdout
      
  Exit codes:
      0: Successful execution
      1: No input provided (no files and no stdin)
      
  Flow:
      1. Parse command line arguments using argparse
      2. Process any sample size adjustments and language restrictions
      3. Import json library if JSON output format is selected
      4. Handle file inputs if specified
      5. Handle stdin input if available
      6. Display help and exit with code 1 if no input is provided
      
  Note:
      - JSON availability is checked if JSON output format is selected
      - Sample size is enforced within the MIN_SAMPLE_SIZE to MAX_SAMPLE_SIZE range
      - Language set is parsed from comma-separated string to a list
      - When verbose mode is enabled, processing details are output to stderr
  """
  parser = argparse.ArgumentParser(
    prog='whatlang',
    description='Detect language of text files or stdin'
  )
  parser.add_argument('files', nargs='*', help='Files to process')
  
  # Performance options
  parser.add_argument('-n', '--sample-size', type=int, default=DEFAULT_SAMPLE_SIZE,
                    help=f'Number of bytes to examine (default: {DEFAULT_SAMPLE_SIZE}, min: {MIN_SAMPLE_SIZE}, max: {MAX_SAMPLE_SIZE})')
  
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
  
  # Enforce sample size limits
  original_size = args.sample_size
  args.sample_size = max(MIN_SAMPLE_SIZE, min(args.sample_size, MAX_SAMPLE_SIZE))
  
  if args.verbose and PRINT_WARNINGS:
    if original_size < MIN_SAMPLE_SIZE:
      print(f"Warning: Sample size adjusted to minimum: {MIN_SAMPLE_SIZE} bytes", file=sys.stderr)
    elif original_size > MAX_SAMPLE_SIZE:
      print(f"Warning: Sample size adjusted to maximum: {MAX_SAMPLE_SIZE} bytes", file=sys.stderr)
  
  # Handle language restriction if specified
  lang_set = args.language_set.split(',') if args.language_set else None
  if lang_set and args.verbose and PRINT_WARNINGS:
    print(f"Restricting to languages: {', '.join(lang_set)}", file=sys.stderr)
  
  # Check if JSON is available when needed
  if args.format == 'json' and not JSON_AVAILABLE:
    if PRINT_WARNINGS:
      print("Error: JSON format selected but json module is not available", file=sys.stderr)
    sys.exit(1)
  
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
    if args.verbose and PRINT_WARNINGS:
      print(f"Reading from stdin (min {MIN_SAMPLE_SIZE}, max {args.sample_size} bytes)...", file=sys.stderr)
      
    text = sys.stdin.read(args.sample_size)
    actual_bytes = len(text)
    
    if args.verbose and PRINT_WARNINGS:
      print(f"Read {actual_bytes} bytes from stdin", file=sys.stderr)
      
    if actual_bytes < MIN_SAMPLE_SIZE and PRINT_WARNINGS:
      print(f"Warning: Text from stdin is smaller than recommended minimum ({actual_bytes} < {MIN_SAMPLE_SIZE} bytes)", file=sys.stderr)
      
    code, name, confidence = detect_language(
      text, 
      lang_set=lang_set,
      fallback_code=args.fallback_langcode,
      fallback_name=args.fallback_langname
    )
    
    if args.verbose and PRINT_WARNINGS:
      print(f"Detection result: {code} ({name}) with {confidence:.2f} confidence", file=sys.stderr)
      
    print(format_output(None, code, name, confidence, args.format))
  else:
    # No files and no stdin - print usage
    parser.print_help()
    sys.exit(1)

if __name__ == "__main__":
  main()

#fin