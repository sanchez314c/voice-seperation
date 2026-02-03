# Contributing to Voice Separation

Thank you for your interest in contributing!

## Development Setup

### Prerequisites

- Python 3.8+
- FFmpeg
- ~4GB RAM for Demucs

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/voice-seperation.git
cd voice-seperation/VoiceSeperation_v0.0.1

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where helpful
- Add docstrings to functions
- Maximum line length: 100 characters

### Formatting

```bash
# Format code
black src/

# Check linting
flake8 src/
```

## Testing

```bash
# Run tests
pytest tests/

# Test with a sample audio file
python src/voice_isolation.py
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run formatting and tests
5. Submit a pull request

### Commit Messages

Use descriptive commit messages:

```
feat: Add command-line argument support
fix: Improve pitch detection accuracy
docs: Update installation instructions
```

## Areas for Contribution

- Command-line interface
- Configuration file support
- Additional gender classification methods
- Performance optimizations
- Unit tests
- Documentation improvements

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
