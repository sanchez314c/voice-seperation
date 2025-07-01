#!/bin/bash
#
# Voice Separation - Universal Launcher
# Detects platform and runs the application
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

case "$(uname -s)" in
    Darwin)
        echo "Detected: macOS"
        exec "$SCRIPT_DIR/run-source-macos.sh"
        ;;
    Linux)
        echo "Detected: Linux"
        exec "$SCRIPT_DIR/run-source-linux.sh"
        ;;
    MINGW*|MSYS*|CYGWIN*)
        echo "Detected: Windows (Git Bash/MSYS)"
        echo "Please use run-source-windows.bat instead"
        exit 1
        ;;
    *)
        echo "Unknown platform: $(uname -s)"
        echo "Attempting generic Linux launcher..."
        exec "$SCRIPT_DIR/run-source-linux.sh"
        ;;
esac
