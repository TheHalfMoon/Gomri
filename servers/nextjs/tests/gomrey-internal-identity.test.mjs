import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import test from "node:test";

const root = process.cwd();
const read = (relativePath) => readFile(path.join(root, relativePath), "utf8");

test("internal event and chart runtime identity is Gomrey-owned", async () => {
  const [eventSource, chartSource] = await Promise.all([
    read("app/(presentation-generator)/_shared/blank-slide-prompt-event.ts"),
    read("lib/chart-browser.ts"),
  ]);
  assert.match(eventSource, /GOMREY_BLANK_SLIDE_PROMPT_EVENT/);
  assert.match(eventSource, /gomrey:blank-slide-prompt/);
  assert.doesNotMatch(eventSource, /PRESENTON_BLANK_SLIDE_PROMPT_EVENT/);
  assert.match(chartSource, /__GOMREY_CHART_BROWSER_RUNTIME__/);
  assert.match(chartSource, /data-gomrey-chart-runtime/);
  assert.doesNotMatch(chartSource, /__PRESENTON_CHART_BROWSER_RUNTIME__/);
});

test("splash source identity is Gomrey while donor artwork remains explicit debt", async () => {
  const [splash, auth, loading, config, css] = await Promise.all([
    read("components/ui/gomrey-splash-loader.tsx"),
    read("components/Auth/AuthGate.tsx"),
    read("app/loading.tsx"),
    read("app/ConfigurationInitializer.tsx"),
    read("app/globals.css"),
  ]);
  assert.match(splash, /GomreySplashLoader/);
  assert.match(splash, /GOMREY_SPLASH_MIN_DURATION_MS/);
  assert.match(splash, /gomrey-splash-/);
  assert.match(splash, /\/Presenton_Splash\.png/);
  assert.match(splash, /P02-G3 asset migration/);
  assert.ok(splash.includes('const SPLASH_MASK_SRC = "/Presenton_Splash.png";'));
  assert.doesNotMatch(splash, /\\nconst SPLASH_MASK_SRC/);
  assert.doesNotMatch(auth + loading + config + css, /presenton-splash-/);
  assert.doesNotMatch(config, /Loading Presenton/);
});
