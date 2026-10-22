/**
 * The export round trip, and the facts measured from it.
 *
 * The round trip is browser-free: `pptx-from-json` builds a PPTX from a
 * synthetic deck and `pptx-to-json` reads it back. No Chromium, no
 * ImageMagick, no LibreOffice — so it can run on CI.
 *
 * Everything here is deterministic. The PPTX bytes are NOT deterministic (the
 * archive carries a UUID file name and wall-clock ZIP timestamps), so the
 * harness pins the **re-imported JSON** and the **PPTX package contents**,
 * never the PPTX bytes.
 */

import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import zlib from "node:zlib";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(HERE, "../../../../..");

export const EXPORT_CORE_VERSION = "1.0.34";
export const MINIMUM_NODE = "22.12.0";

export class ExportFidelityUnavailable extends Error {
  constructor(reason, detail) {
    super(`${reason}${detail ? `: ${detail}` : ""}`);
    this.name = "ExportFidelityUnavailable";
    this.reason = reason;
  }
}

/** Whether the current Node can run the export core. */
export function nodeVersionSatisfies() {
  const [major, minor] = process.versions.node.split(".").map(Number);
  return major > 22 || (major === 22 && minor >= 12);
}

/**
 * Resolve the export core, or explain precisely why it is unavailable.
 *
 * `presentation-export/` is gitignored: it is materialised by
 * `npm run sync:presentation-export`, which fetches a public release
 * tarball. A fresh checkout does not have it.
 */
export async function loadExportCore() {
  if (!nodeVersionSatisfies()) {
    throw new ExportFidelityUnavailable(
      "EF-NODE-VERSION",
      `the export core requires Node >= ${MINIMUM_NODE}, this is Node ${process.versions.node}`,
    );
  }
  const entry = path.join(
    REPO_ROOT,
    "presentation-export",
    "node_modules",
    "@presenton",
    "export-core",
    "dist",
    "index.js",
  );
  try {
    await fs.access(entry);
  } catch {
    throw new ExportFidelityUnavailable(
      "EF-RUNTIME-ABSENT",
      "run `npm run sync:presentation-export` to materialise the export runtime",
    );
  }
  return import(entry);
}

/** Run one deck through the round trip and return what came back. */
export async function roundTrip(core, deck, workDirectory) {
  const outputDirectory = await fs.mkdtemp(
    path.join(workDirectory, "ef-run-"),
  );
  const made = await core.runTask(
    { type: "pptx-from-json", data: deck },
    { outputDirectory },
  );
  const pptxPath = made.filePath ?? made.path ?? made.filePaths?.[0];
  if (!pptxPath) {
    throw new ExportFidelityUnavailable(
      "EF-NO-PPTX",
      "the export core produced no file for this deck",
    );
  }
  const back = await core.runTask(
    { type: "pptx-to-json", pptx_path: pptxPath },
    { outputDirectory },
  );
  const jsonPath = back.filePath ?? back.path ?? back.filePaths?.[0];
  const json = JSON.parse(await fs.readFile(jsonPath, "utf8"));
  return { pptxPath, json };
}

/**
 * Read one entry out of a ZIP archive.
 *
 * The export core's PPTX is a normal ZIP, and Node has no built-in reader
 * for one, so this walks the central directory and inflates the entry with
 * `zlib.inflateRawSync`. Dependency-free and deterministic.
 */
