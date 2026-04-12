# Quick Start

Get Voice Separation running in 3 minutes.

## Prerequisites

* Python 3.8+
* Node.js 18+
* FFmpeg (for MP3 export)

Check:
```bash
python3 --version  # Should be 3.8+
node --version     # Should be 18+
ffmpeg -version    # Should exist
```

## Install

```bash
# Clone the repository
git clone https://github.com/sanchez314c/voice-seperation.git
cd voice-seperation

# Install Python dependencies
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install Node dependencies
npm install
```

## Run

**Linux:**
```bash
./run-source-linux.sh
```

**macOS/Windows:**
```bash
npm start
```

## Use

1. Drop an audio file (MP3, WAV, FLAC) into the upload zone
2. Adjust settings if desired (segment duration, silence threshold)
3. Click "Process Audio"
4. Wait for completion
5. Download the isolated female voice

## Verify

You should see:
* Frameless dark window with Neo Glass theme
* Status dot showing "Idle"
* Log console with "Voice Separation system initialized"

## Troubleshooting

**App doesn't launch (Linux):**
```bash
sudo sysctl -w kernel.unprivileged_userns_clone=1
```

**Demucs fails:**
```bash
pip install demucs
```

**FFmpeg missing:**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

## Next Steps

* Read [INSTALLATION.md](INSTALLATION.md) for detailed setup
* Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand how it works
* Read [FAQ.md](FAQ.md) for common questions
