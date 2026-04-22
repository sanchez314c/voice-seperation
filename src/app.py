#!/usr/bin/env python3
"""
Voice Separation Web Application
=================================
Flask-based web UI for the voice isolation pipeline.
Dark Neo Glass theme frontend with real-time processing progress.
"""

import json
import os
import subprocess
import threading
import time
import uuid
import warnings
from pathlib import Path
from queue import Queue

import numpy as np

warnings.filterwarnings("ignore")

# Audio processing
import torch
import torchaudio
from flask import (
    Flask,
    Response,
    jsonify,
    render_template,
    request,
    send_file,
    stream_with_context,
)
from scipy.io import wavfile

# ── App Configuration ──

app = Flask(__name__, template_folder="templates", static_folder="static")

BASE_DIR = Path(__file__).parent.parent
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
OUTPUT_DIR = BASE_DIR / "data" / "voice_separation_output"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500MB

# ── Allowed file extensions ──
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac"}
ALLOWED_OUTPUT_FORMATS = {"wav", "mp3", "both"}


# ── Security headers ──
@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "media-src 'self' blob:; "
        "connect-src 'self'"
    )
    return response


# ── Task Management ──

tasks = {}
task_queues = {}
cancel_flags = {}
_tasks_lock = threading.Lock()  # protects concurrent mutation of tasks/task_queues/cancel_flags


# ── Voice Isolation Core Functions ──


