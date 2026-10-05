import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { test } from "node:test";

const source = await readFile(new URL("../start.js", import.meta.url), "utf8");

test("startup persists user configuration with owner-only POSIX modes", () => {
  assert.match(source, /openSync\(tempPath, "wx", 0o600\)/);
  assert.match(source, /chmodBestEffort\(userConfigPath, 0o600\)/);
  assert.match(source, /chmodBestEffort\(userConfigBackupPath, 0o600\)/);
  assert.doesNotMatch(source, /chmodBestEffort\(userConfig(?:Backup)?Path, 0o644\)/);
});

test("startup hardens an existing primary before copying its backup", () => {
  const hardenIndex = source.indexOf("chmodBestEffort(userConfigPath, 0o600);");
  const copyIndex = source.indexOf("copyFileSync(userConfigPath, userConfigBackupPath);");

  assert.notEqual(hardenIndex, -1);
  assert.notEqual(copyIndex, -1);
  assert.ok(hardenIndex < copyIndex);
});
