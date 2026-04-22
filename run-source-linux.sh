#!/bin/bash
set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

print_status() { echo -e "${CYAN}[$(date +'%H:%M:%S')]${NC} $1"; }
print_success() { echo -e "${GREEN}[$(date +'%H:%M:%S')] ✔${NC} $1"; }
print_error() { echo -e "${RED}[$(date +'%H:%M:%S')] ✘${NC} $1"; }

print_status "🚀 Starting Voice Separation from source (Linux)..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Linux sandbox fix ──
# Enables unprivileged user namespaces required for Electron on some Linux distros.
# Requires sudo. If not available, Electron will fall back to --no-sandbox mode.
print_status "Applying Linux sandbox fix..."
sudo sysctl -w kernel.unprivileged_userns_clone=1 &>/dev/null 2>&1 || true
print_success "Sandbox permissions configured"

# ── Clean up zombie processes ──
print_status "Cleaning up zombie processes..."
pkill -f "electron.*voice-separation" 2>/dev/null || true
pkill -f "python.*voice.separation.*src/app.py" 2>/dev/null || true
sleep 1
print_success "Cleanup complete"

# ── Check Python venv ──
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

if [ -f "requirements.txt" ]; then
    print_status "Checking Python dependencies..."
    pip install -r requirements.txt -q 2>/dev/null
    print_success "Python dependencies OK"
fi

# ── Check Node dependencies ──
if [ ! -d "node_modules" ]; then
    print_status "Installing Node dependencies..."
    npm install
fi
print_success "Dependencies OK (Node: $(node --version), Python: $(python --version 2>&1 | awk '{print $2}'))"

# ── Launch ──
print_success "Launching Voice Separation..."
npm start

EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    print_success "Application session ended"
else
    print_error "Application exited with code $EXIT_CODE"
fi
