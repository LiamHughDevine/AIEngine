import { app, BrowserWindow } from "electron";
const { spawn } = require('child_process');

async function createWindow() {
    const isDev = (await import("electron-is-dev")).default;

    const win = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true,
        },
    });

    win.loadURL(
        isDev ? "http://localhost:3000" : "file://path-to-your-index.html",
    );
}

app.whenReady().then(createWindow);
