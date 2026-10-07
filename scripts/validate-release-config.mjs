import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

async function read(relativePath) {
  return readFile(path.join(repoRoot, relativePath), "utf8");
}

async function readJson(relativePath) {
  return JSON.parse(await read(relativePath));
}

export async function validateReleaseConfig(root = repoRoot) {
  const errors = [];
  const readRoot = async (relativePath) => readFile(path.join(root, relativePath), "utf8");
  const readRootJson = async (relativePath) => JSON.parse(await readRoot(relativePath));

  let baseline;
  try {
    baseline = await readRootJson("config/release-baseline.json");
  } catch {
    return ["release-baseline: config/release-baseline.json is missing or invalid"];
  }

  const [rootPackage, electronPackage, electronVersion, dockerRelease, r2Workflow] =
    await Promise.all([
      readRootJson("package.json"),
      readRootJson("electron/package.json"),
      readRootJson("electron/version.json"),
      readRoot("docker-compose.yml").then(() => readRoot(".github/workflows/docker-release.yml")).catch(() => ""),
      readRoot(".github/workflows/sync-releaes-to-r2.yml").catch(() => ""),
    ]);

  if (rootPackage.version !== baseline.product.version) {
    errors.push(`root package version ${rootPackage.version} does not match release baseline ${baseline.product.version}`);
  }
  if (electronPackage.version !== baseline.product.version) {
    errors.push(`electron package version ${electronPackage.version} does not match release baseline ${baseline.product.version}`);
  }
  if (electronVersion.version !== baseline.product.version) {
    errors.push(`electron/version.json ${electronVersion.version} does not match release baseline ${baseline.product.version}`);
  }
  for (const url of Object.values(electronVersion.downloads ?? {})) {
    if (!url.includes("github.com/TheHalfMoon/Gomrey/releases")) {
      errors.push(`electron/version.json download does not target Gomrey releases: ${url}`);
    }
    if (/presenton/i.test(url)) errors.push(`electron/version.json download references donor identity: ${url}`);
  }

  for (const forbidden of baseline.release.forbidden_repositories) {
    if (dockerRelease.includes(forbidden)) {
      errors.push(`docker-release workflow targets forbidden repository ${forbidden}`);
    }
  }
  for (const forbidden of baseline.release.forbidden_images) {
    if (dockerRelease.includes(forbidden)) {
      errors.push(`docker-release workflow uses forbidden image ${forbidden}`);
    }
  }
  if (!dockerRelease.includes(baseline.release.docker_image)) {
    errors.push(`docker-release workflow does not use canonical image ${baseline.release.docker_image}`);
  }
  for (const prefix of baseline.release.forbidden_artifact_prefixes) {
    const donorExtraction = new RegExp(`s/\\^${prefix}`);
    if (donorExtraction.test(r2Workflow)) {
      errors.push(`r2 sync workflow still extracts donor artifact prefix ${prefix}`);
    }
  }
  for (const bucket of baseline.release.forbidden_buckets) {
    if (r2Workflow.includes(bucket)) {
      errors.push(`r2 sync workflow targets forbidden bucket ${bucket}`);
    }
  }
  const sbomSurfaces = baseline.sbom.surfaces ?? [];
  if (sbomSurfaces.length !== 4) errors.push("release baseline must list exactly 4 SBOM surfaces");

  return errors;
}

const isMain = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  const errors = await validateReleaseConfig();
  if (errors.length > 0) {
    for (const error of errors) console.error(`release-config: ${error}`);
    console.error(`release-config: FAIL (${errors.length} issue(s))`);
    process.exit(1);
  }
  console.log("release-config: OK (versions aligned; no donor publish target)");
}
