[Reading 48 lines from start (total: 48 lines, 0 remaining)]

# P02-G3c — Store and Artwork Hardening

**Parent:** #11
**Canonical base:** `4470b136363a2df6d753925770ed91cfcbb87ac6`

## Goal

Finish P02 desktop identity without inventing Apple/Microsoft credentials or
relabeling donor artwork.

## Store/signing policy

Gomrey no longer accepts Presenton-prefixed signing or Store variables.
macOS signing uses canonical `GOMREY_*` inputs. MAS builds fail closed unless
an operator supplies a Gomrey-owned App ID, Team ID, matching provisioning
profile, and appropriate signing certificate.

Microsoft Store/AppX packaging stays disabled. electron-builder requires the
AppX publisher to match the certificate Subject, so a donor publisher cannot be
safely renamed. Re-enabling AppX requires a separately verified Gomrey-owned
Store identity and certificate.

The MAS entitlements retain only the capabilities Gomrey needs; the donor
application-group entitlement is removed.

## Artwork policy

No new binary logo is fabricated in this grain.

Default Electron packaging no longer points at imported Presenton icons, and
the imported package/icon sets are removed. Electron uses neutral defaults until
Gomrey-owned binary artwork is explicitly admitted.

The web splash no longer loads `Presenton_Splash.png`; it renders the Gomrey
wordmark directly in code while preserving the existing purple transition.

Presenton provider icons remain where they identify the Presenton provider.
Those are provider provenance, not Gomrey product branding.

## Qualification

- deterministic store/artwork identity tests;
- root/Next.js/Electron CI;
- Graft exact-range analysis;
- Alibaba Open Code Review delegation/host review;
- TypeSafe Jev exact-candidate review;
- exact-head GitHub Actions;
- normal merge commit only.

[executed on device: Abdulaziz (21c6d2a8-392c-4893-8a76-ab80c7e787c4)]

## Local qualification before commit

- Root repository suite: **30/30 PASS**.
- Next.js Gomrey internal/splash identity: **2/2 PASS**.
- `electron/build.js` syntax: PASS.
- Store/release identity JSON contracts: PASS.
- `git diff --check`: PASS.
- Live-reference scan found no active runtime/package reference to the deleted donor
  product-brand assets. Historical evidence and captured Playwright logs may still
  mention the old splash path; those are not runtime dependencies.
- Host semantic review under Alibaba Open Code Review v1.12.12 delegation rules
  found a real blocker: two MAS config entries still referenced the undefined
  `LEGACY_GOMREY_APP_ID`. The candidate was repaired to use the required
  `masAppId`, and a regression assertion now requires both MAS config entries
  to use that symbol.
- Graft v0.21.1 worktree build: SUCCESS; 49 changed files in 3 indexed areas,
  12 seed symbols, and no indexed dependent outside the changed files. Graft
  correctly cannot compute dependents for deleted binary artwork after the graph
  is rebuilt without those files.
- Alibaba Open Code Review v1.12.12 delegation preview selected 13 reviewable
  files from the 51-file pre-cleanup candidate and supplied JS/TS/package review
  rules. Binary assets/docs are outside its semantic parser coverage. No hosted
  OCR-model PASS is claimed.
- TypeSafe Jev `jev-1.13.0`: material-blocker signal **0.25** after the MAS
  repair. Risk triage selected `TEST_COVERAGE` with probability **1.00** and
  assigned zero probability to the listed signing/store/artwork/config risks.
  Exact-head CI is therefore the next mandatory gate.

## Exact-head requirement

Do not merge on local evidence alone. The committed candidate must pass the full
GitHub Actions workflow, including Electron source qualification and Next.js
tests/build/Cypress, before a normal merge commit.
