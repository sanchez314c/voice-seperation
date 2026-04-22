# Wire Audit — Voice Separation

**Date:** 2026-04-17
**Auditor:** Master Control (GLM-5.1)
**Scope:** Full-stack data flow: UI → Flask API → subprocess/storage, Electron IPC

## Result: ALL WIRES INTACT — Zero defects found

---

## 1. Flask Route Inventory

| Route | Method | Handler | Status |
|-------|--------|---------|--------|
| `/` | GET | `index()` :473 | Wired — `render_template("index.html")` |
| `/api/process` | POST | `process_audio()` :479 | Wired — called by main.js:262 |
| `/api/progress/<task_id>` | GET | `progress()` :567 | Wired — called by main.js:290 (EventSource/SSE) |
| `/api/cancel` | POST | `cancel()` :601 | Wired — called by main.js:465 |
| `/api/download/<path:file_path>` | GET | `download()` :617 | Wired — called by main.js:439, :506 |

**Dead routes:** None
**Missing routes:** None

---

## 2. SSE Field Inventory

Server (`queue.put()` in app.py) → Client (`eventSource.onmessage` in main.js:292-319):

| Field | Server Sends | Client Reads | Match |
|-------|-------------|-------------|-------|
| `log` | Yes (multiple locations) | main.js:295 `data.log` | OK |
| `log_type` | Yes | main.js:296 `data.log_type` | OK |
| `progress` | Yes | main.js:299-302 | OK |
| `stage` | Yes | main.js:303 `data.stage` | OK |
| `step` | Yes | main.js:306 `data.step` | OK |
| `step_status` | Yes | main.js:307 `data.step_status` | OK |
| `status` | Yes (`"complete"`, `"error"`) | main.js:310, :315 | OK |
| `error` | Yes (on error) | main.js:455 `data.error` | OK |
| `results` | Yes (on complete) | main.js:375 `data.results` | OK |
| `files` | Yes (on complete) | main.js:397 `data.files` | OK |

**Field mismatches:** None

---

## 3. Form Data Fields

Client (main.js:255-259) → Server (app.py:482-519):

| FormData Key | Client Sends | Server Reads | Match |
|-------------|-------------|-------------|-------|
| `audio` | `selectedFile` | `request.files["audio"]` :482 | OK |
| `segment_duration` | `segmentDuration.value` | `request.form.get("segment_duration")` :508 | OK |
| `silence_threshold` | `silenceThreshold.value` | `request.form.get("silence_threshold")` :514 | OK |
| `output_format` | `outputFormat.value` | `request.form.get("output_format")` :519 | OK |

**Mismatched form fields:** None

---

## 4. Results Payload

Server (app.py:396-403, :431) → Client (main.js:377-393):

| Field | Server Sets | Client Reads | Target Element | Match |
|-------|------------|-------------|----------------|-------|
| `female_segments` | :397 | :378 | `#female-segments` | OK |
| `male_segments` | :398 | :379 | `#male-segments` | OK |
| `ambiguous_segments` | :399 | :380 | `#ambiguous-segments` | OK |
| `silence_segments` | :400 | :381 | `#silence-segments` | OK |
| `duration` | :401 | :382 | `#total-duration` | OK |
| `processing_time` | :431 | :385 | `#processing-time` | OK |
| `files` | :402 (array) | :397 (iterates) | `#output-files` | OK |

File objects: `{name, path, format, size}` — client reads all four fields correctly.

---

## 5. Electron IPC Wires

| Channel | main.js `ipcMain.handle` | preload.js `exposeInMainWorld` | shell.html Caller | Match |
|---------|------------------------|-------------------------------|-------------------|-------|
| `window-minimize` | :191 | :8 `windowMinimize` | :420 | OK |
| `window-maximize` | :194 | :9 `windowMaximize` | :422 | OK |
| `window-close` | :198 | :10 `windowClose` | :425 | OK |
| `open-external` | :203 | :11 `openExternal` | :454 | OK |

**Orphaned IPC handlers:** None
**Mismatched channel names:** None

---

## 6. UI Element Wiring (index.html → main.js)

All 32 `getElementById` calls in main.js resolve to elements in index.html. No undefined references. No orphaned event listeners.

Full ID map verified:

```
upload-zone, file-input, file-info, file-name, file-size, file-remove,
upload-content, process-btn, cancel-btn, reset-btn, segment-duration,
segment-value, silence-threshold, silence-value, output-format,
progress-section, progress-fill, progress-label, progress-percent,
step-1, step-2, step-3, results-section, log-console, status-dot,
status-text, notification, notification-icon, notification-text,
audio-player, audio-player-wrapper, output-files
```

---

## 7. Security Wire Check

| Check | Status |
|-------|--------|
| Path traversal on `/api/download/` | Protected — `resolve()` + `relative_to()` check (:622-625) |
| File extension whitelist on download | Enforced — `.mp3/.wav/.flac/.ogg` only (:627) |
| Upload extension validation | Enforced — `ALLOWED_EXTENSIONS` (:491) |
| UUID filename (no user-controlled names) | Yes — `uuid.uuid4().hex + ext` (:502) |
| `MAX_CONTENT_LENGTH` (500MB) | Set (:48) |
| Security headers | CSP, X-Frame-Options, X-Content-Type-Options (:56-69) |
| IPC `open-external` protocol whitelist | `http/https/mailto` only (:206) |

---

## Applied Fixes

None required. All wires intact, zero defects detected.

---

STATUS: DONE
END OF LINE.
