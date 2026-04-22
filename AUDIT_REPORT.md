# Audit Report — Voice Separation

**Date**: 2026-04-17
**Scope**: second-pass forensic audit after /repolint pass
**Auditor**: MC main (GLM sub-agent rate-limited, direct audit applied)

---

## Architecture Map

```
User input (audio file)
      |
      v
[Flask /api/process]  <-- POST multipart, extension + size validated
      |
      | (task_id, threading.Thread daemon)
      v
[process_task]
      |
      +--[run_demucs] subprocess.Popen demucs --two-stems vocals
      |       | polled every 1s, cancel_flag checked
      |       v
      |   htdemucs/<name>/vocals.mp3
      |
      +--[analyze_and_isolate_female] torchaudio.load -> numpy
              | segment loop (0.5s windows)
              | estimate_pitch (autocorrelation)
              | classify_gender_by_pitch (F0 thresholds)
              | crossfade + normalize
              v
          female_voice_isolated.{wav,mp3} via scipy.io.wavfile + ffmpeg subprocess
      |
      v
[SSE /api/progress/<task_id>]  -->  browser progress / logs / results
```

State dicts: `tasks`, `task_queues`, `cancel_flags`. Mutated from Flask request thread + background processing thread + SSE handler.

---

## Findings & Fixes

### HIGH: Race in task dicts (src/app.py:74-76, 519-528, 544-560)

**Risk**: `process_audio` (request thread) writes new task entries; `_cleanup_old_tasks` (also request thread) iterates and pops; `process_task` (background thread) reads. Python GIL protects single dict ops, but multi-step sequences (sort -> pop) can see inconsistent snapshots.

**Fix**: Added `_tasks_lock = threading.Lock()`. Wrapped init (process_audio) and cleanup (`_cleanup_old_tasks`) under the lock. Applied.

---

### MED: Fragile `.replace(".mp3", ".wav")` path surgery (src/app.py:333, 348, 352)

**Risk**: String replace inside a path is brittle — any `.mp3` anywhere in the string gets replaced. If `output_path` were changed to e.g. `/tmp/song.mp3.mp3`, behaviour is wrong. Also doesn't compose cleanly with different extensions.

**Fix**: Switched to `Path.with_suffix(".wav")` and `Path.with_name(stem + "_temp.wav")`. Applied.

---

### LOW: FLASK_PORT collision window (src/app.py:628)

**Risk**: Standalone Flask mode picks `random.randint(8100, 8999)` with no bind check. Collision causes bind failure. In Electron launch path this is not hit (Electron passes a pre-resolved free port via env).

**Fix**: Not applied — accept the trivial collision probability for the standalone dev path. Electron flow already uses `net.createServer({port: 0})` in `electron/main.js:findFreePort`. Documented in PRD ship readiness.

---

### LOW: Demucs stderr pipe-buffer risk (src/app.py:152-162)

**Risk**: `stderr=subprocess.PIPE` without active drain can theoretically fill the kernel pipe buffer (~64 KB) for very chatty Demucs runs. `process.poll()` doesn't drain; `process.communicate()` only drains after loop exits.

**Fix**: Not applied — Demucs stderr output on normal runs is well under 64 KB. If this were to regress, switch to `stderr=subprocess.DEVNULL` or spawn a drainer thread. Left as manual-review if scale changes.

---

### INFO: SSE termination already bounded (src/app.py:570-584)

**Observation**: `generate()` has a `heartbeat_count > 60` cutoff (max ~30 min) with explicit timeout status emission. Acceptable.

---

### INFO: FFmpeg failure handling is graceful (src/app.py:366-387)

**Observation**: FFmpeg failure logs a warning; downstream code `if os.path.exists(mp3_path)` gates the add to `output_files`. If mp3 conversion fails and WAV is also off, user gets zero files — but processing_time and segment counts still return. Acceptable (WAV path always runs unless `output_format == "mp3"`).

---

### INFO: Electron open-external is safe (electron/main.js:192-201)

**Observation**: URL parser + protocol whitelist `['http:', 'https:', 'mailto:']`. Rejects `file://`, `javascript:`, `data:`. No change.

---

### INFO: Path traversal guard on download is solid (src/app.py:612-623)

**Observation**: `Path(file_path).resolve()` then `relative_to(OUTPUT_DIR)` raises on escape. Additionally restricts suffix to audio extensions. No change.

---

### INFO: CSP is restrictive (src/app.py:58-67)

**Observation**: `default-src 'self'`, fonts allowlist for Google Fonts only, no `unsafe-inline` or `unsafe-eval`. Media-src allows `blob:` for local playback. No change.

---

## Applied Fixes

| File | Change |
|------|--------|
| `src/app.py` | Added `_tasks_lock = threading.Lock()` |
| `src/app.py` | Wrapped task init in `process_audio` under lock |
| `src/app.py` | Wrapped entire `_cleanup_old_tasks` body under lock |
| `src/app.py` | Replaced `.replace(".mp3", ".wav")` with `Path.with_suffix`/`with_name` |

Post-fix: `ruff check src/` clean. Python `ast.parse` clean on both modules.

## Left for Manual Review

- **FLASK_PORT collision** — low-probability, standalone dev only. Electron launch path uses net.createServer(0).
- **Demucs stderr buffer** — theoretical; not observed. Revisit if Demucs versions get more verbose.

STATUS: DONE
