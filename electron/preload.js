/**
 * Voice Separation — Preload Script
 * Exposes window control IPC and external URL opener to the shell HTML.
 */
const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
    windowMinimize: () => ipcRenderer.invoke("window-minimize"),
    windowMaximize: () => ipcRenderer.invoke("window-maximize"),
    windowClose: () => ipcRenderer.invoke("window-close"),
    openExternal: (url) => ipcRenderer.invoke("open-external", url),
});
