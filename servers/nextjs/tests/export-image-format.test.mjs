import assert from "node:assert/strict";
import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";
import { pathToFileURL } from "node:url";

import { build } from "esbuild";

let exportFormats;
let temporaryDirectory;

test.before(async () => {
  temporaryDirectory = await mkdtemp(
    path.join(tmpdir(), "gomrey-export-formats-"),
  );
  const entryFile = path.join(temporaryDirectory, "entry.ts");
  const outputFile = path.join(temporaryDirectory, "bundle.mjs");
  await writeFile(
    entryFile,
    `export { BUNDLED_EXPORT_FORMATS, EXPORT_CONTENT_TYPES, isBundledExportFormat } from ${JSON.stringify(
      path.resolve("lib/export-formats.ts"),
    )};`,
  );
  await build({
    entryPoints: [entryFile],
    bundle: true,
    format: "esm",
    platform: "node",
    outfile: outputFile,
    logLevel: "silent",
  });
  exportFormats = await import(pathToFileURL(outputFile).href);
});

test.after(async () => {
  if (temporaryDirectory) {
    await rm(temporaryDirectory, { recursive: true, force: true });
  }
});

test("the export runtime accepts the image format", () => {
  assert.deepEqual([...exportFormats.BUNDLED_EXPORT_FORMATS], [
    "pdf",
    "pptx",
    "png",
  ]);
});

test("the format guard accepts every supported format", () => {
  for (const format of ["pdf", "pptx", "png"]) {
    assert.equal(exportFormats.isBundledExportFormat(format), true, format);
  }
});

test("the format guard rejects anything else", () => {
  for (const value of ["gif", "jpeg", "webp", "PDF", "", null, undefined, 7, {}]) {
    assert.equal(exportFormats.isBundledExportFormat(value), false, String(value));
  }
});

test("the download route serves image archives as a zip download", () => {
  assert.equal(exportFormats.EXPORT_CONTENT_TYPES[".zip"], "application/zip");
  assert.equal(
    exportFormats.EXPORT_CONTENT_TYPES[".pdf"],
    "application/pdf",
  );
  assert.equal(
    exportFormats.EXPORT_CONTENT_TYPES[".pptx"],
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
  );
});
