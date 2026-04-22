# Voice Separation Documentation

Complete documentation for Voice Separation v1.0.0.

## Quick Start

New here? Start with [QUICK_START.md](QUICK_START.md) to get the app running in 3 minutes.

## Core Documentation

| Document | Description |
|----------|-------------|
| [README](../README.md) | Project overview, features, installation summary |
| [CHANGELOG](../CHANGELOG.md) | Version history and release notes |
| [CONTRIBUTING](../CONTRIBUTING.md) | How to contribute, code standards, PR process |
| [LICENSE](../LICENSE) | MIT license |
| [CODE_OF_CONDUCT](../CODE_OF_CONDUCT.md) | Contributor Covenant v2.1 |
| [SECURITY](../SECURITY.md) | Security policy and vulnerability reporting |
| [CLAUDE.md](../CLAUDE.md) | AI assistant context for working on this project |
| [AGENTS.md](../AGENTS.md) | How AI agents interact with this codebase |
| [VERSION_MAP](../VERSION_MAP.md) | Version tracking and archive locations |

## Technical Documentation

| Document | Description |
|----------|-------------|
| [Architecture](ARCHITECTURE.md) | System design, pipeline flow, component relationships |
| [Installation](INSTALLATION.md) | Prerequisites, setup steps, configuration, verification |
| [Development](DEVELOPMENT.md) | Dev environment, build commands, testing, code conventions |
| [API Reference](API.md) | Flask endpoints, request/response formats, error codes |
| [Build & Compile](BUILD_COMPILE.md) | Build system, platform-specific builds, packaging |
| [Deployment](DEPLOYMENT.md) | Release process, versioning, distribution |
| [FAQ](FAQ.md) | Frequently asked questions with real answers |
| [Troubleshooting](TROUBLESHOOTING.md) | Common issues, error messages, debugging tips |
| [Tech Stack](TECHSTACK.md) | Full technology breakdown, versions, rationale |
| [Workflow](WORKFLOW.md) | Development workflow, branching strategy, CI/CD |
| [Quick Start](QUICK_START.md) | Fastest path from clone to running (minimal steps) |
| [Learnings](LEARNINGS.md) | Development insights, gotchas, things that didn't work |
| [Testing](TESTING.md) | Test plan, layout, coverage goals, fixture inventory |
| [PRD](../PRD.md) | Product requirements document (what this project is, goals, scope) |
| [TODO](TODO.md) | Known issues, planned features, technical debt |

## Entry Points

| Script | Platform | Purpose |
|--------|----------|---------|
| `run-source-linux.sh` | Linux | Start from source (Electron + Flask) |
| `npm start` | macOS/Windows | Start from source |
| `python src/voice_isolation.py` | Any | CLI mode (headless processing) |

## Project Structure

```
voice-seperation/
├── electron/              # Electron main process
│   ├── main.js           # Window management, Flask spawn
│   ├── preload.js        # IPC context bridge
│   └── shell.html        # Custom titlebar
├── src/
│   ├── app.py            # Flask backend + pipeline
│   ├── voice_isolation.py # CLI pipeline (standalone)
│   ├── templates/
│   │   └── index.html    # Main UI
│   └── static/
│       ├── css/theme.css # Dark Neo Glass theme
│       └── js/main.js    # Frontend logic
├── data/
│   ├── uploads/          # Temporary uploaded files
│   └── voice_separation_output/  # Pipeline output
├── docs/                 # This directory
├── tests/                # Unit and integration tests
├── scripts/              # Build and utility scripts
├── requirements.txt      # Python dependencies
├── package.json          # Electron config
└── run-source-linux.sh   # Linux launcher
```

## Key Concepts

### Pipeline Stages

1. **Vocal Extraction** — Demucs separates vocals from music/noise
2. **Pitch Analysis** — Autocorrelation estimates fundamental frequency (F0)
3. **Gender Classification** — Segments classified by F0 thresholds
4. **Post-Processing** — Crossfade and normalization
5. **Export** — WAV and/or MP3 output

### Gender Thresholds

| Classification | F0 Range | Behavior |
|----------------|----------|----------|
| Male | < 165 Hz | Excluded |
| Ambiguous | 165-180 Hz | Included at 50% volume |
| Female | > 180 Hz | Included at full volume |
| Silence | RMS < threshold | Skipped |

## Support

* Check [FAQ](FAQ.md) for common questions
* Check [Troubleshooting](TROUBLESHOOTING.md) for issues
* Search [GitHub Issues](https://github.com/sanchez314c/voice-seperation/issues)
* Open a new issue for bugs or feature requests

## Contributing

We welcome contributions! See [CONTRIBUTING.md](../CONTRIBUTING.md) for:
* Development setup
* Code conventions
* Pull request process
* Code of conduct

## License

MIT License — see [LICENSE](../LICENSE) for details.
