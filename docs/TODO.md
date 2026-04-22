# TODO

Known issues, planned features, and technical debt.

## High Priority

### Add Automated Tests
* [ ] Unit tests for `estimate_pitch()` with known-frequency audio
* [ ] Unit tests for `classify_gender_by_pitch()` boundary values
* [ ] Integration test for full pipeline with sample audio
* [ ] E2E test with Playwright for Electron app

### Windows Support
* [ ] Test on Windows 10/11
* [ ] Fix path separators (use `pathlib` everywhere)
* [ ] Verify FFmpeg integration on Windows

## Medium Priority

### Performance
* [ ] GPU acceleration indicator in UI
* [ ] Progress bar during Demucs download (first run)
* [ ] Caching of pitch analysis results
* [ ] Parallel processing of segments (multiprocessing)

### Features
* [ ] Multiple file upload / batch processing
* [ ] Config file support for user preferences
* [ ] Custom gender thresholds in UI (not hardcoded)
* [ ] Audio preview before processing
* [ ] Export individual segments (not just combined output)

### UI/UX
* [ ] Keyboard shortcuts (Ctrl+O to open, Ctrl+C to cancel)
* [ ] Drag window from custom titlebar
* [ ] Minimize to system tray
* [ ] Dark/light theme toggle
* [ ] Accessibility improvements (ARIA labels, keyboard nav)

## Low Priority

### Nice to Have
* [ ] Speaker diarization (separate all speakers, not just gender)
* [ ] Voice activity detection (skip silence automatically)
* [ ] Noise reduction before pitch analysis
* [ ] Support for more audio formats (WMA, AC3, DTS)
* [ ] Metadata preservation in output files

### Documentation
* [ ] Video demo of the app
* [ ] Tutorial on using the CLI version
* [ ] Explanation of pitch detection algorithm with diagrams
* [ ] Comparison of Demucs models (htdemucs vs htdemucs_ft)

## Technical Debt

### Code Quality
* [ ] Remove hardcoded paths (use config file)
* [ ] Consolidate duplicate code between `app.py` and `voice_isolation.py`
* [ ] Add type hints throughout
* [ ] Improve error messages (be more specific)

### Architecture
* [ ] Separate pipeline logic from Flask routes
* [ ] Use a task queue (Celery/RQ) instead of threads
* [ ] Add a database for task history
* [ ] Implement proper logging (not just print statements)

### Security
* [ ] Add input sanitization for file paths
* [ ] Rate limiting on API endpoints (defense in depth)
* [ ] CSP audit (currently allows Google Fonts)
* [ ] Subprocess timeout (prevent hangs)

### Dependencies
* [ ] Pin Demucs version (currently uses latest)
* [ ] Update PyTorch to latest stable
* [ ] Consider replacing scipy with librosa
* [ ] Audit npm dependencies for vulnerabilities

## Known Issues

### Bugs
* [ ] Progress bar sometimes jumps from 30% to 100% (Demucs doesn't report progress)
* [x] Cancel button now terminates Demucs subprocess (per-task cancel_flag polled in run_demucs + segment loop)
* [ ] Audio player doesn't work on Safari (browser compatibility)
* [ ] Window resize causes visual glitch on macOS (BrowserView bounds)

### Limitations
* [ ] Only one processing task at a time (UI limitation)
* [ ] Pitch detection fails on overlapping speech
* [ ] Gender classification is heuristic, not accurate
* [ ] No undo/redo for operations
* [ ] Uploaded files are not auto-deleted (disk space leak)

## Backlog

### Research
* [ ] Evaluate other source separation models (MDX-Net, HTDemucs 6s)
* [ ] Test pitch detection accuracy with labeled datasets
* [ ] Benchmark performance on different hardware (CPU vs GPU)
* [ ] Survey users about gender threshold preferences

### Infrastructure
* [ ] Set up CI/CD pipeline (GitHub Actions)
* [ ] Automated release builds
* [ ] Code signing for macOS and Windows
* [ ] Homebrew tap for macOS
* [ ] Snap package for Linux

### Community
* [ ] Contributing guide (beyond CONTRIBUTING.md)
* [ ] Code of conduct enforcement
* [ ] Issue templates (partially done)
* [ ] PR review checklist
* [ ] Roadmap for next releases

## Completed

* [x] Initial release (v1.0.0) — March 2025
* [x] Dark Neo Glass UI theme
* [x] Real-time progress updates via SSE
* [x] Cross-platform Electron shell
* [x] CLI mode for headless processing
* [x] FFmpeg integration for MP3 export
* [x] Documentation standardization — April 2026

## Future Releases

### v1.1.0 (Planned)
* Automated tests
* Windows support
* Config file support
* Performance improvements

### v1.2.0 (Considered)
* Batch processing
* Custom thresholds in UI
* Speaker diarization option
* Better error handling

### v2.0.0 (Speculative)
* Neural network gender classifier
* Real-time processing
* Plugin system for custom stages
* Web version (no Electron)
