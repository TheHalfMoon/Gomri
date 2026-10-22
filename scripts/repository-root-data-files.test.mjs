import assert from "node:assert/strict";
import { execFile } from "node:child_process";
import { readdir } from "node:fs/promises";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const selfPath = "scripts/repository-root-data-files.test.mjs";

/**
 * Root-level JSON files that are a real part of the repository.
 *
 * Every entry is a declared source of truth. A file that is not listed here is
 * an orphan: it is not read by anything, but it sits at the repository root
 * where a contributor will assume it is the source of truth for whatever it
 * describes. `layouts.json` was exactly that — 252 KB of slide layouts
 * imported with the Presenton execution base, referenced by nothing.
 */
const DECLARED_ROOT_JSON_FILES = [
  "package-lock.json",
  "package.json",
  "product-identity.json",
];

/**
 * Root-level files that are local tooling state rather than repository
 * content. They are gitignored and must not be treated as source of truth.
 */
const LOCAL_ONLY_ROOT_FILES = new Set(["skills-lock.json"]);

/**
 * Match a reference to a file by its exact quoted name.
 *
 * A root file is named exactly, `"package.json"`. A nested file of the same
 * name is named with a path, `"electron/package.json"`, and that does not count
 * as a reference to the root file.
 */
function exactNamePattern(fileName) {
  const escaped = fileName.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return new RegExp(`["'\`]${escaped}["'\`]`);
}

async function referencesTo(fileName) {
  // Search the tracked tree only: an untracked local file is not a reference
  // that the repository depends on.
  let stdout = "";
  try {
    ({ stdout } = await execFileAsync(
      "git",
      ["grep", "-l", "-E", "-e", exactNamePattern(fileName).source],
      { cwd: repoRoot, maxBuffer: 16 * 1024 * 1024 },
    ));
  } catch (error) {
    // `git grep` exits 1 when there is no match.
    if (error.code === 1) {
      return [];
    }
    throw error;
  }
  return stdout
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line && line !== fileName && line !== selfPath)
    .filter((line) => !line.startsWith("docs/evidence/"))
    .filter((line) => !line.startsWith("research/"));
}

test("the repository root holds no unreferenced JSON file", async () => {
  const entries = await readdir(repoRoot, { withFileTypes: true });
  const rootJsonFiles = entries
    .filter((entry) => entry.isFile() && entry.name.endsWith(".json"))
    .map((entry) => entry.name)
    .filter((name) => !LOCAL_ONLY_ROOT_FILES.has(name))
    .sort();

  assert.deepEqual(
    rootJsonFiles,
    [...DECLARED_ROOT_JSON_FILES].sort(),
    `Unexpected root-level JSON file(s). Every root JSON file must be a declared source of truth in scripts/repository-root-data-files.test.mjs, or be removed as an orphan.`,
  );
});

test("the removed orphan layouts file is gone", async () => {
  const entries = await readdir(repoRoot, { withFileTypes: true });
  const names = entries.filter((entry) => entry.isFile()).map((entry) => entry.name);

  assert.ok(
    !names.includes("layouts.json"),
    "layouts.json is an unreferenced orphan: it was imported with the Presenton execution base and read by nothing. It must not come back.",
  );
});

test("every declared root JSON file is still named in the repository", async () => {
  // A name mention is a *necessary* condition for the root file to be read: a
  // file nothing names is definitely an orphan. It is not sufficient — a
  // mention inside `path.join(someOtherDirectory, "package.json")` names the
  // root file without reading it — so this check catches orphans, it does not
  // prove that the root copy is the one being opened.
  for (const fileName of DECLARED_ROOT_JSON_FILES) {
    const references = await referencesTo(fileName);
    assert.ok(
      references.length > 0,
      `${fileName} is a declared root source of truth but nothing in the repository names it. Either wire it up or remove it.`,
    );
  }
});
