/**
 * Voice Separation — Electron Main Process
 * Spawns the Flask backend and displays it in a frameless neo-glass window.
 */
const { app, BrowserWindow, BrowserView, ipcMain, shell } = require("electron");
const path = require("path");
const { spawn } = require("child_process");
const net = require("net");

let mainWindow = null;
let flaskProcess = null;
let flaskPort = null;

// Linux transparent window fix — must be before app.whenReady
if (process.platform === "linux") {
    app.commandLine.appendSwitch("enable-transparent-visuals");
    app.commandLine.appendSwitch("disable-gpu-compositing"); // NOT disable-gpu
    app.commandLine.appendSwitch("no-sandbox");
}

// ── Find a free port ──
function findFreePort() {
    return new Promise((resolve, reject) => {
        const server = net.createServer();
        server.listen(0, () => {
            const port = server.address().port;
            server.close(() => resolve(port));
        });
        server.on("error", reject);
    });
}

// ── Wait for Flask to be ready ──
function waitForFlask(port, maxRetries = 30) {
    return new Promise((resolve, reject) => {
        let retries = 0;
        const check = () => {
            const client = new net.Socket();
            client.connect(port, "127.0.0.1", () => {
                client.destroy();
                resolve();
            });
            client.on("error", () => {
                client.destroy();
                retries++;
                if (retries >= maxRetries) {
                    reject(
                        new Error(
                            `Flask not ready after ${maxRetries} retries`,
                        ),
                    );
                } else {
                    setTimeout(check, 500);
                }
            });
        };
        check();
    });
}

// ── Start Flask backend ──
async function startFlask() {
    flaskPort = await findFreePort();

    const projectDir = path.join(__dirname, "..");
    const venvPython = path.join(projectDir, "venv", "bin", "python");

    // Prefer venv python, fall back to system
    const pythonCmd = require("fs").existsSync(venvPython)
        ? venvPython
        : "python3";

    const env = {
        ...process.env,
        FLASK_PORT: String(flaskPort),
        OMP_NUM_THREADS: String(require("os").cpus().length),
        MKL_NUM_THREADS: String(require("os").cpus().length),
    };

    flaskProcess = spawn(pythonCmd, [path.join(projectDir, "src", "app.py")], {
        cwd: projectDir,
        env,
        stdio: ["pipe", "pipe", "pipe"],
    });

    flaskProcess.stdout.on("data", (data) => {
        process.stdout.write(`[Flask] ${data}`);
    });

    flaskProcess.stderr.on("data", (data) => {
        process.stderr.write(`[Flask] ${data}`);
    });

    flaskProcess.on("exit", (code) => {
        console.log(`Flask exited with code ${code}`);
        flaskProcess = null;
    });

    console.log(`Waiting for Flask on port ${flaskPort}...`);
    await waitForFlask(flaskPort);
    console.log(`Flask ready on port ${flaskPort}`);
}

// ── Create the main window ──
function createWindow() {
    const isMac = process.platform === "darwin";

    mainWindow = new BrowserWindow({
        width: 1400,
        height: 1024,
        minWidth: 900,
        minHeight: 600,
        frame: false, // NO native chrome — CRITICAL
        transparent: true, // Alpha channel enabled
        backgroundColor: "#00000000", // Fully transparent
        hasShadow: false, // NO OS shadow — CSS handles depth
        resizable: true,
        roundedCorners: true,
        title: "Voice Separation",
        ...(isMac ? { titleBarStyle: "hiddenInset" } : {}),
        webPreferences: {
            contextIsolation: true,
            sandbox: false, // Required for transparent frameless on Linux
            nodeIntegration: false,
            preload: path.join(__dirname, "preload.js"),
            // NEVER: experimentalFeatures: true — breaks IPC on Linux
        },
        show: false,
    });

    // Load the shell HTML (title bar shell)
    mainWindow.loadFile(path.join(__dirname, "shell.html"));

    // Show only when ready
    mainWindow.once("ready-to-show", () => {
        mainWindow.show();
        updateViewBounds();
    });

    // Create a BrowserView for Flask content (below the titlebar)
    const contentView = new BrowserView({
        webPreferences: {
            contextIsolation: true,
            sandbox: false,
            nodeIntegration: false,
        },
    });

    // Dark background prevents white flash before Flask loads
    contentView.setBackgroundColor("#0a0b0e");

    mainWindow.addBrowserView(contentView);
    contentView.webContents.loadURL(`http://127.0.0.1:${flaskPort}`);

    // Position the BrowserView below the titlebar (48px) + body padding (20px).
    // BODY_PAD matches body::before inset in shell.html — the rounded window
    // shadow pseudo-element sits in that 20px gutter. Status bar (28px) is in
    // the shell, so we subtract it to avoid overlap.
    const TITLEBAR_HEIGHT = 48;
    const STATUS_BAR_HEIGHT = 28;
    const BODY_PAD = 20;

    function updateViewBounds() {
        if (!mainWindow || mainWindow.isDestroyed()) return;
        const [width, height] = mainWindow.getContentSize();
        contentView.setBounds({
            x: BODY_PAD + 1,
            y: TITLEBAR_HEIGHT + BODY_PAD,
            width: width - BODY_PAD * 2 - 2,
            height:
                height - TITLEBAR_HEIGHT - STATUS_BAR_HEIGHT - BODY_PAD * 2 - 1,
        });
    }

    mainWindow.on("resize", updateViewBounds);
    mainWindow.on("maximize", () => setTimeout(updateViewBounds, 100));
    mainWindow.on("unmaximize", () => setTimeout(updateViewBounds, 100));

    // Initial bounds after a brief delay
    setTimeout(updateViewBounds, 200);

    // DevTools only with explicit flag
    if (process.argv.includes("--dev")) {
        mainWindow.webContents.openDevTools();
    }

    mainWindow.on("closed", () => {
        mainWindow = null;
    });
}

// ── IPC Handlers (handle = promise-based, works with contextBridge invoke) ──
ipcMain.handle("window-minimize", () => {
    if (mainWindow) mainWindow.minimize();
});
ipcMain.handle("window-maximize", () => {
    if (!mainWindow) return;
    mainWindow.isMaximized() ? mainWindow.unmaximize() : mainWindow.maximize();
});
ipcMain.handle("window-close", () => {
    if (mainWindow) mainWindow.close();
});

// Open external URLs safely (protocol whitelist)
ipcMain.handle("open-external", async (event, url) => {
    try {
        const parsed = new URL(url);
        if (["http:", "https:", "mailto:"].includes(parsed.protocol)) {
            await shell.openExternal(url);
        }
    } catch (_) {
        // Invalid URL — silently reject
    }
});

// ── App lifecycle ──

app.whenReady().then(async () => {
    try {
        await startFlask();

        if (process.platform === "linux") {
            setTimeout(createWindow, 300);
        } else {
            createWindow();
        }
    } catch (err) {
        console.error("Failed to start Flask:", err);
        app.quit();
    }
});

function killFlask() {
    if (!flaskProcess) return;
    try {
        flaskProcess.kill("SIGTERM");
        // Give it 2s to exit cleanly, then force-kill
        setTimeout(() => {
            if (flaskProcess) {
                try {
                    flaskProcess.kill("SIGKILL");
                } catch (_) {}
                flaskProcess = null;
            }
        }, 2000);
    } catch (_) {
        flaskProcess = null;
    }
}

app.on("window-all-closed", () => {
    killFlask();
    app.quit();
});

app.on("before-quit", () => {
    killFlask();
});