def estimate_pitch(audio_segment: np.ndarray, sr: int) -> float:
    """
    Estimate fundamental frequency (pitch) using autocorrelation.
    Returns estimated F0 in Hz, or 0 if unvoiced.
    """
    audio_segment = audio_segment.astype(float)
    if audio_segment.max() > 0:
        audio_segment = audio_segment / np.max(np.abs(audio_segment))

    min_period = int(sr / 400)
    max_period = int(sr / 80)

    if len(audio_segment) < max_period * 2:
        return 0

    corr = np.correlate(audio_segment, audio_segment, mode="full")
    corr = corr[len(corr) // 2 :]

    if max_period >= len(corr):
        max_period = len(corr) - 1

    search_region = corr[min_period:max_period]
    if len(search_region) == 0:
        return 0

    peak_idx = np.argmax(search_region) + min_period

    if corr[peak_idx] > 0.3 * corr[0]:
        f0 = sr / peak_idx
        return f0
    return 0


def classify_gender_by_pitch(f0: float) -> str:
    """Classify gender based on fundamental frequency."""
    if f0 == 0:
        return "unknown"
    elif f0 < 165:
        return "male"
    elif f0 > 180:
        return "female"
    else:
        return "ambiguous"


def run_demucs(input_file: str, output_dir: str, queue: Queue, cancel_flag: dict) -> str:
    """Run Demucs to separate vocals from the audio."""
    queue.put(
        {
            "log": "Starting Demucs vocal extraction (htdemucs model)...",
            "log_type": "accent",
            "step": 1,
            "step_status": "active",
            "progress": 5,
            "stage": "Extracting vocals with Demucs...",
        }
    )

    cmd = [
        "demucs",
        "--two-stems",
        "vocals",
        "-o",
        output_dir,
        "--mp3",
        input_file,
    ]

    queue.put({"log": f"Command: {' '.join(cmd)}", "log_type": "info"})

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Poll for output while checking cancel flag
    while process.poll() is None:
        if cancel_flag.get("cancelled"):
            process.terminate()
            raise RuntimeError("Processing cancelled by user")
        time.sleep(1)
        queue.put({"progress": 20, "stage": "Demucs processing audio..."})

    stdout, stderr = process.communicate()

    if process.returncode != 0:
        queue.put({"log": f"Demucs error: {stderr}", "log_type": "error"})
        raise RuntimeError(f"Demucs failed: {stderr}")

    input_name = Path(input_file).stem
    vocals_path = Path(output_dir) / "htdemucs" / input_name / "vocals.mp3"

    if not vocals_path.exists():
        vocals_path = Path(output_dir) / "htdemucs" / input_name / "vocals.wav"

    if not vocals_path.exists():
        raise RuntimeError("Demucs output not found at expected path")

    queue.put(
        {
            "log": f"Vocals extracted: {vocals_path.name}",
            "log_type": "success",
            "step": 1,
            "step_status": "complete",
            "progress": 30,
            "stage": "Vocal extraction complete",
        }
    )

    return str(vocals_path)


def analyze_and_isolate_female(
    vocals_path: str,
    output_path: str,
    queue: Queue,
    cancel_flag: dict,
    segment_duration: float = 0.5,
    silence_threshold: float = 0.01,
    output_format: str = "both",
):
    """Analyze vocals file and isolate female voice segments."""
    queue.put(
        {
            "log": "Loading vocals for pitch analysis...",
            "log_type": "info",
            "step": 2,
            "step_status": "active",
            "progress": 35,
            "stage": "Analyzing voice segments...",
        }
    )

    waveform, sr = torchaudio.load(vocals_path)
    if waveform.shape[0] > 1:
        waveform = torch.mean(waveform, dim=0, keepdim=True)

    audio = waveform.numpy().squeeze()
    duration = len(audio) / sr

    queue.put(
        {
            "log": f"Audio: {duration:.1f}s at {sr} Hz sample rate",
            "log_type": "info",
        }
    )

    segment_samples = int(segment_duration * sr)
    num_segments = len(audio) // segment_samples

    queue.put(
        {
            "log": f"Analyzing {num_segments} segments ({segment_duration}s each)...",
            "log_type": "info",
        }
    )

    male_segments = 0
    female_segments = 0
    silence_segments = 0
    ambiguous_segments = 0

    female_audio = np.zeros_like(audio)

    for i in range(num_segments):
        if cancel_flag.get("cancelled"):
            raise RuntimeError("Processing cancelled by user")

        start = i * segment_samples
        end = start + segment_samples
        segment = audio[start:end]

        rms = np.sqrt(np.mean(segment**2))
        if rms < silence_threshold:
            silence_segments += 1
            continue

        f0 = estimate_pitch(segment, sr)
        gender = classify_gender_by_pitch(f0)

        if gender == "female":
            female_segments += 1
            female_audio[start:end] = segment
        elif gender == "male":
            male_segments += 1
        elif gender == "ambiguous":
            ambiguous_segments += 1
            female_audio[start:end] = segment * 0.5
        else:
            silence_segments += 1

        # Progress updates every 100 segments
        if (i + 1) % 100 == 0 or i == num_segments - 1:
            pct = 35 + int((i / num_segments) * 45)
            queue.put(
                {
                    "progress": pct,
                    "stage": f"Analyzing segment {i + 1}/{num_segments}...",
                }
            )

        if (i + 1) % 500 == 0:
            queue.put(
                {
                    "log": f"Processed {i + 1}/{num_segments} segments",
                    "log_type": "info",
                }
            )

    queue.put(
        {
            "log": f"Analysis: {female_segments} female, {male_segments} male, {ambiguous_segments} ambiguous, {silence_segments} silence",
            "log_type": "success",
            "step": 2,
            "step_status": "complete",
            "progress": 80,
            "stage": "Analysis complete",
        }
    )

    # Step 3: Post-processing
    queue.put(
        {
            "log": "Post-processing: crossfade and normalization...",
            "log_type": "info",
            "step": 3,
            "step_status": "active",
            "progress": 82,
            "stage": "Post-processing...",
        }
    )

    fade_samples = int(0.01 * sr)
    for i in range(1, num_segments):
        pos = i * segment_samples
        if pos + fade_samples <= len(female_audio):
            fade_in = np.linspace(0, 1, fade_samples)
            fade_out = np.linspace(1, 0, fade_samples)
            if np.any(female_audio[pos - fade_samples : pos] != 0) and np.any(
                female_audio[pos : pos + fade_samples] != 0
            ):
                female_audio[pos - fade_samples : pos] *= fade_out
                female_audio[pos : pos + fade_samples] *= fade_in

    max_val = np.max(np.abs(female_audio))
    if max_val > 0:
        female_audio = female_audio / max_val * 0.9

    queue.put({"progress": 90, "stage": "Saving output files..."})

    output_files = []

    # Save WAV (use Path.with_suffix for robust extension swap)
    output_path_obj = Path(output_path)
    wav_path_obj = output_path_obj.with_suffix(".wav")

    if output_format in ("wav", "both"):
        wav_path = str(wav_path_obj)
        wavfile.write(wav_path, sr, (female_audio * 32767).astype(np.int16))
        wav_size = os.path.getsize(wav_path)
        output_files.append(
            {
                "name": wav_path_obj.name,
                "path": wav_path,
                "format": "wav",
                "size": wav_size,
            }
        )
        queue.put({"log": f"Saved: {wav_path_obj.name}", "log_type": "success"})

    # Save MP3
    if output_format in ("mp3", "both"):
        wav_temp_obj = output_path_obj.with_name(output_path_obj.stem + "_temp.wav")
        wav_temp = str(wav_temp_obj)
        if output_format == "mp3":
            wavfile.write(wav_temp, sr, (female_audio * 32767).astype(np.int16))

        source_wav = wav_temp if output_format == "mp3" else str(wav_path_obj)
        mp3_path = output_path
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            source_wav,
            "-codec:a",
            "libmp3lame",
            "-qscale:a",
            "2",
            mp3_path,
        ]
        ffmpeg_result = subprocess.run(cmd, capture_output=True, text=True)
        if ffmpeg_result.returncode != 0:
            queue.put(
                {
                    "log": f"FFmpeg warning: {ffmpeg_result.stderr[:200]}",
                    "log_type": "warning",
                }
            )

        if output_format == "mp3" and os.path.exists(wav_temp):
            os.remove(wav_temp)

        if os.path.exists(mp3_path):
            mp3_size = os.path.getsize(mp3_path)
            output_files.append(
                {
                    "name": Path(mp3_path).name,
                    "path": mp3_path,
                    "format": "mp3",
                    "size": mp3_size,
                }
            )
            queue.put({"log": f"Saved: {Path(mp3_path).name}", "log_type": "success"})

    queue.put({"progress": 95, "stage": "Finalizing..."})

    return {
        "female_segments": female_segments,
        "male_segments": male_segments,
        "ambiguous_segments": ambiguous_segments,
        "silence_segments": silence_segments,
        "duration": duration,
        "files": output_files,
    }


