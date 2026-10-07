import assert from "node:assert/strict";
import test from "node:test";
import { loadPlatformSupport, validatePlatformSupport } from "./check-platform-support.mjs";

test("platform-support matrix keeps Linux full and Windows/macOS bounded", async () => {
  const matrix = await loadPlatformSupport();
  assert.deepEqual(validatePlatformSupport(matrix), []);
  assert.equal(matrix.matrix.linux.scope, "full-integration");
  assert.equal(matrix.matrix.windows.scope, "bounded-qualification");
  assert.equal(matrix.matrix.macos.scope, "bounded-qualification");
});

test("platform-support matrix requires no Store credentials for ordinary CI", async () => {
  const matrix = await loadPlatformSupport();
  const text = JSON.stringify(matrix);
  assert.doesNotMatch(text, /CSC_IDENTITY|APPLE_ID_|NOTARIZATION_PASSWORD|APP_STORE_CONNECT|SIGNING_CERTIFICATE/);
  assert.match(text.toLowerCase(), /no store/);
  assert.match(text.toLowerCase(), /no .*credentials are required/);
});

test("platform validator rejects donor-style full matrix on all platforms", async () => {
  const bad = {
    runners: { linux: "ubuntu-latest", windows: "windows-latest", macos: "macos-latest" },
    matrix: {
      linux: { scope: "full-integration", jobs: ["all"] },
      windows: { scope: "full-integration", jobs: ["all"] },
      macos: { scope: "full-integration", jobs: ["all"] },
    },
    required_for_merge: ["qualify-windows", "qualify-macos", "g4-baseline"],
  };
  const errors = validatePlatformSupport(bad);
  assert.ok(errors.some((error) => error.includes("windows must be bounded-qualification")));
});
