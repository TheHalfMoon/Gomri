import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";
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

test("Gomrey-owned package identities are canonical", async () => {
  const [identity, rootPackage, rootLock, webPackage, webLock, desktopPackage, desktopLock] =
    await Promise.all([
      readJson("product-identity.json"),
      readJson("package.json"),
      readJson("package-lock.json"),
      readJson("servers/nextjs/package.json"),
      readJson("servers/nextjs/package-lock.json"),
      readJson("electron/package.json"),
      readJson("electron/package-lock.json"),
    ]);

  assert.equal(identity.product.name, "Gomrey");
  assert.equal(identity.product.repository, "https://github.com/TheHalfMoon/Gomrey");
  assert.equal(rootPackage.name, "gomrey");
  assert.equal(rootLock.name, "gomrey");
  assert.equal(rootLock.packages[""].name, "gomrey");
  assert.equal(webPackage.name, "gomrey-web");
  assert.equal(webLock.name, "gomrey-web");
  assert.equal(webLock.packages[""].name, "gomrey-web");
  assert.equal(desktopPackage.name, "gomrey");
  assert.equal(desktopPackage.productName, "Gomrey");
  assert.equal(desktopPackage.repository, "https://github.com/TheHalfMoon/Gomrey");
  assert.equal(desktopLock.name, "gomrey");
  assert.equal(desktopLock.packages[""].name, "gomrey");
});

test("backend and agent-facing identity use Gomrey", async () => {
  const [pyproject, uvLock, mcpServer, banner, start, electronBuild, deployTemplate] = await Promise.all([
    read("servers/fastapi/pyproject.toml"),
    read("servers/fastapi/uv.lock"),
    read("servers/fastapi/mcp_server.py"),
    read("scripts/gomrey-terminal-banner.mjs"),
    read("start.js"),
    read("electron/build.js"),
    read(".do/deploy.template.yaml"),
  ]);

  assert.match(pyproject, /name = "gomrey-backend"/);
  assert.match(uvLock, /name = "gomrey-backend"/);
  assert.match(mcpServer, /# Gomrey MCP/);
  assert.match(mcpServer, /class GomreyTokenVerifier/);
  assert.doesNotMatch(mcpServer, /# Presenton MCP/);
  assert.match(banner, /https:\/\/github\.com\/TheHalfMoon\/Gomrey/);
  assert.match(banner, /Open Gomrey:/);
  assert.match(start, /gomrey-terminal-banner\.mjs/);
  assert.doesNotMatch(start, /presenton-terminal-banner\.mjs/);
  assert.match(electronBuild, /productName: "Gomrey"/);
  assert.match(electronBuild, /copyright: "Copyright 2026 TheHalfMoon"/);
  assert.match(deployTemplate, /name: gomrey/);
  assert.match(deployTemplate, /repository: thehalfmoon\/gomrey/);
  assert.match(deployTemplate, /tag: replace-with-qualified-release/);
  assert.doesNotMatch(deployTemplate, /presenton\/presenton/);
});

test("Gomrey desktop does not poll donor application updates by default", async () => {
  const updater = await read("electron/app/utils/update-checker.ts");

  assert.match(updater, /GOMREY_UPDATE_SERVER_URL/);
  assert.match(updater, /GOMREY_DOWNLOAD_URL/);
  assert.match(updater, /github\.com\/TheHalfMoon\/Gomrey\/releases/);
  assert.match(updater, /Automatic update checks are disabled until a Gomrey update endpoint is configured/);
  assert.doesNotMatch(updater, /raw\.githubusercontent\.com\/presenton\/presenton/);
  assert.doesNotMatch(updater, /https:\/\/presenton\.ai\/download/);
  assert.doesNotMatch(updater, /__presenton_/);
  assert.doesNotMatch(updater, /User-Agent.*Presenton/);
  assert.doesNotMatch(updater, /innerHTML/);
  assert.match(updater, /normalizeHttpUrl/);
  assert.ok(
    updater.indexOf("if (!VERSION_JSON_URL)") <
      updater.indexOf("updateCheckerStopped = false"),
  );
});

test("legacy compatibility and donor provenance are preserved intentionally", async () => {
  const identity = await readJson("product-identity.json");
  const [banner, exportSync, donorReadme] = await Promise.all([
    read("scripts/gomrey-terminal-banner.mjs"),
    read("scripts/sync-presentation-export.cjs"),
    read("docs/donors/presenton/UPSTREAM_README.md"),
  ]);

  assert.equal(identity.compatibility.legacyEnvPrefix, "PRESENTON_");
  assert.match(banner, /PRESENTON_HTTP_HOST_PORT/);
  assert.match(exportSync, /@presenton\/export-core/);
  assert.match(donorReadme, /Presenton/);
  for (const relativePath of identity.provenance.preservePaths) {
    await access(path.join(repoRoot, relativePath));
  }
});
