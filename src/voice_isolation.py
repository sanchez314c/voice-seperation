#!/usr/bin/env python3
"""
Voice Isolation Pipeline: Extract Female Voice from Podcast
============================================================
This script uses:
1. Demucs for vocal extraction (separates voice from music/noise)
2. Pitch analysis for gender classification
3. Segment-based processing to isolate female speaker

Author: OpenCode Assistant
"""

import os
import subprocess
import sys
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")

# Audio processing
import torch
import torchaudio
from scipy.io import wavfile


def run_demucs(input_file: str, output_dir: str) -> str:
    """
    Run Demucs to separate vocals from the audio.
    Returns path to the extracted vocals file.
    """
    print("\n" + "=" * 60)
    print("STEP 1: Extracting vocals using Demucs (Meta AI)")
    print("=" * 60)

    # Use htdemucs model which is optimized for vocals
    cmd = [
        "demucs",
        "--two-stems",
        "vocals",  # Only separate vocals vs other
        "-o",
        output_dir,
        "--mp3",  # Output as mp3
        input_file,
    ]

    print(f"Running: {' '.join(cmd)}")
    print("This may take several minutes for a 41-minute file...")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Demucs stderr: {result.stderr}")
        raise RuntimeError(f"Demucs failed: {result.stderr}")

    # Find the output vocals file
    input_name = Path(input_file).stem
    vocals_path = Path(output_dir) / "htdemucs" / input_name / "vocals.mp3"

    if not vocals_path.exists():
        # Try wav
        vocals_path = Path(output_dir) / "htdemucs" / input_name / "vocals.wav"

    if not vocals_path.exists():
        raise RuntimeError(f"Demucs output not found at expected path: {vocals_path}")

    print(f"✓ Vocals extracted to: {vocals_path}")
    return str(vocals_path)


