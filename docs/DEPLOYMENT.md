# Deployment Guide

How to release and distribute Voice Separation.

## Release Channels

### GitHub Releases (Primary)

Releases are published to GitHub Releases at:

```
https://github.com/sanchez314c/voice-seperation/releases
```

Each release includes:

- Source code (tagged commit)
- Built binaries (AppImage, DMG, EXE)
- Release notes with changelog

### Cloudflare Tunnel (Development)

For testing the app in a browser without Electron, the Cloudflare tunnel exposes the Flask backend to a public subdomain:

```
https://voice.jasonpaulmichaels.co → localhost:18790
```

This is for development only. The production Electron app does not use the tunnel.

## Release Process

### 1. Prepare the Release

```bash
# Update version in package.json
npm version patch  # or minor, major

# Update CHANGELOG.md
# Add release notes with date and changes

# Commit changes
git add package.json CHANGELOG.md
git commit -m "Release v1.0.1"
```

### 2. Tag the Release

```bash
git tag v1.0.1
git push origin main --tags
```

### 3. Build Binaries

```bash
npm run build:linux
npm run build:mac
npm run build:windows
```

### 4. Create GitHub Release

1. Go to GitHub Releases page
2. Click "Draft a new release"
3. Select the tag you just pushed
4. Copy release notes from CHANGELOG.md
5. Attach the built binaries:
    - `Voice-Separation-1.0.1.AppImage`
    - `Voice Separation-1.0.1.dmg`
    - `Voice Separation Setup 1.0.1.exe`
6. Publish the release

## Versioning

Semantic versioning is used:

- **Major** (1.0.0 → 2.0.0): Breaking changes, major features
- **Minor** (1.0.0 → 1.1.0): New features, backward compatible
- **Patch** (1.0.0 → 1.0.1): Bug fixes, minor improvements

Example:

```bash
npm version patch   # 1.0.0 → 1.0.1
npm version minor   # 1.0.0 → 1.1.0
npm version major   # 1.0.0 → 2.0.0
```

## Code Signing

### macOS

macOS builds require code signing to avoid user warnings:

```bash
# Import your developer certificate
security import certificate.p12 -k ~/Library/Keychains/login.keychain

# Sign the build
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name" \
  "dist/Voice Separation.app"

# Notarize (required for macOS 10.15+)
xcrun notarytool submit "dist/Voice Separation-1.0.0.dmg" \
  --apple-id "your@email.com" \
  --password "app-specific-password" \
  --team-id "TEAM_ID"
```

### Windows

Windows builds can be signed with a code signing certificate:

```bash
signtool sign /f certificate.pfx /p password \
  "dist/Voice Separation Setup 1.0.0.exe"
```

### Linux

Linux builds don't require signing, but the AppImage can be:

```bash
# AppImage signing (optional)
appimagetool --sign "dist/Voice-Separation-1.0.0.AppImage"
```

## Auto-Update

Electron's auto-updater can be configured to check for new releases:

```javascript
// In electron/main.js
const { autoUpdater } = require("electron-updater");

app.whenReady().then(() => {
    autoUpdater.checkForUpdatesAndNotify();
});
```

Add to `package.json`:

```json
{
    "publish": {
        "provider": "github",
        "owner": "sanchez314c",
        "repo": "voice-seperation"
    }
}
```

## Distribution

### Direct Download

Users download binaries from GitHub Releases. Add a download button to the README:

```markdown
[![Download for Linux](https://img.shields.io/badge/Linux-AppImage-brightgreen)](https://github.com/sanchez314c/voice-seperation/releases/latest)
```

### Package Managers

Consider publishing to package managers:

- **Homebrew** (macOS): Create a tap
- **Snap Store** (Linux): Create a snap package
- **Microsoft Store** (Windows): Submit for review

### Website

A simple landing page can be hosted at:

```
https://voice.jasonpaulmichaels.co
```

Redirect to the latest GitHub release.

## Post-Release

After publishing a release:

1. **Announce** — Post on social media, update website
2. **Monitor issues** — Watch GitHub for bug reports
3. **Prepare next version** — Create a new section in CHANGELOG.md

## Rollback

If a critical bug is found:

1. Delete the release from GitHub (or mark as "Pre-release")
2. Yank the version from npm (if published)
3. Release a patch version with the fix
4. Communicate the issue to users

## Environment-Specific Configuration

### Development

- Uses `--dev` flag for DevTools
- Flask runs on a random port (8100-8999)
- No auto-update checks

### Production

- DevTools disabled
- Flask runs on a fixed port (configured via environment)
- Auto-update enabled (if configured)
