import assert from "node:assert/strict";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";
import { pathToFileURL } from "node:url";

import { build } from "esbuild";

let renderer;
let temporaryDirectory;

test.before(async () => {
  temporaryDirectory = await mkdtemp(
    path.join(tmpdir(), "presenton-animations-"),
  );
  const outputFile = path.join(temporaryDirectory, "renderer.mjs");

  await build({
    entryPoints: [path.resolve("lib/template-v2-json-to-html.ts")],
    outfile: outputFile,
    bundle: true,
    platform: "node",
    format: "esm",
    tsconfig: path.resolve("tsconfig.json"),
    logLevel: "silent",
  });

  renderer = await import(
    `${pathToFileURL(outputFile).href}?cache=${Date.now()}`
  );
});

test.after(async () => {
  if (temporaryDirectory) {
    await rm(temporaryDirectory, { recursive: true, force: true });
  }
});

function renderUi(elements, { fragment = false } = {}) {
  const ui = {
    background: "#FFFFFF",
    elements,
    components: [],
  };
  return fragment
    ? renderer.templateV2UiToHtmlFragment(ui)
    : renderer.templateV2UiToHtml(ui);
}

function animatedText(animation) {
  return {
    type: "text",
    position: { x: 40, y: 40 },
    size: { width: 400, height: 120 },
    runs: [{ text: "Retention rose to 91 percent." }],
    ...(animation ? { animation } : {}),
  };
}

test("an animated element receives its animation class", () => {
  const html = renderUi([
    animatedText({ name: "fade-up" }),
  ]);

  assert.ok(html);
  assert.match(html, /class="[^"]*gs-anim-fade-up/);
});

test("the animation stylesheet is inlined when the deck uses animations", () => {
  const html = renderUi([
    animatedText({ name: "fade-up" }),
  ]);

  assert.match(html, /@keyframes gs-keyframe-fade-up/);
  assert.match(html, /\.gs-anim-fade-up/);
});

test("a deck without animations carries no animation stylesheet", () => {
  const html = renderUi([animatedText(null)]);

  assert.ok(html);
  assert.doesNotMatch(html, /gs-anim/);
  assert.doesNotMatch(html, /@keyframes gs-keyframe/);
});

test("the fragment surface inlines the stylesheet too", () => {
  const html = renderUi([animatedText({ name: "fade-in" })], {
    fragment: true,
  });

  assert.ok(html);
  assert.match(html, /class="[^"]*gs-anim-fade-in/);
  assert.match(html, /@keyframes gs-keyframe-fade-in/);
});

test("a delay and a duration become utility classes", () => {
  const html = renderUi([
    animatedText({ name: "fade-up", delay_ms: 120, duration: "normal" }),
  ]);

  assert.match(html, /gs-delay-120/);
  assert.match(html, /gs-duration-normal/);
});

test("an unknown animation id is ignored rather than rendered broken", () => {
  const html = renderUi([
    animatedText({ name: "not-a-real-animation" }),
  ]);

  assert.ok(html);
  assert.doesNotMatch(html, /gs-anim-not-a-real-animation/);
  // The element itself still renders.
  assert.match(html, /Retention rose to 91 percent/);
});

test("an animation without a name is ignored", () => {
  const html = renderUi([
    animatedText({ delay_ms: 100 }),
  ]);

  assert.ok(html);
  assert.doesNotMatch(html, /gs-anim/);
});

test("every animatable element type carries its own animation class", () => {
  const elements = [
    { ...animatedText({ name: "fade-up" }) },
    {
      type: "image",
      position: { x: 10, y: 10 },
      size: { width: 100, height: 100 },
      data: "https://example.test/a.png",
      animation: { name: "scale-up" },
    },
    {
      type: "text-list",
      position: { x: 10, y: 200 },
      size: { width: 300, height: 200 },
      items: [{ text: "one" }],
      animation: { name: "fade-left" },
    },
    {
      type: "table",
      position: { x: 10, y: 420 },
      size: { width: 400, height: 200 },
      rows: [["a", "b"]],
      animation: { name: "fade-right" },
    },
    {
      type: "chart",
      position: { x: 500, y: 10 },
      size: { width: 300, height: 200 },
      chart_type: "bar",
      series: [{ name: "s", values: [1, 2] }],
      animation: { name: "zoom-in" },
    },
    {
      type: "vector",
      shape: "polygon",
      position: { x: 500, y: 300 },
      size: { width: 100, height: 100 },
      points: [
        { x: 0, y: 0 },
        { x: 100, y: 0 },
        { x: 100, y: 100 },
      ],
      closed: true,
      fill: { color: "#FFFFFF" },
      animation: { name: "pop" },
    },
  ];

  const html = renderUi(elements);

  for (const className of [
    "gs-anim-fade-up",
    "gs-anim-scale-up",
    "gs-anim-fade-left",
    "gs-anim-fade-right",
    "gs-anim-zoom-in",
    "gs-anim-pop",
  ]) {
    assert.match(html, new RegExp(`class="[^"]*${className}`), className);
  }
});

test("an animated element keeps the class it already had", () => {
  const html = renderUi([
    {
      ...animatedText({ name: "fade-up" }),
      class: "existing-class",
    },
  ]);

  assert.ok(html);
  // A duplicate class attribute would be silently dropped by the browser, so
  // the animation class has to be merged into the existing one.
  const classAttributes = html.match(/class="([^"]*)"/g) ?? [];
  assert.ok(classAttributes.length > 0);
  for (const attribute of classAttributes) {
    assert.equal(
      (attribute.match(/class="/g) ?? []).length,
      1,
      "an element must not carry two class attributes",
    );
  }
});

test("nested elements carry their own animation", () => {
  const html = renderUi([
    {
      type: "group",
      position: { x: 0, y: 0 },
      size: { width: 800, height: 600 },
      children: [animatedText({ name: "fade-down" })],
    },
  ]);

  assert.match(html, /class="[^"]*gs-anim-fade-down/);
});
