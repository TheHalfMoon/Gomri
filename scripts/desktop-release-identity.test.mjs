import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

async function read(relativePath) {
  return readFile(path.join(repoRoot, relativePath), "utf8");
}

async function readJson(relativePath) {
  return JSON.parse(await read(relativePath));
}

test("Gomrey non-store desktop identity is canonical", async () => {
  const [identity, build] = await Promise.all([
    readJson("config/desktop-release-identity.json"),
    read("electron/build.js"),
  ]);

  assert.equal(identity.canonical.app_id, "io.github.thehalfmoon.gomrey");
  assert.match(build, /const GOMREY_APP_ID = "io\.github\.thehalfmoon\.gomrey"/);
  assert.match(
    build,
    /const APP_ID = isMasBuild \? LEGACY_PRESENTON_APP_ID : GOMREY_APP_ID/,
  );
  assert.match(build, /artifactName: "Gomrey-\$\{version\}\.\$\{ext\}"/);
  assert.match(build, /executableName: "Gomrey"/);
  assert.match(build, /shortcutName: "Gomrey"/);
  assert.match(build, /uninstallDisplayName: "Gomrey"/);
  assert.match(build, /target: \["nsis"\]/);
});

test("legacy store identities stay bounded to G3c", async () => {
  const [identity, build] = await Promise.all([
    readJson("config/desktop-release-identity.json"),
    read("electron/build.js"),
  ]);

  assert.equal(
    identity.legacy_store_contracts.mac_app_store_app_id,
    "com.presenton.presenton",
  );
  assert.match(build, /masDev: \{[\s\S]*?appId: LEGACY_PRESENTON_APP_ID/);
  assert.match(build, /mas: \{[\s\S]*?appId: LEGACY_PRESENTON_APP_ID/);
  assert.match(build, /identityName: "PresentonAI\.Presenton"/);
  assert.match(build, /applicationId: "PresentonAI\.Presenton"/);
});

test("generated release metadata targets Gomrey artifacts and repository", async () => {
  const [generator, version] = await Promise.all([
    read("electron/scripts/generate-version.cjs"),
    readJson("electron/version.json"),
  ]);

  assert.match(generator, /github\.com\/TheHalfMoon\/Gomrey\/releases/);
  assert.match(generator, /Gomrey-\$\{version\}/);
  assert.doesNotMatch(generator, /github\.com\/presenton\/presenton/);
  assert.equal(version.message, "");
  for (const url of Object.values(version.downloads)) {
    assert.match(url, /github\.com\/TheHalfMoon\/Gomrey\/releases/);
    assert.match(url, /Gomrey-/);
    assert.doesNotMatch(url, /presenton\/presenton/i);
  }
});

test("desktop telemetry has no inherited donor DSN and is opt-in", async () => {
  const [sentry, rendererSentry, envSetup, upload] = await Promise.all([
    read("electron/app/sentry/main.ts"),
    read("electron/app/preloads/sentry.ts"),
    read("electron/app/utils/index.ts"),
    read("electron/scripts/upload-sourcemaps.cjs"),
  ]);

  assert.match(sentry, /GOMREY_SENTRY_DSN/);
  assert.match(sentry, /process\.env\.SENTRY_DSN/);
  assert.match(sentry, /parseBoolean\(process\.env\.SENTRY_ENABLED, false\)/);
  assert.doesNotMatch(sentry, /ingest\.us\.sentry\.io/);
  assert.match(rendererSentry, /GOMREY_SENTRY_DSN/);
  assert.match(rendererSentry, /parseBoolean\(process\.env\.SENTRY_ENABLED, false\)/);
  assert.doesNotMatch(rendererSentry, /ingest\.us\.sentry\.io/);
  assert.match(sentry, /gomrey-electron@/);
  assert.doesNotMatch(sentry, /presenton-electron@/);
  assert.match(sentry, /setContext\("gomrey"/);
  assert.doesNotMatch(sentry, /setContext\("presenton"/);
  assert.doesNotMatch(envSetup, /presenton-electron@/);
  assert.doesNotMatch(envSetup, /presenton-electron@/);
  assert.match(upload, /gomrey-electron@/);
  assert.doesNotMatch(upload, /presenton-electron@/);
});

test("Linux test release is Gomrey-owned", async () => {
  const workflow = await read(".github/workflows/electron-linux-ubuntu22.yml");
  assert.match(workflow, /gomrey-electron-linux-ubuntu-22/);
  assert.match(workflow, /RELEASE_REPOSITORY: TheHalfMoon\/Gomrey/);
  assert.doesNotMatch(workflow, /presenton\/presenton-export/);
  assert.doesNotMatch(workflow, /from presenton\/presenton@/);
});
