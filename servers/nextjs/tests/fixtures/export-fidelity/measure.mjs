#!/usr/bin/env node
/**
 * Measures the export round trip and writes the expectations file.
 *
 * The expectations are MEASURED, never guessed: this script runs the real
 * round trip over the committed decks and records what came back. The
 * harness (`servers/nextjs/tests/export-fidelity.test.mjs`) then checks that
 * a later run still produces the same facts.
 *
 * Regenerating the expectations is a deliberate act: it means the export
 * core's behaviour changed, and the diff has to be reviewed. The harness
 * fails with a behaviour-change notice when that happens.
 *
 * Usage:  node servers/nextjs/tests/fixtures/export-fidelity/measure.mjs
 */

import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

import {
  EXPORT_CORE_VERSION,
  loadExportCore,
  measureFacts,
  measurePackage,
  roundTrip,
} from "./roundtrip.mjs";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const DECKS = path.join(HERE, "decks");
const EXPECTATIONS = path.join(HERE, "expectations", "v1.json");

async function main() {
  const core = await loadExportCore();
  const workDirectory = await fs.mkdtemp(path.join(os.tmpdir(), "ef-measure-"));
  const files = (await fs.readdir(DECKS))
    .filter((name) => name.endsWith(".json"))
    .sort();

  const decks = {};
  for (const file of files) {
    const name = path.basename(file, ".json");
    const deck = JSON.parse(
      await fs.readFile(path.join(DECKS, file), "utf8"),
    );
    const { pptxPath, json } = await roundTrip(core, deck, workDirectory);
    const facts = measureFacts(pptxPath, json);
    facts.pptx_package = await measurePackage(pptxPath);
    decks[name] = facts;
    console.log(
      `measured ${name}: ${facts.layout_count} layout(s), ` +
        `${facts.element_types.length} element(s), ` +
        `${facts.text_runs.length} run(s)`,
    );
  }

  const expectations = {
    version: 1,
    export_core_version: EXPORT_CORE_VERSION,
    generated_by: "servers/nextjs/tests/fixtures/export-fidelity/measure.mjs",
    decks,
  };
  await fs.mkdir(path.dirname(EXPECTATIONS), { recursive: true });
  await fs.writeFile(
    EXPECTATIONS,
    `${JSON.stringify(expectations, null, 2)}\n`,
    "utf8",
  );
  console.log(
    `wrote ${path.relative(process.cwd(), EXPECTATIONS)} ` +
      `(${files.length} decks)`,
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
