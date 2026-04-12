# Architecture

## Overview

Voice Separation is a desktop application with two main layers: an Electron shell that provides the window chrome, and a Python/Flask backend that does all the audio processing. The two communicate over localhost HTTP. The frontend talks to Flask via SSE for real-time progress during processing.

## High-level diagram

```
┌─────────────────────────────────────────────────────┐
│                  Electron Process                    │
│                                                      │
│  ┌──────────────┐     BrowserView     ┌──────────┐  │
│  │  shell.html  │                     │  Flask   │  │
│  │  (titlebar)  │   http://127.0.0.1  │  web app │  │
│  │  IPC bridge  │◀───────────────────▶│  :PORT   │  │
│  └──────────────┘                     └──────────┘  │
│                                            │         │
│                             Spawns Flask as child    │
│                             process on free port     │
└─────────────────────────────────────────────────────┘
                                            │
                                  ┌─────────▼─────────┐
                                  │  Audio Processing  │
                                  │  Pipeline (Python) │
                                  └─────────┬─────────┘
                                            │
                            ┌───────────────┼───────────────┐
                            │               │               │
                      ┌─────▼────┐   ┌──────▼─────┐  ┌─────▼─────┐
                      │  Demucs  │   │   Pitch    │  │  FFmpeg   │
                      │ (htdemucs│   │  Analysis  │  │ MP3 export│
                      │  model)  │   │ (autocorr) │  └───────────┘
                      └──────────┘   └────────────┘
```

## Component breakdown

### Electron layer (`electron/`)

**`main.js`** — The main process. Responsible for:

- Finding a free TCP port with `net.createServer()`
- Spawning `src/app.py` as a child process with `FLASK_PORT` set in env
- Polling that port until Flask is ready (500ms intervals, 30 retries)
- Creating the frameless `BrowserWindow` with transparent background
- Creating a `BrowserView` positioned below the 40px titlebar to host Flask content
- Handling window resize events to keep BrowserView bounds in sync
- IPC handlers for minimize, maximize, close
- Linux-specific flags: `--enable-transparent-visuals`, `--disable-gpu-compositing`

**`shell.html`** — The custom titlebar. A single HTML file with embedded CSS that renders the floating panel frame and traffic-light window control buttons (red close, yellow minimize, green maximize). Uses `-webkit-app-region: drag` for window dragging.

**`preload.js`** — Bridges the shell HTML to Electron IPC using `contextBridge.exposeInMainWorld`. Exposes `window.electronAPI.{minimize, maximize, close}`.

### Flask backend (`src/app.py`)

Single-file Flask application. Handles:

- File uploads (UUID-prefixed filenames, 500MB limit)
- Task lifecycle with in-memory dictionaries (`tasks`, `task_queues`, `cancel_flags`)
- Background threads for processing (one `threading.Thread` per job)
- SSE endpoint at `/api/progress/<task_id>` that drains a `Queue` and yields JSON events
- Cancel endpoint that sets a flag the processing thread checks between segments
- File download endpoint with path validation against `OUTPUT_DIR`

**Routes:**

| Method | Path                        | Purpose                                 |
| ------ | --------------------------- | --------------------------------------- |
| GET    | `/`                         | Serve main UI                           |
| POST   | `/api/process`              | Start processing job, returns `task_id` |
| GET    | `/api/progress/<task_id>`   | SSE stream of progress events           |
| POST   | `/api/cancel`               | Cancel all running tasks                |
| GET    | `/api/download/<file_path>` | Download output file                    |

### Audio pipeline

The pipeline runs in three stages inside a background thread.

**Stage 1 — Vocal extraction (Demucs)**

Calls `demucs --two-stems vocals -o <output_dir> --mp3 <input>` as a subprocess. The `--two-stems vocals` flag tells Demucs to split into vocals vs. everything-else rather than all four stems (vocals, drums, bass, other). Uses the `htdemucs` model (Hybrid Transformer Demucs). Output lands at `<output_dir>/htdemucs/<filename>/vocals.mp3`.

During processing, the thread polls `process.poll()` in a 1-second loop and checks the cancel flag on each iteration.

**Stage 2 — Pitch analysis and classification**

Loads the vocals file with `torchaudio`, converts stereo to mono by averaging channels, then iterates in `segment_duration`-second chunks (default 0.5s).