def estimate_pitch(audio_segment: np.ndarray, sr: int) -> float:
    """
    Estimate fundamental frequency (pitch) using autocorrelation.
    Returns estimated F0 in Hz, or 0 if unvoiced.
    """
    # Normalize
    audio_segment = audio_segment.astype(float)
    if audio_segment.max() > 0:
        audio_segment = audio_segment / np.max(np.abs(audio_segment))

    # Autocorrelation method for pitch detection
    # Focus on typical speech range: 80-400 Hz
    min_period = int(sr / 400)  # 400 Hz upper bound
    max_period = int(sr / 80)  # 80 Hz lower bound

    if len(audio_segment) < max_period * 2:
        return 0

    # Compute autocorrelation
    corr = np.correlate(audio_segment, audio_segment, mode="full")
    corr = corr[len(corr) // 2 :]

    # Find peaks in valid range
    if max_period >= len(corr):
        max_period = len(corr) - 1

    search_region = corr[min_period:max_period]
    if len(search_region) == 0:
        return 0

    peak_idx = np.argmax(search_region) + min_period

    # Check if it's actually a peak (voiced)
    if corr[peak_idx] > 0.3 * corr[0]:
        f0 = sr / peak_idx
        return f0
    return 0


def classify_gender_by_pitch(f0: float) -> str:
    """
    Classify gender based on fundamental frequency.
    Male: typically 85-180 Hz
    Female: typically 165-255 Hz
    """
    if f0 == 0:
        return "unknown"
    elif f0 < 165:
        return "male"
    elif f0 > 180:
        return "female"
    else:
        return "ambiguous"


def analyze_and_isolate_female(
    vocals_path: str,
    output_path: str,
    segment_duration: float = 0.5,
    silence_threshold: float = 0.01,
):
    """
    Analyze vocals file segment by segment, identify female voice,
    and create output with only female segments.
    """
    print("\n" + "=" * 60)
    print("STEP 2: Analyzing voice segments and identifying speakers")
    print("=" * 60)

    # Load audio
    print(f"Loading vocals from: {vocals_path}")
    waveform, sr = torchaudio.load(vocals_path)

    # Convert to mono if stereo
    if waveform.shape[0] > 1:
        waveform = torch.mean(waveform, dim=0, keepdim=True)

    audio = waveform.numpy().squeeze()

    print(f"Audio duration: {len(audio) / sr:.1f} seconds")
    print(f"Sample rate: {sr} Hz")

    # Process in segments
    segment_samples = int(segment_duration * sr)
    num_segments = len(audio) // segment_samples

    print(f"Analyzing {num_segments} segments of {segment_duration}s each...")

    # Track results
    male_segments = 0
    female_segments = 0
    silence_segments = 0
    ambiguous_segments = 0

    # Create output array (same length as input)
    female_audio = np.zeros_like(audio)

    # Analyze each segment
    for i in range(num_segments):
        start = i * segment_samples
        end = start + segment_samples
        segment = audio[start:end]

        # Check for silence
        rms = np.sqrt(np.mean(segment**2))
        if rms < silence_threshold:
            silence_segments += 1
            continue

        # Estimate pitch
        f0 = estimate_pitch(segment, sr)
        gender = classify_gender_by_pitch(f0)

        if gender == "female":
            female_segments += 1
            female_audio[start:end] = segment
        elif gender == "male":
            male_segments += 1
            # Leave as silence (zeros)
        elif gender == "ambiguous":
            ambiguous_segments += 1
            # Include ambiguous as potential female (err on side of inclusion)
            female_audio[start:end] = segment * 0.5  # Reduce volume for ambiguous
        else:
            silence_segments += 1

        # Progress
        if (i + 1) % 500 == 0:
            print(f"  Processed {i + 1}/{num_segments} segments...")

    print("\n✓ Analysis complete:")
    print(f"  - Female segments: {female_segments}")
    print(f"  - Male segments: {male_segments}")
    print(f"  - Ambiguous segments: {ambiguous_segments}")
    print(f"  - Silence/unvoiced segments: {silence_segments}")

    # Apply light smoothing to reduce artifacts
    print("\n" + "=" * 60)
    print("STEP 3: Post-processing and saving output")
    print("=" * 60)

    # Simple crossfade between segments
    fade_samples = int(0.01 * sr)  # 10ms fade
    for i in range(1, num_segments):
        pos = i * segment_samples
        if pos + fade_samples < len(female_audio):
            fade_in = np.linspace(0, 1, fade_samples)
            fade_out = np.linspace(1, 0, fade_samples)
            # Apply fades at segment boundaries
            if np.any(female_audio[pos - fade_samples : pos] != 0) and np.any(
                female_audio[pos : pos + fade_samples] != 0
            ):
                female_audio[pos - fade_samples : pos] *= fade_out
                female_audio[pos : pos + fade_samples] *= fade_in

    # Normalize output
    max_val = np.max(np.abs(female_audio))
    if max_val > 0:
        female_audio = female_audio / max_val * 0.9

    # Save as WAV first, then convert to MP3
    wav_path = output_path.replace(".mp3", ".wav")
    wavfile.write(wav_path, sr, (female_audio * 32767).astype(np.int16))
    print(f"✓ Saved WAV: {wav_path}")

    # Convert to MP3 using ffmpeg
    mp3_path = output_path
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        wav_path,
        "-codec:a",
        "libmp3lame",
        "-qscale:a",
        "2",
        mp3_path,
    ]
    subprocess.run(cmd, capture_output=True)
    print(f"✓ Saved MP3: {mp3_path}")

    return mp3_path


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Female Voice Isolation Pipeline")
    parser.add_argument(
        "input_file", help="Path to input audio file (MP3, WAV, FLAC, etc.)"
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path.home() / "voice_separation_output"),
        help="Output directory (default: ~/voice_separation_output)",
    )
    args = parser.parse_args()

    input_file = args.input_file
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.isfile(input_file):
        print(f"ERROR: Input file not found: {input_file}")
        sys.exit(1)

    print("=" * 60)
    print("FEMALE VOICE ISOLATION PIPELINE")
    print("=" * 60)
    print(f"Input: {input_file}")
    print(f"Output dir: {output_dir}")

    # Step 1: Extract vocals using Demucs
    vocals_path = run_demucs(input_file, output_dir)

    # Step 2 & 3: Analyze and isolate female voice
    final_output = os.path.join(output_dir, "female_voice_isolated.mp3")
    result = analyze_and_isolate_female(vocals_path, final_output)

    print("\n" + "=" * 60)
    print("COMPLETE!")
    print("=" * 60)
    print(f"Female voice isolated to: {result}")
    print("\nFiles created:")
    for f in Path(output_dir).rglob("*"):
        if f.is_file():
            print(f"  - {f}")


if __name__ == "__main__":
    main()
