import assert from "node:assert/strict";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";
import { pathToFileURL } from "node:url";

import { build } from "esbuild";

/**
 * The Arabic / RTL qualification suite (W13) — the TypeScript half.
 *
 * It reads the ONE shared contract fixture that the Python suite also reads
 * (`servers/fastapi/tests/qualification/arabic_rtl_contract.json`), so the
 * two classifiers are checked against one declaration rather than two copies.
 *
 * Evidence class: every assertion here is `model`- or `markup`-level. There is
 * no headless browser in this test environment, so nothing here claims a
 * rendered-pixel property, and nothing here claims anything about the exported
 * PPTX, whose fidelity belongs to the export-fidelity wave.
 */

const CONTRACT_PATH = path.resolve(
  "../fastapi/tests/qualification/arabic_rtl_contract.json",
);

let renderer;
let direction;
let cssText;
let contract;
let temporaryDirectory;

test.before(async () => {
  contract = JSON.parse(await readFile(CONTRACT_PATH, "utf8"));
  temporaryDirectory = await mkdtemp(
    path.join(tmpdir(), "presenton-arabic-rtl-"),
  );
  const outputFile = path.join(temporaryDirectory, "bundle.mjs");

  const entry = [
    `export * from ${JSON.stringify(path.resolve("lib/template-v2-json-to-html.ts"))};`,
    `export * from ${JSON.stringify(
      path.resolve("components/slide-editor/text/text-direction.ts"),
    )};`,
    `export * from ${JSON.stringify(
      path.resolve("components/slide-editor/text/css-text.ts"),
    )};`,
  ].join("\n");

  await build({
    stdin: { contents: entry, resolveDir: process.cwd(), loader: "ts" },
    outfile: outputFile,
    bundle: true,
    platform: "node",
    format: "esm",
    tsconfig: path.resolve("tsconfig.json"),
    logLevel: "silent",
  });

  const bundle = await import(
    `${pathToFileURL(outputFile).href}?cache=${Date.now()}`
  );
  renderer = bundle;
  direction = bundle;
  cssText = bundle;
});

test.after(async () => {
  if (temporaryDirectory) {
    await rm(temporaryDirectory, { recursive: true, force: true });
  }
});

function cases() {
  return contract.cases;
}

function caseById(id) {
  const found = cases().find((candidate) => candidate.id === id);
  assert.ok(found, `the contract must declare the ${id} case`);
  return found;
}

function renderUi(elements) {
  return renderer.templateV2UiToHtml({
    background: "#FFFFFF",
    elements,
    components: [],
  });
}

function textElement(text, extra = {}) {
  return {
    type: "text",
    position: { x: 40, y: 40 },
    size: { width: 600, height: 200 },
    runs: [{ text }],
    ...extra,
  };
}

// --------------------------------------------------------------------------- //
// The classifier agrees with the contract, in the same way Python does
// --------------------------------------------------------------------------- //

test("the script profile matches the contract for every case", () => {
  for (const contractCase of cases()) {
    const profile = direction.scriptProfile(contractCase.text);
    assert.equal(
      profile.direction,
      contractCase.expected_script_direction,
      contractCase.id,
    );
  }
});

test("the base direction matches the contract for every case", () => {
  for (const contractCase of cases()) {
    assert.equal(
      direction.resolveBaseDirection(contractCase.text),
      contractCase.expected_base_direction,
      contractCase.id,
    );
  }
});

test("the declared script ranges match the contract", () => {
  assert.deepEqual(direction.SCRIPT_RANGES, contract.script_ranges);
});

test("the base direction is resolved from the first strong character", () => {
  assert.equal(direction.resolveBaseDirection("2026"), "ltr");
  assert.equal(direction.resolveBaseDirection("   "), "ltr");
  assert.equal(direction.resolveBaseDirection("2026 مرحبا"), "rtl");
  assert.equal(direction.resolveBaseDirection("Report مرحبا"), "ltr");
});

// --------------------------------------------------------------------------- //
// Markup: what the renderer emits
// --------------------------------------------------------------------------- //

test("arabic-only: the element declares its base direction and an Arabic face", () => {
  const contractCase = caseById("arabic-only");
  const html = renderUi([textElement(contractCase.text)]);

  assert.match(html, /dir="auto"/);
  assert.match(html, /unicode-bidi:plaintext/);
  // The font chain names an Arabic-capable family.
  assert.match(html, /Noto Naskh Arabic|Noto Sans Arabic/);
  // The text is emitted verbatim.
  assert.ok(html.includes(contractCase.text));
});

test("english-only: the design font still leads and the text is verbatim", () => {
  const contractCase = caseById("english-only");
  const html = renderUi([
    textElement(contractCase.text, { font: { family: "Lato", size: 18 } }),
  ]);

  // The design font still comes first, so left-to-right rendering is
  // unchanged by the fallback chain.
  assert.match(html, /font-family:'Lato',/);
  // The portable Arabic families do NOT lead for left-to-right content.
  assert.doesNotMatch(html, /font-family:'Arial', 'Tahoma'/);
  assert.ok(html.includes(contractCase.text));
});

test("mixed-arabic-english: one container, no inner dir, no run splitting", () => {
  const contractCase = caseById("mixed-arabic-english");
  const html = renderUi([textElement(contractCase.text)]);

  // A single declaration of direction: the container. An inner dir would
  // create a separate bidi context and move the run.
  const dirAttributes = html.match(/dir="auto"/g) ?? [];
  assert.equal(dirAttributes.length, 1, "exactly one direction declaration");
  assert.doesNotMatch(html, /dir="(rtl|ltr)"/);

  // No run splitting: the run count is unchanged.
  const runCount = (html.match(/<span/g) ?? []).length;
  assert.ok(runCount <= 3, `unexpected run count: ${runCount}`);

  // The logical order of the source is preserved verbatim.
  assert.ok(html.includes(contractCase.text));
});

