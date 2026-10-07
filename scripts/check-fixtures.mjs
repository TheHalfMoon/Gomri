import { readdir, readFile, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

const DENIED_FILE_PATTERNS = [/\.pem$/, /\.key$/, /id_rsa/, /credentials\.json$/, /production.*dump/i, /\.dump$/];
const DENIED_CONTENT_PATTERNS = [
  /\bAKIA[0-9A-Z]{16}\b/,
  /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/,
  /\bgh[pousr]_[A-Za-z0-9]{36,}\b/,
];

async function readJson(relativePath) {
  return JSON.parse(await readFile(path.join(repoRoot, relativePath), "utf8"));
}

export async function checkFixtures(root = repoRoot) {
  const errors = [];
  const policy = JSON.parse(await readFile(path.join(root, "config/fixture-policy.json"), "utf8"));

  for (const key of ["allowed_kinds", "prohibited", "requirements"]) {
    if (!policy[key]) errors.push(`fixture-policy: missing ${key}`);
  }

  async function walk(relativeDir, findings, allowlisted = new Set()) {
    let entries;
    try {
      entries = await readdir(path.join(root, relativeDir), { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      const relative = path.posix.join(relativeDir, entry.name);
      if (allowlisted.has(relative)) continue;
      if (entry.isDirectory()) {
        if (entry.name === "node_modules" || entry.name === ".venv") continue;
        await walk(relative, findings, allowlisted);
      } else if (entry.isFile()) {
        for (const pattern of DENIED_FILE_PATTERNS) {
          if (pattern.test(entry.name)) findings.push(`${relative}: denied fixture filename pattern ${pattern}`);
        }
        let info;
        try {
          info = await stat(path.join(root, relative));
        } catch {
          continue;
        }
        if (info.size > 1024 * 1024) continue;
        let text;
        try {
          text = await readFile(path.join(root, relative), "utf8");
        } catch {
          continue;
        }
        text.split("\n").forEach((line, index) => {
          if (line.includes("EXAMPLE") || line.includes("placeholder")) return;
          for (const pattern of DENIED_CONTENT_PATTERNS) {
            if (pattern.test(line)) findings.push(`${relative}:${index + 1}: denied credential-like fixture content`);
          }
        });
      }
    }
  }

  const findings = [];
  const allowlisted = new Set((policy.scan.allowlisted_paths ?? []).map((entry) => entry.path));
  for (const scanRoot of policy.scan.roots) {
    await walk(scanRoot, findings, allowlisted);
  }
  for (const finding of findings) errors.push(`fixture-policy: ${finding}`);
  return errors;
}

const isMain = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  const errors = await checkFixtures();
  if (errors.length > 0) {
    for (const error of errors.slice(0, 30)) console.error(error);
    console.error(`fixture-policy: FAIL (${errors.length} issue(s))`);
    process.exit(1);
  }
  console.log("fixture-policy: OK (test roots contain no denied fixture material)");
}
