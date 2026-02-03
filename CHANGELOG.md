# Changelog

## [1.0.2] — 2026-04-11

### Documentation Standardization — Repo Pipeline

- Created comprehensive PRD.md (450 lines) with full architecture, API spec, feature catalog, data models, reconstruction notes
- Added CODE_OF_CONDUCT.md (Contributor Covenant v2.1)
- Added SECURITY.md (vulnerability reporting, security considerations for local app)
- Added docs/DEVELOPMENT.md (dev environment setup, code conventions, testing)
- Added docs/BUILD_COMPILE.md (Electron Builder configuration, platform-specific builds)
- Added docs/DEPLOYMENT.md (release process, versioning, code signing)
- Added docs/FAQ.md (common questions with real answers from codebase)
- Added docs/WORKFLOW.md (branching strategy, development cycle, CI/CD)
- Added docs/QUICK_START.md (3-minute setup guide)
- Added docs/LEARNINGS.md (development insights, gotchas, things that didn't work)
- Added docs/TODO.md (known issues, planned features, technical debt)
- Updated docs/README.md (merged DOCUMENTATION_INDEX.md, comprehensive documentation index)
- Relocated reports to archive/: AUDIT_REPORT.md, ARCHITECTURE.md (root), SETUP.md, implement.md, dev/tech-stack.md
- All 27 standard documentation files now present

## [1.0.1] — 2026-03-14 20:22

### Neo-Noir Glass Monitor Restyle

- Applied Neo-Noir Glass Monitor design system (complete)
- Frameless floating window: `frame: false`, `transparent: true`, `hasShadow: false`, `backgroundColor: #00000000`
- Linux transparency flags: `enable-transparent-visuals`, `disable-gpu-compositing`
- Canonical title bar: app icon (18px), teal app name, muted tagline, flat About icon, circular min/max/close (28px)
- All three window controls wired via IPC contextBridge (no `window.close()`)
- Drag handle at z-index 50, controls at z-index 200
- About modal: dark overlay, layered shadow card, app icon (64px), version (teal monospace), GitHub badge, email, MIT license
- Status bar footer: status dot + text + pipe separator + item count (left), version-only teal (right)
- Complete design token system in `theme.css` with layered shadow variables
- Glass card system: gradient background, `::before` inner highlight, hover lift + shadow escalation
- Hero card with triple radial ambient gradient mesh + dot grid overlay
- Results card with ambient gradient mesh
- Mini-card list items (process steps, output files, result stats) with glass-border + ::before highlight
- Invisible-at-rest scrollbars, visible on hover (6px thin, dark thumb)
- Teal focus border + glow on all inputs
- BrowserView background set to `#0a0b0e` to prevent white flash on load
- BrowserView bounds corrected: status bar height (28px) excluded to prevent shell overlap
- Icon exported from `resources/icons/icon.webp` to `src/icon-titlebar.png` (tight-cropped 128x128)
- No rainbow gradient strip
- No sidebar logo section
- No `experimentalFeatures` in webPreferences
- `body height: 100vh` (corrected from `min-height`)

## [0.2.1] — 2026-03-14

### Security — Forensic Audit Fixes

- **CRIT: Path traversal fixed** — `/api/download` now uses `Path.resolve()` + `Path.relative_to()` instead of `startswith()` string comparison to enforce output directory containment
- **CRIT: Hardcoded personal path removed** — `voice_isolation.py` CLI now uses `argparse` for input/output paths; no personal directory paths remain in source
- **HIGH: XSS in log console fixed** — `addLog()` in `main.js` rewritten using DOM API (`createElement`, `textContent`) instead of `innerHTML` with unsanitized server data
- **HIGH: XSS in output files list fixed** — File list rendering rewritten using DOM API; download button uses `addEventListener` closure instead of `onclick` string interpolation
- **HIGH: Cancel race condition fixed** — `/api/cancel` now accepts `{"task_id": "..."}` and cancels only the specified task; frontend sends active task_id on cancel
- **HIGH: Hardcoded sudo password removed** — `run-source-linux.sh` no longer pipes `echo "1234"` to sudo; relies on standard sudo authentication

### Fixed

- **Parameter injection prevention** — `segment_duration`, `silence_threshold` are now clamped to valid ranges with `try/except`; `output_format` validated against `ALLOWED_OUTPUT_FORMATS` whitelist
- **File upload sanitization** — Uploaded files now stored as `{uuid}{validated_ext}` only; extension validated against `ALLOWED_EXTENSIONS` set
- **FFmpeg result now checked** — `subprocess.run()` return code is checked; failure logged as warning to SSE stream
- **Unbounded memory growth** — `_cleanup_old_tasks()` added; oldest tasks evicted when more than 20 accumulate
- **Flask bound to localhost** — Changed from `0.0.0.0` to `127.0.0.1` (Electron-only service has no reason to bind all interfaces)
- **Flask process cleanup** — Added `killFlask()` with SIGKILL fallback after 2s if SIGTERM is ignored
- **`nodeIntegration: false` made explicit** — Added to both BrowserWindow and BrowserView webPreferences

### Added

- **Security headers** — `@app.after_request` hook sets `X-Content-Type-Options`, `X-Frame-Options`, and `Content-Security-Policy`
- **`escapeHtml()` utility** — Added to `main.js` for safe DOM construction
- **`AUDIT_REPORT.md`** — Full forensic audit report with all findings, severity ratings, and fix documentation

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-02-08 18:14 UTC

### Added — Electron Desktop Wrapper

- **`electron/main.js`** — Electron main process: spawns Flask backend as child process, auto-detects free port, frameless transparent window with BrowserView
- **`electron/preload.js`** — contextBridge IPC for window controls (minimize/maximize/close)
- **`electron/shell.html`** — Custom titlebar chrome with traffic-light window controls (red/yellow/green dots), drag-to-move, neo-glass floating panel frame
- **`package.json`** — Electron 27.x dependency, npm start/dev scripts

### Changed

- **`src/app.py`** — Flask port now accepts `FLASK_PORT` environment variable from Electron
- **`src/static/css/theme.css`** — Removed body padding and app-container border-radius/shadow/border (Electron shell provides float gap)
- **`run-source-linux.sh`** — Rewritten to launch via Electron (installs node_modules, activates venv, runs `npm start`)

### Architecture

- App now runs as a standalone desktop application (Electron + Flask backend)
- Flask spawned automatically as child process with auto port detection
- Linux transparent window fixes: `--enable-transparent-visuals`, `--disable-gpu-compositing`, 300ms delay

## [0.0.1] - 2025-01-06

### Added

- Initial voice isolation pipeline
- Demucs integration for vocal extraction (htdemucs model)
- Pitch-based gender classification using autocorrelation
- Segment-based processing (0.5-second windows)
- Support for MP3 and WAV output formats
- Silence detection and filtering
- Crossfade processing to reduce artifacts
- Peak normalization

### Technical

- Male threshold: F0 < 165 Hz
- Female threshold: F0 > 180 Hz
- Ambiguous range: 165-180 Hz (50% volume)
- F0 detection range: 80-400 Hz

## [0.2.0] - 2026-02-08 15:01 EST

### Added — Dark Neo Glass Web UI

- Flask-based web application with Dark Neo Glass theme
- Complete design token system (:root CSS custom properties)
- File upload with drag-and-drop support (MP3, WAV, FLAC, OGG)
- Real-time processing progress via Server-Sent Events (SSE)
- 3-step pipeline visualization (Demucs > Pitch Analysis > Post-Processing)
- Live console log output with color-coded message types
- Processing result statistics display (segment counts, duration, timing)
- Audio preview player for isolated output
- File download capability for all output formats
- Configurable pipeline settings (segment duration, silence threshold, output format)
- Notification toast system (success, error, info, warning)
- Glass card system with ::before inner highlights and layered shadows
- Ambient gradient mesh on hero and result cards
- Themed scrollbars, inputs, buttons, and select elements
- Responsive grid layout adapting to screen width
- Random port assignment to avoid conflicts

### Changed

- Converted from CLI-only to web application architecture
- Updated run-source-linux.sh to launch Flask web server
- Added flask>=3.0.0 to requirements.txt
- Background thread processing with cancellation support

### Theme Compliance (Dark Neo Glass)

- body padding: 16px (floating panel effect)
- All cards use layered shadows (var(--shadow-card), 3+ layers)
- All cards have ::before inner highlight (1px gradient)
- All hover states include translateY(-2px) + shadow escalation
- No hardcoded hex/rgb colors — all via CSS custom properties
- Scrollbars themed (6px, dark thumb, transparent track)
- Input focus states: teal border + glow shadow
- Font: Inter + system stack with -webkit-font-smoothing
- Glass effects via rgba() backgrounds, NOT backdrop-filter

## [Unreleased]

### Planned

- Command-line argument support (CLI mode preserved)
- Multi-speaker separation
- Real-time processing mode
- Waveform visualization
- Batch processing

---

## [REPO-PREP] - 2026-02-13 00:00 UTC

### Fixed — Structural Compliance

- **LICENSE**: Added copyright holder name "Jason" (was missing)
- **.gitignore**: Added Node.js patterns (node_modules, npm logs, package-lock.json)
- **.gitignore**: Added environment variable patterns (.env, .env.local, .env.\*.local)
- **README.md**: Added tech stack badges (Python, PyTorch, Electron, Flask, License)
- **README.md**: Added Tech Stack section with detailed framework versions
- **README.md**: Added Project Structure section with directory tree
- **README.md**: Updated License section to include copyright holder

### Verified — Repo Health

- All entry points exist and are correctly referenced in package.json
- Python dependencies declared with minimum versions
- Electron dependency locked to v27.x
- Lock files present (package-lock.json)
- Changelog follows Keep a Changelog format
- Git workflows present (.github/workflows/ci.yml)
