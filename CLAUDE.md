# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Voice Separation** is a Python pipeline for isolating female voice from podcast/audio files. It uses Meta's Demucs for vocal extraction followed by pitch-based gender classification to separate speakers.

**Stack**: Python 3 / PyTorch / torchaudio / Demucs / scipy / ffmpeg
**Platform**: Linux/macOS/Windows

## Commands

```bash
# Run the pipeline
python voice_isolation.py

# Install dependencies
pip install torch torchaudio scipy demucs
# Also requires: ffmpeg (system package)
```

## Architecture

| File                 | Purpose                    |
| -------------------- | -------------------------- |
| `voice_isolation.py` | Main pipeline (~287 lines) |

### Pipeline Stages

```
Input MP3 → Demucs (vocal extraction) → Pitch Analysis → Gender Classification → Female Isolation → Output MP3
```

**Stage 1: Vocal Extraction (Demucs)**

- Uses `htdemucs` model with `--two-stems vocals` mode
- Separates vocals from music/background noise
- Output: `htdemucs/<filename>/vocals.mp3`

**Stage 2: Pitch Analysis & Gender Classification**

- Processes audio in 0.5-second segments
- Estimates fundamental frequency (F0) using autocorrelation
- Classifies by pitch range:
    - Male: < 165 Hz
    - Female: > 180 Hz
    - Ambiguous: 165-180 Hz (included at 50% volume)

**Stage 3: Post-Processing**

- Applies 10ms crossfades at segment boundaries
- Normalizes output to 0.9 peak
- Exports as WAV then converts to MP3 via ffmpeg

### Key Functions

| Function                       | Purpose                                               |
| ------------------------------ | ----------------------------------------------------- |
| `run_demucs()`                 | Shell out to demucs CLI for vocal extraction          |
| `estimate_pitch()`             | Autocorrelation-based F0 estimation (80-400 Hz range) |
| `classify_gender_by_pitch()`   | Map F0 to male/female/ambiguous                       |
| `analyze_and_isolate_female()` | Segment-by-segment processing and output generation   |

## Configuration

Hardcoded in `main()`:

- `input_file`: Path to source audio
- `output_dir`: `/home/heathen-admin/voice_separation_output`

Tunable parameters in `analyze_and_isolate_female()`:

- `segment_duration`: 0.5 seconds
- `silence_threshold`: 0.01 RMS

## Requirements

```bash
# Python packages
pip install torch torchaudio scipy demucs numpy

# System dependencies
sudo apt install ffmpeg  # Ubuntu/Debian
brew install ffmpeg      # macOS
```

## Output Structure

```
voice_separation_output/
├── htdemucs/
│   └── <input_filename>/
│       └── vocals.mp3        # Demucs vocal extraction
├── female_voice_isolated.wav # Isolated female voice
└── female_voice_isolated.mp3 # Final MP3 output
```

## Notes

- Processing time scales with audio length (41-minute file = several minutes)
- Pitch-based classification has limitations with overlapping speakers
- Ambiguous segments (165-180 Hz overlap zone) are included at reduced volume
- Requires significant disk space for intermediate files
