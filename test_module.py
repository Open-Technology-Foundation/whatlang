#!/usr/bin/env python3
"""
Test script for whatlang module usage (no warnings should be printed).
"""
import whatlang
import sys
from io import StringIO
import contextlib

@contextlib.contextmanager
def capture_stderr():
    """Capture stderr output to a string."""
    old_stderr = sys.stderr
    stderr = StringIO()
    sys.stderr = stderr
    try:
        yield stderr
    finally:
        sys.stderr = old_stderr

# Test with very short text (should trigger warning about being too short)
with capture_stderr() as stderr:
    result = whatlang.detect_language("Hi")
    stderr_output = stderr.getvalue()

print(f"Default mode (should have no warnings): {result[0]}, {result[1]}, {result[2]}")
print(f"Default stderr output: '{stderr_output}'")

# Enable warnings
whatlang.set_warning_output(True)
with capture_stderr() as stderr:
    result = whatlang.detect_language("Hi")
    stderr_output = stderr.getvalue()

print(f"Warnings enabled: {result[0]}, {result[1]}, {result[2]}")
print(f"Warnings enabled stderr output: '{stderr_output}'")

# Disable warnings again
whatlang.set_warning_output(False)
with capture_stderr() as stderr:
    result = whatlang.detect_language("Hi")
    stderr_output = stderr.getvalue()

print(f"Warnings disabled: {result[0]}, {result[1]}, {result[2]}")
print(f"Warnings disabled stderr output: '{stderr_output}'")