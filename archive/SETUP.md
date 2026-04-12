# Setup Guide

## Prerequisites

| Requirement | Minimum | Recommended                                  |
| ----------- | ------- | -------------------------------------------- |
| Python      | 3.8     | 3.10+                                        |
| Node.js     | 18      | 20 LTS                                       |
| FFmpeg      | 4.0     | Latest                                       |
| RAM         | 4 GB    | 8 GB                                         |
| Disk        | 3 GB    | 5 GB (model + working space)                 |
| GPU         | None    | NVIDIA CUDA (speeds up Demucs significantly) |

Demucs downloads the `htdemucs` model on first run — about 200 MB. Make sure you have an internet connection for that initial download.

## Linux (Ubuntu / Debian)

### 1. Install system dependencies

```bash
sudo apt update
sudo apt install ffmpeg python3 python3-pip python3-venv
```

Check Node.js version:

```bash
node --version
```

If you need Node.js 18+:

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs
```

### 2. Clone the repo

```bash
git clone https://github.com/yourusername/voice-seperation.git
cd voice-seperation
```

### 3. Run the launcher

```bash
./run-source-linux.sh
```

The launcher will:

- Apply the Linux Electron sandbox fix (`kernel.unprivileged_userns_clone=1`)
- Kill any zombie processes from previous runs
- Create a Python venv if one doesn't exist
- Install Python dependencies from `requirements.txt`
- Install Node modules if `node_modules` doesn't exist
- Launch the Electron app via `npm start`

That's it. The app opens on the first run.

### Manual setup (if you prefer)

```bash
# Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Node modules
npm install

# Launch
npm start
```

## macOS

### 1. Install dependencies

```bash
brew install ffmpeg python3 node
```

### 2. Set up the project

```bash
git clone https://github.com/yourusername/voice-seperation.git
cd voice-seperation

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

npm install
npm start
```

Or use the launcher:

```bash
./run-source-mac.sh
```

## Windows

### 1. Install prerequisites

- Python 3.8+ from [python.org](https://python.org) — check "Add Python to PATH" during install
- Node.js from [nodejs.org](https://nodejs.org)
- FFmpeg from [ffmpeg.org/download.html](https://ffmpeg.org/download.html) — add to PATH

### 2. Set up the project

```powershell
git clone https://github.com/yourusername/voice-seperation.git
cd voice-seperation

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

npm install
npm start
```

Or run `run-source-windows.bat`.

## GPU support (optional)

Demucs runs on CPU by default. NVIDIA GPU support cuts processing time substantially on long files.

```bash
# Check if you have CUDA available
python3 -c "import torch; print(torch.cuda.is_available())"

# If False and you have an NVIDIA GPU, reinstall PyTorch with CUDA
pip uninstall torch torchaudio
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

Replace `cu118` with your CUDA version (`cu121` for CUDA 12.1, etc.). Check yours with:

```bash
nvidia-smi
```

## Verify the install

```bash
source venv/bin/activate

# Python deps
python3 -c "import torch; print('PyTorch:', torch.__version__)"
python3 -c "import demucs; print('Demucs OK')"
python3 -c "import flask; print('Flask:', flask.__version__)"

# FFmpeg
ffmpeg -version | head -1

# Node
node --version
npm --version
```

## CLI mode (no desktop app)

If you just want to run the pipeline from the command line without Electron:

1. Edit `src/voice_isolation.py` and set `input_file` and `output_dir` in the `main()` function
2. Run:

```bash
source venv/bin/activate
python src/voice_isolation.py
```

Output files appear in the directory you specified.

## Environment variables

The app picks these up automatically. You don't need to set them manually for normal use.

| Variable          | Default          | Description                                                  |
| ----------------- | ---------------- | ------------------------------------------------------------ |
| `FLASK_PORT`      | Random 8100-8999 | Port for the Flask server. Electron sets this automatically. |
| `OMP_NUM_THREADS` | CPU count        | OpenMP thread count. Electron sets this for performance.     |
| `MKL_NUM_THREADS` | CPU count        | MKL thread count. Electron sets this for performance.        |

## Troubleshooting

### Electron won't open on Linux (permission error)

The Electron sandbox requires user namespaces. The launcher handles this automatically, but if you're running manually:

```bash
sudo sysctl -w kernel.unprivileged_userns_clone=1
```

Or launch without sandbox:

```bash
npm start -- --no-sandbox
```

### Demucs model download fails

The model downloads on first run from an S3 bucket. If it fails:

- Check your internet connection
- Try running Demucs directly to trigger the download: `demucs --help`
- If behind a proxy, set `HTTPS_PROXY` before running

### FFmpeg not found during MP3 export

The MP3 conversion step calls `ffmpeg` directly. Make sure it's on your PATH:

```bash
which ffmpeg
ffmpeg -version
```

If installed but not on PATH, add it:

```bash
# Linux
export PATH="/usr/bin:$PATH"

# macOS (Homebrew)
export PATH="/opt/homebrew/bin:$PATH"
```

### Out of memory during Demucs

- Demucs on CPU needs ~2-3 GB RAM for the model itself, plus more for audio buffers
- Close other applications
- For very long files (1 hour+), consider splitting first with FFmpeg:
    ```bash
    ffmpeg -i input.mp3 -f segment -segment_time 600 -c copy chunk_%03d.mp3
    ```
- CPU will always work if GPU runs out of VRAM

### No output audio (silent file)

1. Check that Demucs actually extracted vocals — look for `htdemucs/<filename>/vocals.mp3` in the output directory
2. Check the console log in the UI for segment counts. If all segments are "male" or "silence", the pitch thresholds may not match your audio
3. Adjust thresholds in the UI (lower `silence_threshold` if too much is being dropped as silence)

### WAV works but MP3 is corrupt

FFmpeg is required for MP3 encoding. The WAV is written directly by Python's scipy. If WAV plays fine:

```bash
# Test FFmpeg manually
ffmpeg -i data/voice_separation_output/female_voice_isolated.wav -codec:a libmp3lame -qscale:a 2 test_output.mp3
```

### App exits immediately with "Flask exited with code X"

The Electron main process quits if Flask fails to start. Common causes:

- Missing Python dependencies — run `pip install -r requirements.txt` in the venv
- Port already in use — the app picks a free port dynamically, so this is rare, but you can restart to get a different port
- Python not found — make sure the venv is at `./venv/` or Python3 is on PATH
