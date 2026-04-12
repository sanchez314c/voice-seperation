# Frequently Asked Questions

## General

### What does Voice Separation do?

It extracts female voices from podcast recordings and mixed audio files. You drop in an MP3, and it uses Meta's Demucs neural network to isolate vocals, then pitch analysis to identify female segments, producing a clean female-only vocal track.

### Is it free?

Yes. It's open source under the MIT license. The Demucs model is also free.

### What audio formats are supported?

**Input:** MP3, WAV, FLAC, OGG, M4A, AAC
**Output:** WAV and/or MP3

### Do I need an internet connection?

No. All processing happens locally on your machine. The only exception is the first run, when Demucs downloads the model (~2GB).

## Installation

### Why does the first run take so long?

Demucs downloads the htdemucs model (~2GB) on first use. Subsequent runs use the cached model.

### What if FFmpeg isn't installed?

MP3 export will fail, but WAV export will still work. Install FFmpeg:

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### Can I run it without the Electron UI?

Yes. Use the CLI:

```bash
source venv/bin/activate
python src/voice_isolation.py path/to/audio.mp3
```

Edit `input_file` in `src/voice_isolation.py` first.

## Usage

### How long does processing take?

Roughly 10-30 seconds per minute of audio, depending on your hardware. GPU acceleration helps if you have an NVIDIA GPU.

### Why are some male voices included?

The pitch thresholds are heuristic. Male voices with high pitch (falsetto, certain microphones) may be classified as "ambiguous" and included at 50% volume. You can adjust the thresholds in `src/app.py`.

### Can I adjust the gender thresholds?

Yes. Edit these constants in `src/app.py` and `src/voice_isolation.py`:

```python
MALE_THRESHOLD = 165    # Hz
FEMALE_THRESHOLD = 180  # Hz
```

Lower the female threshold to be more strict, raise it to be more inclusive.

### What does "ambiguous" mean?

Segments with fundamental frequency between 165-180 Hz are in the overlap zone between typical male and female ranges. These are included at 50% volume to avoid cutting out borderline female voices.

### Can I process multiple files at once?

Not in the current UI. You can run multiple CLI instances in parallel:

```bash
python src/voice_isolation.py file1.mp3 &
python src/voice_isolation.py file2.mp3 &
```

## Troubleshooting

### The app crashes on startup

**Linux:** You may need to fix the sandbox issue:

```bash
sudo sysctl -w kernel.unprivileged_userns_clone=1
```

Or use `run-source-linux.sh`, which applies this fix.

**macOS/Windows:** Make sure you have the latest Electron version.

### Processing hangs at "Demucs processing audio..."

Demucs is running. This can take several minutes for long files. Check the terminal for output. If it hangs for more than 30 minutes, kill the process and try again.

### "Demucs failed" error

Make sure Demucs is installed:

```bash
pip install demucs
```

If that doesn't work, try reinstalling:

```bash
pip uninstall demucs
pip install demucs
```

### No output files generated

Check the log console for errors. Common issues:

- FFmpeg not installed (for MP3 output)
- Disk space full
- File permissions

### The Electron window is black

This is a transparency issue on Linux. Run:

```bash
export ELECTRON_ENABLE_LOGGING=1
npm start
```

Check the terminal for errors. You may need to disable transparency in `electron/main.js`.

### Audio player doesn't work

The audio player requires the file to be served via the Flask backend. If you're running the CLI version, there's no audio player. Open the output file in your preferred audio player.

## Technical

### How does pitch detection work?

It uses autocorrelation. The audio segment is correlated with itself at different time lags. The lag with the highest correlation corresponds to the fundamental frequency (pitch). This is robust but not perfect — it can fail on overlapping speech or noisy audio.

### Why Demucs and not Spleeter?

Demucs (htdemucs model) generally produces better vocal separation than Spleeter, especially for music-heavy content. It's also actively maintained by Meta AI.

### Can I use a different Demucs model?

Yes. Edit the `run_demucs()` function in `src/app.py`:

```python
cmd = [
    "demucs",
    "-n", "htdemucs_ft",  # or "htdemucs", "htdemucs_6s", etc.
    "--two-stems",
    "vocals",
    # ...
]
```

### Is my audio data private?

Yes. All processing happens locally. No data is sent to external servers (except for Google Fonts in the UI, which can be removed).

### Can I use this commercially?

Yes. The MIT license allows commercial use. Demucs is also under a permissive license.

## Contributing

### How can I help?

- Report bugs on GitHub
- Suggest features
- Submit pull requests
- Improve the documentation

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

### Do you accept feature requests?

Yes. Open an issue with the "feature request" template. I can't promise to implement everything, but I'll consider all suggestions.

## Support

### Where can I get help?

- Check this FAQ and [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Search existing GitHub issues
- Open a new issue with details

### Is there a Discord or community forum?

Not currently. GitHub issues are the best place for support.
