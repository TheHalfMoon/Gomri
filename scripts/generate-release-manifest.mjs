import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { execFile } from "node:child_process";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);
const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

export function sha256(text) {
  return createHash("sha256").update(text, "utf8").digest("hex");
}

export async function generateReleaseManifest(root = repoRoot) {
  const readRoot = (relativePath) => readFile(path.join(root, relativePath), "utf8");
  const baseline = JSON.parse(await readRoot("config/release-baseline.json"));
  const [desktopIdentity, platformSupport] = await Promise.all([
    readRoot("config/desktop-release-identity.json").then((text) => JSON.parse(text)),
    readRoot("config/platform-support.json").then((text) => JSON.parse(text)),
  ]);

  let commit = process.env.GOMREY_RELEASE_COMMIT ?? "";
  if (!commit) {
    try {
      const { stdout } = await execFileAsync("git", ["rev-parse", "HEAD"], { cwd: root });
      commit = stdout.trim();
    } catch {
      commit = "unknown";
    }
  }

  const lockfiles = [];
  for (const lockfile of baseline.source_binding.lockfiles) {
    try {
      const text = await readRoot(lockfile);
      lockfiles.push({ path: lockfile, sha256: sha256(text), bytes: text.length });
    } catch {
      throw new Error(`release-manifest: missing required lockfile ${lockfile}`);
    }
  }

  return {
    schema_version: 1,
    product: baseline.product.name,
    version: baseline.product.version,
    repository: baseline.product.repository,
    commit,
    app_id: desktopIdentity.canonical?.app_id ?? baseline.desktop.app_id,
    artifact_template: baseline.desktop.artifact_template,
    platforms: baseline.platforms,
    sbom: baseline.sbom,
    platform_support: platformSupport.matrix,
    lockfiles,
    generated_by: "scripts/generate-release-manifest.mjs",
  };
}

const isMain = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  const manifest = await generateReleaseManifest();
  if (process.argv.includes("--check-only")) {
    const problems = [];
    if (!/^[0-9a-f]{40}$/.test(manifest.commit)) problems.push(`commit is not a full SHA: ${manifest.commit}`);
    if (manifest.lockfiles.length !== 4) problems.push("expected 4 bound lockfiles");
    if (problems.length > 0) {
      for (const problem of problems) console.error(`release-manifest: ${problem}`);
      process.exit(1);
    }
    console.log(`release-manifest: OK (${manifest.product} ${manifest.version} @ ${manifest.commit.slice(0, 7)})`);
  } else {
    process.stdout.write(`${JSON.stringify(manifest, null, 2)}\n`);
  }
}
