# Whatlang

A command-line language detection tool for text files and stdin input.

## Features

- Identifies natural language of text content
- Processes files or stdin input
- Controls sample size for efficient analysis
- Restricts detection to specific languages
- Provides multiple output formats (text, JSON, CSV, Bash)
- Customizes fallback language for detection failures
- Includes verbose mode for diagnostics

## Installation

```bash
# Clone repository
git clone <repository-url>
cd whatlang

# Setup environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Make executable
chmod +x whatlang

# Optional: add to path
sudo ln -s "$(pwd)"/whatlang /usr/local/bin/whatlang
```

## Usage

### Basic Usage

```bash
# Process a file
whatlang document.txt
# Output: document.txt: en  English  0.98

# Process multiple files
whatlang file1.txt file2.txt

# Process from stdin
echo "Bonjour le monde" | whatlang
# Output: fr  French  0.99

# Use input redirection
whatlang < document.txt
```

### Options

```
Usage: whatlang [OPTIONS] [FILES...]

Options:
  -n, --sample-size INT  Bytes to examine (default: 420)
  -L, --language-set STR Limit to specific languages (comma-separated)
  -f, --fallback-langcode STR  Code for failed detection (default: unknown)
  -F, --fallback-langname STR  Name for failed detection (default: Unknown)
  --format FMT          Output format: text, json, csv, bash (default: text)
  -v, --verbose         Show processing details
  -h, --help            Show help message
```

### Output Formats

```bash
# Default text format
whatlang file.txt
# Output: file.txt: en  English  0.99

# JSON format
whatlang --format json file.txt
# Output: {"file":"file.txt","language_code":"en","language_name":"English","confidence":0.99}

# CSV format
whatlang --format csv file.txt
# Output: file.txt,en,English,0.99

# Bash format
whatlang --format bash file.txt
# Output: declare -A LANG_INFO=([file]="file.txt" [code]="en" [name]="English" [confidence]="0.99")
```

### Examples

#### Document Sorting

```bash
# Sort documents by language
for file in *.txt; do
  lang=$(whatlang "$file" | cut -d':' -f2 | cut -f1)
  mkdir -p "by-lang/$lang"
  cp "$file" "by-lang/$lang/"
done
```

#### Script Integration

```bash
# Use in a script
eval $(whatlang --format bash document.txt)
echo "Language: ${LANG_INFO[name]} (${LANG_INFO[code]})"
echo "Confidence: ${LANG_INFO[confidence]}"
```

## Limitations

- Requires at least 10 characters for reliable detection
- Limited to languages supported by langdetect
- Mixed-language content returns only dominant language
- Assumes UTF-8 encoding

## Dependencies

- Python 3.12+
- langdetect (1.0.9)
- pycountry (24.6.1)

## License

[Your license information]