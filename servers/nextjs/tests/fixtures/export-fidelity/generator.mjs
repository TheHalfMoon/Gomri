#!/usr/bin/env node
/**
 * Generates the export-fidelity deck fixtures.
 *
 * Every deck here is SYNTHETIC: it contains no real user data, no donor
 * material and no credential. The decks are deterministic — there is no
 * random source and no timestamp — so regenerating them reproduces byte
 * identical files. See PROVENANCE.md.
 *
 * Usage:  node servers/nextjs/tests/fixtures/export-fidelity/generator.mjs
 */

import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const DECKS = path.join(HERE, "decks");

const FONT = (overrides = {}) => ({
  name: "Lato",
  size: 18,
  font_weight: 400,
  italic: false,
  color: "#111827",
  ...overrides,
});

const textbox = (position, paragraphs, extra = {}) => ({
  shape_type: "textbox",
  position,
  text_wrap: true,
  vertical_alignment: "top",
  paragraphs,
  ...extra,
});

/** 01 — text runs and fonts: the core "did the text survive" contract. */
function deckTextRunsAndFonts() {
  return {
    name: "01-text-runs-fonts",
    slides: [
      {
        background: { color: "#FFFFFF", opacity: 1 },
        shapes: [
          textbox(
            { left: 40, top: 40, width: 600, height: 80 },
            [
              {
                alignment: "left",
                line_height: 1.2,
                letter_spacing: 0.5,
                font: FONT(),
                text_runs: [
                  {
                    text: "Hello ",
                    font: FONT({ font_weight: 700 }),
                  },
                  {
                    text: "world",
                    font: FONT({
                      name: "Inter",
                      italic: true,
                      color: "#333333",
                      underline: true,
                    }),
                  },
                ],
              },
            ],
            {
              fill: { color: "#FFFFFF", opacity: 0 },
              stroke: { color: "#2563EB", thickness: 2, opacity: 1 },
            },
          ),
        ],
        note: "marker-note-01",
      },
    ],
  };
}

/** 02 — alignment, vertical alignment, bullets and line height. */
function deckAlignmentAndBullets() {
  return {
    name: "02-alignment-bullets",
    slides: [
      {
        background: { color: "#FFFFFF", opacity: 1 },
        shapes: [
          textbox(
            { left: 40, top: 40, width: 600, height: 200 },
            [
              {
                alignment: "center",
                vertical_alignment: "middle",
                line_height: 1.5,
                font: FONT(),
                text: "centered",
              },
              {
                alignment: "right",
                level: 1,
                bullet: { type: "number", color: "#2563EB" },
                font: FONT(),
                text: "numbered",
              },
              {
                alignment: "justify",
                bullet: { type: "default" },
                font: FONT(),
                text: "justified",
              },
            ],
          ),
        ],
      },
    ],
  };
}

/** 03 — a table with a header row and a body row. */
function deckTable() {
  return {
    name: "03-table",
    slides: [
      {
        background: { color: "#FFFFFF", opacity: 1 },
        shapes: [
          {
            shape_type: "table",
            position: { left: 40, top: 40, width: 600, height: 200 },
            rows: 2,
            cols: 2,
            row_heights: [40, 60],
            col_widths: [300, 300],
            cells: [
              { text: "Header A", bold: true, color: "#FFFFFF", fill: "#1F2937" },
              { text: "Header B", bold: true, color: "#FFFFFF", fill: "#1F2937" },
              { text: "Cell A1" },
              { text: "Cell B1" },
            ],
          },
        ],
      },
    ],
  };
}

/** 04 — vector geometry: an autoshape and a connector. */
function deckVectors() {
  return {
    name: "04-vectors",
    slides: [
      {
        background: { color: "#FFFFFF", opacity: 1 },
        shapes: [
          {
            shape_type: "autoshape",
            type: "ellipse",
            position: { left: 40, top: 40, width: 200, height: 120 },
            fill: { color: "#2563EB", opacity: 0.5 },
            stroke: { color: "#111827", thickness: 3, opacity: 1 },
            rotation: 15,
          },
          {
            shape_type: "connector",
            type: "straight",
            position: { left: 300, top: 100, width: 200, height: 0 },
            thickness: 2,
            color: "#111827",
            opacity: 1,
          },
        ],
      },
    ],
  };
}

