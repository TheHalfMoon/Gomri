# Gomrey Canonical Architecture

**Status:** FOUNDATION PLAN  
**Date:** 2026-10-05

## 1. Architectural objective

Gomrey is an **agent-first, evidence-grounded creation and knowledge platform**. Humans and AI agents operate over the same core capabilities. The human UI is a client of those capabilities, not a privileged implementation path.

The system must:

- reuse mature donor implementation whenever it is safer/faster than rebuilding;
- ingest heterogeneous, very large source collections without silent loss;
- preserve exact provenance from original source to extracted span to retrieved evidence to generated claim to final artifact;
- support NotebookLM-class source workflows plus deeper web/video/multimodal understanding;
- create editable artifacts, not screenshots pretending to be editable documents;
- expose first-class MCP/API/A2A/plugin surfaces;
- use Jev-class typed decisions for bounded probabilistic choices while keeping policy/authority deterministic;
- remain useful with local/self-hosted providers and without a mandatory hosted inference backend.

## 2. System shape

```text
+--------------------------------------------------------------------------------+
|                              User / Agent Clients                               |
| Web UI | Desktop | API SDKs | MCP Hosts | A2A Agents | CLI | Browser Extension |
+--------------------------------------+-----------------------------------------+
                                       |
                                       v
+--------------------------------------------------------------------------------+
|                         Identity / Workspace / Policy                           |
| Auth | org/workspace | roles/scopes | approvals | budgets | secrets | audit     |
+--------------------------------------+-----------------------------------------+
                                       |
                                       v
+--------------------------------------------------------------------------------+
|                              Gomrey Control Plane                               |
| Source Gateway | Job Engine | Knowledge | Creation | Agent Platform | Plugins   |
+-----------+------------------+----------------+-------------------+---------------+
            |                  |                |                   |
            v                  v                v                   v
+-------------------+ +------------------+ +------------------+ +------------------+
| Source/Document IR| | Retrieval Fabric | | Artifact Compiler| | Decision Fabric  |
| provenance/spans  | | lexical/semantic | | narrative/design | | typed/calibrated |
| tables/visuals    | | visual/graph     | | render/export    | | abstain/route    |
+---------+---------+ +---------+--------+ +---------+--------+ +---------+--------+
          |                     |                    |                    |
          +---------------------+--------------------+--------------------+
                                |
                                v
+--------------------------------------------------------------------------------+
|                             Verification / Assurance                            |
| citations | claims | numbers | layout | brand | security | provenance | policy  |
+--------------------------------------+-----------------------------------------+
                                       |
                                       v
+--------------------------------------------------------------------------------+
|                          Canonical Storage / Projections                         |
| metadata DB | content-addressed blobs | job ledger | source snapshots | indexes  |
| FTS/BM25 | vectors | visual index | graph | caches | artifact revisions          |
+--------------------------------------------------------------------------------+
                                       |
                                       v
+--------------------------------------------------------------------------------+
|                         Bounded Workers / External Adapters                      |
| Docling | PaddleOCR | MinerU | Crawl4AI | yt-dlp | Whisper | render/export       |
| local models | remote model adapters | connectors | MCP servers | publish targets |
+--------------------------------------------------------------------------------+
```

## 3. Core architectural rule: canonical vs rebuildable

Canonical state includes:

- source identity, original bytes/reference, digest, rights/access metadata;
- source-unit accounting and ingestion job truth;
- normalized Source IR and exact evidence spans where admitted;
- workspace/permission/policy state;
- artifact semantic revisions and edit history;
- immutable/append-oriented decision, verification, and audit receipts;
- plugin/connector identities and granted scopes.

Rebuildable projections include:

- FTS/BM25 index;
- dense vector index;
- visual/multimodal index;
- graph projections;
- caches;
- summaries;
- thumbnails/previews;
- derived search facets.

A projection may be deleted and rebuilt from canonical state. A vector similarity score never becomes canonical truth.

## 4. Gomrey Source IR

Every source type normalizes into a Gomrey-owned model rather than leaking donor-specific parser objects throughout the product.

