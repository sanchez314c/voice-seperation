# Learnings

Notes from development — gotchas, discoveries, things that didn't work.

## Electron on Linux

### Transparent Windows Require Three Switches

Getting a true transparent frameless window on Linux took forever. You need ALL of these before `app.whenReady()`:

```javascript
if (process.platform === 'linux') {
  app.commandLine.appendSwitch('enable-transparent-visuals');
  app.commandLine.appendSwitch('disable-gpu-compositing');
  app.commandLine.appendSwitch('no-sandbox');
}
```

Missing any one causes either a black background or a crash.

### Sandbox Must Be Disabled for Transparency

`webPreferences.sandbox` must be `false` on Linux for transparency to work. This is acceptable for a local app that doesn't load external content.

### BrowserView Bounds Update Timing

The BrowserView bounds must be updated AFTER the window is shown. A 200ms delay is needed:

```javascript
mainWindow.once('ready-to-show', () => {
  mainWindow.show();
  setTimeout(updateViewBounds, 200);
});
```

Also need to update on resize, maximize, and unmaximize with a 100ms delay.

### IPC Bridge Breaks With experimentalFeatures

Setting `experimentalFeatures: true` in webPreferences breaks the context bridge IPC on Linux. No idea why, but removing it fixed the issue.

## Demucs Integration

### Subprocess Polling for Cancel

Demucs runs as a subprocess and can take a long time. To support cancellation, poll the process:

```python
while process.poll() is None:
  if cancel_flag.get("cancelled"):
    process.terminate()
    raise RuntimeError("Cancelled by user")
  time.sleep(1)
```

### Output Path Variability

Demucs outputs to `htdemucs/{input_filename}/vocals.mp3` OR `vocals.wav`. The extension depends on whether you use `--mp3` flag. Always check both:

```python
vocals_path = Path(output_dir) / "htdemucs" / input_name / "vocals.mp3"
if not vocals_path.exists():
  vocals_path = Path(output_dir) / "htdemucs" / input_name / "vocals.wav"
```

## Pitch Detection

### Autocorrelation Threshold Matters

Initially set the threshold too low (0.1), causing noise to be detected as voiced. Raising to 0.3 * corr[0] eliminated false positives:

```python
if corr[peak_idx] > 0.3 * corr[0]:
  f0 = sr / peak_idx
  return f0
```

### Gender Thresholds Are Heuristic

The 165/180 Hz split is arbitrary. Some male voices go above 180 Hz (falsetto, certain microphones), some female voices drop below 165 Hz. The 15 Hz "ambiguous" zone helps by including borderline cases at 50% volume.

### Crossfade Only Between Non-Zero Segments

First attempt applied crossfades everywhere, creating artificial noise during silence. Fixed by checking both sides:

```python
if np.any(female_audio[pos - fade_samples : pos] != 0) and \
   np.any(female_audio[pos : pos + fade_samples] != 0):
  # Apply crossfade
```

## Flask and SSE

### SSE Timeout Causes Reconnect Loop

If the SSE generator blocks too long, the browser reconnects. Added a 30-second timeout with heartbeat:

```python
try:
  data = queue.get(timeout=30)
  yield f"data: {json.dumps(data)}\n\n"
except Exception:
  yield f"data: {json.dumps({'log': 'Heartbeat'})}\n\n"
```

### Task Cleanup Prevents Memory Leak

Without cleanup, abandoned tasks accumulate. Now keeps only 20 tasks:

```python
if len(tasks) > 20:
  # Remove oldest by start time
```

## File Upload Security

### UUID Filenames Prevent Collision

Using original filenames is risky — collisions and path traversal. Now use UUID:

```python
safe_filename = f"{uuid.uuid4().hex}{original_ext}"
```

### Path Traversal Protection

Download endpoint must validate paths stay inside OUTPUT_DIR:

```python
resolved = Path(file_path).resolve()
resolved.relative_to(OUTPUT_DIR.resolve())  # Raises ValueError if outside
```

## FFmpeg Integration

### FFmpeg Failure Shouldn't Block

If FFmpeg isn't installed, MP3 export fails but WAV export should still succeed. FFmpeg errors are logged as warnings, not failures:

```python
if ffmpeg_result.returncode != 0:
  queue.put({"log": f"FFmpeg warning: {stderr}", "log_type": "warning"})
```

## Port Management

### Dynamic Port Allocation Prevents Conflicts

Hardcoding a port causes conflicts if another instance is running. Now use `findFreePort()`:

```javascript
function findFreePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.listen(0, () => {
      const port = server.address().port;
      server.close(() => resolve(port));
    });
  });
}
```

## UI/UX

### Progress Updates Every 100 Segments

Sending progress for every segment floods the SSE channel. Now batch updates:

```python
if (i + 1) % 100 == 0 or i == num_segments - 1:
  queue.put({"progress": pct, "stage": f"Segment {i}/{num_segments}"})
```

### Status Indicators Need All States

Step indicators must handle: pending, active (spinner), complete (checkmark), error (X). Missing the error state caused confusion when processing failed.

## Things That Didn't Work

### Using Spleeter Instead of Demucs

Spleeter is slower and produces lower quality vocal separation. Demucs htdemucs is worth the longer model download time.

### Web Workers for Pitch Analysis

Tried to offload pitch analysis to a web worker (client-side processing). Complexity wasn't worth it — Python backend is faster and simpler.

### Real-Time Processing

Tried to process audio in real-time as it's being uploaded. Too complex for the MVP. Batch processing is fine for this use case.

## Future Improvements

### Add Tests

Currently have no automated tests. Need:
* Unit tests for `estimate_pitch()`
* Integration test for full pipeline
* E2E test with Playwright for Electron app

### Config File

Settings are hardcoded. Should support a `config.json` for user preferences.

### Multiple File Support

UI only handles one file at a time. Could add a queue system.

### Better Gender Classification

Pitch-based classification is limited. Could explore:
* Neural network classifier
* Speaker diarization (separate all speakers, not just gender)
* Voice activity detection

## Platform-Specific Gotchas

### macOS: Title Bar Style

macOS needs `titleBarStyle: 'hiddenInset'` for proper traffic light positioning. Other platforms use `frame: false`.

### Windows: Untested

Haven't tested on Windows. May need adjustments to path handling and shell commands.

### Linux: System Dependencies

Need `libnotify4` and `libappindicator3-1` for Electron to work properly. The `run-source-linux.sh` script should check for these.
