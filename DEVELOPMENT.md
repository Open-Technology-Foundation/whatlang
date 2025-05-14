# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Whatlang

Whatlang is a lightweight command-line tool for detecting the language of text content. It provides ISO language codes, full language names, and confidence scores for text from files or standard input.

## Commands

### Development Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Make script executable
chmod +x whatlang
```

### Testing Commands
```bash
# Run all tests with coverage report
pytest

# Run specific test file
pytest tests/test_detect_language.py

# Run specific test
pytest tests/test_detect_language.py::test_detect_english

# Generate HTML coverage report
pytest --cov-report=html
```

### Running the Tool
```bash
# Process a single file
./whatlang document.txt

# Process multiple files at once
./whatlang file1.txt file2.txt file3.txt

# Process text from stdin via pipe
echo "Bonjour le monde" | ./whatlang

# Process text from stdin via redirection
./whatlang < document.txt

# With options
./whatlang -n 1000 -L en,fr,es --format json file.txt

# Verbose output (useful for debugging)
./whatlang -v file.txt
```

## Code Architecture

### Core Components

1. **whatlang.py**: Main Python implementation with three core functions:
   - `detect_language()`: Detects the language of text content with options for language restriction
   - `format_output()`: Formats detection results in different output formats (text, JSON, CSV, Bash variables)
   - `process_file()`: Handles file I/O, encoding detection, and calls the other functions
   - `main()`: CLI entry point that handles argument parsing and program flow

2. **whatlang**: Bash wrapper script that:
   - Resolves the path to the installation directory
   - Activates the Python virtual environment
   - Runs the main Python script with provided arguments

### Program Flow

1. The CLI wrapper (whatlang) activates the virtual environment and calls whatlang.py
2. whatlang.py:main() parses command-line arguments 
3. For file input: process_file() is called for each file
   - Detects file encoding using chardet
   - Reads a sample of the file content
   - Calls detect_language() to identify the language
4. For stdin input: detect_language() is called directly on stdin content
5. Results are formatted using format_output() and printed to stdout
6. Errors and verbose information go to stderr

### Key Design Features

- **Sample Size Control**: Only reads a configurable portion of files (default: 512 bytes)
- **Language Restriction**: Optional filtering to specific languages
- **Custom Fallbacks**: Configurable handling of detection failures
- **Multiple Output Formats**: Supports text, JSON, CSV, and Bash variable formats
- **Automatic Encoding Detection**: Uses chardet to detect file encoding with fallbacks
- **Error Handling**: Robust error handling with fallback values and warnings

## Testing Structure

The test suite is organized into focused modules:

- `test_detect_language.py`: Tests core language detection functionality
- `test_format_output.py`: Tests output formatting in different formats
- `test_process_file.py`: Tests file processing capabilities
- `test_cli.py`: Integration tests for the command-line interface
- `test_edge_cases.py`: Tests edge cases and error handling
- `test_additional_languages.py`: Tests for language support

## Code Style Guidelines

### Python
- 2-space indentation, shebang `#!/usr/bin/env python3`
- Import order: standard library, third-party, local
- Constants: UPPER_CASE at file top
- Descriptive function and variable names
- Google-style docstrings for all functions
- End scripts with '\n#fin\n'

### Shell Scripts
- Shebang '#!/bin/bash'
- Set `set -euo pipefail` for safer execution
- 2-space indentation
- End scripts with '\n#fin\n'

## Dependencies

Core dependencies:
- Python 3.12.3
- langdetect (≥1.0.9) - Core language detection functionality
- pycountry (≥24.6.1) - ISO language code mapping
- chardet (≥5.0.0) - Character encoding detection

Development dependencies:
- pytest (≥7.4.0) - Testing framework
- pytest-cov (≥4.1.0) - Test coverage reporting

## Programmatic Usage

Whatlang can be used as a Python module:

```python
import whatlang

# Basic language detection
text = "Hello world! This is a sample English text."
code, name, confidence = whatlang.detect_language(text)
print(f"Detected language: {name} ({code}) with {confidence:.2f} confidence")

# With language restriction
text = "Este es un texto en español."
code, name, confidence = whatlang.detect_language(text, lang_set=["es", "fr", "it"])
print(f"Detected language: {name} ({code}) with {confidence:.2f} confidence")

# With custom fallback
empty_text = ""
code, name, confidence = whatlang.detect_language(
    empty_text, 
    fallback_code="xx", 
    fallback_name="Unknown Language"
)
print(f"Fallback: {name} ({code}) with {confidence:.2f} confidence")

# Enable warning messages (for debugging)
whatlang.set_warning_output(True)
```