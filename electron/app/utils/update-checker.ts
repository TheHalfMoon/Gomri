import { net } from "electron";
import { app, BrowserWindow } from "electron";
import { isDev } from "./constants";
import { safeStderrWrite } from "./safe-console";

function normalizeHttpUrl(value: string | undefined): string {
  const raw = value?.trim();
  if (!raw) return "";
  try {
    const parsed = new URL(raw);
    return parsed.protocol === "http:" || parsed.protocol === "https:"
      ? parsed.toString()
      : "";
  } catch {
    return "";
  }
}

/**
 * Gomrey update checks are opt-in until a Gomrey-owned release feed is qualified.
 * UPDATE_SERVER_URL remains a generic legacy development override.
 */
const VERSION_JSON_URL = normalizeHttpUrl(
  process.env.GOMREY_UPDATE_SERVER_URL || process.env.UPDATE_SERVER_URL,
);

const CURRENT_VERSION = app.getVersion();
const WEBSITE_DOWNLOAD_URL =
  normalizeHttpUrl(process.env.GOMREY_DOWNLOAD_URL) ||
  "https://github.com/TheHalfMoon/Gomrey/releases";

/** Maximum number of fetch attempts (polls). */
const MAX_ATTEMPTS = 3;

/** Wait 2 minutes after load before first poll (10s in dev for testing). */
const INITIAL_DELAY_MS = isDev ? 10 * 1_000 : 2 * 60 * 1_000;

/** 1 minute between poll attempts (5s in dev for testing). */
const POLL_INTERVAL_MS = isDev ? 5 * 1_000 : 1 * 60 * 1_000;

/** Short delay before injecting banner to allow React/Next.js to mount. */
const INJECT_DELAY_MS = isDev ? 500 : 1_000;

function log(msg: string): void {
  const line = `[UpdateChecker] ${msg}\n`;
  safeStderrWrite(line);
}

interface VersionResponse {
  version: string;
  message?: string;
  downloads?: {
    linux: string;
    mac: string;
    windows: string;
  };
}

/**
 * Simple semver comparison that strips pre-release labels for numeric comparison.
 * Returns true if `remote` is strictly newer than `current`.
 */
function isNewerVersion(current: string, remote: string): boolean {
  const toNumbers = (v: string) =>
    v
      .replace(/[^0-9.]/g, "")
      .split(".")
      .map(Number);

  const curr = toNumbers(current);
  const rem = toNumbers(remote);
  const len = Math.max(curr.length, rem.length);

  for (let i = 0; i < len; i++) {
    const c = curr[i] ?? 0;
    const r = rem[i] ?? 0;
    if (r > c) return true;
    if (r < c) return false;
  }
  return false;
}

async function fetchVersionInfo(): Promise<VersionResponse | null> {
  if (!VERSION_JSON_URL) return null;
  try {
    log(`Fetching ${VERSION_JSON_URL}...`);
    const response = await net.fetch(VERSION_JSON_URL, {
      method: "GET",
      headers: { "User-Agent": `Gomrey/${CURRENT_VERSION}` },
    });
    if (!response.ok) {
      log(`Fetch failed: HTTP ${response.status}`);
      return null;
    }
    const data = (await response.json()) as VersionResponse;
    log(`Fetched version: ${data.version}`);
    return data;
  } catch (err) {
    log(`Fetch error: ${err}`);
    return null;
  }
}

/** Pending update to re-inject on navigation (production: React/Next.js may replace DOM). */
let pendingUpdate: { version: string; downloadUrl: string; message?: string } | null = null;
type UpdateTimer = ReturnType<typeof setTimeout>;
const scheduledTimers = new Set<UpdateTimer>();
const delayCancels = new Set<() => void>();
let updateCheckerStopped = true;
let cleanupUpdateCheckerListeners: (() => void) | null = null;

function hasLiveWebContents(win: BrowserWindow): boolean {
  return !win.isDestroyed() && !win.webContents.isDestroyed();
}

