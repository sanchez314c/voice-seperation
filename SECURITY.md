# Security Policy

## Supported Versions

Currently supported versions of Voice Separation:

| Version | Supported | Notes |
|---------|-----------|-------|
| 1.0.x | Yes | Current stable release |

## Reporting a Vulnerability

If you discover a security vulnerability, please email it to jason@jasonpaulmichaels.co.

**Please include:**
* A description of the vulnerability
* Steps to reproduce the issue
* Potential impact assessment
* Suggested fix (if known)

I will respond within 48 hours and provide regular updates on the remediation progress.

## Security Considerations

### Local Application Scope

Voice Separation is a local desktop application. All processing happens on your machine. No data is sent to external servers (except for Google Fonts, which can be disabled by removing the `<link>` tag from `index.html`).

### File Upload Safety

* Uploaded files are saved to `data/uploads/` with UUID-based filenames
* File extensions are validated against an allowlist (`.mp3`, `.wav`, `.flac`, `.ogg`, `.m4a`, `.aac`)
* Maximum file size is enforced at 500MB
* Path traversal protection is implemented on the download endpoint

### Network Exposure

The Flask server binds to `127.0.0.1` only (localhost). It is not exposed to the network. The Electron app communicates with Flask via a local HTTP connection on a dynamic port (8100-8999).

### Subprocess Execution

The application executes external commands:
* `demucs` — for vocal separation
* `ffmpeg` — for audio encoding

Both are called with user-controlled file paths. Paths are validated, and these commands are only executed on files within the project's data directories.

### Electron Security

* Context isolation is enabled
* Node integration is disabled in the BrowserView
* IPC is handled through a preload script
* The sandbox is disabled on Linux (required for transparent frameless windows — this is acceptable for a local app)

### Content Security Policy

The Flask backend applies strict CSP headers:
* Default source: `'self'` only
* Scripts: `'self'` only
* Styles: `'self'` and Google Fonts
* No `unsafe-eval` or `unsafe-inline`

## Known Limitations

* No authentication mechanism (not needed for a local app)
* Uploaded files are not automatically deleted (manual cleanup required)
* No rate limiting on API endpoints (not needed for a local app)

## Security Updates

Security fixes will be released as patch versions (e.g., 1.0.1). Update by pulling the latest code and reinstalling dependencies.
