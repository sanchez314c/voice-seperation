# Troubleshooting Guide

## Common Issues

### Demucs Fails to Run

**Symptom:** Error when running Demucs command

**Solutions:**

1. **Check Demucs installation:**
   ```bash
   python3 -c "import demucs; print('OK')"
   demucs --help
   ```

2. **Install/reinstall Demucs:**
   ```bash
   pip install --upgrade demucs
   ```

3. **Model download issues:**
   - First run downloads ~200MB model
   - Check internet connection
   - Try: `python3 -m demucs -n htdemucs --help`

### Out of Memory

**Symptom:** Process killed or memory error

**Solutions:**

1. **Use CPU instead of GPU:**
   ```python
   # Demucs will auto-fallback to CPU if CUDA unavailable
   ```

2. **Process shorter files:**
   - Split long audio into chunks
   - Process each chunk separately

3. **Increase swap space (Linux):**
   ```bash
   sudo fallocate -l 4G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

### FFmpeg Not Found

**Symptom:** MP3 conversion fails

**Solutions:**

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org and add to PATH
```

### Poor Separation Quality

**Symptom:** Female voice contains male artifacts or vice versa

**Causes:**
1. Overlapping speakers
2. Similar pitch ranges
3. Background noise

**Solutions:**
- Adjust thresholds in code:
  ```python
  # More conservative female threshold
  if f0 > 200:  # Instead of 180
      return "female"
  ```
- Pre-process audio to reduce noise
- Use longer segment duration for stability

### No Audio in Output

**Symptom:** Output file is silent or very quiet

**Check:**
1. Input file has actual audio content
2. Vocals were successfully extracted by Demucs
3. Gender classification isn't filtering everything

**Debug:**
```python
# Add debug output in analyze_and_isolate_female()
print(f"Segment {i}: RMS={rms:.4f}, F0={f0:.1f}, Gender={gender}")
```

### WAV File Works, MP3 Doesn't

**Symptom:** WAV plays fine but MP3 is corrupted

**Solutions:**
1. Check FFmpeg installation
2. Verify MP3 encoding command:
   ```bash
   ffmpeg -i input.wav -codec:a libmp3lame -qscale:a 2 output.mp3
   ```
3. Check disk space

## Debug Mode

### Enable Verbose Output

Add print statements to track processing:

```python
# In analyze_and_isolate_female()
for i in range(num_segments):
    # ... existing code ...
    if i % 100 == 0:
        print(f"Segment {i}/{num_segments}: F={female_segments}, M={male_segments}")
```

### Check Intermediate Files

```bash
# Verify Demucs output exists
ls -la output_dir/htdemucs/*/

# Check file sizes
du -h output_dir/*

# Play intermediate vocals file
ffplay output_dir/htdemucs/*/vocals.mp3
```

### Validate Audio Properties

```bash
# Check input file
ffprobe -v error -show_format -show_streams input.mp3

# Check output file
ffprobe -v error -show_format -show_streams female_voice_isolated.mp3
```

## Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: demucs` | Demucs not installed | `pip install demucs` |
| `RuntimeError: CUDA out of memory` | GPU memory full | Use CPU or smaller batches |
| `FileNotFoundError: ffmpeg` | FFmpeg not installed | Install FFmpeg |
| `ValueError: could not broadcast` | Array shape mismatch | Check audio channel count |

## Getting Help

1. Check the log output for specific error messages
2. Verify all dependencies are installed
3. Test with a small audio file first
4. Open an issue with:
   - Error message
   - Input file format/duration
   - System specs (OS, Python version, RAM)
