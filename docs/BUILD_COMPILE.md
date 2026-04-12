# Build & Compilation Guide

How to build and package Voice Separation for distribution.

## Overview

Voice Separation is an Electron app that wraps a Flask backend. No compilation step is required for the Python or JavaScript code — the app runs from source.

## Development Build

Run from source without packaging:

```bash
npm start
```

This launches Electron with the Flask backend spawned as a subprocess.

## Production Builds

### Electron Builder

The project uses Electron Builder for packaging. Configuration is in `package.json`.

```bash
# Build for current platform
npm run build

# Build for specific platforms
npm run build:linux
npm run build:mac
npm run build:windows
```

**Build outputs:**

- Linux: `dist/Voice-Separation-1.0.0.AppImage`, `dist/voice-separation_1.0.0_amd64.deb`
- macOS: `dist/Voice Separation-1.0.0.dmg`, `dist/Voice Separation-1.0.0.pkg`
- Windows: `dist/Voice Separation Setup 1.0.0.exe`

### Packaging Requirements

The Python environment and dependencies must be included with the distributed app. Electron Builder handles this through the `extraResources` configuration.

## Platform-Specific Builds

### Linux

**AppImage (universal):**

```bash
npx electron-builder --linux appimage
```

**Debian package:**

```bash
npx electron-builder --linux deb
```

**RPM package:**

```bash
npx electron-builder --linux rpm
```

### macOS

**DMG (drag-and-install):**

```bash
npx electron-builder --mac dmg
```

**PKG (installer):**

```bash
npx electron-builder --mac pkg
```

**Note:** macOS builds require code signing. See [DEPLOYMENT.md](DEPLOYMENT.md) for details.

### Windows

**NSIS installer:**

```bash
npx electron-builder --win nsis
```

**Portable executable:**

```bash
npx electron-builder --win portable
```

## Build Configuration

Edit `package.json` to customize builds:

```json
{
    "build": {
        "appId": "co.jasonpaulmichaels.voice-separation",
        "productName": "Voice Separation",
        "directories": {
            "output": "dist",
            "buildResources": "build"
        },
        "files": ["electron/**/*", "src/**/*", "package.json"],
        "extraResources": [
            {
                "from": "venv/",
                "to": "venv/",
                "filter": ["**/*"]
            }
        ]
    }
}
```

## Optimization

### Reduce Bundle Size

- Exclude test files from production builds
- Use `--asar` to package JavaScript into an archive
- Minify CSS/JS (not currently implemented)

### Speed Up Builds

- Use `--emulate=true` for faster testing (no actual packaging)
- Cache node_modules between builds

## Continuous Integration

GitHub Actions workflow (`.github/workflows/build.yml`) can automate builds on releases. Example:

```yaml
name: Build
on:
    release:
        types: [created]
jobs:
    build:
        runs-on: ${{ matrix.os }}
        strategy:
            matrix:
                os: [ubuntu-latest, macos-latest, windows-latest]
        steps:
            - uses: actions/checkout@v3
            - uses: actions/setup-node@v3
            - run: npm install
            - run: npm run build
            - uses: actions/upload-artifact@v3
              with:
                  name: build-${{ matrix.os }}
                  path: dist/*
```

## Troubleshooting

### Build Fails on Linux

Install missing dependencies:

```bash
sudo apt install libnotify4 libappindicator3-1
```

### Python Not Found in Build

Ensure `extraResources` includes the venv directory and that paths are relative.

### FFmpeg Missing

FFmpeg must be installed on the user's system. Consider bundling it with the app:

```json
"extraResources": [
  {
    "from": "/usr/bin/ffmpeg",
    "to": "ffmpeg"
  }
]
```

## Release Checklist

Before publishing a build:

- [ ] Update version in `package.json`
- [ ] Update `CHANGELOG.md`
- [ ] Test the build on a clean machine
- [ ] Verify Demucs model downloads on first run
- [ ] Check FFmpeg integration
- [ ] Test on all target platforms
