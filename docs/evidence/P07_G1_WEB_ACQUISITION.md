# P07-G1 — Bounded Web Acquisition

**Parent:** #53
**Issue:** #54
**Canonical base:** `4df2783df46fd89138f40690cd5941dd2cb706f4` (P06 exit merged)

## Goal

Crawl plans as explicit, budgeted, auditable permissions: same-origin by
default, named expansion only, depth/page bounds that cannot silently
grow, per-page retrieval snapshots, and recorded robots/terms decisions.

## Scope

- `servers/fastapi/gomrey/web_acquisition.py`: `CrawlScope` /
  `plan_crawl` (seed classification, bound ceilings, domain/sitemap
  validation — planning only, never visiting); `admit_child`
  (same-origin default, suffix-anchored subdomain rule, DNS pinning for
  hostnames, cap-before-spend ordering, idempotent revisits, visited
  tracking); `page_snapshot` (canonical URL, origin, digest, taint);
  `acquisition_policy` (fetch-unless-disallowed with unknown-flagging,
  redistribution-denied-by-default, reasoned). Pure logic, never
  fetches, no new deps.
- `servers/fastapi/tests/test_gomrey_web_acquisition.py`: 4 tests
  (plan/admit/revisit, scope-escape + pinning, depth/page bounds,
  snapshot taint + policy matrix).
- Package exports extended.

## Out of scope

Fetcher/render workers, media pipeline (G2), connector sync (G3).

## Local qualification before commit

- `py_compile` on new/changed files: PASS.
- Gomrey-scoped pytest (16 modules incl. new web_acquisition): 87 PASS.
- Root Node suite: 48 PASS. `git diff --check`: PASS.
- Full FastAPI suite runs in exact-head CI (pre-existing env gap).
- Graft standing: additive over remote_gateway/budgets.
- TypeSafe Jev `jev-1.13.0` (real): first expansion probe 0.27.
  Audit found two real soft spots — budget spent before the page-cap
  check, revisits double-spending. Fixed (cap-first, idempotent
  revisits, pinned by test); re-probe 0.09. Terms probe 0.09.
- PStack: still no canonical install; `PSTACK_NOT_EXECUTED`.
- Alibaba OCR: no OCR workflow in this repository; hosted OCR not
  executable. Delegation: exact-diff manual review; no BLOCKING
  findings; not a hosted PASS.
- Dependabot disabled (403); code scanning no analysis (404). Recorded.

## Review findings

- Jev-driven fixes above (spend order, revisit idempotency) — FIXED,
  re-probed 0.09.
- Unresolved material findings: 0.

## Exact-head requirement

Do not merge on local evidence alone. The committed candidate must pass
the full GitHub Actions workflow, including FastAPI pytest with the new
web_acquisition module, before a normal merge commit.
