import assert from "node:assert/strict";
import test from "node:test";
import { SBOM_SURFACES, buildSbom, npmComponents, uvComponents } from "./generate-sbom.mjs";

test("SBOM covers every shipped dependency surface without silent omission", async () => {
  assert.deepEqual(
    SBOM_SURFACES.map((surface) => surface.name).sort(),
    ["electron", "fastapi", "nextjs", "root"],
  );
  const bom = await buildSbom();
  assert.equal(bom.bomFormat, "CycloneDX");
  assert.equal(bom.specVersion, "1.6");
  assert.equal(bom.surfaces.length, 4);
  for (const surface of bom.surfaces) {
    assert.ok(surface.componentCount > 10, `${surface.name} has too few components`);
    assert.match(surface.lockfileSha256, /^[0-9a-f]{64}$/);
  }
  assert.ok(bom.metadata.tools[0].version.startsWith("repo-package:"));
});

test("SBOM parsers extract deterministic sorted components", () => {
  const npm = npmComponents({
    packages: {
      "": { name: "root", version: "0.1.0" },
      "node_modules/b": { version: "2.0.0" },
      "node_modules/a": { version: "1.0.0" },
    },
  });
  assert.deepEqual(npm.map((entry) => entry.purl), ["pkg:npm/a@1.0.0", "pkg:npm/b@2.0.0"]);

  const uv = uvComponents('name = "b"\nversion = "2.0"\nname = "a"\nversion = "1.0"\n');
  assert.deepEqual(uv.map((entry) => entry.purl), ["pkg:pypi/a@1.0", "pkg:pypi/b@2.0"]);
});