export async function readZipEntry(zipPath, entryName) {
  const buffer = await fs.readFile(zipPath);
  const endSignature = 0x06054b50;
  let end = -1;
  for (let i = buffer.length - 22; i >= 0; i -= 1) {
    if (buffer.readUInt32LE(i) === endSignature) {
      end = i;
      break;
    }
  }
  if (end < 0) {
    throw new ExportFidelityUnavailable("EF-NOT-A-ZIP", zipPath);
  }
  const entryCount = buffer.readUInt16LE(end + 10);
  let offset = buffer.readUInt32LE(end + 16);
  for (let index = 0; index < entryCount; index += 1) {
    if (buffer.readUInt32LE(offset) !== 0x02014b50) {
      throw new ExportFidelityUnavailable("EF-BAD-CENTRAL-DIRECTORY", zipPath);
    }
    const method = buffer.readUInt16LE(offset + 10);
    const compressedSize = buffer.readUInt32LE(offset + 20);
    const nameLength = buffer.readUInt16LE(offset + 28);
    const extraLength = buffer.readUInt16LE(offset + 30);
    const commentLength = buffer.readUInt16LE(offset + 32);
    const localOffset = buffer.readUInt32LE(offset + 42);
    const name = buffer.toString("utf8", offset + 46, offset + 46 + nameLength);
    if (name === entryName) {
      const localNameLength = buffer.readUInt16LE(localOffset + 26);
      const localExtraLength = buffer.readUInt16LE(localOffset + 28);
      const dataStart = localOffset + 30 + localNameLength + localExtraLength;
      const data = buffer.subarray(
        dataStart,
        dataStart + compressedSize,
      );
      return method === 0 ? data : zlib.inflateRawSync(data);
    }
    offset += 46 + nameLength + extraLength + commentLength;
  }
  return null;
}

/** Every entry name in the archive. */
export async function listZipEntries(zipPath) {
  const buffer = await fs.readFile(zipPath);
  const endSignature = 0x06054b50;
  let end = -1;
  for (let i = buffer.length - 22; i >= 0; i -= 1) {
    if (buffer.readUInt32LE(i) === endSignature) {
      end = i;
      break;
    }
  }
  if (end < 0) return [];
  const entryCount = buffer.readUInt16LE(end + 10);
  let offset = buffer.readUInt32LE(end + 16);
  const names = [];
  for (let index = 0; index < entryCount; index += 1) {
    const nameLength = buffer.readUInt16LE(offset + 28);
    const extraLength = buffer.readUInt16LE(offset + 30);
    const commentLength = buffer.readUInt16LE(offset + 32);
    const name = buffer.toString(
      "utf8",
      offset + 46,
      offset + 46 + nameLength,
    );
    names.push(name);
    offset += 46 + nameLength + extraLength + commentLength;
  }
  return names.sort();
}

/**
 * The facts the harness pins, extracted from a round trip.
 *
 * These are *measured*, not asserted in advance: `measure.mjs` produces them
 * by running the round trip, and the harness then checks that a later run
 * still produces them.
 */
export function measureFacts(pptxPath, json) {
  const layouts = json.layouts ?? [];
  const elements = layouts.flatMap((layout) => layout.elements ?? []);
  const textElements = elements.filter((element) => element.type === "text");

  const facts = {
    layout_count: layouts.length,
    element_types: elements.map((element) => element.type),
    text_runs: textElements.flatMap((element) =>
      (element.runs ?? []).map((run) => run.text),
    ),
    run_families: textElements.flatMap((element) =>
      (element.runs ?? []).map((run) => ({
        family: run.font?.family ?? null,
        bold: run.font?.bold ?? null,
        italic: run.font?.italic ?? null,
        color: run.font?.color ?? null,
        size: run.font?.size ?? null,
      })),
    ),
    positions: elements
      .filter((element) => element.position && element.size)
      .map((element) => ({
        x: element.position.x,
        y: element.position.y,
        width: element.size.width,
        height: element.size.height,
      })),
    alignments: textElements.map(
      (element) => element.alignment?.horizontal ?? null,
    ),
    vertical_alignments: textElements.map(
      (element) => element.alignment?.vertical ?? null,
    ),
    decorative: textElements.map((element) => element.decorative ?? null),
    has_notes_key: layouts.some((layout) => "notes" in layout),
  };
  facts.pptx_entries = null; // filled in by the caller, which can read the zip
  return facts;
}

/** The package part names the harness cares about. */
export async function measurePackage(pptxPath) {
  const entries = await listZipEntries(pptxPath);
  return {
    has_notes_slide: entries.some((name) =>
      name.startsWith("ppt/notesSlides/notesSlide"),
    ),
    has_chart: entries.some((name) => name.startsWith("ppt/charts/chart")),
    has_media: entries.some((name) => name.startsWith("ppt/media/")),
    slide_count: entries.filter((name) =>
      /^ppt\/slides\/slide\d+\.xml$/.test(name),
    ).length,
  };
}
