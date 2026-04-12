# Tech Stack

Voice Separation v1.0.0

## Runtime Environment

| Component | Version | Notes |
|-----------|---------|-------|
| Node.js | 24.x | `.nvmrc` pinned |
| Python | 3.11 | `.python-version` pinned |
| Electron | ^27.3.11 | Desktop shell |

## Frontend / UI

| Technology | Purpose |
|------------|---------|
| Electron | Desktop application shell |
| HTML/CSS/JS | UI in `electron/shell.html` |
| Neo-glass design system | Dark transparent UI theme |

## Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| Flask | 3.0+ | HTTP backend serving UI and API |
| Python | 3.11 | Backend language |

## Audio Processing

| Library | Version | Purpose |
|---------|---------|---------|
| Demucs (Meta AI) | 4.0+ | Vocal extraction via htdemucs model |
| PyTorch | 2.0+ | Deep learning runtime for Demucs |
| torchaudio | 2.0+ | Audio loading and format handling |
| scipy | 1.7+ | Signal processing, autocorrelation |
| numpy | 1.21+ | Numerical array operations |
| FFmpeg | Latest | MP3 encoding (system dependency) |

## Platform Support

| Platform | Status | Notes |
|----------|--------|-------|
| Linux | Primary | `run-source-linux.sh`, full GPU support |
| macOS | Supported | `run-source-mac.sh` |
| Windows | Supported | `run-source-windows.bat` |

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 4 GB | 8 GB+ |
| GPU | None (CPU mode) | CUDA-capable (NVIDIA) |
| Disk | 2 GB | 10 GB+ (for audio processing) |

## Key Algorithms

### Pitch Detection
Autocorrelation-based F0 estimation over 0.5s segments in the 80-400 Hz range.

### Gender Classification
- Male: F0 < 165 Hz
- Ambiguous: 165-180 Hz (included at 50% volume)
- Female: F0 > 180 Hz

### Audio Pipeline
`Input MP3/WAV -> Demucs (htdemucs, --two-stems vocals) -> Pitch Analysis -> Gender Filter -> Crossfade -> Normalize -> WAV + MP3 output`