/** 05 — a chart with categories, two datasets, a title and a legend. */
function deckChart() {
  return {
    name: "05-chart",
    slides: [
      {
        background: { color: "#FFFFFF", opacity: 1 },
        shapes: [
          {
            shape_type: "chart",
            type: "bar",
            position: { left: 40, top: 40, width: 600, height: 300 },
            categories: ["Q1", "Q2", "Q3"],
            datasets: [
              { name: "Series A", values: [10, 20, 30] },
              { name: "Series B", values: [5, 15, 25] },
            ],
            title: "Quarterly revenue",
            show_legend: true,
            x_axis_title: "Quarter",
            y_axis_title: "Revenue",
          },
        ],
      },
    ],
  };
}

/**
 * 06 — fills, strokes and a non-default background.
 *
 * The original design proposed a picture fixture here. The picture shape's
 * model is NOT documented in the export-core type declarations, and every
 * plausible construction throws `Cannot read properties of undefined (reading
 * 'path')`. Rather than pin a failure that may be our own misuse of an
 * undocumented shape, this deck covers the constructs that ARE constructible,
 * and the picture gap is recorded as an open item in the wave's evidence.
 */
function deckFillsAndBackground() {
  return {
    name: "06-fills-and-background",
    slides: [
      {
        background: { color: "#F3F4F6", opacity: 1 },
        shapes: [
          {
            shape_type: "autoshape",
            type: "rect",
            position: { left: 40, top: 40, width: 300, height: 200 },
            fill: { color: "#2563EB", opacity: 0.35 },
            stroke: { color: "#1F2937", thickness: 2, opacity: 0.8 },
          },
          textbox(
            { left: 40, top: 260, width: 300, height: 60 },
            [{ alignment: "center", font: FONT(), text: "filled shape" }],
            { fill: { color: "#FFFFFF", opacity: 0.6 } },
          ),
        ],
      },
    ],
  };
}

/** 07 — a speaker note. The note is written to the PPTX; the question is
 * whether it comes back on re-import. */
function deckSpeakerNotes() {
  return {
    name: "07-speaker-notes",
    slides: [
      {
        background: { color: "#FFFFFF", opacity: 1 },
        shapes: [
          textbox(
            { left: 40, top: 40, width: 600, height: 80 },
            [{ alignment: "left", font: FONT(), text: "slide body" }],
          ),
        ],
        note: "marker-note-07",
      },
    ],
  };
}

/** 08 — adversarial: the shapes most likely to break a round trip. */
function deckAdversarial() {
  const longText = "A".repeat(2000);
  return {
    name: "08-adversarial",
    slides: [
      {
        background: { color: "#FFFFFF", opacity: 1 },
        shapes: [
          textbox(
            { left: 40, top: 40, width: 40, height: 20 },
            [{ alignment: "left", font: FONT(), text: longText }],
          ),
          textbox(
            { left: 100, top: 100, width: 200, height: 40 },
            [
              {
                alignment: "left",
                font: FONT({ name: "NoSuchFontXYZ" }),
                text: "missing font",
              },
            ],
          ),
          textbox(
            { left: 100, top: 160, width: 200, height: 40 },
            [{ alignment: "right", font: FONT(), text: "مرحبا 🌍 mixed" }],
          ),
          {
            shape_type: "autoshape",
            type: "rect",
            position: { left: 0, top: 0, width: 0, height: 0 },
            fill: { color: "#FFFFFF", opacity: 1 },
            stroke: { color: "#000000", thickness: 1, opacity: 1 },
          },
        ],
      },
      { background: { color: "#FFFFFF", opacity: 1 }, shapes: [] },
    ],
  };
}

const DECKS_BY_NAME = {
  "01-text-runs-fonts": deckTextRunsAndFonts,
  "02-alignment-bullets": deckAlignmentAndBullets,
  "03-table": deckTable,
  "04-vectors": deckVectors,
  "05-chart": deckChart,
  "06-fills-and-background": deckFillsAndBackground,
  "07-speaker-notes": deckSpeakerNotes,
  "08-adversarial": deckAdversarial,
};

async function main() {
  await fs.mkdir(DECKS, { recursive: true });
  for (const [name, build] of Object.entries(DECKS_BY_NAME)) {
    const deck = build();
    const file = path.join(DECKS, `${name}.json`);
    await fs.writeFile(file, `${JSON.stringify(deck, null, 2)}\n`, "utf8");
    console.log(`wrote ${path.relative(process.cwd(), file)}`);
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
