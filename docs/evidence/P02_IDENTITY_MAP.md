# P02 Identity and Compatibility Map

**Phase:** P02 — Gomrey identity and engineering baseline  
**Issue:** #6  
**Canonical base:** `a36b2a95bf3aa24c8f42ac00c977c6baed7ec2d7`  
**Policy:** classify before rename; never perform a blind global replacement.

## Classification

Every Presenton-derived identity occurrence is assigned one of four states:

- `RENAME_NOW` — Gomrey-owned product, package, container, app, log, documentation, or agent-facing identity.
- `COMPAT_ALIAS` — an existing external/runtime contract that must continue to work while a Gomrey canonical name is introduced.
- `DONOR_PROVENANCE` — source identity, legal notice, historical evidence, or attribution that must remain Presenton-identifiable.
- `THIRD_PARTY_CONTRACT` — a package, binary, release feed, asset, or other separately owned contract that must not be relabeled as Gomrey without separate admission and qualification.

The machine-readable contract is `product-identity.json`.

## RENAME_NOW surfaces

| Surface | Canonical Gomrey identity | Notes |
| --- | --- | --- |
| Root npm package | `gomrey` | Package metadata only; version remains inherited until P02-G4. |
| Next.js npm package | `gomrey-web` | Internal workspace identity. |
| FastAPI project | `gomrey-backend` | Lockfile editable package identity changes with it. |
| Electron npm package | `gomrey` | Desktop package metadata. |
| Electron product name | `Gomrey` | App-facing display identity. |
| Electron builder product metadata | `Gomrey` / `TheHalfMoon` | App ID, executable, artifact, and store identities remain deferred to G3. |
| Deployment template | Gomrey-owned image namespace only | P02-G4 must replace the non-deployable placeholder with an exact qualified release; donor `latest` is forbidden. |
| Repository metadata in package files | `https://github.com/TheHalfMoon/Gomrey` | No unverified commercial domain is invented. |
| MCP display name and user-facing instructions | `Gomrey` | Tool/API behavior is preserved. |
| Startup banner | `Gomrey` | File/function/ascii identity becomes Gomrey-owned. |
| User-visible Electron logs/errors | `Gomrey` | Environment compatibility names remain unchanged in G1. |
| Update-checker UI/User-Agent | `Gomrey` | Donor update feed is removed as the default. |

## COMPAT_ALIAS surfaces

The imported base exposes a large family of `PRESENTON_*` environment variables. They are external configuration contracts and are **not** blindly renamed in G1.

P02-G2 introduces canonical `GOMREY_*` variables at config boundaries with explicit fallback to the corresponding legacy `PRESENTON_*` variable. Precedence is:

```text
GOMREY_* explicit value
  -> PRESENTON_* legacy compatibility value
  -> documented default
```

No compatibility alias may silently override an explicitly supplied Gomrey value. Deprecation/removal requires a later versioned policy; P02 does not remove legacy variables.

Functions whose names encode Presenton but implement legacy compatibility, such as `get_presenton_public_url` or `is_presenton_electron_desktop`, may remain temporarily until the alias seam is introduced. Renaming symbols is not more important than preserving behavior.

The imported MCP request marker `X-Presenton-MCP-Request` is also a compatibility contract. P02-G2 introduces canonical `X-Gomrey-MCP-Request` handling while accepting the legacy marker during the migration window; G1 does not break the existing auth/middleware path.

## THIRD_PARTY_CONTRACT surfaces

### `@presenton/export-core`

The presentation export runtime is independently packaged under the Presenton namespace and is downloaded/synchronized from Presenton release infrastructure by the imported scripts.

P02 must not rename this package string to a fictitious `@gomrey/*` package. Until the export implementation is separately admitted/copied/replaced and qualified, these remain donor contracts:

- `@presenton/export-core`;
- Presenton export-core release asset names;
- Presenton export-core release repository URLs required to retrieve the pinned runtime;
- compatibility paths inside the imported runtime package.

This exception does **not** authorize unrelated Gomrey product surfaces to contact Presenton infrastructure.

### Electron updater

The imported Electron update checker points at Presenton's application `version.json` and download site. That is not a third-party runtime dependency; it is donor application infrastructure. A Gomrey-branded app must not poll it by default.

P02-G1 therefore makes automatic update checking opt-in until Gomrey has its own qualified release feed. An explicit Gomrey/update endpoint may be configured for development or future releases.

## DONOR_PROVENANCE surfaces

The following remain Presenton-identifiable and are excluded from brand-cleanup assertions:

- root `LICENSE` and `NOTICE` where donor/legal text requires preservation;
- `servers/fastapi/NOTICE`;
- `docs/donors/**`;
- `docs/SOURCE_LEDGER.md` donor records;
- P01 evidence and historical commit/revision references;
- historical or legal strings required to identify the exact copied source;
- third-party notice entries embedded in generated notice corpora.

Provenance is not stale branding.

## Deferred P02 identity surfaces

### P02-G2 — environment and configuration migration

- introduce `GOMREY_*` canonical variables;
- preserve legacy `PRESENTON_*` fallbacks;
- add precedence and parity tests;
- update compose/examples/docs without silently breaking existing deployments.

### P02-G3 — desktop/release identity

- choose and freeze Gomrey desktop app ID/bundle ID;
- signing/notarization/store identifiers;
- installer/executable/artifact names;
- app-data/cache/temp migration paths;
- binary icons and installer artwork;
- update-feed contract and rollback behavior.

The imported `com.presenton.presenton`, Microsoft Store identities, and donor signing variable names are not relabeled until this grain has migration evidence.

### P02-G4 — engineering/release baseline

- release version baseline;
- CI target-platform matrix;
- dependency/security scanning;
- SBOM generation and artifact retention;
- release artifact manifest/checksums;
- fixture/test-data policy;
- environment promotion/feature-flag baseline.

## G1 acceptance

P02-G1 is accepted only when:

1. owned package/product/MCP/startup identity is Gomrey;
2. no default Gomrey application path contacts Presenton's application updater/download infrastructure;
3. `@presenton/export-core` remains explicitly classified rather than falsely renamed;
4. donor legal/provenance material remains intact;
5. legacy `PRESENTON_*` contracts remain functional and intentionally deferred to G2;
6. identity contract tests pass;
7. baseline application CI remains green;
8. Graft, Alibaba OCR review evidence, and TypeSafe Jev are revision-bound to the exact candidate.
