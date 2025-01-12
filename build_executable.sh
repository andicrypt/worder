#!/bin/bash

# Variables
SCRIPT_NAME="main.py"
EXECUTABLE_NAME="worder"
JAMO_DATA_DIR=$(find / -type d -name "data" -path "*/jamo/*" 2>/dev/null)
EPITRAN_DATA_DIR=$(find / -type d -name "data" -path "*/epitran/*" 2>/dev/null)
PANPHON_DATA_DIR=$(find / -type d -name "data" -path "*/panphon/*" 2>/dev/null)

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null
then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Check if the script exists
if [ ! -f "$SCRIPT_NAME" ]; then
    echo "Error: $SCRIPT_NAME not found in the current directory."
    exit 1
fi

# Check if the data directories exist
if [ -z "$JAMO_DATA_DIR" ]; then
    echo "Error: jamo data directory not found."
    exit 1
fi

if [ -z "$EPITRAN_DATA_DIR" ]; then
    echo "Error: epitran data directory not found."
    exit 1
fi

if [ -z "$PANPHON_DATA_DIR" ]; then
    echo "Error: panphon data directory not found."
    exit 1
fi

# Build the executable
echo "Building the executable..."
pyinstaller --onefile \
    --add-data "$JAMO_DATA_DIR:jamo/data" \
    --add-data "$EPITRAN_DATA_DIR:epitran/data" \
    --add-data "$PANPHON_DATA_DIR:panphon/data" \
    --add-data "examples:examples" \
    --add-data "questions:questions" \
    --add-data "resources:resources" \
    --name "$EXECUTABLE_NAME" \
    "$SCRIPT_NAME"

# Check if the build was successful
if [ -f "dist/$EXECUTABLE_NAME" ]; then
    echo "Executable created successfully: dist/$EXECUTABLE_NAME"
else
    echo "Error: Failed to create the executable."
    exit 1
fi

# Make the executable globally accessible
echo "Making the executable globally accessible..."
sudo mv "dist/$EXECUTABLE_NAME" /usr/local/bin/
echo "Executable is now accessible system-wide as: $EXECUTABLE_NAME"

deactivate
