#!/bin/bash
#
# Voice Separation - Linux Launcher
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== Voice Separation - Linux ==="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found"
    echo "Install: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi
echo "✓ Python: $(python3 --version)"

# Check FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "ERROR: FFmpeg not found"
    echo "Install: sudo apt install ffmpeg"
    exit 1
fi
echo "✓ FFmpeg found"

# Check/create virtual environment
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$PROJECT_DIR/venv"
fi

# Activate virtual environment
source "$PROJECT_DIR/venv/bin/activate"

# Install dependencies
echo "Checking dependencies..."
pip install -q -r "$PROJECT_DIR/requirements.txt"

# Check PyTorch
if python3 -c "import torch" 2>/dev/null; then
    CUDA=$(python3 -c "import torch; print('CUDA' if torch.cuda.is_available() else 'CPU')")
    echo "✓ PyTorch ($CUDA mode)"
else
    echo "Installing PyTorch..."
    pip install torch torchaudio
fi

# Check Demucs
if python3 -c "import demucs" 2>/dev/null; then
    echo "✓ Demucs installed"
else
    echo "Installing Demucs..."
    pip install demucs
fi

echo ""
echo "=== Starting Voice Separation ==="
echo ""

cd "$PROJECT_DIR"
python3 src/voice_isolation.py