def process_task(task_id, file_path, segment_duration, silence_threshold, output_format):
    """Main processing task that runs in a background thread."""
    queue = task_queues[task_id]
    cancel_flag = cancel_flags[task_id]
    start_time = time.time()

    try:
        output_dir = str(OUTPUT_DIR)

        # Step 1: Demucs
        vocals_path = run_demucs(file_path, output_dir, queue, cancel_flag)

        # Step 2 & 3: Analyze and isolate
        final_output = os.path.join(output_dir, "female_voice_isolated.mp3")
        results = analyze_and_isolate_female(
            vocals_path,
            final_output,
            queue,
            cancel_flag,
            segment_duration=segment_duration,
            silence_threshold=silence_threshold,
            output_format=output_format,
        )

        elapsed = time.time() - start_time
        results["processing_time"] = elapsed

        tasks[task_id]["status"] = "complete"
        queue.put(
            {
                "status": "complete",
                "step": 3,
                "step_status": "complete",
                "progress": 100,
                "stage": "Complete",
                "log": f"Pipeline complete in {elapsed:.1f}s",
                "log_type": "success",
                "results": results,
                "files": results["files"],
            }
        )

    except RuntimeError as e:
        tasks[task_id]["status"] = "error"
        queue.put(
            {
                "status": "error",
                "error": str(e),
                "log": f"Error: {str(e)}",
                "log_type": "error",
            }
        )
    except Exception as e:
        tasks[task_id]["status"] = "error"
        queue.put(
            {
                "status": "error",
                "error": f"Unexpected error: {str(e)}",
                "log": f"Unexpected error: {str(e)}",
                "log_type": "error",
            }
        )


# ── Routes ──


@app.route("/")
def index():
    """Serve the main UI."""
    return render_template("index.html")


