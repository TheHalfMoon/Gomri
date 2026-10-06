# P02-G3b — Package and Release Identity

**Parent:** #11
**Canonical base:** `a351ecc2d56aff02cee62e48c4c8448e2a2206ab`

## Goal

Make Gomrey-owned non-store package, executable, release-metadata, log, and
observability identity canonical without pretending that donor Store/signing
credentials belong to Gomrey.

## Canonical identity

The machine-readable contract is
`config/desktop-release-identity.json`.

- non-store desktop app ID: `io.github.thehalfmoon.gomrey`
- product/executable/shortcut/uninstall name: `Gomrey`
- release artifact template: `Gomrey-${version}.${ext}`
- release repository: `TheHalfMoon/Gomrey`
- Sentry release prefix: `gomrey-electron`

electron-builder uses the top-level `appId` for macOS bundle identity and the
Windows NSIS Application User Model ID. MAS targets explicitly override the
app ID with the legacy donor identifier until G3c qualifies a Gomrey-owned
provisioning/store identity.

## Store boundary

G3b deliberately keeps these donor Store contracts unchanged:

- MAS app ID: `com.presenton.presenton`
- AppX identity/application ID: `PresentonAI.Presenton`
- existing Microsoft publisher identity
- default Windows packaging emits NSIS only; AppX stays disabled until G3c owns the Store identity
- existing signing/notarization environment variables and certificate handling

These values are compatibility/deferred contracts, not Gomrey branding.

## Telemetry boundary

The imported hardcoded Sentry DSN is removed. Gomrey desktop telemetry is
disabled by default and initializes only when an explicit DSN is configured.
`GOMREY_SENTRY_DSN` is canonical; generic `SENTRY_DSN` is accepted as a
fallback. This prevents an imported build from sending Gomrey runtime data to a
donor telemetry project by default.

## Release metadata

`electron/scripts/generate-version.cjs` and the checked-in
`electron/version.json` target Gomrey GitHub releases and Gomrey artifact
names. This does not enable automatic updates by itself; the G1 update checker
still requires an explicitly configured Gomrey update endpoint.

## Exclusions

G3b does not replace binary icons, installer artwork, the splash image, Store
publisher identity, provisioning profiles, signing certificates, or notarization
credentials. Those remain G3c work.

## Qualification

Before merge:

1. root identity tests must verify package, release, Store-boundary, and telemetry
   invariants;
2. Electron typecheck/build/main-global checks must pass;
3. Graft exact-range analysis must be bound to the final head;
4. Alibaba Open Code Review delegation/host review must cover the final range;
5. TypeSafe Jev must review the exact candidate;
6. exact-head GitHub Actions must be green;
7. normal merge commit only.

## Pre-push qualification evidence

- Final worktree targeted release/package tests: **8/8 PASS**.
- Root repository suite before the final telemetry/workflow boundary patch: **24/24 PASS**; the final patch is covered by the 8/8 targeted suite and exact-head CI remains mandatory.
- `git diff --check`: **PASS**.
- Local Electron dependency install was intentionally not recreated under severe C: disk pressure; no local TypeScript/build PASS is claimed. GitHub Actions installs the locked dependencies and is the exact-head merge gate.
- Graft v0.21.1 rebuilt the graph from the candidate: **9,017 nodes / 23,678 edges / 797 parsed files**. Worktree blast: **16 changed files / 5 areas / 19 seed symbols / 10 impacted symbols**.
- Alibaba Open Code Review v1.12.12 delegation preview selected **17/18** files as reviewable and supplied JavaScript/TypeScript/workflow security and correctness rules. Hosted LLM review is **not claimed**.
- Host semantic review under those delegated rules found no remaining donor telemetry endpoint, donor release repository target, unbounded Store identity relabel, or default mixed-identity AppX build.
- TypeSafe Jev model `jev-1.13.0`: material-blocker signal **0.18**. Final triage selected `NONE` with probability **0.62**; `TEST_COVERAGE` was the largest alternative at 0.20, so exact-head CI remains mandatory.
