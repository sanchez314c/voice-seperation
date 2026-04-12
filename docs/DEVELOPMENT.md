# Development Guide

Development setup and workflow for Voice Separation.

## Prerequisites

- Python 3.8+
- Node.js 18+
- FFmpeg (system package)
- Git

## Dev Environment Setup

### 1. Clone and Install

```bash
git clone https://github.com/sanchez314c/voice-seperation.git
cd voice-seperation

# Python environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Node dependencies
npm install
```

### 2. Launch Development Mode

**Linux:**

```bash
./run-source-linux.sh
```

**macOS/Windows:**

```bash
npm start
```

The `--dev` flag opens DevTools automatically:

```bash
npm run dev
```

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
├── tests/                # Unit and integration tests
├── scripts/              # Build and utility scripts
├── requirements.txt      # Python dependencies
├── package.json          # Electron config
└── run-source-linux.sh   # Linux launcher
```

## Code Conventions

### Python

- PEP 8 style (4-space indentation)
- Type hints for function signatures
- Docstrings for all public functions
- Maximum line length: 100 characters

### JavaScript

- ES6+ syntax
- Strict mode (`'use strict'`)
- No framework (vanilla JS)
- Event delegation for dynamic elements

### CSS

- BEM-ish naming for components
- CSS custom properties for theming
- Mobile-first responsive design

## Testing

```bash
# Run Python tests (when implemented)
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

## Build Commands

```bash
# Start the app
npm start

# Start with DevTools
npm run dev

# Lint Python code (when configured)
flake8 src/
black src/

# Type check (when configured)
mypy src/
```

## Debugging

### Backend (Flask)

Logs appear in the terminal where you ran `npm start`. For detailed logging:

```python
# In app.py, set:
app.run(debug=True, port=port)
```

### Frontend (Electron)

Open DevTools with `--dev` flag or use the keyboard shortcut:

- Linux/Windows: `Ctrl+Shift+I`
- macOS: `Cmd+Option+I`

### Pipeline Issues

To debug the voice isolation pipeline without the UI:

```bash
source venv/bin/activate
python src/voice_isolation.py path/to/audio.mp3
```

## Common Tasks

### Add a New Pipeline Stage

1. Implement the function in `src/app.py`
2. Add progress updates to the Queue
3. Update the step counter in `src/templates/index.html`
4. Handle the new step in `src/static/js/main.js`

### Change Gender Thresholds

Edit the constants in `src/app.py` and `src/voice_isolation.py`:

```python
# Current values:
MALE_THRESHOLD = 165    # Hz
FEMALE_THRESHOLD = 180  # Hz
```

### Add a New Output Format

1. Implement the export logic in `analyze_and_isolate_female()`
2. Add the format to `ALLOWED_OUTPUT_FORMATS`
3. Update the UI dropdown in `index.html`

## Workflow

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make changes and test locally
3. Run tests: `pytest tests/`
4. Commit with descriptive message
5. Push and create a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full contribution process.
