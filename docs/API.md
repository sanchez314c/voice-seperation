# API Reference

## Module: voice_isolation.py

### Functions

#### `run_demucs(input_file: str, output_dir: str) -> str`

Run Demucs to separate vocals from audio.

**Parameters:**

- `input_file`: Path to input audio file (MP3, WAV, etc.)
- `output_dir`: Directory for output files

**Returns:**

- Path to extracted vocals file

**Example:**

```python
vocals_path = run_demucs("/path/to/audio.mp3", "/output/dir")
# Returns: /output/dir/htdemucs/audio/vocals.mp3
```

---

#### `estimate_pitch(audio_segment: np.ndarray, sr: int) -> float`

Estimate fundamental frequency using autocorrelation.

**Parameters:**

- `audio_segment`: Audio samples as numpy array
- `sr`: Sample rate in Hz

**Returns:**

- Estimated F0 in Hz, or 0 if unvoiced

**Example:**

```python
f0 = estimate_pitch(segment, 44100)
# Returns: 220.0 (Hz) or 0 if unvoiced
```

---

#### `classify_gender_by_pitch(f0: float) -> str`

Classify gender based on fundamental frequency.

**Parameters:**

- `f0`: Fundamental frequency in Hz

**Returns:**

- `"male"`: F0 < 165 Hz
- `"female"`: F0 > 180 Hz
- `"ambiguous"`: 165-180 Hz
- `"unknown"`: F0 == 0

**Example:**

```python
gender = classify_gender_by_pitch(220.0)
# Returns: "female"
```

---

#### `analyze_and_isolate_female(vocals_path: str, output_path: str, segment_duration: float = 0.5, silence_threshold: float = 0.01)`

Analyze vocals and isolate female voice segments.

**Parameters:**

- `vocals_path`: Path to vocals audio file
- `output_path`: Path for output MP3 file
- `segment_duration`: Analysis window in seconds (default: 0.5)
- `silence_threshold`: RMS threshold for silence (default: 0.01)

**Returns:**

- Path to output MP3 file

**Example:**

```python
result = analyze_and_isolate_female(
    "/path/to/vocals.mp3",
    "/output/female_voice.mp3",
    segment_duration=0.5,
    silence_threshold=0.01
)
```

---

#### `main()`

Main entry point. Runs the complete pipeline.

**Configuration:**
Edit these variables in the function:

```python
input_file = "/path/to/input.mp3"
output_dir = "/path/to/output"
```

---

## Constants

| Constant           | Value  | Description                     |
| ------------------ | ------ | ------------------------------- |
| Min F0             | 80 Hz  | Lower bound for pitch detection |
| Max F0             | 400 Hz | Upper bound for pitch detection |
| Male Threshold     | 165 Hz | Below = classified as male      |
| Female Threshold   | 180 Hz | Above = classified as female    |
| Crossfade Duration | 10ms   | Segment boundary smoothing      |
| Normalization Peak | 0.9    | Output amplitude limit          |

---

## CLI Usage (via main)

```bash
# Edit paths in voice_isolation.py, then:
python src/voice_isolation.py
```

### Output

```
============================================================
FEMALE VOICE ISOLATION PIPELINE
============================================================
Input: /path/to/audio.mp3
Output dir: /path/to/output

============================================================
STEP 1: Extracting vocals using Demucs (Meta AI)
============================================================
Running: demucs --two-stems vocals -o /path/to/output --mp3 /path/to/audio.mp3
✓ Vocals extracted to: /path/to/output/htdemucs/audio/vocals.mp3

============================================================
STEP 2: Analyzing voice segments and identifying speakers
============================================================
Loading vocals from: /path/to/output/htdemucs/audio/vocals.mp3
Audio duration: 2460.5 seconds
Analyzing 4921 segments of 0.5s each...

✓ Analysis complete:
  - Female segments: 2100
  - Male segments: 1800
  - Ambiguous segments: 300
  - Silence/unvoiced segments: 721

============================================================
STEP 3: Post-processing and saving output
============================================================
✓ Saved WAV: /path/to/output/female_voice_isolated.wav
✓ Saved MP3: /path/to/output/female_voice_isolated.mp3

============================================================
COMPLETE!
============================================================
Female voice isolated to: /path/to/output/female_voice_isolated.mp3
```
