import assert from "node:assert/strict";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";
import { pathToFileURL } from "node:url";

import { build } from "esbuild";

let catalog;
let stylesheetModule;
let temporaryDirectory;

const GOMREY_CLASS_PREFIX = "gs-anim-";
const GOMREY_KEYFRAME_PREFIX = "gs-keyframe-";

/**
 * Tailwind CSS v4 utility class names that a wildcard attribute selector such
 * as the donor's `[class*="animate-"]` would match. Adopting the donor's
 * selector unchanged would blank every spinner and loading indicator.
 */
const TAILWIND_ANIMATE_UTILITIES = [
  "animate-spin",
  "animate-pulse",
  "animate-bounce",
  "animate-ping",
];

test.before(async () => {
  temporaryDirectory = await mkdtemp(
    path.join(tmpdir(), "gomrey-slide-animations-"),
  );
  const catalogOutput = path.join(temporaryDirectory, "catalog.mjs");
  const stylesheetOutput = path.join(temporaryDirectory, "stylesheet.mjs");

  await Promise.all([
    build({
      entryPoints: [path.resolve("lib/slide-animations/catalog.ts")],
      outfile: catalogOutput,
      bundle: true,
      platform: "node",
      format: "esm",
      tsconfig: path.resolve("tsconfig.json"),
      logLevel: "silent",
    }),
    build({
      entryPoints: [path.resolve("lib/slide-animations/stylesheet.ts")],
      outfile: stylesheetOutput,
      bundle: true,
      platform: "node",
      format: "esm",
      tsconfig: path.resolve("tsconfig.json"),
      logLevel: "silent",
    }),
  ]);

  catalog = await import(
    `${pathToFileURL(catalogOutput).href}?cache=${Date.now()}`
  );
  stylesheetModule = await import(
    `${pathToFileURL(stylesheetOutput).href}?cache=${Date.now()}`
  );
});

test.after(async () => {
  if (temporaryDirectory) {
    await rm(temporaryDirectory, { recursive: true, force: true });
  }
});

function autoCss() {
  return stylesheetModule.buildSlideAnimationStylesheet({ mode: "auto" });
}

function gatedCss() {
  return stylesheetModule.buildSlideAnimationStylesheet({ mode: "gated" });
}

/* ------------------------------------------------------------------ */
/* Catalog shape                                                       */
/* ------------------------------------------------------------------ */

test("catalog preserves the donor animation count: 20 entrance + 4 emphasis", () => {
  const animations = catalog.SLIDE_ANIMATIONS;
  assert.equal(animations.length, 24);
  assert.equal(
    animations.filter((a) => a.category === "entrance").length,
    20,
  );
  assert.equal(
    animations.filter((a) => a.category === "emphasis").length,
    4,
  );
});

test("catalog ids and class names are unique", () => {
  const ids = catalog.SLIDE_ANIMATIONS.map((a) => a.id);
  const classes = catalog.SLIDE_ANIMATIONS.map((a) => a.className);
  assert.equal(new Set(ids).size, ids.length);
  assert.equal(new Set(classes).size, classes.length);
});

test("every animation id is resolvable and unknown ids are rejected", () => {
  for (const animation of catalog.SLIDE_ANIMATIONS) {
    assert.equal(catalog.findSlideAnimation(animation.id)?.id, animation.id);
  }
  assert.equal(catalog.findSlideAnimation("does-not-exist"), undefined);
  assert.equal(catalog.findSlideAnimation(null), undefined);
  assert.equal(catalog.findSlideAnimation(undefined), undefined);
  assert.equal(catalog.findSlideAnimation("toString"), undefined);
});

/* ------------------------------------------------------------------ */
/* Namespace and collision safety                                      */
/* ------------------------------------------------------------------ */

test("all animation classes use the Gomrey namespace, never the donor prefix", () => {
  for (const animation of catalog.SLIDE_ANIMATIONS) {
    assert.ok(
      animation.className.startsWith(GOMREY_CLASS_PREFIX),
      `${animation.className} must start with ${GOMREY_CLASS_PREFIX}`,
    );
    assert.ok(
      !animation.className.startsWith("animate-"),
      `${animation.className} must not reuse the donor animate- prefix`,
    );
  }
});

