#!/bin/bash
#
# Voice Separation - Linux Build Script
# Creates standalone binary using PyInstaller
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
APP_NAME="voice-separation"

cd "$PROJECT_DIR"

echo "=== PURGING EXISTING BUILD ARTIFACTS ==="
rm -rf dist/ build/ *.spec

echo "=== INSTALLING DEPENDENCIES ==="
pip install -r requirements.txt
pip install pyinstaller

echo "=== BUILDING LINUX BINARY ==="
echo "Note: PyInstaller binary will still require FFmpeg and Demucs models at runtime"

pyinstaller \
    --onefile \
    --name "$APP_NAME" \
    --distpath dist/ \
    --workpath build/ \
    --hidden-import torch \
    --hidden-import torchaudio \
    --hidden-import demucs \
    --hidden-import scipy \
    --collect-all demucs \
    src/voice_isolation.py

echo "=== POST-BUILD ==="
chmod +x dist/$APP_NAME 2>/dev/null || true

echo "=== BUILD COMPLETE ==="
echo ""
if [ -f "dist/$APP_NAME" ]; then
    echo "Binary location: $PROJECT_DIR/dist/$APP_NAME"
    echo "Size: $(du -h dist/$APP_NAME | cut -f1)"
    echo ""
    echo "Note: Runtime requirements:"
    echo "  - FFmpeg must be installed"
    echo "  - Demucs models download on first run"
else
    echo "BUILD FAILED: Binary not created"
    exit 1
fi
