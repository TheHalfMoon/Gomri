import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

export function extractAdvisoryIds(auditJson) {
  const text = typeof auditJson === "string" ? auditJson : JSON.stringify(auditJson);
  const ids = new Set();
  for (const match of text.matchAll(/GHSA-[a-z0-9-]{4,}/g)) {
    ids.add(match[0]);
  }
  return [...ids].sort();
}

export function collectTransitiveIds(name, vulnerabilities, seen = new Set()) {
  if (seen.has(name)) return [];
  seen.add(name);
  const entry = vulnerabilities[name];
  if (!entry) return [];
  const ids = [];
  for (const via of entry.via ?? []) {
    if (typeof via === "string") {
      ids.push(...collectTransitiveIds(via, vulnerabilities, seen));
    } else if (via?.url) {
      const match = via.url.match(/GHSA-[a-z0-9-]+/);
      if (match) ids.push(match[0]);
    }
  }
  return [...new Set(ids)];
}

export function checkAudit(severity, auditJson, allowlist, today = new Date().toISOString().slice(0, 10)) {
  const errors = [];
  const vulnerabilities = auditJson?.vulnerabilities ?? auditJson?.advisories ?? {};
  const relevant = [];
  for (const [name, entry] of Object.entries(vulnerabilities)) {
    const entrySeverity = entry?.severity;
    if (entrySeverity !== "critical" && entrySeverity !== "high") continue;
    const ids = collectTransitiveIds(name, vulnerabilities);
    relevant.push({ name, severity: entrySeverity, range: entry.range ?? "", ids });
  }
  const allowed = new Map(
    (allowlist?.entries ?? [])
      .filter((entry) => !entry.surfaces || entry.surfaces.includes(severity))
      .map((entry) => [entry.id, entry]),
  );
  for (const item of relevant) {
    const ids = item.ids.length > 0 ? item.ids : [`NO-ADVISORY-ID:${item.name}@${item.range}`];
    for (const id of ids) {
      const entry = allowed.get(id);
      if (!entry) {
        errors.push(`${severity}/${item.name}: ${id} is not allowlisted`);
        continue;
      }
      if (entry.review_by && entry.review_by < today) {
        errors.push(`${severity}/${item.name}: allowlist entry ${id} expired on ${entry.review_by}`);
      }
    }
  }
  const observed = new Set(relevant.flatMap((item) => (item.ids.length > 0 ? item.ids : [])));
  for (const entry of allowed.values()) {
    if (!observed.has(entry.id) && !entry.keep_if_absent) {
      errors.push(`stale allowlist entry ${entry.id}: advisory no longer reported; remove or set keep_if_absent`);
    }
  }
  return { errors, relevantCount: relevant.length };
}

export async function loadAllowlist(root = repoRoot) {
  const raw = await readFile(path.join(root, "config/security-allowlist.json"), "utf8");
  return JSON.parse(raw);
}

const isMain = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  const [surface, auditPath] = process.argv.slice(2);
  if (!surface || !auditPath) {
    console.error("usage: node scripts/check-dependency-audit.mjs <surface> <audit-json-path>");
    process.exit(2);
  }
  const [auditRaw, allowlist] = await Promise.all([
    readFile(path.resolve(auditPath), "utf8"),
    loadAllowlist(),
  ]);
  const { errors, relevantCount } = checkAudit(surface, JSON.parse(auditRaw), allowlist);
  if (errors.length > 0) {
    for (const error of errors.slice(0, 50)) console.error(`dependency-audit: ${error}`);
    console.error(`dependency-audit: FAIL (${errors.length} issue(s) across ${relevantCount} high/critical package(s))`);
    process.exit(1);
  }
  console.log(`dependency-audit: OK (${surface}: ${relevantCount} high/critical package(s) all allowlisted)`);
}