test("no animation class collides with a Tailwind animate-* utility", () => {
  const classes = new Set(catalog.SLIDE_ANIMATIONS.map((a) => a.className));
  for (const utility of TAILWIND_ANIMATE_UTILITIES) {
    assert.ok(
      !classes.has(utility),
      `catalog must not define ${utility}, which collides with Tailwind CSS v4`,
    );
  }
});

test("all keyframes use the Gomrey namespace", () => {
  for (const animation of catalog.SLIDE_ANIMATIONS) {
    if (animation.keyframeName === null) {
      continue;
    }
    assert.ok(
      animation.keyframeName.startsWith(GOMREY_KEYFRAME_PREFIX),
      `${animation.keyframeName} must start with ${GOMREY_KEYFRAME_PREFIX}`,
    );
  }
});

/* ------------------------------------------------------------------ */
/* Stylesheet generation                                               */
/* ------------------------------------------------------------------ */

test("stylesheet is deterministic for identical options", () => {
  assert.equal(autoCss(), autoCss());
  assert.equal(gatedCss(), gatedCss());
  assert.notEqual(autoCss(), gatedCss());
});

test("stylesheet contains no wildcard class or attribute selectors", () => {
  for (const css of [autoCss(), gatedCss()]) {
    assert.ok(
      !css.includes("[class*="),
      "stylesheet must not use the donor wildcard attribute selector",
    );
    assert.ok(
      !/\*\s*\{/.test(css),
      "stylesheet must not use a universal selector",
    );
    assert.ok(
      !/^\s*\*\s*[,{]/m.test(css),
      "stylesheet must not use a universal selector in a selector list",
    );
  }
});

test("stylesheet contains no external asset or network reference", () => {
  const css = autoCss();
  assert.ok(!css.includes("@import"), "stylesheet must not @import");
  assert.ok(!css.includes("url("), "stylesheet must not reference url()");
  assert.ok(!/https?:\/\//.test(css), "stylesheet must not reference a URL");
});

test("every catalogued animation is emitted into the stylesheet", () => {
  const css = autoCss();
  for (const animation of catalog.SLIDE_ANIMATIONS) {
    assert.ok(
      css.includes(`.${animation.className}`),
      `stylesheet must emit .${animation.className}`,
    );
    if (animation.keyframeName) {
      assert.ok(
        css.includes(`@keyframes ${animation.keyframeName}`),
        `stylesheet must emit @keyframes ${animation.keyframeName}`,
      );
    }
  }
});

test("every emitted animation-name resolves to a declared keyframe", () => {
  const css = autoCss();
  const declared = new Set(
    [...css.matchAll(/@keyframes\s+([A-Za-z0-9_-]+)/g)].map((m) => m[1]),
  );
  const used = new Set(
    [...css.matchAll(/animation-name:\s*([A-Za-z0-9_-]+)/g)].map((m) => m[1]),
  );
  assert.ok(used.size > 0, "stylesheet must declare at least one animation-name");
  for (const name of used) {
    assert.ok(
      declared.has(name),
      `animation-name ${name} has no matching @keyframes block`,
    );
  }
});

test("stylesheet braces are balanced and declarations are terminated", () => {
  for (const css of [autoCss(), gatedCss()]) {
    const open = (css.match(/\{/g) ?? []).length;
    const close = (css.match(/\}/g) ?? []).length;
    assert.equal(open, close, "unbalanced braces in generated stylesheet");

    // Keyframe bodies legitimately contain inline `from { ... }` steps. Strip
    // them so the declaration scan only inspects real declaration blocks.
    const withoutKeyframes = css.replace(
      /@keyframes\s+[A-Za-z0-9_-]+\s*\{[\s\S]*?\n\}/g,
      "",
    );

    const declarations = withoutKeyframes
      .split("\n")
      .map((line) => line.trim())
      .filter(
        (line) =>
          line.includes(":") &&
          !line.startsWith("@") &&
          !line.endsWith("{") &&
          !line.endsWith(",") &&
          !line.endsWith(";"),
      );
    for (const declaration of declarations) {
      assert.ok(
        declaration.length > 0,
        "declaration must not be empty",
      );
    }

    // Every declaration line that is a property assignment must end in `;`.
    const propertyLines = withoutKeyframes
      .split("\n")
      .map((line) => line.trim())
      .filter(
        (line) =>
          /^[a-z-]+:\s*.+;$/.test(line) ||
          (/^[a-z-]+:\s*.+$/.test(line) && !line.endsWith("{")),
      );
    for (const declaration of propertyLines) {
      assert.ok(
        declaration.endsWith(";"),
        `declaration must be terminated with a semicolon: ${declaration}`,
      );
    }
  }
});

/* ------------------------------------------------------------------ */
/* Activation modes                                                    */
/* ------------------------------------------------------------------ */

test("auto mode does not pause animations", () => {
  const css = autoCss();
  assert.ok(!css.includes("animation-play-state: paused"));
  assert.ok(!css.includes('data-gs-slide-active="true"'));
});

test("gated mode pauses by default and plays only the active slide", () => {
  const css = gatedCss();
  assert.ok(css.includes("animation-play-state: paused"));
  assert.ok(
    css.includes('[data-gs-slide-active="true"] .gs-anim-fade-up'),
    "gated mode must re-enable animations inside the active slide container",
  );
  assert.ok(css.includes("animation-play-state: running"));
});

/* ------------------------------------------------------------------ */
/* Reduced motion                                                      */
/* ------------------------------------------------------------------ */

test("reduced motion neutralises every catalogued animation", () => {
  const css = autoCss();
  const reducedBlock = css.slice(
    css.indexOf("@media (prefers-reduced-motion: reduce)"),
  );
  for (const animation of catalog.SLIDE_ANIMATIONS) {
    assert.ok(
      reducedBlock.includes(`.${animation.className}`),
      `reduced motion must cover .${animation.className}`,
    );
  }
});

test("reduced motion stops looping emphasis animations and restores opacity", () => {
  const css = autoCss();
  const reducedBlock = css.slice(
    css.indexOf("@media (prefers-reduced-motion: reduce)"),
  );
  assert.ok(reducedBlock.includes("animation-iteration-count: 1 !important"));
  assert.ok(reducedBlock.includes("animation-duration: 0.01ms !important"));
  assert.ok(reducedBlock.includes("opacity: 1 !important"));
  assert.ok(reducedBlock.includes("transform: none !important"));
});

test("reduced motion is scoped to Gomrey classes and does not blanket the page", () => {
  const css = autoCss();
  const reducedBlock = css.slice(
    css.indexOf("@media (prefers-reduced-motion: reduce)"),
  );
  assert.ok(
    !reducedBlock.includes("*,"),
    "reduced motion must not use a universal selector",
  );
  assert.ok(
    !reducedBlock.includes("* {"),
    "reduced motion must not use a universal selector",
  );
});

test("reduced motion can be excluded explicitly", () => {
  const css = stylesheetModule.buildSlideAnimationStylesheet({
    mode: "auto",
    includeReducedMotion: false,
  });
  assert.ok(!css.includes("prefers-reduced-motion"));
});

/* ------------------------------------------------------------------ */
/* Class attribute construction                                        */
/* ------------------------------------------------------------------ */

test("class attribute builder returns the Gomrey class for known ids", () => {
  assert.equal(
    stylesheetModule.slideAnimationClassAttribute("fade-up"),
    "gs-anim-fade-up",
  );
  assert.equal(
    stylesheetModule.slideAnimationClassAttribute("shimmer"),
    "gs-anim-shimmer",
  );
});

test("class attribute builder rejects unknown ids without emitting a class", () => {
  assert.equal(stylesheetModule.slideAnimationClassAttribute("nope"), "");
  assert.equal(stylesheetModule.slideAnimationClassAttribute(null), "");
  assert.equal(stylesheetModule.slideAnimationClassAttribute(undefined), "");
  assert.equal(stylesheetModule.slideAnimationClassAttribute(""), "");
  assert.equal(
    stylesheetModule.slideAnimationClassAttribute("toString"),
    "",
    "prototype keys must not resolve to an animation",
  );
});

test("class attribute builder appends delay and duration utilities", () => {
  assert.equal(
    stylesheetModule.slideAnimationClassAttribute("fade-up", {
      delayMs: 200,
      duration: "slow",
    }),
    "gs-anim-fade-up gs-delay-200 gs-duration-slow",
  );
});

test("class attribute builder ignores invalid delay and duration values", () => {
  assert.equal(
    stylesheetModule.slideAnimationClassAttribute("fade-up", {
      delayMs: -5,
    }),
    "gs-anim-fade-up",
  );
  assert.equal(
    stylesheetModule.slideAnimationClassAttribute("fade-up", {
      delayMs: Number.NaN,
    }),
    "gs-anim-fade-up",
  );
  assert.equal(
    stylesheetModule.slideAnimationClassAttribute("fade-up", {
      duration: "turbo",
    }),
    "gs-anim-fade-up",
  );
});

/* ------------------------------------------------------------------ */
/* Engine honesty                                                      */
/* ------------------------------------------------------------------ */

test("counter-up is classified as controller-backed, not as a CSS animation", () => {
  const counter = catalog.findSlideAnimation("counter-up");
  assert.ok(counter);
  assert.equal(counter.engine, "controller");
  assert.equal(counter.keyframeName, null);
  assert.equal(counter.controllerAttribute, "data-gs-count-target");
  assert.ok(
    !autoCss().includes("@keyframes gs-keyframe-counter-up"),
    "a controller-backed animation must not declare CSS keyframes",
  );
});

test("controller-backed animations are never hidden by a static rule", () => {
  const css = autoCss();
  for (const animation of catalog.SLIDE_ANIMATIONS) {
    if (animation.engine !== "controller") {
      continue;
    }
    assert.equal(
      animation.hidesUntilStart,
      false,
      `${animation.id} has no CSS keyframe to reveal it and must not be hidden`,
    );
    const rule = css.match(
      new RegExp(`\\.${animation.className} \\{([^}]*)\\}`),
    );
    assert.ok(rule, `stylesheet must emit a rule for .${animation.className}`);
    assert.ok(
      !/opacity:\s*0/.test(rule[1]),
      `${animation.className} must not be permanently hidden`,
    );
  }
});

test("easing variable names do not stutter", () => {
  const css = autoCss();
  assert.ok(css.includes("--gs-ease-in-out: ease-in-out"));
  assert.ok(css.includes("--gs-ease-linear: linear"));
  assert.ok(css.includes("--gs-ease-steps: steps(40, end)"));
  assert.ok(!css.includes("--gs-ease-ease-in-out"));
  assert.ok(!css.includes("--gs-ease-ease-"));
});

test("draw-line declares its measured-geometry dependency", () => {
  const drawLine = catalog.findSlideAnimation("draw-line");
  assert.ok(drawLine);
  assert.equal(drawLine.requiredCustomProperty, "--gs-path-length");
  assert.ok(autoCss().includes("--gs-path-length"));
});

/* ------------------------------------------------------------------ */
/* Utility classes                                                     */
/* ------------------------------------------------------------------ */

test("stagger delay and duration utilities are emitted", () => {
  const css = autoCss();
  for (const delay of catalog.SLIDE_ANIMATION_STAGGER_DELAYS) {
    assert.ok(css.includes(`.gs-delay-${delay}`));
    assert.ok(css.includes(`animation-delay: ${delay}ms`));
  }
  assert.ok(css.includes(".gs-duration-fast"));
  assert.ok(css.includes(".gs-duration-normal"));
  assert.ok(css.includes(".gs-duration-slow"));
});

test("utility classes can be excluded", () => {
  const css = stylesheetModule.buildSlideAnimationStylesheet({
    mode: "auto",
    includeUtilityClasses: false,
  });
  assert.ok(!css.includes(".gs-delay-100"));
  assert.ok(!css.includes(".gs-duration-fast"));
});
