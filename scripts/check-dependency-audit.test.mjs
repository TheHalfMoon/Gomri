import assert from "node:assert/strict";
import test from "node:test";
import { checkAudit, extractAdvisoryIds } from "./check-dependency-audit.mjs";

test("advisory extraction finds GHSA identifiers in npm audit output", () => {
  const ids = extractAdvisoryIds({ vulnerabilities: { x: { via: [{ url: "https://github.com/advisories/GHSA-abcd-1234-efgh" }] } } });
  assert.deepEqual(ids, ["GHSA-abcd-1234-efgh"]);
});

test("audit checker fails on non-allowlisted advisories and expired entries", () => {
  const audit = {
    vulnerabilities: {
      foo: { severity: "high", range: "<=1.0", via: [{ url: "https://github.com/advisories/GHSA-new0-0000-0000" }] },
    },
  };
  const empty = checkAudit("root", audit, { entries: [] }, "2026-10-07");
  assert.ok(empty.errors.some((error) => error.includes("GHSA-new0-0000-0000")));

  const expired = checkAudit(
    "root",
    audit,
    { entries: [{ id: "GHSA-new0-0000-0000", review_by: "2026-01-01" }] },
    "2026-10-07",
  );
  assert.ok(expired.errors.some((error) => error.includes("expired")));
});

test("audit checker passes allowlisted advisories and flags stale entries", () => {
  const audit = {
    vulnerabilities: {
      foo: { severity: "high", range: "<=1.0", via: [{ url: "https://github.com/advisories/GHSA-keep-0000-0000" }] },
    },
  };
  const allowlist = {
    entries: [
      { id: "GHSA-keep-0000-0000", review_by: "2027-04-05", surfaces: ["root"] },
      { id: "GHSA-gone-0000-0000", review_by: "2027-04-05", surfaces: ["root"] },
      { id: "GHSA-other-0000-0000", review_by: "2027-04-05", surfaces: ["electron"] },
    ],
  };
  const result = checkAudit("root", audit, allowlist, "2026-10-07");
  assert.ok(result.errors.some((error) => error.includes("stale allowlist entry GHSA-gone-0000-0000")));
  assert.ok(!result.errors.some((error) => error.includes("GHSA-keep-0000-0000 is not allowlisted")));
  assert.ok(!result.errors.some((error) => error.includes("GHSA-other-0000-0000")));
});
