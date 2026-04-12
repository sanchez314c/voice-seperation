# Voice Separation — Implementation Notes

## Current State (v0.2.0)

The project is a working Electron desktop app wrapping a Flask backend. Core pipeline is functional end-to-end.

### What works

- Full three-stage pipeline: Demucs vocal extraction > pitch-based gender classification > output generation
- Electron desktop wrapper with frameless transparent window, custom titlebar, and traffic-light controls
- Flask web UI with Dark Neo Glass design system
- Real-time SSE progress stream (step indicators, segment counts, log console)
- Drag-and-drop audio upload (MP3, WAV, FLAC, OGG)
- WAV and MP3 output with audio preview player
- Cancel mid-processing
- Configurable segment duration, silence threshold, output format
- One-command launcher scripts for Linux, macOS, Windows
- GPU acceleration via CUDA (Demucs handles this transparently)

### Known limitations

- Pitch-based classification is simple. Two speakers of similar pitch talking simultaneously will bleed into each other.
- No multi-speaker separation — just binary male/female based on F0 threshold.
- Task state lives in-memory (module-level dicts). Restarting the app loses task history.
- Output always goes to a fixed filename (`female_voice_isolated.wav/mp3`). Multiple runs overwrite previous output.
- CLI script (`voice_isolation.py`) has hardcoded paths in `main()`.

## Planned features

These are captured from the CHANGELOG under `[Unreleased]`:

- **Multi-speaker separation**: Move beyond binary male/female to detect and separate N distinct speakers
- **Waveform visualization**: Show waveform of input and output in the UI
- **Batch processing**: Queue multiple files and process them in sequence
- **Real-time processing mode**: Stream input and process on the fly
- **CLI argument support**: Replace hardcoded paths in `voice_isolation.py` with `argparse`

## Ideas to explore

- Use a speaker diarization library (pyannote-audio) instead of raw pitch analysis — would handle edge cases better and not assume binary gender
- Configurable output filename/path instead of fixed `female_voice_isolated`
- Persistent task history with SQLite so past results survive app restarts
- Progress bar in the taskbar/dock (Electron supports this)
- Dark/light mode toggle
- Waveform comparison (input vocals vs. output) using WebAudio API or a canvas renderer
