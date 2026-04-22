# Lint Report

**Date**: 2026-04-17
**Repo**: voice-seperation
**Scope**: src/*.py, electron/*.js, src/templates/*.html, src/static/**/*

## Tools Run

| Tool | Version | Result |
|------|---------|--------|
| ruff check --fix | 0.15.10 | 7 errors (all E402, not auto-fixable) |
| ruff format | 0.15.10 | 1 file reformatted |
| black --check | 26.3.1 | 2 files clean (no-op after ruff format) |
| pyflakes | system | 0 issues |
| prettier --write | 3.7.4 | 5 files reformatted |
| node --check | v24.14.1 | 3 JS files pass syntax check |
| json.tool (package.json) | — | Valid |
| shellcheck | 0.9.0 | 6 findings (1 warning, 2 unused-var warnings, 3 info) |

## Files Touched (6)

| File | Tool | Change |
|------|------|--------|
| `src/app.py` | ruff format | Import grouping reformatted |
| `electron/main.js` | prettier | Formatted |
| `electron/preload.js` | prettier | Formatted |
| `src/static/js/main.js` | prettier | Formatted |
| `src/static/css/theme.css` | prettier | Formatted |
| `src/templates/index.html` | prettier | Formatted |

## Issues Auto-Fixed

- **ruff format**: 1 file (import grouping in `src/app.py`)
- **prettier**: 5 files (JS/HTML/CSS formatting)
- **Total**: 6 files reformatted, 0 semantic changes

## Issues Requiring Manual Review

### Python (ruff E402 — module imports not at top of file)

Both files intentionally place `warnings.filterwarnings("ignore")` before heavy imports (torch, torchaudio). This suppresses noisy warnings from those libraries during import. Options:
1. Add `# noqa: E402` on each flagged import line
2. Add `per-file-ignores` in a `ruff.toml` or `pyproject.toml`

| File | Lines | Detail |
|------|-------|--------|
| `src/app.py` | 24-27 | torch, torchaudio, flask, scipy imports after warnings filter |
| `src/voice_isolation.py` | 24-26 | torch, torchaudio, scipy imports after warnings filter |

### Shell (shellcheck — report only)

| File | Line | Code | Issue |
|------|------|------|-------|
| `run-source-linux.sh` | 7 | SC2034 | `BLUE` variable unused |
| `run-source-linux.sh` | 40 | SC1091 | `source venv/bin/activate` not followed (expected — venv not present during lint) |
| `run-source-mac.sh` | 15 | SC1091 | Same as above |
| `scripts/run-source-linux.sh` | 37 | SC1091 | Same as above |
| `scripts/run-source-macos.sh` | 37 | SC1091 | Same as above |
| `scripts/run-source.sh` | 8 | SC2034 | `PROJECT_DIR` variable unused |
| `scripts/build-linux.sh` | 16 | SC2035 | `rm -rf *.spec` should be `rm -rf ./*.spec` or `-- *.spec` |

**SC1091** is ignorable (venv activate not present at lint time).
**SC2034/SC2035** are low-priority cosmetic fixes.

## Files in Scope (untouched, clean)

- `src/voice_isolation.py` — pyflakes clean, ruff format clean, E402 only

## Tools Not Available

None. All requested tools were present on the system.
