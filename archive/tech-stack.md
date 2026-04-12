# Technology Stack

## Core Technologies

| Technology | Version | Purpose                    |
| ---------- | ------- | -------------------------- |
| Python     | 3.8+    | Primary language           |
| PyTorch    | 2.0+    | Deep learning framework    |
| torchaudio | 2.0+    | Audio loading/processing   |
| Demucs     | 4.0+    | Vocal separation (Meta AI) |
| scipy      | 1.7+    | Signal processing          |
| numpy      | 1.21+   | Numerical operations       |
| FFmpeg     | Latest  | Audio format conversion    |

## Architecture

### Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Voice Isolation Pipeline                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Input     │───▶│   Demucs    │───▶│   Pitch     │     │
│  │  (MP3/WAV)  │    │  (htdemucs) │    │  Analysis   │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                              │              │
│                                              ▼              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Output    │◀───│    Post-    │◀───│   Gender    │     │
│  │  (MP3/WAV)  │    │  Processing │    │   Filter    │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Processing Flow

1. **Demucs Stage** (GPU/CPU)
    - Model: `htdemucs` with `--two-stems vocals`
    - Separates vocals from instrumental/background
    - Output: Clean vocal track

2. **Analysis Stage** (CPU)
    - Segment audio into 0.5-second windows
    - Autocorrelation for pitch detection
    - F0 range: 80-400 Hz

3. **Classification Stage** (CPU)
    - Male threshold: < 165 Hz
    - Female threshold: > 180 Hz
    - Ambiguous: 165-180 Hz (reduced volume)

4. **Output Stage** (CPU)
    - 10ms crossfades between segments
    - Peak normalization to 0.9
    - WAV + MP3 export via FFmpeg

## Key Algorithms

### Pitch Detection (Autocorrelation)

```python
# Estimate fundamental frequency
corr = np.correlate(segment, segment, mode='full')
# Find peak in speech range (80-400 Hz)
peak_idx = find_peak_in_range(corr, sr/400, sr/80)
f0 = sr / peak_idx
```

### Gender Classification

| F0 Range   | Classification   |
| ---------- | ---------------- |
| 0 Hz       | Unvoiced/Silence |
| < 165 Hz   | Male             |
| 165-180 Hz | Ambiguous        |
| > 180 Hz   | Female           |

## Performance Characteristics

| Stage    | Speed          | Memory     |
| -------- | -------------- | ---------- |
| Demucs   | ~0.3x realtime | 2-4 GB     |
| Analysis | ~50x realtime  | < 500 MB   |
| Total    | ~0.3x realtime | ~4 GB peak |

## External Dependencies

- **FFmpeg**: Required for MP3 encoding
- **CUDA** (optional): GPU acceleration for Demucs

## Limitations

1. Pitch-based classification doesn't work well with:
    - Overlapping speakers
    - Singing (different pitch ranges)
    - Processed/pitch-shifted audio

2. Demucs requires significant memory for long audio files

3. Processing time scales linearly with audio duration