function scheduleUpdateTimer(callback: () => void, delayMs: number): void {
  if (updateCheckerStopped) return;

  const timer = setTimeout(() => {
    scheduledTimers.delete(timer);
    if (!updateCheckerStopped) {
      callback();
    }
  }, delayMs);
  scheduledTimers.add(timer);
}

function waitForUpdateDelay(delayMs: number): Promise<boolean> {
  if (updateCheckerStopped) {
    return Promise.resolve(false);
  }

  return new Promise((resolve) => {
    let settled = false;
    let cancel = () => {};
    const timer = setTimeout(() => {
      if (settled) return;
      settled = true;
      scheduledTimers.delete(timer);
      delayCancels.delete(cancel);
      resolve(!updateCheckerStopped);
    }, delayMs);

    cancel = () => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      scheduledTimers.delete(timer);
      delayCancels.delete(cancel);
      resolve(false);
    };

    scheduledTimers.add(timer);
    delayCancels.add(cancel);
  });
}

function clearScheduledUpdateWork(): void {
  for (const cancel of Array.from(delayCancels)) {
    cancel();
  }
  for (const timer of Array.from(scheduledTimers)) {
    clearTimeout(timer);
    scheduledTimers.delete(timer);
  }
  if (cleanupUpdateCheckerListeners) {
    cleanupUpdateCheckerListeners();
    cleanupUpdateCheckerListeners = null;
  }
}

/**
 * Schedules banner injection after INJECT_DELAY_MS so React/Next.js can mount first.
 * In production (.deb), the DOM may not be ready when did-finish-load fires.
 */
function scheduleBannerInjection(
  win: BrowserWindow,
  version: string,
  downloadUrl: string,
  message?: string
): void {
  pendingUpdate = { version, downloadUrl, message };
  scheduleUpdateTimer(() => {
    if (!hasLiveWebContents(win) || !pendingUpdate) return;
    log(`Injecting banner now`);
    injectUpdateBanner(win, pendingUpdate.version, pendingUpdate.downloadUrl, pendingUpdate.message);
  }, INJECT_DELAY_MS);
}

/**
 * Injects an update banner at the bottom, aligned with the app UI.
 * Includes a "View details" overlay for changelog/message.
 */
