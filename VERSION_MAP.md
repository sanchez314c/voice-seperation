# Version Map

This repository tracks Voice Separation version history.

## Current Version

| Version | Status | Description |
|---------|--------|-------------|
| v1.0.0 | Active | Electron + Flask UI, Demucs + pitch classification pipeline |

## Version History

| Version | Status | Description |
|---------|--------|-------------|
| v1.0.0 | Active | Full Electron UI, Flask backend, neo-glass theme |
| v0.2.0 | Legacy | Electron wrapper introduced |
| v0.0.1 | Legacy | Initial CLI pipeline release |

## Version Details

### v1.0.0 (Current)
- **Status**: Active Development
- **Features**:
  - Electron desktop UI with neo-glass design
  - Flask backend REST API
  - Demucs vocal extraction (htdemucs model)
  - Pitch-based gender classification
  - Segment processing (0.5s windows)
  - WAV and MP3 output
- **Entry Point**: `electron/main.js` (UI), `src/app.py` (backend)

### v0.2.0 (Legacy)
- **Status**: Superseded
- **Features**: Electron wrapper added around Flask backend
- **Entry Point**: `electron/main.js`

### v0.0.1 (Legacy)
- **Status**: Superseded
- **Features**: CLI pipeline only
- **Entry Point**: `src/voice_isolation.py`

## Adding New Versions

When creating a new version:
1. Archive current state: `tar -czf archive/$(date +%Y%m%d_%H%M%S).tar.gz . --exclude=node_modules --exclude=.git`
2. Increment version in `package.json`
3. Update this VERSION_MAP.md