```text
SourceArtifact
  source_id
  source_type
  original_uri/reference
  original_digest
  title/authors/timestamps
  mime/languages
  rights/access class
  parser/transcriber identities
  ingestion manifest
  units[]
  relationships[]
  warnings[]
```

A `SourceUnit` is the smallest independently accountable structural unit appropriate to the source:

- PDF/document: page/section/slide/sheet;
- web: page/DOM section/linked resource;
- YouTube/video: time segment/scene/keyframe/chapter;
- audio: timestamped transcript segment;
- spreadsheet: workbook/sheet/range/table;
- image: region/object/text span;
- connector source: provider-native revision/item.

Derived structures include:

```text
EvidenceSpan
  source_id
  source_unit_id
  page/time/sheet coordinates
  text offsets where stable
  bounding region where visual
  extracted digest
  parser/OCR/transcriber identity
  confidence/quality observations
```

Tables, figures, charts, formulas, annotations, links, headings, lists, code blocks, and media references remain typed objects rather than flattened strings whenever possible.

## 5. No-silent-loss ingestion contract

A source is not “processed” because a parser returned text.

Every ingestion produces a durable manifest:

```text
declared_units
observed_units
accounted_units
verified_units
uncertain_units
failed_units
skipped_units_with_reason
duplicate_units
silent_drop_count
```

Completion requires:

```text
accounted_units == declared_or_reconciled_units
silent_drop_count == 0
```

Every unit ends in an explicit terminal or resumable state. A 1,000-page document with 997 successful pages and three unresolved pages is **not** silently reported as fully parsed; it is an explicitly partial result with exact unresolved coordinates.

## 6. Durable Job Engine

Long work is represented by durable jobs and stages, borrowing proven patterns from founder sibling work and donor systems.

Properties:

- stable job and stage-attempt identity;
- idempotency keys;
- bounded retries with permanent-vs-transient classification;
- crash-safe checkpoints;
- exact input/artifact baseline identity;
- reconciliation of ambiguous outcomes;
- cancellation/deadlines;
- resumability without starting from zero;
- per-stage resource and capability budgets;
- task progress suitable for MCP Tasks/API streaming/UI.

No non-idempotent effect is silently retried after an ambiguous completion state.

## 7. Source Gateway and hostile-input boundary

All external/untrusted sources enter through a bounded gateway.

Controls include:

- MIME/content sniffing and extension reconciliation;
- archive/decompression/page/size limits;
- path traversal and active-content denial;
- external-resource/network policy;
- SSRF/DNS/redirect protections for web acquisition;
- parser worker isolation;
- cancellation/time/memory/CPU budgets;
- content digesting before and after transformations;
- malware/supply-chain hooks where applicable;
- prompt-injection/taint metadata that does not magically disappear after summarization.

Workers do not receive the workspace database handle, vault master keys, or ambient outbound network by default.

## 8. Document and OCR pipeline

The default strategy is a **router + parser ensemble**, not one universal parser.

```text
source/page
  -> deterministic preflight
  -> cheap classification
  -> default parser (Docling-class)
  -> OCR/layout worker when needed
  -> secondary parser for disagreement/high-risk regions
  -> structural reconciliation
  -> Gomrey Source IR
  -> quality/coverage verification
```

PaddleOCR-class workers cover multilingual/scanned/table/formula/chart workloads. MinerU-class workers are optional difficult-document challengers. Existing Presenton LiteParse paths remain usable until benchmarked replacements prove superior.

Arabic/English mixed content is a P0 qualification target, not a later localization task.

## 9. Web pipeline

A web source is more than body text.

Candidate acquisition flow:

```text
URL
 -> network/security admission
 -> fetch/browser render as required
 -> canonical URL + retrieval timestamp + content digest
 -> DOM/semantic sections
 -> images/tables/charts/code/linked docs
 -> optional sitemap/domain crawl under explicit scope
 -> screenshots/visual regions when useful
 -> Source IR + relationship graph
```

Crawl4AI-class code is the preferred current donor path. Child-page traversal must be explicit and bounded; a page cannot silently expand into an unbounded crawl.

