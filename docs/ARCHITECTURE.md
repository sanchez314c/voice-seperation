# Architecture

## System Overview

Voice Separation is a three-stage audio processing pipeline that isolates female voices from mixed audio using signal processing and machine learning.

## Pipeline Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    VOICE ISOLATION PIPELINE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  STAGE 1: VOCAL EXTRACTION                                      │
│  ┌─────────────┐         ┌─────────────┐                       │
│  │   Input     │  ──────▶│   Demucs    │                       │
│  │  (MP3/WAV)  │         │  (htdemucs) │                       │
│  └─────────────┘         └──────┬──────┘                       │
│                                 │                               │
│                                 ▼                               │
│  STAGE 2: PITCH ANALYSIS       vocals.mp3                       │
│  ┌─────────────────────────────────────────────────────┐       │
│  │  For each 0.5s segment:                              │       │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │       │
│  │  │  Check   │─▶│  Pitch   │─▶│ Classify │          │       │
│  │  │ Silence  │  │Detection │  │  Gender  │          │       │
│  │  └──────────┘  └──────────┘  └──────────┘          │       │
│  └─────────────────────────────────────────────────────┘       │
│                                 │                               │
│                                 ▼                               │
│  STAGE 3: OUTPUT GENERATION                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Crossfade  │─▶│  Normalize  │─▶│   Export    │             │
│  │  Segments   │  │   Audio     │  │  WAV/MP3    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### Stage 1: Demucs Vocal Extraction

**Tool**: Meta's Demucs (htdemucs model)

```bash
demucs --two-stems vocals -o output_dir input.mp3
```

- Separates audio into vocals and "other" (instruments/background)
- Uses deep learning for high-quality separation
- GPU acceleration supported (CUDA)

### Stage 2: Pitch Analysis & Classification

**Algorithm**: Autocorrelation-based F0 estimation

```
Input Segment (0.5s)
        │
        ▼
┌───────────────────┐
│ Silence Check     │── RMS < 0.01 ──▶ Skip
│ (RMS threshold)   │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Autocorrelation   │
│ Pitch Detection   │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Gender Classify   │
│ F0 < 165: Male    │
│ F0 > 180: Female  │
│ 165-180: Ambiguous│
└───────────────────┘
```

### Stage 3: Output Generation

1. **Segment Assembly**: Combine classified segments
2. **Crossfade**: Apply 10ms fades at boundaries
3. **Normalization**: Scale to 0.9 peak amplitude
4. **Export**: WAV (scipy) + MP3 (FFmpeg)

## Data Flow

```
Input: audio.mp3
    │
    ▼
Demucs: htdemucs/<filename>/vocals.mp3
    │
    ▼
Analysis: Per-segment gender labels
    │
    ▼
Output: female_voice_isolated.wav
        female_voice_isolated.mp3
```

## Key Parameters

| Parameter         | Value    | Purpose              |
| ----------------- | -------- | -------------------- |
| Segment Duration  | 0.5s     | Analysis window      |
| Silence Threshold | 0.01 RMS | Skip silent segments |
| Male Cutoff       | 165 Hz   | Below = male voice   |
| Female Cutoff     | 180 Hz   | Above = female voice |
| Crossfade         | 10ms     | Smooth transitions   |
| Normalization     | 0.9 peak | Prevent clipping     |
