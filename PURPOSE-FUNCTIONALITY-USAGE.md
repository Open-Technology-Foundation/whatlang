# Whatlang: Purpose, Functionality, and Usage

## Purpose

Whatlang is a command-line utility designed to solve the common problem of identifying the natural language of text content. It addresses several key needs:

1. **Quick language identification**: Provides a simple way to determine what language a piece of text is written in without requiring linguistic expertise or manual analysis.

2. **Automation-friendly**: Enables language detection in scripts, pipelines, and automated workflows through its standard input/output design and multiple output formats.

3. **Efficiency with large files**: Optimizes processing by examining only a sample of text rather than entire documents, making it suitable for large files while maintaining accuracy.

4. **Flexibility in deployment**: Works as a standalone tool that can be integrated into various environments and workflows, from simple one-off checks to complex document processing systems.

## Functionality

Whatlang uses statistical language detection to identify the natural language of text content by:

1. **Core detection mechanism**: 
   - Leverages the `langdetect` Python library (a port of Google's language detection algorithm) to analyze text patterns
   - Maps ISO language codes to human-readable names using the `pycountry` library
   - Provides confidence scores to indicate detection reliability

2. **Versatile input handling**:
   - Processes text from files specified as command-line arguments
   - Accepts text via standard input (stdin) through pipes or redirections
   - Handles multiple files in a single command
   - Controls text sample size to optimize performance

3. **Flexible output options**:
   - Text format (default): `language_code\tlanguage_name\tconfidence`
   - JSON format: Structured data for programmatic processing
   - CSV format: Tabular data for spreadsheet applications
   - Bash format: Shell-compatible variable declarations

4. **Configuration capabilities**:
   - Language set restriction to limit detection to specific languages
   - Custom fallback language settings for detection failures
   - Verbose mode for diagnostic information

## Usage

### When to Use

Whatlang is particularly useful in the following scenarios:

1. **Content organization**: Sorting multilingual documents by language
2. **Pre-processing for NLP**: Determining language before applying language-specific processing
3. **Data validation**: Verifying that content is in the expected language
4. **Internationalization testing**: Checking correctness of translated content
5. **Text analysis**: Basic characterization of unknown text samples

### How to Use

#### Basic Usage Patterns

For examining files:
```bash
# Analyze a single file
whatlang document.txt

# Process multiple files at once
whatlang file1.txt file2.txt file3.txt
```

For processing text from other commands:
```bash
# Pipe text from another command
curl -s https://example.com | whatlang

# Use input redirection
whatlang < document.txt
```

#### Advanced Options

Sample size control for performance optimization:
```bash
# Only analyze the first 200 bytes (faster)
whatlang -n 200 large-document.txt

# Analyze more text for higher accuracy
whatlang -n 1000 ambiguous-text.txt
```

Language set restriction for targeted detection:
```bash
# Only detect English or Spanish
whatlang -L en,es document.txt
```

Output format selection for integration with other tools:
```bash
# JSON output for programmatic processing
whatlang --format json document.txt | jq .

# CSV output for spreadsheet applications
whatlang --format csv *.txt > languages.csv

# Bash format for shell scripts
eval $(whatlang --format bash document.txt)
echo "The document is in ${LANG_INFO[name]}"
```

Custom fallback handling:
```bash
# Set a custom fallback language
whatlang -f en -F English unknown-text.txt
```

### Constraints and Considerations

1. **Text length**: Requires sufficient text for reliable detection (at least 10 characters)
2. **Language coverage**: Limited to the languages supported by the langdetect library
3. **Ambiguous content**: Short texts or content with mixed languages may have lower confidence scores
4. **Processing efficiency**: Default sample size of 420 bytes balances speed and accuracy
5. **Character encoding**: Assumes UTF-8 encoding for all text processing

## Real-World Applications

1. **Content Management Systems**: Automatically tagging articles or documents by language
2. **Data Mining**: Categorizing text data by language before further analysis
3. **Web Scraping**: Determining the language of scraped content
4. **Document Processing**: Routing documents to appropriate translators or processors
5. **Academic Research**: Language identification in corpus linguistics
6. **Digital Libraries**: Organizing multilingual content
7. **Log Analysis**: Identifying language patterns in user-generated content

## Integration Examples

As part of a document processing pipeline:
```bash
# Process all PDFs in a directory, extract text, detect language, and organize
for pdf in *.pdf; do
  pdftotext "$pdf" - | whatlang --format bash > /dev/null
  mkdir -p "by-language/${LANG_INFO[code]}"
  cp "$pdf" "by-language/${LANG_INFO[code]}/"
done
```

In a content validation script:
```bash
# Verify that a translation is in the expected language
expected_lang="fr"
detected_lang=$(cat translation.txt | whatlang | cut -f1)
if [ "$detected_lang" != "$expected_lang" ]; then
  echo "Error: Expected $expected_lang but detected $detected_lang"
  exit 1
fi
```

As part of a data analysis workflow:
```bash
# Generate language statistics for a collection of documents
whatlang --format csv *.txt > language-data.csv
# Then analyze with statistical tools or spreadsheet software
```