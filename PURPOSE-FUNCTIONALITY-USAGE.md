# Purpose, Functionality, and Usage of Whatlang

## I. Executive Summary

Whatlang is a lightweight, command-line language detection tool designed to identify the primary language of text content from files or standard input streams. It addresses the challenge of programmatically determining the language of textual content with configurable precision. By leveraging established language detection libraries while providing a user-friendly interface, Whatlang offers a flexible solution for text language identification with confidence scoring, language filtering, and multiple output formats suitable for integration into automated workflows, content analysis systems, and text processing pipelines.

## II. Core Purpose & Rationale (The "Why")

### Problem Domain
Whatlang addresses the fundamental challenge of automated natural language identification in digital text content. This challenge frequently arises in content management systems, data processing pipelines, document classification, multilingual corpus analysis, and internationalization workflows where automated language detection is necessary for subsequent processing steps.

### Primary Goal(s)
The primary objective of Whatlang is to provide a simple, reliable, and flexible command-line interface for language detection that can be easily incorporated into scripts, data pipelines, and other automated workflows. It aims to reduce the complexity of identifying text languages while offering sufficient configurability to handle diverse use cases.

### Value Proposition
Whatlang offers several key advantages:
- Simplicity through a straightforward command-line interface
- Flexibility via configurable sample sizes and language restrictions
- Integration-friendly output formats (text, JSON, CSV, Bash)
- Performance optimization through sample-based analysis rather than processing entire documents
- Scriptability for batch processing and workflow automation

### Intended Audience/Users
Whatlang targets:
- Data engineers and analysts processing multilingual text corpora
- DevOps engineers automating content workflows
- Developers building multilingual applications
- System administrators managing content categorization
- Researchers analyzing language distributions in datasets
- Anyone who needs a quick, scriptable way to identify text languages

## III. Functionality & Capabilities (The "What" & "How")

### Key Features
1. **Language Detection**: Identifies the primary language of text content with a confidence score
2. **Multiple Input Sources**: Processes text from files or standard input (stdin)
3. **Sample-Based Analysis**: Analyzes a configurable portion of text for efficiency
4. **Language Set Restriction**: Limits detection to specified languages
5. **Custom Fallback**: Allows custom handling of failed detections
6. **Multiple Output Formats**: Supports text, JSON, CSV, and Bash variable formats
7. **Verbose Mode**: Provides processing details for diagnostics

### Core Mechanisms & Operations
Whatlang operates through the following process:
1. It reads text input from files or stdin, with a configurable sample size (defaulting to 512 bytes)
2. The core detection leverages the `langdetect` Python library with a fixed random seed for reproducible results
3. If language restriction is enabled, it filters detection results to only include specified languages
4. For successful detections, it uses the `pycountry` library to map language codes to full language names
5. It formats the results according to the specified output format (text, JSON, CSV, or Bash variables)
6. In cases of failed detection or insufficient text, it returns configurable fallback values

### Inputs & Outputs
**Inputs:**
- Text files in UTF-8 encoding
- Text streams via stdin/pipes
- Command-line arguments for configuration

**Outputs:**
- Language identification results with:
  - Language code (ISO 639-1 standard, e.g., "en", "fr")
  - Full language name (e.g., "English", "French")
  - Confidence score (0.0-1.0)
- Results formatted in text, JSON, CSV, or Bash variable format
- Diagnostic information (when verbose mode is enabled)

### Key Technologies Involved
- Python 3.12+ as the implementation language
- `langdetect` (1.0.9) for core language detection functionality
- `pycountry` (24.6.1) for mapping language codes to full names
- Bash scripting for the command-line wrapper

### Scope
Whatlang is designed to:
- Identify the primary language of UTF-8 encoded text
- Work with the languages supported by the langdetect library
- Process both file inputs and stdin streams
- Integrate into command-line workflows and scripts
- Provide machine-readable output for automated processing

## IV. Usage & Application (The "When," "How," Conditions & Constraints)

### Typical Usage Scenarios/Use Cases

1. **Content Management Systems**
   - Automatically detect languages of user-submitted content
   - Sort content by language for localization workflows
   - Flag content in unexpected languages for review

2. **Multilingual Data Processing**
   - Categorize or route documents based on language
   - Create language-specific processing pipelines
   - Build language statistics for corpus analysis

3. **Document Organization**
   - Sort a collection of text files into language-specific folders
   - Create metadata tags based on detected languages
   - Filter documents by language criteria

4. **Script Integration**
   - Use as part of shell scripts for automated workflows
   - Incorporate language detection into data processing operations
   - Generate language-aware variables for downstream processing

5. **Batch Processing**
   - Process multiple files to gather language demographics
   - Prepare datasets for language-specific training or analysis
   - Filter corpus collections by language

### Mode of Operation
Whatlang operates as a command-line tool with several modes:
1. **File Processing Mode**: `whatlang file.txt` or `whatlang file1.txt file2.txt`
2. **Stdin Processing Mode**: `cat file.txt | whatlang` or `whatlang < file.txt`
3. **Help Mode**: `whatlang -h` to display usage information

The tool can be integrated into shell scripts, used in terminal pipelines, or invoked directly on files.

### Operating Environment & Prerequisites
- **Platform**: Any system supporting Python 3.12+ and Bash
- **Dependencies**:
  - Python 3.12 or higher
  - langdetect (1.0.9)
  - pycountry (24.6.1)
  - A Python virtual environment (.venv) with dependencies installed
- **File Systems**: Read access to target files
- **Text Requirements**: UTF-8 encoded text files

### Constraints & Limitations
1. **Detection Accuracy**:
   - Requires approximately 5 characters for reliable detection
   - Accuracy depends on the underlying langdetect library's capabilities
   - May struggle with specialized or technical vocabulary
   - Cannot reliably identify constructed languages (like Elvish)

2. **Language Support**:
   - Limited to languages supported by the langdetect library
   - May not distinguish well between closely related language variants

3. **Mixed Content**:
   - Only identifies the dominant language in mixed-language content
   - Cannot detect multiple languages within the same text

4. **Technical Limitations**:
   - Assumes UTF-8 encoding for all text
   - Sample size is limited to 4096 bytes maximum
   - Minimum sample size is 50 bytes (smaller texts will still be processed with a warning)
   - Default sample size (512 bytes) balances accuracy and performance for most texts

### Integration Points
Whatlang provides several integration mechanisms:
1. **Command Output**: Standard output for piping to other commands
2. **Return Codes**: Standard exit codes for error handling in scripts
3. **Output Formats**:
   - Text format for human readability
   - JSON format for structured data processing
   - CSV format for spreadsheet and database imports
   - Bash format for direct variable integration in shell scripts

## V. Conclusion

Whatlang serves as a practical solution to the common need for language identification in text processing workflows. Its straightforward approach, combined with flexible configuration options and integration-friendly output formats, makes it a valuable tool for developers, analysts, and system administrators working with multilingual content. While it operates within certain constraints inherent to language detection technology, Whatlang's simplicity and scriptability make it particularly useful for automated workflows where programmatic language identification is required. By focusing on a specific problem domain and solving it well, Whatlang exemplifies the Unix philosophy of creating tools that do one thing and do it effectively.