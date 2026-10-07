import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

export const SBOM_SURFACES = [
  { name: "root", lockfile: "package-lock.json", type: "npm" },
  { name: "electron", lockfile: "electron/package-lock.json", type: "npm" },
  { name: "nextjs", lockfile: "servers/nextjs/package-lock.json", type: "npm" },
  { name: "fastapi", lockfile: "servers/fastapi/uv.lock", type: "uv" },
];

export function sha256(text) {
  return createHash("sha256").update(text, "utf8").digest("hex");
}

export function npmComponents(lock) {
  const packages = lock.packages ?? {};
  const components = [];
  for (const [key, entry] of Object.entries(packages)) {
    if (!key) continue;
    const name = key.replace(/^node_modules\//, "");
    if (!name || name.includes("node_modules/")) continue;
    if (!entry?.version) continue;
    components.push({
      type: "library",
      name,
      version: entry.version,
      purl: `pkg:npm/${name}@${entry.version}`,
    });
  }
  components.sort((a, b) => a.purl.localeCompare(b.purl));
  return components;
}

export function uvComponents(text) {
  const components = [];
  const namePattern = /^name\s*=\s*"([^"]+)"\s*$/gm;
  const versionPattern = /^version\s*=\s*"([^"]+)"\s*$/gm;
  const names = [...text.matchAll(namePattern)].map((match) => match[1]);
  const versions = [...text.matchAll(versionPattern)].map((match) => match[1]);
  const seen = new Set();
  for (let index = 0; index < names.length; index += 1) {
    const name = names[index];
    const version = versions[index] ?? "unknown";
    const purl = `pkg:pypi/${name}@${version}`;
    if (seen.has(purl)) continue;
    seen.add(purl);
    components.push({ type: "library", name, version, purl });
  }
  components.sort((a, b) => a.purl.localeCompare(b.purl));
  return components;
}

export async function buildSbom(root = repoRoot) {
  const toolVersion = JSON.parse(await readFile(path.join(root, "package.json"), "utf8")).version;
  const surfaces = [];
  for (const surface of SBOM_SURFACES) {
    let lockText;
    try {
      lockText = await readFile(path.join(root, surface.lockfile), "utf8");
    } catch {
      throw new Error(`sbom: missing required lockfile ${surface.lockfile}; refusing to silently omit ${surface.name}`);
    }
    const components = surface.type === "npm" ? npmComponents(JSON.parse(lockText)) : uvComponents(lockText);
    if (components.length === 0) {
      throw new Error(`sbom: parsed zero components for ${surface.name}; refusing to emit an empty SBOM`);
    }
    surfaces.push({
      name: surface.name,
      lockfile: surface.lockfile,
      lockfileSha256: sha256(lockText),
      componentCount: components.length,
      components,
    });
  }
  return {
    bomFormat: "CycloneDX",
    specVersion: "1.6",
    version: 1,
    metadata: {
      timestamp: new Date().toISOString(),
      tools: [{ name: "gomrey-sbom", version: `repo-package:${toolVersion}` }],
    },
    surfaces: surfaces.map(({ components, ...rest }) => rest),
    components: surfaces.flatMap((surface) =>
      surface.components.map((component) => ({ ...component, "gomrey:surface": surface.name })),
    ),
  };
}

export async function writeSbom(root = repoRoot, outDir = path.join(root, "sbom")) {
  const bom = await buildSbom(root);
  await mkdir(outDir, { recursive: true });
  const perSurface = [];
  for (const surface of SBOM_SURFACES) {
    const match = bom.surfaces.find((entry) => entry.name === surface.name);
    const components = bom.components.filter((component) => component["gomrey:surface"] === surface.name);
    const document = {
      bomFormat: "CycloneDX",
      specVersion: "1.6",
      version: 1,
      metadata: bom.metadata,
      components: components.map(({ "gomrey:surface": _ignored, ...rest }) => rest),
    };
    const file = path.join(outDir, `${surface.name}.cdx.json`);
    await writeFile(file, `${JSON.stringify(document, null, 2)}\n`);
    perSurface.push({ name: surface.name, file: `sbom/${surface.name}.cdx.json`, sha256: sha256(JSON.stringify(document)) });
  }
  const manifest = {
    tool: "gomrey-sbom",
    surfaces: bom.surfaces.map((surface) => ({
      ...surface,
      file: `sbom/${surface.name}.cdx.json`,
    })),
    files: perSurface,
  };
  await writeFile(path.join(outDir, "manifest.json"), `${JSON.stringify(manifest, null, 2)}\n`);
  return manifest;
}

const isMain = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  const manifest = await writeSbom();
  console.log(`sbom: OK (${manifest.surfaces.map((surface) => `${surface.name}:${surface.componentCount}`).join(", ")})`);
}
