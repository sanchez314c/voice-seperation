# Testing

Status: TDD scaffolding in place, test suite pending.

## Layout

```
tests/
  unit/           # pytest unit tests for pure functions
  integration/    # end-to-end pipeline runs against sample audio
```

## Planned Coverage

### `src/voice_isolation.py` (CLI pipeline)

| Target | Type | What to assert |
|--------|------|----------------|
| `estimate_pitch(segment, sr)` | unit | Synth 200 Hz sine -> ~200 Hz; synth 120 Hz sine -> ~120 Hz; silence/zero segment -> 0 |
| `classify_gender_by_pitch(f0)` | unit | 0 -> "unknown"; 100 -> "male"; 200 -> "female"; 170 -> "ambiguous"; boundary 165 -> "male"; 180 -> "ambiguous" |
| `run_demucs()` | integration | Mock subprocess.run, assert cmd args, verify path resolution |
| `analyze_and_isolate_female()` | integration | Short sample audio, assert female_audio array is non-zero only in expected ranges |
| `main()` | integration | Invoke with synthetic file, assert output MP3 created |

### `src/app.py` (Flask server)

| Target | Type | What to assert |
|--------|------|----------------|
| `add_security_headers` | unit | GET `/` response includes CSP, nosniff, DENY headers |
| `/api/process` | integration | Upload valid MP3 -> 200 + task_id; invalid extension -> 400; missing file -> 400 |
| `/api/process` param clamping | unit | segment_duration=5.0 clamped to 2.0; silence_threshold=-1 clamped to 0.001 |
| `/api/download/<path>` | integration | Valid path inside OUTPUT_DIR -> file returned; path traversal `../etc/passwd` -> 404 |
| `/api/cancel` | integration | POST with task_id sets cancel flag; fallback cancels all active |
| `_cleanup_old_tasks` | unit | Add 25 fake tasks, verify only 20 remain |

### `electron/` (Electron shell)

| Target | Type | What to assert |
|--------|------|----------------|
| Window creation | playwright | App launches, window is visible, frameless, transparent |
| Titlebar controls | playwright | Min / max / close buttons send correct IPC |
| BrowserView bounds | playwright | View positioned below titlebar, above status bar; resizes with window |
| External link opener | unit | `open-external` rejects non-http(s)/mailto protocols |

## Running Tests

```bash
# Python (once tests are written)
source venv/bin/activate
pytest tests/ -v --cov=src --cov-report=term-missing

# Electron (playwright - once configured)
npm run test:e2e
```

## Coverage Goal

80% minimum on `src/` modules. Higher on security-sensitive paths (`/api/download`, upload validation, IPC handlers).

## Fixtures Needed

- `tests/fixtures/sample_male.wav` - 5s clip, F0 ~120 Hz
- `tests/fixtures/sample_female.wav` - 5s clip, F0 ~220 Hz
- `tests/fixtures/sample_mixed.wav` - alternating male/female segments
- `tests/fixtures/sample_silence.wav` - 1s silence

## CI

GitHub Actions workflow at `.github/workflows/ci.yml`. Runs pytest on push to main and PRs. Does not currently gate on coverage threshold (coverage report is informational until test suite builds out).
