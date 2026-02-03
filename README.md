# Voice Separation

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)
![Electron](https://img.shields.io/badge/Electron-27.x-47848F.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-000000.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A desktop app that pulls female voices out of podcast recordings and mixed audio. Drop in an MP3, get back a clean isolated vocal track. Built on Meta's Demucs model for source separation plus autocorrelation-based pitch analysis for speaker classification.

## What it does

1. Runs your audio through Demucs (Meta's htdemucs model) to strip out music and background noise, leaving only vocals
2. Cuts the vocal track into 0.5-second segments and estimates the fundamental frequency of each one
3. Keeps segments classified as female (F0 > 180 Hz), drops male segments, and softens ambiguous ones
4. Crossfades the boundaries, normalizes to 0.9 peak, and exports WAV and MP3

The UI is a frameless Electron window wrapping a local Flask server. Real-time progress comes through over Server-Sent Events so you can watch the pipeline run segment by segment.

## Tech stack

- **Backend**: Python 3.8+ / Flask 3.0+ / PyTorch / torchaudio / scipy / numpy
- **ML model**: Meta Demucs (htdemucs) for source separation
- **Desktop shell**: Electron 27.x, frameless transparent window with BrowserView
- **Frontend**: Dark Neo Glass theme, SSE for real-time progress, drag-and-drop upload
- **Audio conversion**: FFmpeg for MP3 encoding

## Features

- Drag-and-drop file upload (MP3, WAV, FLAC, OGG)
- Real-time pipeline progress with step-by-step status
- Live console log with color-coded message types
- Segment stats on completion (female / male / ambiguous / silence counts)
- Audio preview player for the isolated output
- Configurable segment duration, silence threshold, and output format
- Cancel button to stop processing mid-run
- Auto-detects free port, no port conflicts
- GPU acceleration if CUDA is available (Demucs handles this automatically)

## Quick start

### Prerequisites

- Python 3.8+
- Node.js 18+
- FFmpeg
- ~2 GB disk for the Demucs htdemucs model (downloads on first run)
- 4 GB RAM minimum, 8 GB recommended

### Install

```bash
# Ubuntu/Debian
sudo apt install ffmpeg python3 python3-pip python3-venv

# macOS
brew install ffmpeg

# Clone the repo
git clone https://github.com/yourusername/voice-seperation.git
cd voice-seperation
```

### Run (Linux)

```bash
./run-source-linux.sh
```

This script handles everything: creates the Python venv, installs dependencies, installs Node modules, applies the Linux sandbox fix, and launches the Electron app.

### Run manually

```bash
# Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install Electron
npm install

# Launch
npm start
```

### CLI mode (no desktop)

Edit the input/output paths in `src/voice_isolation.py`, then:

```bash
source venv/bin/activate
python src/voice_isolation.py
```

## Configuration

The pipeline parameters are adjustable in the web UI before processing or in the source for CLI use.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `segment_duration` | 0.5s | Analysis window size per segment |
| `silence_threshold` | 0.01 RMS | Below this RMS is treated as silence and skipped |
| `output_format` | both | `wav`, `mp3`, or `both` |

**Pitch thresholds** (hardcoded in `src/app.py` and `src/voice_isolation.py`):

| Label | Range | Behavior |
|-------|-------|----------|
| Male | F0 < 165 Hz | Dropped |
| Ambiguous | 165 - 180 Hz | Included at 50% volume |
| Female | F0 > 180 Hz | Kept at full volume |

## Output

```
data/voice_separation_output/
├── htdemucs/
│   └── <input_filename>/
│       └── vocals.mp3          # Demucs extracted vocals
├── female_voice_isolated.wav
└── female_voice_isolated.mp3
```

## Project structure

```
voice-seperation/
├── electron/
│   ├── main.js             # Electron main process, spawns Flask
│   ├── preload.js          # IPC context bridge for window controls
│   └── shell.html          # Frameless titlebar with traffic-light buttons
├── src/
│   ├── app.py              # Flask web app, task management, SSE progress
│   ├── voice_isolation.py  # Standalone CLI pipeline script
│   ├── templates/
│   │   └── index.html      # Main UI template
│   └── static/
│       ├── css/theme.css   # Dark Neo Glass design system
│       └── js/main.js      # Frontend logic
├── data/
│   ├── uploads/            # Temporary uploaded files
│   └── voice_separation_output/  # Pipeline output
├── docs/                   # Extended documentation
├── tests/                  # Unit and integration tests
├── scripts/                # Build and run scripts
├── requirements.txt        # Python dependencies
├── package.json            # Electron config
└── run-source-linux.sh     # One-command Linux launcher
```

## License

MIT License - Copyright (c) 2025 Jason
