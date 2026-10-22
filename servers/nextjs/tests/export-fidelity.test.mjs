import assert from "node:assert/strict";
import fs from "node:fs/promises";
import { readFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

/**
 * The export-fidelity harness (W12).
 *
 * A synthetic deck is exported to PPTX and re-imported to JSON, and the facts
 * that came back are checked against the measured expectations. The round
 * trip is browser-free — `pptx-from-json` then `pptx-to-json` — so it can run
 * on CI without Chromium, ImageMagick or LibreOffice.
 *
 * The expectations in `expectations/v1.json` are MEASURED, not guessed: they
 * were produced by `measure.mjs` running the same round trip. If the export
 * core's behaviour changes, this harness fails with a behaviour-change notice
 * rather than a silent regression. Regenerating the expectations is a
 * deliberate act that has to be reviewed.
 *
 * What is NOT asserted, and why:
 *
 * - **The PPTX bytes.** Two runs of the same deck differ: the archive carries
 *   a UUID file name and wall-clock ZIP timestamps. The re-imported JSON and
 *   the package part list ARE deterministic, and those are what is pinned.
 * - **Rendered pixels.** The production export path is browser-bound; this
 *   harness is the deterministic tier beneath it. Pixel-level fidelity is a
 *   separate concern and is not claimed here.
 *
 * The runtime is not committed: `presentation-export/` is gitignored and is
 * materialised by `npm run sync:presentation-export`. On a checkout without
 * it, every case reports an explicit skip with a reason. A skip is never
 * reported as a pass.
 */

const HERE = path.dirname(fileURLToPath(import.meta.url));
const FIXTURES = path.join(HERE, "fixtures", "export-fidelity");
const DECKS = path.join(FIXTURES, "decks");
const EXPECTATIONS = path.join(FIXTURES, "expectations", "v1.json");

const {
  EXPORT_CORE_VERSION,
  ExportFidelityUnavailable,
  loadExportCore,
  measureFacts,
  measurePackage,
  roundTrip,
} = await import(path.join(FIXTURES, "roundtrip.mjs"));

// The expectations are read synchronously at module scope: the deck list is
// needed to register the cases, and registration happens before any hook runs.
const expectations = JSON.parse(readFileSync(EXPECTATIONS, "utf8"));

let core = null;
let unavailable = null;
let workDirectory = null;

test.before(async () => {
  workDirectory = await fs.mkdtemp(path.join(os.tmpdir(), "ef-harness-"));
  try {
    core = await loadExportCore();
  } catch (error) {
    unavailable = error;
  }
});

test.after(async () => {
  if (workDirectory) {
    await fs.rm(workDirectory, { recursive: true, force: true });
  }
});

/**
 * Run one deck and return its measured facts, or skip the case with the
 * precise reason. A skip is never a pass.
 */
async function measureDeck(name) {
  if (unavailable) {
    return { skipped: unavailable.reason, detail: unavailable.message };
  }
  const deck = JSON.parse(
    await fs.readFile(path.join(DECKS, `${name}.json`), "utf8"),
  );
  const { pptxPath, json } = await roundTrip(core, deck, workDirectory);
  const facts = measureFacts(pptxPath, json);
  facts.pptx_package = await measurePackage(pptxPath);
  return { facts };
}

function deckNames() {
  return Object.keys(expectations.decks);
}

test("the expectations are pinned to an export core version", () => {
  assert.equal(expectations.export_core_version, EXPORT_CORE_VERSION);
  assert.equal(expectations.version, 1);
});

test("the expectations cover every committed deck", async () => {
  const files = (await fs.readdir(DECKS))
    .filter((name) => name.endsWith(".json"))
    .map((name) => path.basename(name, ".json"))
    .sort();
  assert.deepEqual(files, deckNames().sort());
});

for (const name of deckNames()) {
  test(`the round trip preserves what it is expected to preserve: ${name}`, async (t) => {
    const measured = await measureDeck(name);
    if (measured.skipped) {
      // A real skip, with its reason. Never reported as a pass.
      t.skip(measured.detail);
      return;
    }
    const expected = expectations.decks[name];
    const actual = measured.facts;

    // The element sequence is the shape of the slide.
    assert.deepEqual(
      actual.element_types,
      expected.element_types,
      "the element type sequence changed",
    );
    // The text that was written must come back.
    assert.deepEqual(
      actual.text_runs,
      expected.text_runs,
      "the run text changed",
    );
    // The font attributes that were written must come back.
    assert.deepEqual(
      actual.run_families,
      expected.run_families,
      "the run font attributes changed",
    );
    // The geometry must come back exactly.
    assert.deepEqual(
      actual.positions,
      expected.positions,
      "the element geometry changed",
    );
    assert.deepEqual(
      actual.alignments,
      expected.alignments,
      "the paragraph alignment changed",
    );
    assert.deepEqual(
      actual.vertical_alignments,
      expected.vertical_alignments,
      "the vertical alignment changed",
    );
    // The package contents must come back.
    assert.deepEqual(
      actual.pptx_package,
      expected.pptx_package,
      "the PPTX package contents changed",
    );
  });
}

test("a speaker note is written to the PPTX but is not re-imported", async (t) => {
  const measured = await measureDeck("07-speaker-notes");
  if (measured.skipped) { t.skip(measured.detail); return; }
  const facts = measured.facts;

  // The note reached the archive.
  assert.equal(
    facts.pptx_package.has_notes_slide,
    true,
    "the notes slide is missing from the package",
  );
  // It did not come back. This is a real, currently-undocumented fidelity
  // gap; it is pinned so that closing it produces a visible notice instead of
  // a silent change.
  assert.equal(
    facts.has_notes_key,
    false,
    "the re-imported JSON now carries a notes key: the gap has been closed",
  );
});

test("bullets are inlined as literal text rather than kept as bullets", async (t) => {
  const measured = await measureDeck("02-alignment-bullets");
  if (measured.skipped) { t.skip(measured.detail); return; }
  const joined = measured.facts.text_runs.join("");

  assert.match(joined, /1\. numbered/);
  assert.match(joined, /• justified/);
});

test("right-to-left and emoji content survives the round trip", async (t) => {
  const measured = await measureDeck("08-adversarial");
  if (measured.skipped) { t.skip(measured.detail); return; }

  assert.ok(
    measured.facts.text_runs.some((text) => text.includes("مرحبا 🌍 mixed")),
    "the mixed right-to-left and emoji run did not survive",
  );
});

test("a chart keeps its package part and a table keeps its element", async (t) => {
  const chart = await measureDeck("05-chart");
  if (chart.skipped) { t.skip(chart.detail); return; }
  assert.equal(chart.facts.pptx_package.has_chart, true);
  assert.ok(chart.facts.element_types.includes("chart"));

  const table = await measureDeck("03-table");
  if (table.skipped) { t.skip(table.detail); return; }
  assert.ok(table.facts.element_types.includes("table"));
});

test("the harness reports an explicit reason when the runtime is absent", async () => {
  if (!unavailable) return;
  assert.ok(
    unavailable instanceof ExportFidelityUnavailable,
    "an unavailable runtime must be a typed, explained condition",
  );
  assert.match(
    unavailable.reason,
    /^EF-(RUNTIME-ABSENT|NODE-VERSION)$/,
    "the reason must name the condition",
  );
});
