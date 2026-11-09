# Gamma 5 Deep REA — 04: Real API Contracts, n8n Source, MCP and Limits

**As-of:** 2026-11-09. Evidence: current official Gamma help/developer references and actual 2026 Gamma-owned open-source package gamma-app/n8n-nodes-gamma, copied as a **source snapshot only** into third_party/gamma-public/n8n-nodes-gamma. This is **client code**, not Gamma's internal server, model, or agent prompt.

## 1. Two engines coexist

The public n8n client implements both Gamma 5 and classic. They have different request contracts and capability coverage.

| Capability | Gamma 5 Agent API | Classic API |
|---|---|---|
| Prompt / request type | a creative **brief**; conversational agent | structured text for presentation |
| Presentation | yes | yes |
| Document | yes | yes |
| Social post | yes | yes where supported |
| Webpage generation | **not direct Gamma5 agent format** | yes |
| Theme ID | not a Gamma5 generation input | yes |
| Classic text amount/mode/split | unsupported, rejected | yes |
| Additional instructions | yes | yes (different schema) |
| Template | optional Gamma5 brief reference | classic template remix |
| Multi-page file generation | not same legacy operation | classic supports up to 50 pages for some formats |
| Async job | yes, generationId | yes, generationId |
| Edit an existing page | separate Gamma5 Agent edit operation | legacy generation not equivalent |

**Source:** https://github.com/gamma-app/n8n-nodes-gamma/blob/main/README.md and file nodes/Gamma/actions/generation/create.operation.ts. A user choosing "Classic" does not mean Gamma5 removed legacy functionality.

## 2. Source-level operations — all implemented by public n8n node

| Resource | Operations confirmed in README/code | Gomri analogue |
|---|---|---|
| Generation | Create with Gamma5, Create Classic, Create From Template, Create Multi-Page, Get Status | typed generate + durable jobs |
| Gamma File | Search, Get, Edit, Get Edit Status, Export, Archive, Delete | artifact search/read/edit/export/lifecycle |
| Export | Get Status | durable export job |
| Theme | List | brand/theme catalog |
| Folder | List | workspace/folder catalog |
| User | Get user information | authenticated account/capability limits |
| Image | Create, Get Status, Archive Media | bounded media generation and storage |
| Comment | Get Many | collaboration comment list |
| Analytics | Get Document, Get Cards, Get Many Viewers, Get Viewer | viewer engagement metrics |

The public code does not prove that all actions work for every account, role, plan or current API release. Test them only where user is authorized and credit costs are acceptable.

## 3. Observed request lifecycle

**Gamma5 Create** source: nodes/Gamma/actions/generation/index.ts, create.operation.ts.

    POST /v1.0/agent/generations
      -> generationId
      -> poll status until completed | failed
      -> file ID / gamma URL / optional export URL

**Gamma5 Edit** source: nodes/Gamma/actions/gamma/index.ts and current official help:

    POST /v1.0/agent/gammas/{gammaId}/edits
      -> editId
      -> GET /v1.0/agent/edits/{editId}

The edit API documents constraints: one target page per edit; cannot add pages via this operation; no two simultaneous edits on the same page. Do **not** infer that every edit inside Gamma's private interactive UI has these same API limitations.

**Gamma Export:** initiate export to PPTX/PDF/PNG, then poll. File IDs commonly begin with g_. Some operations also accept document URL slug while Archive/Delete require file ID; passing a slug to delete may fail with 403. Use source-level typed resource identifiers rather than guessing.

Official: https://help.gamma.app/en/articles/11962420-does-gamma-have-an-api

## 4. Async and error behavior — copied source reveals practical semantics

Gamma's n8n README documents:
- generation with Gamma5 may take up to approximately 25 minutes; generation plus export can extend to approximately 40 minutes;
- creating a second job on a delayed response may duplicate output; poll the **original** generationId;
- excess concurrent workspace jobs can return 429 with Retry-After 60 seconds;
- n8n example polls every ~5 seconds in a loop, not indefinite blind create retries;
- requests use Gamma API key in X-API-KEY header; workspace-scoped credits apply;
- OAuth is a future option in that public n8n integration, not implemented there.

These are operational claims in publicly published client code/README, not independently exercised during this session. **No Gamma API key was read, copied, created, or used** and no credits charged by this REA.

### Gomri design rule

Use:
- jobId, idempotencyKey, expectedRevision and source digest;
- typed result states queued/running/completed/failed/cancelled;
- Retry-After aware backoff, status polling, cancellation/recovery;
- server-side per-slide mutation locking or revision conflicts;
- never assume 429 means safe to generate another deck.

