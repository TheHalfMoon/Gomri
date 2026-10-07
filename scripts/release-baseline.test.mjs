import assert from "node:assert/strict";
import test from "node:test";
import { generateReleaseManifest } from "./generate-release-manifest.mjs";
import { validateReleaseConfig } from "./validate-release-config.mjs";

test("release configuration binds versions and forbids donor publish targets", async () => {
  const errors = await validateReleaseConfig();
  assert.deepEqual(errors, []);
});

test("release manifest binds exact commit and lockfiles", async () => {
  const manifest = await generateReleaseManifest();
  assert.equal(manifest.product, "Gomrey");
  assert.equal(manifest.version, "0.1.0");
  assert.match(manifest.commit, /^[0-9a-f]{40}$/);
  assert.equal(manifest.lockfiles.length, 4);
  for (const lockfile of manifest.lockfiles) {
    assert.match(lockfile.sha256, /^[0-9a-f]{64}$/);
  }
  assert.deepEqual(Object.keys(manifest.platforms).sort(), ["linux", "macos", "windows"]);
});
