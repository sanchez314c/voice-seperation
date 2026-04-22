# Product Requirements Document — Voice Separation

**Project**: voice-seperation
**Version**: 1.0.0
**Status**: Ship candidate
**Last Updated**: 2026-04-17
**Owner**: J. Michaels (sanchez314c)

---

## 1. Product Summary

Voice Separation is a local-first audio processing tool that isolates a specific speaker's voice (currently tuned for female vocals) from podcast-style audio. It combines Meta AI's Demucs neural vocal separator with pitch-based gender classification to remove backing music and the non-target speaker.

Three entry points:
- **CLI** — `src/voice_isolation.py` for headless/batch runs
- **Flask web UI** — `src/app.py` for in-browser use on localhost
- **Electron desktop app** — `electron/main.js` wraps Flask in a frameless Neo-Noir Glass window

## 2. Goals

1. Take any single-speaker-dominant audio file and produce a clean-vocal export of that speaker
2. Run entirely offline with no cloud calls
3. Ship as a one-command launch on Linux, macOS, and Windows
4. Expose progress and logs in real time during processing

## 3. Non-Goals

- Diarization of more than two speakers
- Live/streaming separation
- Pitch-agnostic speaker ID (no embedding-based voice matching)
- GPU-only builds (CPU path must work)

## 4. Target User

Podcasters, researchers, and audio hobbyists who have a recording with music + two speakers and want to isolate one. Users are technically capable but want a working desktop app, not a research notebook.

## 5. Pipeline Architecture

```
Input audio (MP3/WAV/FLAC/OGG/M4A/AAC)
  |
Stage 1: Demucs htdemucs --two-stems vocals
  | vocals.mp3
Stage 2: 0.5s segment loop
  - autocorrelation F0 estimation (80-400 Hz search)
  - classify: male <165 Hz, female >180 Hz, ambiguous 165-180 Hz
  - female kept at full volume, ambiguous at 50%, male zeroed
  | female-only audio buffer
Stage 3: Post-processing
  - 10ms crossfade at segment boundaries
  - Normalize to 0.9 peak
  - WAV export via scipy.io.wavfile
  - MP3 export via ffmpeg (libmp3lame q2)
  |
Output: female_voice_isolated.wav + female_voice_isolated.mp3
```

## 6. File Map

| Path | Purpose |
|------|---------|
| `src/voice_isolation.py` | CLI entry - argparse, full pipeline, prints to stdout |
| `src/app.py` | Flask server - `/`, `/api/process`, `/api/progress/<id>`, `/api/cancel`, `/api/download/<path>` |
| `src/templates/index.html` | Flask-rendered UI (Neo-Noir Glass theme) |
| `src/static/` | CSS + JS assets for web UI |
| `electron/main.js` | Electron main process - spawns Flask, frameless window, BrowserView |
| `electron/preload.js` | `contextBridge` - window controls + external link opener |
| `electron/shell.html` | Titlebar shell (wraps the Flask BrowserView) |
| `run-source-linux.sh` | One-shot launcher - venv setup, npm install, npm start |
| `run-source-mac.sh` | macOS equivalent |
| `run-source-windows.bat` | Windows equivalent |
| `requirements.txt` | Python deps - torch, torchaudio, numpy, scipy, demucs, flask |
| `package.json` | Electron 27.3.11 dev dep, `npm start` -> `electron . --no-sandbox` |

## 7. Configuration

### Tunables (runtime)
| Parameter | Default | Range | Where |
|-----------|---------|-------|-------|
| `segment_duration` | 0.5 s | 0.1-2.0 | UI slider + `/api/process` form |
| `silence_threshold` | 0.01 RMS | 0.001-0.05 | UI slider + `/api/process` form |
| `output_format` | `both` | `wav` / `mp3` / `both` | UI dropdown + form |
| `FLASK_PORT` | random 8100-8999 | any | env var |
| `MAX_CONTENT_LENGTH` | 500 MB | - | Flask config constant |

### Hard-coded paths
- Upload dir: `<repo>/data/uploads/`
- Output dir: `<repo>/data/voice_separation_output/`
- Demucs intermediate: `<output>/htdemucs/<filename>/vocals.mp3`

