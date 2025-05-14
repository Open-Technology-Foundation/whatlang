#!/bin/bash
# Whatlang installation script
# Installs whatlang to /usr/local/share/whatlang and creates a symlink in /usr/local/bin

set -euo pipefail

# Ensure script is run as root
if ((EUID)); then
  echo "This installation script must be run as root (with sudo)"
  exit 1
fi

echo "Installing whatlang..."
INSTALL_DIR="/usr/local/share/whatlang"
SYMLINK_PATH="/usr/local/bin/whatlang"

# Create installation directory
mkdir -p "$INSTALL_DIR"

# Copy all files to installation directory
cp -R . "$INSTALL_DIR"

# Create virtual environment
echo "Setting up Python virtual environment..."
cd "$INSTALL_DIR"
python3 -m venv .venv

# Install dependencies
echo "Installing dependencies..."
"$INSTALL_DIR/.venv/bin/pip" install langdetect pycountry chardet

# Make script executable
chmod +x "$INSTALL_DIR/whatlang"

# Create symlink
if [ -L "$SYMLINK_PATH" ]; then
  echo "Removing existing symlink..."
  rm "$SYMLINK_PATH"
fi

echo "Creating symlink in $SYMLINK_PATH..."
ln -s "$INSTALL_DIR/whatlang" "$SYMLINK_PATH"

echo "Installation complete!"
echo "You can now use whatlang by running: whatlang [OPTIONS] [FILES...]"
echo "Run 'whatlang -h' for help."

#fin
