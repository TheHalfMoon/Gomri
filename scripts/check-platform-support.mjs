import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

export async function loadPlatformSupport(root = repoRoot) {
  const raw = await readFile(path.join(root, "config/platform-support.json"), "utf8");
  return JSON.parse(raw);
}

export function validatePlatformSupport(matrix) {
  const errors = [];
  if (!matrix || typeof matrix !== "object") {
    return ["platform-support matrix is not an object"];
  }
  for (const platform of ["linux", "windows", "macos"]) {
    const entry = matrix.matrix?.[platform];
    if (!entry) {
      errors.push(`missing matrix entry for ${platform}`);
      continue;
    }
    if (!entry.scope) errors.push(`${platform}: missing scope`);
    if (!Array.isArray(entry.jobs) || entry.jobs.length === 0) {
      errors.push(`${platform}: jobs must be a non-empty array`);
    }
  }
  if (matrix.matrix?.linux?.scope !== "full-integration") {
    errors.push("linux must remain the full-integration path");
  }
  for (const platform of ["windows", "macos"]) {
    if (matrix.matrix?.[platform]?.scope !== "bounded-qualification") {
      errors.push(`${platform} must be bounded-qualification`);
    }
  }
  const required = matrix.required_for_merge ?? [];
  for (const job of ["qualify-windows", "qualify-macos", "g4-baseline"]) {
    if (!required.includes(job)) errors.push(`required_for_merge must include ${job}`);
  }
  const runners = matrix.runners ?? {};
  if (runners.linux !== "ubuntu-latest") errors.push("linux runner must be ubuntu-latest");
  if (runners.windows !== "windows-latest") errors.push("windows runner must be windows-latest");
  if (runners.macos !== "macos-latest") errors.push("macos runner must be macos-latest");
  return errors;
}

const isMain = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  const matrix = await loadPlatformSupport();
  const errors = validatePlatformSupport(matrix);
  if (errors.length > 0) {
    for (const error of errors) console.error(`platform-support: ${error}`);
    process.exit(1);
  }
  console.log("platform-support: OK (linux full-integration; windows/macos bounded)");
}