test("arabic-with-latin-numerals: both numeral systems survive", () => {
  const contractCase = caseById("arabic-with-latin-numerals");
  const html = renderUi([textElement(contractCase.text)]);

  assert.ok(html.includes("2026"), "western digits survive");
  assert.ok(html.includes("٢٥٠٠"), "arabic-indic digits survive");
  assert.ok(html.includes(contractCase.text));
});

test("arabic-in-table-cell: the cell declares its own base direction", () => {
  const contractCase = caseById("arabic-in-table-cell");
  const html = renderUi([
    {
      type: "table",
      position: { x: 40, y: 40 },
      size: { width: 600, height: 200 },
      rows: [[contractCase.text, "Revenue"]],
    },
  ]);

  assert.match(html, /dir="auto"/);
  assert.match(html, /unicode-bidi:plaintext/);
  assert.ok(html.includes(contractCase.text));
});

test("arabic-plus-english-in-one-table-row: each cell resolves its own direction", () => {
  const contractCase = caseById("arabic-plus-english-in-one-table-row");
  const html = renderUi([
    {
      type: "table",
      position: { x: 40, y: 40 },
      size: { width: 600, height: 200 },
      rows: [[contractCase.text, "Revenue"]],
    },
  ]);

  // Both cells declare a direction; neither is forced to the other's.
  const dirAttributes = html.match(/dir="auto"/g) ?? [];
  assert.ok(dirAttributes.length >= 2, "each cell declares its direction");
  assert.ok(html.includes(contractCase.text));
  assert.ok(html.includes("Revenue"));
});

test("arabic-in-chart-label: the label text survives verbatim", () => {
  const contractCase = caseById("arabic-in-chart-label");
  const html = renderUi([
    {
      type: "chart",
      position: { x: 40, y: 40 },
      size: { width: 600, height: 300 },
      chart_type: "bar",
      series: [{ name: contractCase.text, values: [1, 2, 3] }],
    },
  ]);

  assert.ok(html.includes(contractCase.text));
  // Chart labels are drawn on a canvas: the rendered order is NOT asserted.
});

test("arabic-in-vector-shape: the text is classified, and the surface is not claimed", () => {
  const contractCase = caseById("arabic-in-vector-shape");
  const html = renderUi([
    {
      type: "vector",
      shape: "rect",
      position: { x: 40, y: 40 },
      size: { width: 300, height: 120 },
      text: contractCase.text,
      fill: { color: "#FFFFFF" },
    },
  ]);

  // The HTML export surface renders a vector's geometry, not its text. The
  // vector's text is laid out by the LTR segment engine in the canvas, where
  // Arabic word order is wrong. This is a pre-existing surface gap, recorded
  // rather than asserted away.
  assert.ok(html);
  assert.doesNotMatch(html, /dir="auto"/);
  // The text itself is classified correctly, which is the model-level claim.
  assert.equal(
    direction.resolveBaseDirection(contractCase.text),
    contractCase.expected_base_direction,
  );
});

test("arabic-in-speaker-note: the note is classified, and the surface is not claimed", () => {
  const contractCase = caseById("arabic-in-speaker-note");
  const html = renderUi([
    textElement("مرحبا", { __speaker_note__: contractCase.text }),
  ]);

  // A speaker note is a separate slide field, not part of the rendered
  // slide, so the HTML surface neither emits nor direction-declares it.
  assert.ok(html);
  assert.ok(
    !html.includes(contractCase.text),
    "the speaker note is not part of the rendered slide",
  );
  // The rendered text element still declares its own direction.
  assert.match(html, /dir="auto"/);
  assert.equal(
    direction.resolveBaseDirection(contractCase.text),
    contractCase.expected_base_direction,
  );
});

test("long-arabic-with-diacritics: diacritics survive and no bidi marks are injected", () => {
  const contractCase = caseById("long-arabic-with-diacritics");
  const html = renderUi([textElement(contractCase.text)]);

  assert.ok(html.includes(contractCase.text));
  // The renderer must not inject bidi control characters; the browser's own
  // algorithm owns the reordering.
  assert.doesNotMatch(html, /[\u202A-\u202E\u2066-\u2069]/);
});

test("the logical alignment replaces the physical one", () => {
  const html = renderUi([
    textElement("مرحبا", { alignment: { horizontal: "left" } }),
  ]);

  // `left` becomes `start`, so the element's own resolved direction decides.
  assert.match(html, /text-align:start/);
  assert.doesNotMatch(html, /text-align:left/);
});

// --------------------------------------------------------------------------- //
// The shared font stack
// --------------------------------------------------------------------------- //

test("the font stack names an Arabic family after the design font", () => {
  const stack = cssText.cssFontFamilyStack("Lato");

  assert.match(stack, /^'Lato',/);
  assert.match(stack, /'Noto Naskh Arabic'/);
  assert.match(stack, /'Noto Sans Arabic'/);
});

test("the font stack leads with the portable families for right-to-left content", () => {
  const stack = cssText.cssFontFamilyStack("Lato", { rtl: true });

  assert.match(stack, /^'Arial', 'Tahoma',/);
  assert.match(stack, /'Noto Naskh Arabic'/);
  assert.match(stack, /'Lato'/);
});

test("the contract declares what the suite does not measure", () => {
  assert.ok(contract.evidence_classes.rendered);
  for (const contractCase of cases()) {
    assert.ok(
      ["model", "markup", "model+markup"].includes(contractCase.evidence_class),
      contractCase.id,
    );
  }
});
