import assert from "node:assert/strict";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";
import { pathToFileURL } from "node:url";
import { build } from "esbuild";

let protocol;
let createTemplateV2ClipboardPayload;
let temporaryDirectory;

test.before(async () => {
  temporaryDirectory = await mkdtemp(path.join(tmpdir(), "gomrey-protocol-"));
  const entryFile = path.join(temporaryDirectory, "entry.ts");
  const outputFile = path.join(temporaryDirectory, "bundle.mjs");
  await writeFile(
    entryFile,
    [
      "export * from " +
        JSON.stringify(
          path.resolve("components/slide-editor/clipboard/protocol.ts"),
        ) +
        ";",
      "export { createTemplateV2ClipboardPayload } from " +
        JSON.stringify(
          path.resolve("components/slide-editor/clipboard/clipboard.ts"),
        ) +
        ";",
    ].join("\n"),
  );
  await build({
    entryPoints: [entryFile],
    outfile: outputFile,
    bundle: true,
    platform: "node",
    format: "esm",
    tsconfig: path.resolve("tsconfig.json"),
    logLevel: "silent",
  });
  protocol = await import(
    `${pathToFileURL(outputFile).href}?cache=${Date.now()}`
  );
  createTemplateV2ClipboardPayload =
    protocol.createTemplateV2ClipboardPayload;
});

test.after(async () => {
  if (temporaryDirectory) {
    await rm(temporaryDirectory, { recursive: true, force: true });
  }
});

test("new clipboard payloads use Gomrey identity", () => {
  const payload = createTemplateV2ClipboardPayload([
    {
      data: { id: "box" },
      absoluteBox: { x: 1, y: 2, width: 3, height: 4 },
    },
  ]);
  assert.equal(payload.format, "gomrey/template-v2");
});

test("clipboard text accepts canonical and legacy prefixes", () => {
  assert.equal(
    protocol.serializedTemplateV2PayloadFromText(
      'GOMREY_TEMPLATE_V2:{"a":1}',
    ),
    '{"a":1}',
  );
  assert.equal(
    protocol.serializedTemplateV2PayloadFromText(
      'PRESENTON_TEMPLATE_V2:{"a":1}',
    ),
    '{"a":1}',
  );
  assert.equal(protocol.serializedTemplateV2PayloadFromText("other"), "");
});

test("canonical clipboard MIME has precedence by presence", () => {
  const data = {
    types: [
      "application/x-gomrey-template-v2",
      "application/x-presenton-template-v2",
    ],
    getData(type) {
      return type === "application/x-gomrey-template-v2" ? "" : "legacy";
    },
  };
  assert.equal(
    protocol.serializedTemplateV2PayloadFromClipboardData(data),
    "",
  );
});

test("legacy MIME and payload format remain readable contracts", () => {
  const data = {
    types: ["application/x-presenton-template-v2"],
    getData() {
      return "legacy";
    },
  };
  assert.equal(
    protocol.serializedTemplateV2PayloadFromClipboardData(data),
    "legacy",
  );
  assert.equal(
    protocol.isSupportedTemplateV2ClipboardFormat("gomrey/template-v2"),
    true,
  );
  assert.equal(
    protocol.isSupportedTemplateV2ClipboardFormat("presenton/template-v2"),
    true,
  );
  assert.equal(
    protocol.isSupportedTemplateV2ClipboardFormat("other"),
    false,
  );
});

test("chart source writes canonical protocol and retains bounded legacy reads", async () => {
  const [preview, renderer] = await Promise.all([
    readFile(
      path.resolve(
        "app/(presentation-generator)/components/TemplateV2HtmlSlidePreview.tsx",
      ),
      "utf8",
    ),
    readFile(path.resolve("lib/template-v2-json-to-html.ts"), "utf8"),
  ]);
  assert.match(preview, /__GOMREY_JSON_CHARTS__/);
  assert.match(preview, /__PRESENTON_JSON_CHARTS__/);
  assert.match(
    preview,
    /canvas\[data-gomrey-chart\],canvas\[data-presenton-chart\]/,
  );
  assert.match(renderer, /data-gomrey-chart="true"/);
  assert.match(renderer, /gomreyFormat/);
  assert.match(renderer, /presentonFormat/);
  assert.match(renderer, /gomreyBarRadius/);
  assert.match(renderer, /presentonBarRadius/);
});
