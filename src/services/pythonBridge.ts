// ============================================================
// Python Bridge — 前端管理 Python FastAPI 进程生命周期
//
// 在 Tauri 环境中通过 shell plugin 启动 Python；
// 在浏览器开发模式下手动启动（npm run python-api）
// ============================================================

import { setBaseUrl, checkHealth } from "./api";

const PYTHON_PORT = 8000;
const PYTHON_BASE = `http://127.0.0.1:${PYTHON_PORT}`;

let _running = false;
let _pollTimer: ReturnType<typeof setInterval> | null = null;

// --- State ---
export function isPythonRunning(): boolean {
  return _running;
}

// --- Start Python backend (Tauri mode) ---
export async function startPythonBackend(): Promise<boolean> {
  // First check if already running
  if (await checkHealthWithBase(PYTHON_BASE)) {
    _running = true;
    setBaseUrl(PYTHON_BASE);
    return true;
  }

  try {
    // Try Tauri shell plugin
    if (window.__TAURI_INTERNALS__) {
      const { Command } = await import("@tauri-apps/plugin-shell");
      const cmd = Command.create("python-backend", [
        "api/app.py",
        "--port",
        String(PYTHON_PORT),
      ]);
      cmd.spawn();
      // Wait for it to be ready
      const ok = await waitForReady(PYTHON_BASE, 15_000);
      if (ok) {
        _running = true;
        setBaseUrl(PYTHON_BASE);
      }
      return ok;
    }
    // Browser dev mode: user must start manually
    console.warn(
      "[PythonBridge] 非 Tauri 环境，请手动启动: python api/app.py --port 8000",
    );
    return false;
  } catch (e) {
    console.error("[PythonBridge] 启动失败:", e);
    return false;
  }
}

// --- Stop Python backend ---
export async function stopPythonBackend(): Promise<void> {
  if (_pollTimer) {
    clearInterval(_pollTimer);
    _pollTimer = null;
  }
  _running = false;

  // In Tauri, process cleanup handled by app lifecycle
  // In browser, user closes terminal manually
  try {
    if (window.__TAURI_INTERNALS__) {
      // Send SIGTERM via health endpoint shutdown
      await fetch(`${PYTHON_BASE}/health/shutdown`, { method: "POST" }).catch(
        () => {},
      );
    }
  } catch {
    // Ignore
  }
}

// --- Poll until API is ready ---
async function waitForReady(
  base: string,
  timeoutMs: number,
): Promise<boolean> {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    if (await checkHealthWithBase(base)) return true;
    await sleep(500);
  }
  return false;
}

async function checkHealthWithBase(base: string): Promise<boolean> {
  try {
    const res = await fetch(`${base}/health`, { signal: AbortSignal.timeout(2000) });
    return res.ok;
  } catch {
    return false;
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise((r) => setTimeout(r, ms));
}