function injectUpdateBanner(
  win: BrowserWindow,
  latest: string,
  downloadUrl: string,
  message?: string
): void {
  if (!hasLiveWebContents(win)) {
    return;
  }

  const dataJson = JSON.stringify({
    latest,
    currentVersion: CURRENT_VERSION,
    downloadUrl,
    message: message?.trim() || "",
  });

  const script = /* js */ `
    (function () {
      if (document.getElementById('__gomrey_update_banner__')) return;

      const data = ${dataJson};
      const banner = document.createElement('div');
      banner.id = '__gomrey_update_banner__';
      banner.style.cssText = [
        'position:fixed',
        'bottom:16px',
        'left:50%',
        'transform:translateX(-50%)',
        'max-width:min(560px,calc(100vw - 32px))',
        'width:100%',
        'background:rgba(255,255,255,0.95)',
        'backdrop-filter:blur(12px)',
        '-webkit-backdrop-filter:blur(12px)',
        'color:#191919',
        'display:flex',
        'align-items:center',
        'justify-content:space-between',
        'padding:12px 16px',
        'font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif',
        'font-size:13px',
        'z-index:2147483646',
        'border:1px solid rgba(148,163,184,0.3)',
        'border-radius:12px',
        'box-shadow:0 4px 24px rgba(0,0,0,0.08)',
        'gap:12px',
      ].join(';');

      const summary = document.createElement('span');
      summary.style.cssText = 'display:flex;align-items:center;gap:8px;flex:1;min-width:0;';
      const sparkle = document.createElement('span');
      sparkle.style.fontSize = '18px';
      sparkle.textContent = '✨';
      const summaryText = document.createElement('span');
      summaryText.append(document.createTextNode('Gomrey '));
      const latestStrong = document.createElement('strong');
      latestStrong.style.color = '#5141e5';
      latestStrong.textContent = data.latest;
      summaryText.append(latestStrong);
      summaryText.append(document.createTextNode(' is available — you have '));
      const currentStrong = document.createElement('strong');
      currentStrong.textContent = data.currentVersion;
      summaryText.append(currentStrong);
      summary.append(sparkle, summaryText);

      const actions = document.createElement('div');
      actions.style.cssText = 'display:flex;gap:8px;align-items:center;flex-shrink:0;';

      let overlay = null;
      if (data.message) {
        const details = document.createElement('button');
        details.id = '__gomrey_view_details_btn__';
        details.type = 'button';
        details.textContent = 'View details';
        details.style.cssText = 'color:#64748b;background:none;border:none;cursor:pointer;font-size:12px;padding:4px 8px;text-decoration:underline;text-underline-offset:2px;';
        actions.append(details);

        overlay = document.createElement('div');
        overlay.id = '__gomrey_update_overlay__';
        overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.4);display:none;align-items:center;justify-content:center;z-index:2147483647;padding:24px;';
        overlay.addEventListener('click', (event) => {
          if (event.target === overlay) overlay.style.display = 'none';
        });

        const panel = document.createElement('div');
        panel.style.cssText = 'background:#fff;border-radius:16px;max-width:420px;width:100%;max-height:80vh;overflow:auto;box-shadow:0 24px 48px rgba(0,0,0,0.15);padding:24px;';
        panel.addEventListener('click', (event) => event.stopPropagation());
        const headingRow = document.createElement('div');
        headingRow.style.cssText = 'display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;';
        const heading = document.createElement('h3');
        heading.style.cssText = 'margin:0;font-size:18px;font-weight:600;color:#191919;';
        heading.textContent = "What's new in " + data.latest;
        const closeOverlay = document.createElement('button');
        closeOverlay.type = 'button';
        closeOverlay.textContent = '×';
        closeOverlay.style.cssText = 'background:none;border:none;color:#94a3b8;cursor:pointer;font-size:24px;line-height:1;padding:0;';
        closeOverlay.addEventListener('click', () => { overlay.style.display = 'none'; });
        headingRow.append(heading, closeOverlay);
        const content = document.createElement('div');
        content.id = '__gomrey_overlay_content__';
        content.style.cssText = 'color:#475569;font-size:14px;line-height:1.6;white-space:pre-wrap;';
        content.textContent = data.message;
        panel.append(headingRow, content);
        overlay.append(panel);
        document.body.appendChild(overlay);
        details.addEventListener('click', () => { overlay.style.display = 'flex'; });
      }

      const download = document.createElement('a');
      download.href = data.downloadUrl;
      download.target = '_blank';
      download.rel = 'noopener noreferrer';
      download.textContent = 'Download update';
      download.style.cssText = 'color:#fff;text-decoration:none;background:#5141e5;padding:6px 14px;border-radius:8px;font-size:12px;font-weight:500;white-space:nowrap;';
      actions.append(download);

      const dismiss = document.createElement('button');
      dismiss.type = 'button';
      dismiss.title = 'Dismiss';
      dismiss.textContent = '×';
      dismiss.style.cssText = 'background:none;border:none;color:#94a3b8;cursor:pointer;font-size:20px;line-height:1;padding:0 2px;';
      dismiss.addEventListener('click', () => {
        banner.remove();
        if (overlay) overlay.remove();
      });
      actions.append(dismiss);

      banner.append(summary, actions);
      document.body.appendChild(banner);
    })();
  `;

  win.webContents.executeJavaScript(script).catch((err) => {
    log(`Banner injection failed: ${err}`);
  });
}

/**
 * Polls for version info up to MAX_ATTEMPTS times with 1 min between attempts.
 * Stops as soon as a successful response is received or all attempts are exhausted.
 */