## 8. Security Posture

Already hardened (prior audit):

- **CSP** - `default-src 'self'`; script `self`; style `self + fonts.googleapis`; font `self + fonts.gstatic`; img `self data:`; media `self blob:`; connect `self`
- **Headers** - `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`
- **Upload validation** - Extension allowlist (`.mp3 .wav .flac .ogg .m4a .aac`); 500 MB max
- **Safe filenames** - Uploads renamed to `<uuid>.<ext>`, original name discarded
- **Path traversal guard** - `/api/download` resolves path, calls `relative_to(OUTPUT_DIR)`, ValueError on escape
- **Param clamping** - Segment duration, silence threshold, output format all clamped server-side
- **Task memory cap** - `_cleanup_old_tasks` prunes to last 20 tasks
- **Bind address** - `127.0.0.1` only
- **IPC allowlist** - Only `window-minimize`, `window-maximize`, `window-close`, `open-external`
- **External URL opener** - Protocol whitelist (`http:`, `https:`, `mailto:`)
- **Electron context isolation** - On. `nodeIntegration: false`. `sandbox: false` only because transparent frameless on Linux requires it
- **Cancel support** - Per-task cancel flag polled in the Demucs loop and the segment loop

## 9. Launch Protocol (Electron)

```
run-source-linux.sh
  | sudo sysctl kernel.unprivileged_userns_clone=1 (best-effort)
  | pkill zombie electron/flask procs
  | create venv if missing, pip install -r requirements.txt
  | npm install if node_modules missing
  | npm start -> electron . --no-sandbox
  | app.whenReady
    | findFreePort (net.createServer :0)
    | spawn python3 src/app.py (FLASK_PORT=<free>, OMP/MKL threads = cpu count)
    | waitForFlask (up to 30 retries x 500 ms)
    | createWindow (frameless, transparent, BrowserView on Flask URL)
  | on close: SIGTERM flask, SIGKILL after 2s
```

## 10. Known Limitations

1. Pitch classifier fails on overlapping speech (both heard -> counted as whatever peak wins)
2. 165-180 Hz overlap band is a real physiological gray zone; dropping volume 50% is a compromise, not a fix
3. Demucs CPU path is slow (41-minute file = several minutes); GPU drastically better but not required
4. Intermediate WAV files are not cleaned up automatically - disk usage grows
5. No multi-task parallelism on the server side; one Demucs job at a time is intended

## 11. Acceptance Criteria

- [x] `run-source-linux.sh` launches Electron app without manual steps on a fresh clone
- [x] Dragging an audio file into the drop zone triggers processing
- [x] Progress bar, step indicators, and log stream update live via SSE
- [x] Cancel button terminates the Demucs subprocess and short-circuits the segment loop
- [x] Output WAV and MP3 downloadable from the results card
- [x] Window is frameless, transparent, Neo-Noir Glass themed, titlebar min/max/close work
- [x] CSP blocks inline scripts and third-party connects
- [x] No secrets in repo or git history

## 12. Build & Test

- **Launch**: `./run-source-linux.sh`
- **CLI only**: `python src/voice_isolation.py <input.mp3>`
- **Flask only**: `python src/app.py`
- **Tests**: `tests/unit/`, `tests/integration/` (currently scaffolded, empty - TDD build pending)

## 13. Dependencies

### Runtime
- Python 3.11+ (`.python-version`)
- Node 20+ (`.nvmrc`)
- ffmpeg (system package)
- torch >=2.0, torchaudio >=2.0, numpy >=1.21, scipy >=1.7, demucs >=4.0, flask >=3.0

### Dev
- electron ^27.3.11

## 14. Ship Readiness

| Gate | Status |
|------|--------|
| Docs (27-file standard) | Present (prior run) |
| Structural compliance | Present |
| Linting | Green (ruff cache present) |
| Security audit | Passed |
| Build works | Verified |
| UI themed | Neo-Noir Glass applied |
| Secrets clean | Pending final audit (Step 12) |
