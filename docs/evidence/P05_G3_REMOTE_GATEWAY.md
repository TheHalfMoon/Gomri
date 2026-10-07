# P05-G3 — Remote Source Gateway

**Parent:** #33
**Issue:** #36
**Canonical base:** `2da02c4e73f952c58a647d1ed29d3e8ae15725d0` (P05-G2 merged)

## Goal

URL ingestion that cannot become an SSRF primitive: strong URL policy,
DNS-rebinding-safe authorization, bounded redirects, remote budgets, and
a tainted fetch contract.

## Scope

- `servers/fastapi/gomrey/remote_gateway.py`: scheme allowlist (https
  default, http explicit opt-in, file/ftp/data/javascript never);
  credential-bearing URL denial; literal-IP SSRF classification
  (loopback, RFC1918, link-local incl. metadata address, unique-local,
  unspecified, multicast, reserved, IPv4-mapped IPv6 unwrapped);
  internal-name denial (localhost, single-label, .internal/.local,
  metadata hostnames); `resolution_required` + `authorize_fetch` DNS
  pinning contract; `validate_redirect_chain` (max 5, pinned hops only,
  no https downgrade, budget-backed); `enforce_remote_budgets`;
  `normalized_fetch_result` carrying `untrusted_origin` taint and
  `data-not-instructions` treatment. Pure logic, never fetches, no new
  deps (stdlib ipaddress/urllib only).
- `servers/fastapi/tests/test_gomrey_remote_gateway.py`: 7 tests
  (15 hostile literal IPs, internal names/schemes, credentialed URLs,
  https default/opt-in, rebinding pin denial, redirect attacks, budget
  exhaustion).
- Package exports extended.

## Out of scope

The actual fetcher worker and browser-render path (P07), parser
normalization (G4), file bytes (G2).

## Local qualification before commit

- `py_compile` on new/changed files: PASS.
- Gomrey-scoped pytest (10 modules incl. new remote_gateway): 59 PASS.
- Root Node suite: 48 PASS. `git diff --check`: PASS.
- Full FastAPI suite runs in exact-head CI (pre-existing env gap).
- Graft ask/workflow standing: grain additive over gateway/budgets.
- TypeSafe Jev `jev-1.13.0` (real): SSRF-risk 0.07, taint-loss 0.11.
  No blocking signal.
- PStack: still no canonical install; `PSTACK_NOT_EXECUTED`.
- Alibaba OCR: no OCR workflow in this repository; hosted OCR not
  executable. Delegation: exact-diff manual review of the 3 reviewable
  files; no BLOCKING findings; not a hosted PASS.
- Dependabot disabled (403); code scanning no analysis (404). Recorded.

## Review findings

- Delegation review: single-label deny may refuse odd-but-public
  intranet-style names — intended fail-closed direction for a gateway;
  allowlisting belongs to later connector policy, NOT_APPLICABLE now.
- Delegation review: `authorize_fetch` re-checks https instead of
  trusting the verdict object — defense-in-depth, NOT_APPLICABLE.
- Unresolved material findings: 0.

## Exact-head requirement

Do not merge on local evidence alone. The committed candidate must pass
the full GitHub Actions workflow, including FastAPI pytest with the new
remote_gateway module, before a normal merge commit.