For each segment:

1. Calculate RMS. If below `silence_threshold` (default 0.01), skip.
2. Run autocorrelation pitch detection to estimate F0 in the 80-400 Hz range.
3. Classify by F0: male (<165 Hz), female (>180 Hz), ambiguous (165-180 Hz).
4. Copy female segments into the output array at full amplitude.
5. Copy ambiguous segments at 50% amplitude.
6. Male segments become silence (zeros).

Progress events fire every 100 segments. The cancel flag is checked every segment.

**Stage 3 — Post-processing**

1. Apply 10ms crossfade at each segment boundary where both sides have audio.
2. Normalize the output to 0.9 peak amplitude.
3. Write WAV via `scipy.io.wavfile.write` (16-bit PCM).
4. Encode MP3 via `ffmpeg -codec:a libmp3lame -qscale:a 2` if requested.

### Frontend (`src/static/`, `src/templates/`)

Single-page app served by Flask. The HTML template uses a Dark Neo Glass design system with CSS custom properties. JavaScript opens an `EventSource` to the SSE endpoint on job start, parses events, and updates:

- A numeric progress bar
- A step indicator (Demucs > Pitch Analysis > Post-Processing)
- A live console log with color-coded entries
- Result stats on completion
- An audio player and download links

## Data flow

```
User uploads file
        │
        ▼
POST /api/process
  → saves file to data/uploads/<uuid>_<filename>
  → spawns background thread
  → returns task_id
        │
        ▼
Background thread:
  Stage 1: demucs subprocess
    → data/voice_separation_output/htdemucs/<name>/vocals.mp3
  Stage 2: pitch analysis per 0.5s segment
    → builds female_audio numpy array
  Stage 3: crossfade + normalize + export
    → data/voice_separation_output/female_voice_isolated.wav
    → data/voice_separation_output/female_voice_isolated.mp3
        │
        ▼
GET /api/progress/<task_id>  (SSE, open during processing)
  → streams JSON events from Queue
  → final event includes file list and stats

GET /api/download/<file_path>
  → streams output file to browser
```

## Key design decisions

**Electron + Flask over pure Electron** — The audio pipeline is Python because of Demucs and PyTorch. Rather than write a native Node.js binding, Electron spawns Flask as a child process and proxies content through a BrowserView. This keeps the Python stack intact while delivering a native desktop experience.

**SSE over WebSocket** — Progress events are one-directional (server to client), so SSE is simpler and doesn't require a persistent bidirectional connection. Each event is a JSON object drained from a per-task `Queue`.

**In-process task queue** — Tasks are stored in module-level dicts keyed by UUID. This is fine for single-user desktop use but would not scale to concurrent users on a server.

**Subprocess for Demucs and FFmpeg** — Both are called via `subprocess` rather than Python APIs. This avoids dependency on internal Demucs Python APIs and makes it easy to check the cancel flag between poll intervals.

**Segment-based classification** — Pitch estimation runs per 0.5s chunk rather than on the full file. This is intentional: speaker pitch can vary and a finer window catches transitions more accurately than a whole-file average.

## Directory structure

```
voice-seperation/
├── electron/               # Electron shell (Node.js)
│   ├── main.js             # Main process
│   ├── preload.js          # IPC context bridge
│   └── shell.html          # Titlebar chrome
├── src/                    # Python backend
│   ├── app.py              # Flask app + pipeline logic
│   ├── voice_isolation.py  # Standalone CLI script
│   ├── templates/
│   │   └── index.html      # Main UI
│   └── static/
│       ├── css/theme.css   # Dark Neo Glass design tokens
│       └── js/main.js      # Frontend JS (SSE, upload, UI)
├── data/                   # Runtime I/O (gitignored)
│   ├── uploads/            # Uploaded files (temp)
│   └── voice_separation_output/  # Pipeline output
├── docs/                   # Extended docs (API, troubleshooting)
├── tests/
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── scripts/                # Build scripts
├── config/                 # Config files
├── requirements.txt        # Python deps
├── package.json            # Node/Electron config
├── run-source-linux.sh     # Linux launcher
├── run-source-mac.sh       # macOS launcher
└── run-source-windows.bat  # Windows launcher
```
