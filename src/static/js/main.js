/* ══════════════════════════════════════════════════════════════
   VOICE SEPARATION — Frontend Logic
   Dark Neo Glass Theme
   ══════════════════════════════════════════════════════════════ */

(function () {
    'use strict';

    // ── State ──
    let selectedFile = null;
    let isProcessing = false;
    let eventSource = null;

    // ── DOM Refs ──
    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-input');
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');
    const fileRemoveBtn = document.getElementById('file-remove');
    const uploadContent = document.getElementById('upload-content');

    const processBtn = document.getElementById('process-btn');
    const cancelBtn = document.getElementById('cancel-btn');
    const resetBtn = document.getElementById('reset-btn');

    const segmentDuration = document.getElementById('segment-duration');
    const segmentValue = document.getElementById('segment-value');
    const silenceThreshold = document.getElementById('silence-threshold');
    const silenceValue = document.getElementById('silence-value');
    const outputFormat = document.getElementById('output-format');

    const progressSection = document.getElementById('progress-section');
    const progressFill = document.getElementById('progress-fill');
    const progressLabel = document.getElementById('progress-label');
    const progressPercent = document.getElementById('progress-percent');

    const step1 = document.getElementById('step-1');
    const step2 = document.getElementById('step-2');
    const step3 = document.getElementById('step-3');

    const resultsSection = document.getElementById('results-section');
    const logConsole = document.getElementById('log-console');
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');

    const notification = document.getElementById('notification');
    const notificationIcon = document.getElementById('notification-icon');
    const notificationText = document.getElementById('notification-text');

    // ── Utility Functions ──

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.appendChild(document.createTextNode(String(str)));
        return div.innerHTML;
    }

    function formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    function formatTime(seconds) {
        const m = Math.floor(seconds / 60);
        const s = Math.floor(seconds % 60);
        return m > 0 ? `${m}m ${s}s` : `${s}s`;
    }

    function getTimestamp() {
        const now = new Date();
        return now.toLocaleTimeString('en-US', { hour12: false });
    }

    // ── Notification System ──

    let notificationTimeout = null;

    function showNotification(type, message) {
        if (notificationTimeout) clearTimeout(notificationTimeout);

        notification.className = 'notification ' + type;
        notificationText.textContent = message;

        const icons = { success: '\u2713', error: '\u2715', info: '\u2139', warning: '\u26A0' };
        notificationIcon.textContent = icons[type] || '\u2139';

        requestAnimationFrame(() => {
            notification.classList.add('visible');
        });

        notificationTimeout = setTimeout(() => {
            notification.classList.remove('visible');
        }, 4000);
    }

    // ── Log Console ──

    function addLog(message, type = 'info') {
        const line = document.createElement('div');
        line.className = 'log-line';

        const timeSpan = document.createElement('span');
        timeSpan.className = 'log-time';
        timeSpan.textContent = `[${getTimestamp()}]`;

        const msgSpan = document.createElement('span');
        msgSpan.className = `log-msg ${escapeHtml(type)}`;
        msgSpan.textContent = message;

        line.appendChild(timeSpan);
        line.appendChild(msgSpan);
        logConsole.appendChild(line);
        logConsole.scrollTop = logConsole.scrollHeight;
    }

    // ── Status Management ──

    function setStatus(state, text) {
        statusDot.className = 'status-dot ' + state;
        statusText.textContent = text;
    }

    // ── File Upload ──

    uploadZone.addEventListener('click', () => {
        if (!isProcessing) fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        if (!isProcessing) uploadZone.classList.add('drag-over');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('drag-over');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('drag-over');
        if (!isProcessing && e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    function handleFile(file) {
        const validTypes = ['audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/x-wav', 'audio/flac', 'audio/ogg'];
        const validExtensions = ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac'];
        const ext = '.' + file.name.split('.').pop().toLowerCase();

        if (!validTypes.includes(file.type) && !validExtensions.includes(ext)) {
            showNotification('error', 'Invalid file type. Please upload an audio file (MP3, WAV, FLAC, OGG).');
            return;
        }

        selectedFile = file;
        fileName.textContent = file.name;
        fileSize.textContent = formatBytes(file.size);
        fileInfo.style.display = 'flex';
        uploadContent.style.display = 'none';
        uploadZone.classList.add('has-file');
        processBtn.disabled = false;

        addLog(`File selected: ${file.name} (${formatBytes(file.size)})`, 'accent');
        setStatus('ready', 'Ready to process');
    }

    fileRemoveBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        removeFile();
    });

    function removeFile() {
        selectedFile = null;
        fileInput.value = '';
        fileInfo.style.display = 'none';
        uploadContent.style.display = 'block';
        uploadZone.classList.remove('has-file');
        processBtn.disabled = true;
        addLog('File removed', 'warning');
        setStatus('ready', 'Idle');
    }

    // ── Range Sliders ──

    segmentDuration.addEventListener('input', () => {
        segmentValue.textContent = segmentDuration.value + 's';
    });

    silenceThreshold.addEventListener('input', () => {
        silenceValue.textContent = silenceThreshold.value;
    });

    // ── Processing ──

    processBtn.addEventListener('click', startProcessing);
    cancelBtn.addEventListener('click', cancelProcessing);
    resetBtn.addEventListener('click', resetUI);

    async function startProcessing() {
        if (!selectedFile || isProcessing) return;

        isProcessing = true;
        processBtn.disabled = true;
        cancelBtn.style.display = 'inline-flex';

        // Show progress section
        progressSection.classList.add('active');
        resultsSection.classList.remove('active');

        // Reset steps
        [step1, step2, step3].forEach(s => s.className = 'process-step');
        progressFill.style.width = '0%';
        progressPercent.textContent = '0%';

        setStatus('processing', 'Processing...');
        addLog('Starting voice isolation pipeline...', 'accent');

        // Prepare form data
        const formData = new FormData();
        formData.append('audio', selectedFile);
        formData.append('segment_duration', segmentDuration.value);
        formData.append('silence_threshold', silenceThreshold.value);
        formData.append('output_format', outputFormat.value);

        try {
            const response = await fetch('/api/process', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.error || 'Processing failed');
            }

            const data = await response.json();

            if (data.task_id) {
                window._currentTaskId = data.task_id;
                // Start listening for progress
                listenForProgress(data.task_id);
            }
        } catch (err) {
            addLog('Error: ' + err.message, 'error');
            showNotification('error', err.message);
            setStatus('error', 'Error');
            isProcessing = false;
            processBtn.disabled = false;
            cancelBtn.style.display = 'none';
        }
    }

    function listenForProgress(taskId) {
        eventSource = new EventSource('/api/progress/' + taskId);

        eventSource.onmessage = function (event) {
            const data = JSON.parse(event.data);

            if (data.log) {
                addLog(data.log, data.log_type || 'info');
            }

            if (data.progress !== undefined) {
                const pct = Math.round(data.progress);
                progressFill.style.width = pct + '%';
                progressPercent.textContent = pct + '%';
                progressLabel.textContent = data.stage || 'Processing...';
            }

            if (data.step !== undefined) {
                updateSteps(data.step, data.step_status);
            }

            if (data.status === 'complete') {
                eventSource.close();
                onProcessingComplete(data);
            }

            if (data.status === 'error') {
                eventSource.close();
                onProcessingError(data);
            }
        };

        eventSource.onerror = function () {
            eventSource.close();
            addLog('Connection to server lost', 'error');
            showNotification('error', 'Lost connection to server');
            setStatus('error', 'Connection lost');
            isProcessing = false;
            processBtn.disabled = false;
            cancelBtn.style.display = 'none';
        };
    }

    function updateSteps(stepNum, status) {
        const steps = [step1, step2, step3];
        steps.forEach((s, i) => {
            if (i + 1 < stepNum) {
                s.className = 'process-step complete';
                s.querySelector('.step-indicator').textContent = '\u2713';
            } else if (i + 1 === stepNum) {
                s.className = 'process-step ' + (status || 'active');
                if (status === 'active') {
                    s.querySelector('.step-indicator').innerHTML = '<div class="spinner"></div>';
                } else if (status === 'complete') {
                    s.querySelector('.step-indicator').textContent = '\u2713';
                } else if (status === 'error') {
                    s.querySelector('.step-indicator').textContent = '\u2715';
                }
            } else {
                s.className = 'process-step';
                s.querySelector('.step-indicator').textContent = (i + 1).toString();
            }
        });
    }

    function onProcessingComplete(data) {
        isProcessing = false;
        cancelBtn.style.display = 'none';
        resetBtn.style.display = 'inline-flex';

        setStatus('ready', 'Complete');
        showNotification('success', 'Voice isolation complete!');
        addLog('Pipeline complete. Output files ready.', 'success');

        // Update progress to 100%
        progressFill.style.width = '100%';
        progressPercent.textContent = '100%';
        progressLabel.textContent = 'Complete';

        // Show results
        resultsSection.classList.add('active');

        // Populate results
        if (data.results) {
            const stats = data.results;
            const statElements = {
                'female-segments': stats.female_segments || 0,
                'male-segments': stats.male_segments || 0,
                'ambiguous-segments': stats.ambiguous_segments || 0,
                'silence-segments': stats.silence_segments || 0,
                'total-duration': stats.duration ? formatTime(stats.duration) : '--',
                'processing-time': stats.processing_time ? formatTime(stats.processing_time) : '--'
            };

            Object.entries(statElements).forEach(([id, value]) => {
                const el = document.getElementById(id);
                if (el) el.textContent = value;
            });
        }

        // Populate output files
        if (data.files && data.files.length > 0) {
            const filesContainer = document.getElementById('output-files');
            filesContainer.innerHTML = '';

            data.files.forEach(file => {
                const fileEl = document.createElement('div');
                fileEl.className = 'output-file';

                const iconDiv = document.createElement('div');
                iconDiv.className = 'output-file-icon';
                iconDiv.textContent = '\u266B';

                const infoDiv = document.createElement('div');
                infoDiv.className = 'output-file-info';

                const nameDiv = document.createElement('div');
                nameDiv.className = 'output-file-name';
                nameDiv.textContent = file.name;

                const metaDiv = document.createElement('div');
                metaDiv.className = 'output-file-meta';
                metaDiv.textContent = `${String(file.format).toUpperCase()}${file.size ? ' - ' + formatBytes(file.size) : ''}`;

                infoDiv.appendChild(nameDiv);
                infoDiv.appendChild(metaDiv);

                const dlBtn = document.createElement('button');
                dlBtn.className = 'btn-download';
                dlBtn.textContent = 'Download';
                dlBtn.addEventListener('click', () => downloadFile(file.path));

                fileEl.appendChild(iconDiv);
                fileEl.appendChild(infoDiv);
                fileEl.appendChild(dlBtn);
                filesContainer.appendChild(fileEl);
            });

            // Audio player for primary output
            if (data.files[0]) {
                const audioPlayer = document.getElementById('audio-player');
                if (audioPlayer) {
                    audioPlayer.src = '/api/download/' + encodeURIComponent(data.files[0].path);
                    document.getElementById('audio-player-wrapper').style.display = 'block';
                }
            }
        }
    }

    function onProcessingError(data) {
        isProcessing = false;
        processBtn.disabled = false;
        cancelBtn.style.display = 'none';

        setStatus('error', 'Error');
        showNotification('error', data.error || 'Processing failed');
        addLog('Error: ' + (data.error || 'Unknown error'), 'error');
    }

    function cancelProcessing() {
        if (eventSource) {
            eventSource.close();
        }

        const currentTaskId = window._currentTaskId || null;
        fetch('/api/cancel', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task_id: currentTaskId }),
        })
            .then(() => {
                addLog('Processing cancelled by user', 'warning');
                showNotification('warning', 'Processing cancelled');
            })
            .catch(() => {});

        isProcessing = false;
        processBtn.disabled = false;
        cancelBtn.style.display = 'none';
        setStatus('ready', 'Cancelled');
    }

    function resetUI() {
        removeFile();
        progressSection.classList.remove('active');
        resultsSection.classList.remove('active');
        resetBtn.style.display = 'none';

        [step1, step2, step3].forEach((s, i) => {
            s.className = 'process-step';
            s.querySelector('.step-indicator').textContent = (i + 1).toString();
        });

        progressFill.style.width = '0%';
        progressPercent.textContent = '0%';
        progressLabel.textContent = 'Waiting...';
        logConsole.innerHTML = '';

        setStatus('ready', 'Idle');
        addLog('UI reset. Ready for new processing.', 'info');
    }

    // ── Download Handler ──

    window.downloadFile = function (filePath) {
        const a = document.createElement('a');
        a.href = '/api/download/' + encodeURIComponent(filePath);
        a.download = '';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    };

    // ── Initialize ──

    addLog('Voice Separation system initialized', 'accent');
    addLog('Powered by Meta Demucs + Pitch Analysis', 'info');
    setStatus('ready', 'Idle');

})();