async function checkForUpdatesWithRetry(win: BrowserWindow): Promise<void> {
  log(`Starting check (current: ${CURRENT_VERSION})`);
  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
    if (updateCheckerStopped || !hasLiveWebContents(win)) {
      log("Window destroyed, aborting");
      return;
    }

    log(`Attempt ${attempt}/${MAX_ATTEMPTS}`);
    const data = await fetchVersionInfo();
    if (updateCheckerStopped || !hasLiveWebContents(win)) {
      log("Window destroyed, aborting");
      return;
    }

    if (data) {
      const newer = isNewerVersion(CURRENT_VERSION, data.version);
      log(`Remote ${data.version} vs current ${CURRENT_VERSION} -> newer? ${newer}`);
      if (newer) {
        const downloadUrl = WEBSITE_DOWNLOAD_URL;
        log(`Injecting banner for ${data.version} (after ${INJECT_DELAY_MS}ms delay)`);
        scheduleBannerInjection(win, data.version, downloadUrl, data.message);
      } else {
        log("No update needed, skipping banner");
      }
      return;
    }

    // Wait 1 minute before the next poll (skip delay after the last attempt)
    if (attempt < MAX_ATTEMPTS) {
      log(`Next poll in ${POLL_INTERVAL_MS / 1_000}s...`);
      const shouldContinue = await waitForUpdateDelay(POLL_INTERVAL_MS);
      if (!shouldContinue) return;
    }
  }
  log("All attempts failed, no update info");
}

/**
 * Starts the update checker.
 * Waits 2 minutes after load, then polls 3 times with 1 min interval.
 * Re-injects banner on every navigation (handles Next.js client routing).
 */
export function startUpdateChecker(win: BrowserWindow): void {
  stopUpdateChecker();
  if (!VERSION_JSON_URL) {
    log("Automatic update checks are disabled until a Gomrey update endpoint is configured");
    return;
  }
  updateCheckerStopped = false;
  if (!hasLiveWebContents(win)) {
    updateCheckerStopped = true;
    return;
  }

  log("Registered, waiting for did-finish-load");
  let hasRunCheck = false;

  const onLoad = () => {
    if (updateCheckerStopped || !hasLiveWebContents(win)) return;

    if (pendingUpdate) {
      log("did-finish-load (navigation), re-injecting banner");
      scheduleBannerInjection(win, pendingUpdate.version, pendingUpdate.downloadUrl, pendingUpdate.message);
    } else if (!hasRunCheck) {
      hasRunCheck = true;
      log(`did-finish-load fired, first poll in ${INITIAL_DELAY_MS / 1_000}s`);
      scheduleUpdateTimer(() => {
        if (!hasLiveWebContents(win)) return;
        void checkForUpdatesWithRetry(win).catch((err) => {
          log(`Update check failed: ${err}`);
        });
      }, INITIAL_DELAY_MS);
    }
  };

  const onClosed = () => {
    stopUpdateChecker();
  };
  win.once("closed", onClosed);
  cleanupUpdateCheckerListeners = () => {
    if (hasLiveWebContents(win)) {
      win.webContents.removeListener("did-finish-load", onLoad);
    }
    try {
      win.removeListener("closed", onClosed);
    } catch {
      // BrowserWindow may already be torn down when cleanup runs from "closed".
    }
  };

  if (!win.webContents.isLoading()) {
    log(`Page already loaded, first poll in ${INITIAL_DELAY_MS / 1_000}s`);
    hasRunCheck = true;
    scheduleUpdateTimer(() => {
      if (!hasLiveWebContents(win)) return;
      void checkForUpdatesWithRetry(win).catch((err) => {
        log(`Update check failed: ${err}`);
      });
    }, INITIAL_DELAY_MS);
  }
  win.webContents.on("did-finish-load", onLoad);
}

export function stopUpdateChecker(): void {
  updateCheckerStopped = true;
  pendingUpdate = null;
  clearScheduledUpdateWork();
}
