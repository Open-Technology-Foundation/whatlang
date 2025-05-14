# Whatlang

A lightweight command-line tool for detecting the language of text content from files or standard input.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Overview

Whatlang identifies the language of text content, providing ISO language codes, full language names, and confidence scores. It's designed for efficiency and integration into automated workflows with multiple output formats.

## Key Features

- **Language Detection** - Identifies text language with confidence scores
- **Multiple Input Sources** - Processes files or stdin input through pipes/redirection
- **Performance Optimization** - Controls sample size for efficient analysis (default: 512 bytes)
- **Language Filtering** - Optional restriction to specific languages
- **Flexible Output** - Multiple formats (text, JSON, CSV, Bash variables)
- **Custom Fallbacks** - Configurable handling for failed detection
- **Automatic Encoding Detection** - Handles files with various character encodings
- **Diagnostic Mode** - Verbose output for troubleshooting

## Installation

### Quick Install (One-liner)

```bash
git clone https://github.com/Open-Technology-Foundation/whatlang && cd whatlang && sudo ./install.sh
```

### Option 1: Using the Installation Script (Recommended)

```bash
# Clone repository
git clone https://github.com/Open-Technology-Foundation/whatlang
cd whatlang

# Run the installation script (requires sudo)
sudo ./install.sh
```

This will:
- Install whatlang to `/usr/local/share/whatlang`
- Set up the Python virtual environment and install dependencies
- Create a symlink to `/usr/local/bin/whatlang`

### Option 2: Manual Installation

```bash
# Clone repository
git clone https://github.com/Open-Technology-Foundation/whatlang
cd whatlang

# Setup Python environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies directly
pip install langdetect pycountry chardet

# Make the wrapper script executable
chmod +x whatlang

# Optional: add to system path for global access
sudo ln -s "$(pwd)/whatlang" /usr/local/bin/whatlang
```

### Dependencies

Whatlang relies on the following Python packages (automatically installed with pip):
- **langdetect** (≥1.0.9) - Core language detection functionality
- **pycountry** (≥24.6.1) - For mapping language codes to names
- **chardet** (≥5.0.0) - For automatic file encoding detection

### System Requirements

- Python 3.12 or higher

## Usage

### Basic Usage

```bash
# Process a single file
whatlang document.txt
# Output: document.txt: en  English  0.98

# Process multiple files at once
whatlang file1.txt file2.txt file3.txt

# Process text from stdin via pipe
echo "Bonjour le monde" | whatlang
# Output: fr  French  0.99

# Process text from stdin via redirection
whatlang < document.txt
```

### Command-line Options

```
Usage: whatlang [OPTIONS] [FILES...]

Options:
  -n, --sample-size INT  Bytes to examine (default: 512, min: 50, max: 4096)
  -L, --language-set STR Limit to languages (comma-separated, e.g., "en,fr,es")
  -f, --fallback-langcode STR  Code for failed detection (default: unknown)
  -F, --fallback-langname STR  Name for failed detection (default: Unknown)
  --format FMT          Output format: text, json, csv, bash (default: text)
  -v, --verbose         Show processing details
  -h, --help            Show help message
```

### Output Formats

Whatlang supports multiple output formats to integrate with various workflows:

#### Text Format (default)
```bash
whatlang file.txt
# Output: file.txt: en  English  0.99
```

#### JSON Format
```bash
whatlang --format json file.txt
# Output: {"file":"file.txt","language_code":"en","language_name":"English","confidence":0.99}
```

#### CSV Format
```bash
whatlang --format csv file.txt
# Output: file.txt,en,English,0.99
```

#### Bash Format
```bash
whatlang --format bash file.txt
# Output: declare -A LANG_INFO=([file]="file.txt" [code]="en" [name]="English" [confidence]="0.99")
```

### Performance Tuning

You can adjust the sample size to balance speed and accuracy:

```bash
# Use a smaller sample for faster processing (less accurate)
whatlang -n 100 large-document.txt

# Use a larger sample for higher accuracy (slower)
whatlang -n 2000 ambiguous-document.txt
```

### Language Restriction

Restrict language detection to a specific set of languages:

```bash
# Only detect English, Spanish, or French
whatlang -L en,es,fr document.txt
```

### Custom Fallback Values

Set custom language code and name for failed detections:

```bash
# Set fallback to English
whatlang -f en -F English document.txt
```

## Practical Examples

### Programmatic Usage in Python

You can use Whatlang as a Python module in your applications:

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

### Sorting Files by Language

Create language-specific directories and sort files into them:

```bash
# Sort all text files into language-specific directories
for file in *.txt; do
  lang=$(whatlang "$file" | cut -d':' -f2 | cut -d$'\t' -f1)
  mkdir -p "by-language/$lang"
  cp "$file" "by-language/$lang/"
done
```

### Using Whatlang in Shell Scripts

Use Bash output format for direct variable integration:

```bash
# Integrate language information into a shell script
eval $(whatlang --format bash document.txt)
echo "This document is written in ${LANG_INFO[name]} (${LANG_INFO[code]})"

# Check if a file is in English
eval $(whatlang --format bash document.txt)
if [ "${LANG_INFO[code]}" = "en" ]; then
  echo "English document detected!"
fi
```

### Batch Processing with Output Analysis

Process multiple files and analyze language distribution:

```bash
# Generate CSV of all document languages for further analysis
whatlang --format csv *.txt > language-analysis.csv

# Count documents by language
whatlang --format csv *.txt | cut -d',' -f2 | sort | uniq -c | sort -nr
```

## Limitations

- **Minimum Text Length**: Requires approximately 5 characters for reliable detection
- **Language Support**: Limited to languages supported by the langdetect library
- **Mixed Content**: Only identifies the dominant language in mixed-language text
- **Constructed Languages**: May not reliably detect constructed languages (e.g., Elvish, Klingon)
- **Confidence Scores**: Confidence values are relative and may vary between language detection runs

## System Requirements

- Python 3.12+

## Building and Distribution

If you want to build the package for distribution:

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# This creates both source distribution and wheel files in the dist/ directory
# - dist/whatlang-1.0.0.tar.gz
# - dist/whatlang-1.0.0-py3-none-any.whl

# Test the package on TestPyPI (optional)
twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# Upload to PyPI (requires PyPI account)
twine upload dist/*
```

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0) - see the [LICENSE](LICENSE) file for details.

## Testing

Whatlang includes a comprehensive test suite using pytest. The tests cover core functionality, edge cases, and CLI integration.

To run the tests:

```bash
# Activate virtual environment
source .venv/bin/activate

# Install test dependencies
pip install -r requirements.txt

# Run all tests with coverage report
pytest

# Run tests for a specific module
pytest tests/test_detect_language.py

# Run tests with more verbose output
pytest -v

# Generate HTML coverage report
pytest --cov-report=html
```

The test suite includes:
- Unit tests for core functions
- Integration tests for CLI functionality
- Edge case handling
- Input/output format testing

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

When contributing code, please:
1. Add tests for new functionality
2. Ensure all tests pass
3. Maintain code quality and documentation
4. Follow the existing coding style

For development guidelines and more detailed information, see the [DEVELOPMENT.md](DEVELOPMENT.md) file.