@app.route("/api/process", methods=["POST"])
def process_audio():
    """Start audio processing."""
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    file = request.files["audio"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    # Validate file extension
    original_ext = Path(file.filename).suffix.lower()
    if original_ext not in ALLOWED_EXTENSIONS:
        return (
            jsonify(
                {
                    "error": f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
                }
            ),
            400,
        )

    # Safe filename: UUID only, preserve extension
    safe_filename = f"{uuid.uuid4().hex}{original_ext}"
    file_path = str(UPLOAD_DIR / safe_filename)
    file.save(file_path)

    # Get parameters — clamp to valid ranges
    try:
        segment_duration = float(request.form.get("segment_duration", 0.5))
        segment_duration = max(0.1, min(2.0, segment_duration))
    except (ValueError, TypeError):
        segment_duration = 0.5

    try:
        silence_threshold = float(request.form.get("silence_threshold", 0.01))
        silence_threshold = max(0.001, min(0.05, silence_threshold))
    except (ValueError, TypeError):
        silence_threshold = 0.01

    output_format = request.form.get("output_format", "both")
    if output_format not in ALLOWED_OUTPUT_FORMATS:
        output_format = "both"

    # Create task (hold lock to prevent a concurrent cleanup from racing the init)
    task_id = uuid.uuid4().hex
    with _tasks_lock:
        task_queues[task_id] = Queue()
        cancel_flags[task_id] = {"cancelled": False}
        tasks[task_id] = {
            "status": "processing",
            "file": file_path,
            "started": time.time(),
        }

    # Start processing in background thread
    thread = threading.Thread(
        target=process_task,
        args=(task_id, file_path, segment_duration, silence_threshold, output_format),
        daemon=True,
    )
    thread.start()

    # Clean up stale tasks (keep last 20)
    _cleanup_old_tasks()

    return jsonify({"task_id": task_id, "status": "started"})


def _cleanup_old_tasks(max_tasks: int = 20):
    """Remove oldest completed/errored tasks to prevent unbounded memory growth."""
    with _tasks_lock:
        if len(tasks) <= max_tasks:
            return
        sorted_ids = sorted(tasks.keys(), key=lambda tid: tasks[tid].get("started", 0))
        removed = 0
        target = len(tasks) - max_tasks
        for tid in sorted_ids:
            if removed >= target:
                break
            if tasks[tid].get("status") == "processing":
                continue
            tasks.pop(tid, None)
            task_queues.pop(tid, None)
            cancel_flags.pop(tid, None)
            removed += 1


@app.route("/api/progress/<task_id>")
def progress(task_id):
    """Server-Sent Events endpoint for real-time progress."""
    if task_id not in task_queues:
        return jsonify({"error": "Task not found"}), 404

    queue = task_queues[task_id]

    def generate():
        heartbeat_count = 0
        while True:
            try:
                data = queue.get(timeout=30)
                yield f"data: {json.dumps(data)}\n\n"

                if data.get("status") in ("complete", "error"):
                    break
            except Exception:
                heartbeat_count += 1
                if heartbeat_count > 60:
                    yield f"data: {json.dumps({'status': 'error', 'error': 'Task timed out'})}\n\n"
                    break
                yield f"data: {json.dumps({'log': 'Heartbeat', 'log_type': 'info'})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.route("/api/cancel", methods=["POST"])
def cancel():
    """Cancel a specific processing task by task_id. Falls back to cancelling all active tasks."""
    data = request.get_json(silent=True) or {}
    task_id = data.get("task_id")

    if task_id and task_id in cancel_flags:
        cancel_flags[task_id]["cancelled"] = True
    else:
        # Fallback: cancel all active tasks
        for tid in list(cancel_flags.keys()):
            cancel_flags[tid]["cancelled"] = True

    return jsonify({"status": "cancelled"})


@app.route("/api/download/<path:file_path>")
def download(file_path):
    """Download an output file. Enforces path stays within OUTPUT_DIR."""
    try:
        # Resolve to absolute, canonical path to prevent traversal via ../
        resolved = Path(file_path).resolve()
        output_dir_resolved = OUTPUT_DIR.resolve()
        # Ensure the resolved path is inside OUTPUT_DIR
        resolved.relative_to(output_dir_resolved)  # raises ValueError if outside
        # Only serve audio output files
        if resolved.suffix.lower() not in {".mp3", ".wav", ".flac", ".ogg"}:
            return jsonify({"error": "Invalid file type"}), 400
        if resolved.is_file():
            return send_file(str(resolved), as_attachment=True)
    except (ValueError, OSError):
        pass
    return jsonify({"error": "File not found"}), 404


# ── Entry Point ──

if __name__ == "__main__":
    import random

    env_port = os.environ.get("FLASK_PORT")
    if env_port:
        port = int(env_port)
        if not (1 <= port <= 65535):
            print(f"FLASK_PORT={port} out of range, using random port")
            port = random.randint(8100, 8999)
    else:
        port = random.randint(8100, 8999)
    print(f"\n{'=' * 60}")
    print("  Voice Separation — Dark Neo Glass UI")
    print(f"  Running on: http://localhost:{port}")
    print(f"{'=' * 60}\n")
    app.run(host="127.0.0.1", port=port, debug=False, threaded=True)
