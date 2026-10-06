const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");
const { candidateCleanupPaths } = require("./cleanup-installed-app-cache.cjs");

const {
  inspectPersistedAppState,
  resolveUserDataDirectory,
} = require("../app_dist/utils/app-path-migration.js");

function withTempRoot(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "gomrey-path-migration-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  return {
    canonicalDir: path.join(root, "Gomrey"),
    legacyDir: path.join(root, "Presenton Open Source"),
  };
}

function writeFile(filePath, content = "state") {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, content);
}

test("fresh installs choose the canonical Gomrey directory", (t) => {
  const paths = withTempRoot(t);
  const result = resolveUserDataDirectory(paths);
  assert.equal(result.source, "fresh");
  assert.equal(result.directory, path.resolve(paths.canonicalDir));
});

test("legacy strong state wins over canonical config-only state", (t) => {
  const paths = withTempRoot(t);
  writeFile(path.join(paths.canonicalDir, "userConfig.json"), "{}\n");
  writeFile(path.join(paths.legacyDir, "fastapi.db"), "sqlite-state");

  const result = resolveUserDataDirectory(paths);
  assert.equal(result.source, "legacy");
  assert.equal(result.directory, path.resolve(paths.legacyDir));
  assert.equal(result.legacyState.level, "strong");
});

test("canonical strong state wins over legacy config-only state", (t) => {
  const paths = withTempRoot(t);
  writeFile(path.join(paths.canonicalDir, "fastapi.db"), "sqlite-state");
  writeFile(path.join(paths.legacyDir, "userConfig.json"), "{}\n");

  const result = resolveUserDataDirectory(paths);
  assert.equal(result.source, "canonical");
  assert.equal(result.directory, path.resolve(paths.canonicalDir));
});

test("non-empty app-owned directories count as strong state", (t) => {
  const paths = withTempRoot(t);
  writeFile(path.join(paths.legacyDir, "uploads", "source.pdf"), "pdf");
  assert.deepEqual(inspectPersistedAppState(paths.legacyDir), {
    level: "strong",
    markers: ["uploads"],
  });
});

test("empty app-owned directories do not create false persisted state", (t) => {
  const paths = withTempRoot(t);
  fs.mkdirSync(path.join(paths.legacyDir, "uploads"), { recursive: true });
  assert.deepEqual(inspectPersistedAppState(paths.legacyDir), {
    level: "none",
    markers: [],
  });
});

test("conflicting strong states fail closed instead of merging", (t) => {
  const paths = withTempRoot(t);
  writeFile(path.join(paths.canonicalDir, "fastapi.db"), "canonical");
  writeFile(path.join(paths.legacyDir, "fastapi.db"), "legacy");

  assert.throws(
    () => resolveUserDataDirectory(paths),
    /GOMREY_USER_DATA_DIRECTORY/,
  );
});

test("conflicting config-only states also fail closed", (t) => {
  const paths = withTempRoot(t);
  writeFile(path.join(paths.canonicalDir, "userConfig.json"), '{"a":1}');
  writeFile(path.join(paths.legacyDir, "userConfig.json"), '{"b":2}');

  assert.throws(
    () => resolveUserDataDirectory(paths),
    /will not merge or delete either directory automatically/,
  );
});

test("explicit override wins without mutating either detected state", (t) => {
  const paths = withTempRoot(t);
  const overrideDir = path.join(path.dirname(paths.canonicalDir), "chosen");
  writeFile(path.join(paths.canonicalDir, "fastapi.db"), "canonical");
  writeFile(path.join(paths.legacyDir, "fastapi.db"), "legacy");

  const result = resolveUserDataDirectory({ ...paths, overrideDir });
  assert.equal(result.source, "override");
  assert.equal(result.directory, path.resolve(overrideDir));
  assert.equal(result.canonicalState.level, "strong");
  assert.equal(result.legacyState.level, "strong");
});

test("config-only legacy state remains discoverable", (t) => {
  const paths = withTempRoot(t);
  writeFile(path.join(paths.legacyDir, "userConfig.json"), '{"provider":"local"}');
  const result = resolveUserDataDirectory(paths);
  assert.equal(result.source, "legacy");
});

test("config-only canonical state remains authoritative when legacy is empty", (t) => {
  const paths = withTempRoot(t);
  writeFile(path.join(paths.canonicalDir, "userConfig.json"), '{"provider":"local"}');
  const result = resolveUserDataDirectory(paths);
  assert.equal(result.source, "canonical");
});

test("installed-app cleanup candidates are limited to ephemeral paths", () => {
  const forbiddenBasenames = new Set([
    "userConfig.json",
    "fastapi.db",
    "exports",
    "uploads",
    "templates",
    "fonts",
    "images",
    "app_data",
    "mem0",
  ]);
  for (const targetPath of candidateCleanupPaths()) {
    assert.equal(
      forbiddenBasenames.has(path.basename(targetPath)),
      false,
      "persistent path must never be a cleanup target: " + targetPath,
    );
  }
});