All of these can be implemented locally using Gomri durable jobs and current Presenton editor; Gamma remote API should NOT become a mandatory Gomri dependency.

## 5. API configuration matrix from actual client

Gamma5 Create takes prompt and format (presentation/document/social), quality/effort options, card/page count where accepted, optional template reference, source URLs, additional instructions, connector controls and export format. Classic exposes text mode, amount, tone, language, audience, themes, card splitting, 16:9 and alternate card dimensions, header/footer and some external sharing options.

**Do not transfer classic-only fields to Gamma5**: the public node intentionally hides/rejects incompatible parameters. This matters to Gomri's own versioned generator APIs: unsupported fields should be validated as errors, not silently ignored.

Source: https://github.com/gamma-app/n8n-nodes-gamma/blob/main/nodes/Gamma/actions/generation/create.operation.ts

## 6. Dynamic model/language enums — a major engineering lesson

The Gamma-owned n8n package includes scripts/sync-api-enums.mjs and nodes/Gamma/apiEnums.ts. CI compares generated option enums against published developer reference material, including image models, supported languages and card dimensions. The changelog reports schema drift when values were manually copied, then introduces a generated-source check.

Gomri should expose one authoritative schema for model/image providers, locales, aspect ratios, export targets and optional flags. SDK/MCP/CLI/UI enums should be generated from it and CI should fail on drift. This is a safer reusable pattern than copying dozens of hard-coded options.

**Interesting but limited insight:** the client also mentions GET /v1.0/me as a useful yet undocumented endpoint and returns account limits in tests. It was independently verified by upstream authors in Aug 2026, **not by us**, and may change without stability guarantees. Never treat it as a durable public API for Gomri.

## 7. Gamma's MCP is distinct from this n8n package

Gamma advertises an MCP integration and connection to external assistants. Its API and MCP workflows can expose generation/search/edit/export/comment/analytics under user- or workspace-scoped permissions. However the public n8n node is a REST client, **not a dump of Gamma's private MCP server implementation**.

Source:
- https://help.gamma.app/en/articles/13943863-how-do-i-use-gamma-with-outbound-connectors-and-integrations
- https://developers.gamma.app

Product and plan restrictions differ for Enterprise API editing, Free credits, agent generation and external access. An integration advertised in Gamma marketing is not proof it is available in this user's Free workspace.

## 8. API documentation drift

A historical Gamma developer page still says editing existing Gamma through API is not available. Current 2026 Gamma help and n8n code expose edit routes. Treat the older page as stale; document page version and date. A robust REA has a conflict log with latest operation source, source version, last tested date and plan requirements.

## 9. Actual source status inside Gomri

The following snapshots are already imported, each with exact upstream SHA and preserved licenses:
- n8n-nodes-gamma @ 5d0b466a9ae4be994a722577daa0a761cb28cfaf (MIT; 54 files).
- aijsx @ 2900075d8251b7a83c6b855fcf36e6df4c5d2539 (MIT; 39 files; **historical** Gamma-owned derivative of Fixie AI JSX-based prompt composition).
- pptx-renderer @ 68cb570940fb28d5c4628f31d1365016c4483521 (Apache-2.0; 381 files; **fork** of aiden0z, not Gamma authored).

These source snapshots are **not imported into the running product** or validated at runtime. They reveal actual client/helper implementations and afford copy-first development, but not proprietary Gamma 5 LLM agent source.

Source admission register: ../../third_party/gamma-public/SOURCE_REGISTER.md

## 10. High-value API acceptance tests for Gomri

1. Submit one generation; preserve jobId on retry, never create duplicate.
2. Submit duplicate idempotency key; get same canonical output.
3. Edit one slide; other slides remain byte/semantically stable.
4. Edit two different slides concurrently; no lost updates.
5. Edit same slide concurrently; explicit conflict/serialization.
6. Unknown generation format or classic-only param on Agent endpoint: schema error.
7. Workspace viewer never gains write via MCP.
8. Failed export must be visible, retriable and never serve partial file as complete.
9. Queue congestion/429 uses backoff and preserves task receipts.
10. Public API, MCP, UI and CLI share the same canonical Deck IR mutations.
11. Export to PPTX/PDF/image preserves source claims, permissions and flattening disclosure.
12. Local provider disabled/offline: deterministic failure or local fallback, no silent paid API invocation.

**Status:** public API source inspected and staged. No live Gamma API use or spend; no Gomri endpoint parity claimed.
