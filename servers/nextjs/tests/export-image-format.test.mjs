import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import test from "node:test";

const exportRoutePath = path.resolve("app/api/export-presentation/route.ts");
const bundledExportLibPath = path.resolve("lib/run-bundled-presentation-export.ts");
const exportFileRoutePath = path.resolve("app/api/export-presentation/file/route.ts");

test("the export route accepts the image formats", async () => {
  const source = await readFile(exportRoutePath, "utf8");

  assert.match(source, /value === "png"/);
  assert.match(source, /value === "pptx"/);
  assert.match(source, /value === "pdf"/);
});

test("the bundled export runtime declares the image format", async () => {
  const source = await readFile(bundledExportLibPath, "utf8");

  assert.match(
    source,
    /BundledPresentationExportFormat\s*=\s*"pdf"\s*\|\s*"pptx"\s*\|\s*"png"/,
  );
});

test("the download route serves image archives as zip", async () => {
  const source = await readFile(exportFileRoutePath, "utf8");

  assert.match(source, /"\.zip":\s*"application\/zip"/);
});
