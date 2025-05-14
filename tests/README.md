# Whatlang Test Suite

This directory contains a comprehensive test suite for the Whatlang language detection tool. The tests cover core functionality, edge cases, and CLI integration.

## Test Structure

- `test_detect_language.py`: Tests for the core language detection functionality
- `test_format_output.py`: Tests for the various output formats
- `test_process_file.py`: Tests for file processing functionality
- `test_cli.py`: Integration tests for the command-line interface
- `test_edge_cases.py`: Tests for edge cases and error handling
- `test_additional_languages.py`: Tests for language support with various scripts
- `conftest.py`: Pytest fixtures and test configuration
- `mock_whatlang.py`: A testing-friendly version of the whatlang module

## Running Tests

To run the tests, activate your virtual environment and use pytest:

```bash
# Activate virtual environment
source ../.venv/bin/activate

# Install test dependencies
pip install -r ../requirements.txt

# Run all tests
pytest

# Run tests with coverage report
pytest --cov=whatlang

# Run a specific test file
pytest test_detect_language.py

# Run a specific test
pytest test_detect_language.py::test_detect_english
```

## Test Coverage

The test suite includes:

1. **Unit Tests**:
   - Language detection functions
   - Output formatting
   - File processing

2. **Integration Tests**:
   - CLI argument parsing
   - End-to-end processing

3. **Edge Cases**:
   - Empty files
   - Very short texts
   - Very long texts
   - Mixed language content
   - Invalid inputs
   - Unicode handling

## Test Fixtures

The test fixtures in `conftest.py` provide:

- `sample_texts`: Sample text in multiple languages for testing
- `sample_filepath`: Function to create temporary files with sample content
- `empty_file`: Creates a temporary empty file for testing
- `short_file`: Creates a file with text too short for reliable detection
- `stdin_redirect`: Mocks stdin input for CLI testing
- `stdout_capture` and `stderr_capture`: Capture stdout/stderr for testing CLI output

## Mock Implementation

The `mock_whatlang.py` file provides a testing-friendly version of the main module that:

- Imports all necessary dependencies for testing
- Contains simplified versions of the core functions
- Makes it easier to test the CLI functionality without side effects

## Adding New Tests

When adding new functionality to Whatlang, please ensure:

1. Add corresponding tests for the new feature
2. Follow the existing test patterns
3. Include both normal usage and edge cases
4. Run the full test suite to ensure no regressions

## Implementation Notes

- Tests use temporary files and directory fixtures from pytest
- Standard input is mocked for CLI testing
- Test output capture is used to validate stdout/stderr
- Tests are written to be isolated and not depend on global state