## 10. YouTube/video/audio pipeline

YouTube is not transcript-only by default.

```text
video URL
 -> metadata/chapters/subtitles
 -> audio acquisition (when permitted)
 -> transcript/ASR
 -> scene detection
 -> keyframes
 -> visual OCR/VLM analysis
 -> timestamp/source-span alignment
 -> Video Source IR
```

Degraded modes such as transcript-only are explicitly labeled.

## 11. Connector architecture

Connectors normalize provider-native changes into source snapshots while preserving provider identity and permissions.

Required properties:

- initial sync + incremental cursor/change sync;
- deletion/tombstone propagation;
- provider-native revision identity;
- ACL/permission mapping where available;
- backoff/rate-limit handling;
- credential isolation;
- explicit source scope;
- sync receipts and stale-state detection;
- no “connected” state implying unrestricted workspace authority.

SurfSense and Onyx CE are primary donor pools for these patterns.

## 12. Retrieval Fabric

Gomrey retrieval is layered. Vector search is not the entire RAG system.

```text
scope/ACL filter
 -> exact identifier/location lookup
 -> lexical FTS/BM25/grep-style retrieval
 -> metadata/structure retrieval
 -> dense semantic candidates
 -> visual/multimodal candidates
 -> optional graph/global-local candidates
 -> fusion
 -> reranking
 -> diversity/authority/freshness constraints
 -> evidence resolver
 -> sufficiency/contradiction check
```

The cheapest trustworthy signal should be used before escalating to expensive models. Missing vector models must not make exact/lexical search unusable.

## 13. Evidence Bundle

Generation receives a bounded, inspectable `EvidenceBundle`, not an arbitrary dump of retrieved chunks.

It binds:

- exact source revisions;
- selected evidence spans;
- ranking/retrieval identities;
- contradictions;
- omissions/truncation;
- source freshness;
- permission scope;
- bundle digest;
- verification state.

Answers/artifacts can therefore be reproduced or audited against the exact evidence set.

## 14. Claim and citation model

Material generated claims should be linkable to support evidence.

Support states include:

```text
SUPPORTED
PARTIALLY_SUPPORTED
CONTRADICTED
DOES_NOT_ESTABLISH
UNRESOLVED
SOURCE_UNAVAILABLE
```

Citation locators are source-specific:

- PDF/document: page + paragraph/table/cell/region;
- web: URL + retrieval snapshot + DOM/section locator;
- video: video ID + timestamp + transcript span + optional scene/keyframe;
- spreadsheet: workbook/sheet/range/table/cell;
- image: region/bounding box.

A citation ID that cannot resolve back to its source location is broken evidence.

## 15. Decision Fabric

Gomrey uses a provider-neutral Jev-class typed decision subsystem for bounded choices, scoring, ranking, and abstention. See `JEV_BUILD_POLICY.md`.

Hard deterministic policy remains authoritative. Confidence is evidence, not permission.

## 16. Creation and Artifact IR

The Presenton-derived application provides the initial working generation/editor/export stack. Gomrey progressively separates content semantics from rendering so one evidence-backed narrative can create multiple artifact types.

```text
EvidenceBundle
   -> Narrative IR
   -> Artifact intent
   -> Design IR / layout plan
   -> Renderer/exporter
      -> presentation
      -> document/report
      -> website
      -> infographic/social
      -> images/PDF/PPTX/etc.
```

Generated visual artifacts retain editable semantic elements where the target format allows it. The system must not flatten editable charts/text to images merely for implementation convenience unless the user explicitly chooses a rasterized export.

## 17. Artifact revision model

Artifacts are versioned and agent-safe:

- stable artifact/revision identities;
- optimistic expected-revision checks;
- idempotent mutation keys;
- structured diffs;
- undo/history;
- branch/merge semantics for concurrent agent work where useful;
- citations/evidence links versioned with the content they support.

## 18. Agent Platform

