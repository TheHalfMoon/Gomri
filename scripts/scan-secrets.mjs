import { readFile, readdir, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { execFile } from "node:child_process";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);
const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

const SECRET_PATTERNS = [
  { name: "aws-access-key", pattern: /\bAKIA[0-9A-Z]{16}\b/ },
  { name: "aws-secret-key", pattern: /\baws_secret_access_key\s*=\s*['"][^'"]{8,}['"]/i },
  { name: "private-key-block", pattern: /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/ },
  { name: "github-token", pattern: /\bgh[pousr]_[A-Za-z0-9]{36,}\b/ },
  { name: "openai-key", pattern: /\bsk-[A-Za-z0-9]{20,}\b/ },
  { name: "generic-password-assign", pattern: /\b(password|passwd|secret)\s*=\s*['"][^'"]{8,}['"]/i },
];

const EXCLUDED_DIRS = new Set([
  ".git",
  "node_modules",
  ".venv",
  "venv",
  "dist",
  "app_dist",
  ".next",
  ".next-build",
  "presentation-export",
  "document-extraction-liteparse",
  "app_data",
  "sbom",
]);

const EXCLUDED_FILES = [
  "package-lock.json",
  "uv.lock",
  "pnpm-lock.yaml",
  "yarn.lock",
  "NOTICE",
  "P02_G3C_STORE_ARTWORK.md",
  "P02_G3B_PACKAGE_IDENTITY.md",
  // Intentional synthetic scanner-validation strings with no real credential
  // value; required to prove the scanner detects credential-like material.
  "scan-secrets.test.mjs",
];

const EXCLUDED_PREFIXES = ["docs/donors/", "docs/evidence/", "readme_assets/"];

export function isExcluded(relativePath) {
  const normalized = relativePath.replace(/\\/g, "/");
  for (const prefix of EXCLUDED_PREFIXES) {
    if (normalized.startsWith(prefix)) return true;
  }
  const base = path.basename(normalized);
  if (EXCLUDED_FILES.includes(base)) return true;
  const segments = normalized.split("/");
  if (segments.some((segment) => EXCLUDED_DIRS.has(segment))) return true;
  if (/\.(png|jpg|jpeg|gif|ico|icns|deb|dmg|exe|AppImage|zip|tar\.gz|whl)$/i.test(normalized)) return true;
  return false;
}

export function scanText(relativePath, text) {
  const findings = [];
  const lines = text.split("\n");
  lines.forEach((line, index) => {
    if (line.includes("EXAMPLE") || line.includes("placeholder") || line.includes("replace-with-")) return;
    for (const { name, pattern } of SECRET_PATTERNS) {
      if (pattern.test(line)) {
        findings.push({ file: relativePath, line: index + 1, rule: name });
      }
    }
  });
  return findings;
}

async function trackedFiles(root) {
  try {
    const { stdout } = await execFileAsync("git", ["ls-files", "-z"], { cwd: root, maxBuffer: 16 * 1024 * 1024 });
    return stdout.split("\0").filter(Boolean);
  } catch {
    return null;
  }
}

async function walkFiles(root, dir) {
  const entries = await readdir(path.join(root, dir), { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const relative = path.posix.join(dir, entry.name);
    if (isExcluded(relative)) continue;
    if (entry.isDirectory()) {
      files.push(...(await walkFiles(root, relative)));
    } else if (entry.isFile()) {
      files.push(relative);
    }
  }
  return files;
}

export async function scanRepo(root = repoRoot) {
  let files = await trackedFiles(root);
  if (!files) {
    files = await walkFiles(root, ".");
  } else {
    files = files.map((file) => file.replace(/\\/g, "/")).filter((file) => !isExcluded(file));
  }
  const findings = [];
  for (const file of files) {
    let info;
    try {
      info = await stat(path.join(root, file));
    } catch {
      continue;
    }
    if (!info.isFile() || info.size > 2 * 1024 * 1024) continue;
    let text;
    try {
      text = await readFile(path.join(root, file), "utf8");
    } catch {
      continue;
    }
    findings.push(...scanText(file, text));
  }
  return findings;
}

const isMain = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  const findings = await scanRepo();
  if (findings.length > 0) {
    for (const finding of findings.slice(0, 50)) {
      console.error(`secret-scan: ${finding.rule} in ${finding.file}:${finding.line}`);
    }
    console.error(`secret-scan: FAIL (${findings.length} finding(s))`);
    process.exit(1);
  }
  console.log("secret-scan: OK (no credential-like matches in repository-owned files)");
}
