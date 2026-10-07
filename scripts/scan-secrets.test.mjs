import assert from "node:assert/strict";
import test from "node:test";
import { isExcluded, scanText } from "./scan-secrets.mjs";

test("secret scanner flags credential-like material", () => {
  const findings = scanText("config/example.env", "OPENAI_KEY=sk-abcdefghijklmnopqrstuvw\n");
  assert.equal(findings.length, 1);
  assert.equal(findings[0].rule, "openai-key");

  const keyBlock = scanText("notes.txt", "-----BEGIN RSA PRIVATE KEY-----\nabc");
  assert.equal(keyBlock.length, 1);
});

test("secret scanner ignores placeholders and excluded provenance paths", () => {
  assert.deepEqual(scanText("x", "OPENAI_KEY=replace-with-qualified-release\n"), []);
  assert.deepEqual(scanText("x", "EXAMPLE: sk-abcdefghijklmnopqrstuvw\n"), []);
  assert.ok(isExcluded("docs/donors/presenton/NOTICE.md"));
  assert.ok(isExcluded("docs/evidence/P01_PRESENTON_IMPORT.md"));
  assert.ok(isExcluded("package-lock.json"));
  assert.ok(isExcluded("servers/fastapi/uv.lock"));
  assert.ok(!isExcluded("config/release-baseline.json"));
});
