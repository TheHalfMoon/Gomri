import assert from "node:assert/strict";
import { access, readFile, stat } from "node:fs/promises";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

const read = (relativePath) => readFile(path.join(repoRoot, relativePath), "utf8");

async function assertMissing(relativePath) {
  await assert.rejects(access(path.join(repoRoot, relativePath)));
}

test("desktop signing and MAS inputs are Gomrey-owned and fail closed", async () => {
  const [build, pkg, entitlements] = await Promise.all([
    read("electron/build.js"),
    read("electron/package.json"),
    read("electron/build/entitlements.mas.plist"),
  ]);

  assert.match(build, /GOMREY_MAC_TARGET/);
  assert.match(build, /GOMREY_MAS_APP_ID/);
  assert.match(build, /GOMREY_TEAM_ID/);
  assert.match(build, /GOMREY_MAS_DEV_PROVISIONING_PROFILE/);
  assert.match(build, /GOMREY_MAS_PROVISIONING_PROFILE/);
  assert.match(build, /GOMREY_MAC_SIGN_IDENTITY/);
  assert.equal((build.match(/appId: masAppId/g) || []).length, 2);
  assert.doesNotMatch(build, /LEGACY_GOMREY_APP_ID/);
  assert.doesNotMatch(build + pkg, /PRESENTON_(?:MAC|MAS|APP_STORE|REQUIRE_MAC|SKIP_NOTARIZATION|CODESIGN)/);
  assert.doesNotMatch(build, /com\.presenton\.presenton/);
  assert.doesNotMatch(build, /PresentonAI\.Presenton/);
  assert.doesNotMatch(build, /Presenton Inc\./);
  assert.doesNotMatch(build, /S6W5C54KL6/);
  assert.doesNotMatch(entitlements, /presenton/i);
  assert.doesNotMatch(entitlements, /S6W5C54KL6/);
});

test("Microsoft Store packaging stays disabled until owned identity is admitted", async () => {
  const [build, identity] = await Promise.all([
    read("electron/build.js"),
    read("config/store-artwork-identity.json").then(JSON.parse),
  ]);

  assert.equal(identity.microsoft_store.status, "disabled");
  assert.match(build, /target: \["nsis"\]/);
  assert.doesNotMatch(build, /appx:\s*\{/);
});

test("default runtime and packages do not reference donor binary branding", async () => {
  const [build, main, splash] = await Promise.all([
    read("electron/build.js"),
    read("electron/app/main.ts"),
    read("servers/nextjs/components/ui/gomrey-splash-loader.tsx"),
  ]);

  assert.doesNotMatch(build, /icon:\s*"build\//);
  assert.doesNotMatch(build, /installerIcon|uninstallerIcon|installerHeaderIcon/);
  assert.doesNotMatch(main, /presenton_short_filled\.png/);
  assert.match(splash, /GOMREY_WORDMARK = "GOMREY"/);
  assert.doesNotMatch(splash, /Presenton_Splash|maskImage|WebkitMaskImage/);

  for (const asset of [
    "servers/nextjs/public/Presenton_Splash.png",
    "electron/resources/ui/assets/images/presenton_short_filled.png",
    "electron/resources/ui/assets/images/presenton_logo.png",
    "electron/build/icon.icns",
    "electron/build/icon.ico",
    "electron/build/icon-1024.png",
    "electron/build/logo.png",
    "electron/build/icons",
    "electron/build/icon.iconset",
    "electron/build/appx",
  ]) {
    await assertMissing(asset);
  }
});

test("Presenton provider artwork remains provider provenance, not Gomrey branding", async () => {
  const providerIcon = path.join(repoRoot, "servers/nextjs/public/providers/presenton.png");
  assert.equal((await stat(providerIcon)).isFile(), true);
  const providerSource = await read("servers/nextjs/utils/providerConstants.ts");
  assert.match(providerSource, /\/providers\/presenton\.png/);
});

test("macOS operator docs no longer instruct donor signing identities", async () => {
  const docs = (
    await Promise.all([
      read("docs/macos/dev/mac-app-store-setup.md"),
      read("docs/macos/dev/direct-distribution.md"),
      read("docs/macos/dev/signed-dmg-build-steps.md"),
    ])
  ).join("\n");

  assert.doesNotMatch(docs, /PRESENTON_(?:MAC|MAS|APP_STORE|REQUIRE_MAC|SKIP_NOTARIZATION|CODESIGN)/);
  assert.doesNotMatch(docs, /com\.presenton\.presenton|Presenton Inc\.|S6W5C54KL6/);
  assert.match(docs, /GOMREY_MAS_APP_ID/);
  assert.match(docs, /GOMREY_MAC_SIGN_IDENTITY/);
});