Every load-bearing capability exposes a structured agent surface. MCP is first-class and must track the current final specification supported by the implementation; long-running calls use the MCP Tasks extension where supported. A2A support exposes Gomrey as an autonomous specialist to agent networks. Plugins/skills/connectors are capability-bounded. See `AGENT_PLATFORM.md`.

## 19. Plugin runtime

A plugin may package skills, templates, connectors, evaluators, MCP configuration/tools, and artifact rules, but it cannot bypass capability policy.

Plugin code is untrusted by default and requires:

- declared permissions;
- exact package identity/digest;
- sandbox or bounded host APIs;
- explicit network/filesystem/secret grants;
- update provenance;
- install/disable/remove lifecycle;
- compatibility contract.

## 20. Human-agent parity rule

A product capability is not complete if it exists only in a GUI.

For every core capability, define:

1. domain contract;
2. human UI surface where needed;
3. structured API/MCP/A2A surface;
4. permissions/scopes;
5. idempotency/revision semantics for mutations;
6. structured result/error model;
7. audit/evidence behavior.

The inverse also applies: agent-only high-risk powers must not bypass policy merely because no UI button exists.

## 21. Identity, auth, permissions and approvals

The control plane separates:

- user/agent/service principal;
- organization/workspace;
- role;
- OAuth/API token/session identity;
- connector credential handle;
- plugin identity;
- delegated capability grant.

Core scopes include source read/write, knowledge search/research, artifact read/create/edit/publish, connector management, plugin install/admin, and workspace administration.

High-impact actions such as external publishing, destructive deletion, credential changes, or broad connector grants can require explicit approval policy.

## 22. Storage

The exact initial store may inherit from the imported base, but the architecture requires narrow repositories/contracts so storage can evolve without rewriting domain logic.

Required data classes:

- workspace/auth metadata;
- source and source-unit manifests;
- content-addressed blobs/assets;
- job/stage ledger;
- Source IR/evidence spans;
- retrieval projections;
- Decision Fabric receipts/calibration refs;
- artifact semantic revisions;
- plugin/connector registry;
- audit/evidence ledger.

No index service, graph server, or vector server is mandatory until benchmarks prove the need.

## 23. Model/provider routing

Generative, embedding, reranking, visual, ASR, OCR, and decision models use provider-neutral contracts.

Routes account for:

- task type and quality profile;
- local/remote privacy mode;
- language;
- latency/cost/resource budget;
- context/input modality;
- model capability and measured benchmark profile;
- user/provider policy;
- degraded/offline behavior.

No silent cloud fallback is permitted in a local-only policy.

## 24. Verification and repair loop

Artifact completion is proof-based:

```text
generate/edit
 -> structural validation
 -> citation/claim checks
 -> numeric/date/unit checks
 -> layout/overflow checks
 -> brand/accessibility checks
 -> source-coverage checks
 -> security/policy checks
 -> repair candidate
 -> re-verify
 -> PASS | NEEDS_REVIEW | ABSTAIN/BLOCKED
```

The generator does not grade itself as sufficient evidence.

## 25. Observability and audit

Record structured events for:

- source acquisition/ingestion;
- parser/model/provider identity;
- job lifecycle/retries;
- retrieval/evidence selection;
- decision outputs and calibration refs;
- artifact mutations;
- connector/plugin actions;
- publish/export operations;
- approvals/denials.

Logs must redact secrets and avoid dumping unrestricted private source content by default.

## 26. Reliability target

The reliability promise is **100% source-unit accounting**, not impossible claims of 100% OCR semantic accuracy.

For large inputs, Gomrey must be able to prove which units succeeded, remain uncertain, failed, were skipped for a declared reason, or were retried. No unit disappears silently.

## 27. Architecture anti-goals

Gomrey must not become:

- a blind concatenation of donor repositories;
- a UI that hides an ungoverned Python service fleet;
- vector-search-only “RAG”;
- a cloud-only product with fake local mode;
- a presentation generator whose agents must click the UI;
- a probabilistic system where confidence grants authority;
- a plugin ecosystem with ambient filesystem/network/secrets access;
- a product whose “done” state means only that an LLM returned output.
