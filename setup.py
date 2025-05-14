#!/usr/bin/env python3
"""
Setup script for the whatlang package.
"""

from setuptools import setup, find_packages

# Read the content of README.md for the long description
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="whatlang",
    version="1.0.0",
    description="A lightweight command-line tool for detecting the language of text content",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Whatlang Contributors",
    author_email="user@example.com",  # Replace with actual email
    url="https://github.com/username/whatlang",  # Replace with actual URL
    packages=find_packages(),
    py_modules=["whatlang"],
    entry_points={
        "console_scripts": [
            "whatlang-py=whatlang:main",
        ],
    },
    install_requires=[
        "langdetect>=1.0.9",
        "pycountry>=24.6.1",
        "chardet>=5.0.0",
    ],
    python_requires=">=3.12",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Utilities",
    ],
    keywords="language detection, text analysis, nlp, linguistics",
    project_urls={
        "Documentation": "https://github.com/username/whatlang",  # Replace with actual URL
        "Bug Reports": "https://github.com/username/whatlang/issues",  # Replace with actual URL
        "Source Code": "https://github.com/username/whatlang",  # Replace with actual URL
    },
)