# Gomrey Master Implementation Plan

**Status:** FOUNDATION PLAN  
**Date:** 2026-10-05  
**Execution style:** copy-first, evidence-first, dependency-ordered, exact-revision qualification.

## 1. Product definition

Gomrey is the creation and knowledge layer for humans and AI agents. It combines:

- Gamma/Presenton-class artifact creation and editing;
- NotebookLM-class source notebooks and grounded answers;
- deep multimodal ingestion for documents, web, audio, video, images and structured data;
- durable large-source processing with zero silent source-unit loss;
- layered lexical/semantic/visual/graph retrieval;
- Jev-class typed decision and abstention fabric;
- exact citations and post-generation claim verification;
- MCP, A2A, REST/SDK and plugin/skill interfaces;
- editable presentation/document/site/graphic outputs.

The user should be able to provide a prompt, a handful of sources, or thousands of pages and trust Gomrey to account for the work, surface uncertainty explicitly, and produce inspectable outputs.

## 2. Governing execution rules

1. **Reuse before rebuild.** Search admitted donors first. Native code requires a reason when an equivalent mature donor implementation exists.
2. **Do not blindly concatenate repositories.** Donor code is admitted behind Gomrey contracts.
3. **Exact provenance.** Every copied/adapted slice is bound to exact source revision/path/rights/notice/modification/test evidence.
4. **No fabricated evidence.** Tests, CI, benchmarks, Jev reviews, parser results, model quality and performance are claimed only when executed and recorded.
5. **Jev in the build loop.** Non-trivial implementation grains require Jev-class review evidence when available, under `JEV_BUILD_POLICY.md`; unavailable TypeSafe Jev is recorded honestly, never impersonated.
6. **Agent-first parity.** A core capability is incomplete without structured agent/API access, permissions, idempotency and typed results.
7. **No silent loss.** Ingestion/research/export jobs expose explicit partial/uncertain/failed states.
8. **Confidence is not authority.** Hard policy and deterministic integrity checks override model confidence.
9. **Local/self-hostable is first-class.** Cloud adapters may enhance quality but cannot be hidden correctness dependencies.
10. **Promotion by benchmark.** Parser/model/retrieval/decision replacements must beat or match the incumbent on frozen Gomrey benchmarks before becoming default.

## 3. Program dependency ladder

```text
P00 Foundation + donor admission
 -> P01 Presenton full-base import and parity
 -> P02 Gomrey identity + build/release baseline
 -> P03 Core contracts / Source IR / Artifact IR / storage seams
 -> P04 Durable job engine + source-unit accounting
 -> P05 Source gateway + security + permissions
 -> P06 Document/OCR structured ingestion
 -> P07 Web/media/connectors
 -> P08 Retrieval fabric + citations
 -> P09 Decision Fabric + verification
 -> P10 Notebook/Research/Studio experience
 -> P11 Creation compiler + Gamma selective absorption
 -> P12 Agent platform: MCP/API/A2A
 -> P13 Plugin/Skill ecosystem
 -> P14 Collaboration/publishing/analytics
 -> P15 Benchmark arena + hardening
 -> P16 Release/operations/migration/GA
```

Some implementation can run in parallel after its prerequisites are stable, but no phase may claim completion using unqualified downstream assumptions.

---

# P00 — Foundation, source admission and program contracts

## Goal

Freeze the architectural contracts, provenance process, quality bars and exact donor candidates before importing large codebases.

## Deliverables

- `ARCHITECTURE.md` accepted;
- `SOURCE_LEDGER.md` accepted;
- `AGENT_PLATFORM.md` accepted;
- `JEV_BUILD_POLICY.md` accepted;
- no-gaps acceptance matrix accepted;
- exact Presenton snapshot and import procedure;
- Gamma source marked blocked until exact authorized archive/repository is supplied;
- repository contribution/review/merge policy;
- initial CI policy and secret/provenance rules.

## Exit

No unresolved architectural contradiction, licensing/provenance blocker for the Presenton base, or undefined P01 import/rollback procedure.

---

# P01 — Presenton full-base import

## Goal

Start from a working product, not a scaffold.

## Strategy

Import the admitted Presenton snapshot with provenance and required notices. Preserve as much of the known-working structure as possible. Do **not** combine the import with broad Gomrey redesign.

## Required proof

- imported source identity/digest documented;
- notices/licenses preserved;
- build/install instructions reproduced;
- presentation creation works;
- editor loads and edits;
- PPTX/PDF export works;
- REST and existing MCP surfaces work;
- local/self-hosted path behavior understood;
- tests/CI baseline captured;
- known upstream defects/nonclaims recorded.

## Exit

A reproducible Gomrey repository build behaves materially like the imported Presenton snapshot before major replacement work starts.

---

# P02 — Gomrey identity and engineering baseline

## Goal

Turn the imported base into a clean Gomrey product identity without destabilizing core functionality.

## Work

- project/package/container/app identity rename;
- remove/replace donor-owned branding only where permitted and appropriate;
- retain legal provenance/notices;
- standardize env/config conventions;
- define repository layout boundaries for Gomrey-owned modules vs imported/adapted modules;
- CI across target platforms;
- dependency/SBOM/security scanning;
- fixture/test data policy;
- release artifact baseline.

## Exit

Gomrey boots, creates/edits/exports presentations and passes baseline CI under its own identity.

---

# P03 — Core contracts and storage seams

## Goal

Introduce Gomrey-owned contracts before replacing donor internals.

## Core models

- Workspace / Principal / CapabilityGrant;
- SourceArtifact / SourceUnit / EvidenceSpan;
- SourceSnapshot / IngestionManifest;
- EvidenceBundle / Claim / Citation;
- Job / StageAttempt / ArtifactBaseline;
- DecisionRequest / DecisionResult;
- Artifact / ArtifactRevision / NarrativeIR / DesignIR;
- Plugin / Skill / Connector identity.

## Storage and identity rules

- canonical vs rebuildable projection split;
- content-addressed immutable blobs/assets;
- migration discipline;
- deletion/tombstone behavior;
- exact source/artifact revisions;
- tenant/organization/workspace identity is carried on every durable record, job, cache/index projection and audit record; authorization is evaluated before retrieval/disclosure, not after ranking;
- session/token/service-principal contracts support explicit revocation and least privilege; enterprise SSO/MFA/WebAuthn/SCIM are adapters or qualification profiles rather than hidden assumptions;
- supported server profiles require encrypted transport; sensitive canonical metadata/blobs require a qualified encryption-at-rest/key-custody profile, with keys separated from content and logs;
- no privileged support/admin identity silently bypasses tenant scope or audit;
- no vector/graph server mandatory by architecture.

## Exit

Contracts have serialization/schema tests and adapters can map the imported Presenton state into Gomrey-owned models without rewriting the editor.

---

# P04 — Durable jobs and 100% source-unit accounting

## Goal

Make 1,000+ page/source workloads a normal durable workflow.

## Work

- stable job/stage identity;
- idempotency and expected revisions;
- checkpoint/restart;
- permanent vs transient failure classification;
- bounded retry/backoff;
- cancellation/deadlines;
- ambiguous outcome reconciliation;
- resource budgets;
- task progress events;
- unit manifests and no-silent-drop invariant.

## Required torture tests

Kill/restart during:

- upload/staging;
- page parsing;
- OCR;
- embedding/indexing;
- reranking;
- artifact generation/export.

Verify restart does not lose completed work or duplicate non-idempotent effects.

## Exit

A synthetic 1,000-unit job can be interrupted repeatedly and finishes with every unit explicitly accounted for.

---

# P05 — Source gateway, hostile-input boundary and access control

## Goal

Make source acquisition safe before broadening format/connectors.

## Work

- MIME/content classification;
- archive/decompression/page/size limits;
- parser isolation;
- SSRF/DNS/redirect controls;
- active-content denial;
- connector credential isolation;
- source ACL model;
- data classification hooks for secrets, credentials, PII/sensitive/confidential content and DLP/egress decisions where applicable;
- prompt-injection/taint metadata;
- plugin/worker capability restrictions;
- source rights/access metadata plus acquisition/robots/terms policy and explicit redistribution/export restrictions where source rights require them;
- source revocation/deletion invalidates dependent caches, indexes, embeddings and derived evidence projections without erasing audit history;
- quarantine and explicit rejection states.

## Exit

Adversarial fixtures prove forbidden paths fail closed without contaminating trusted storage/indexes.

---

# P06 — Document/OCR intelligence

## Goal

Replace single-parser assumptions with an accountable parser ensemble.

## Initial donor order

1. retain Presenton LiteParse path as baseline comparator;
2. qualify Docling default structured path;
3. qualify PaddleOCR for scanned/multilingual/table/formula/chart workloads;
4. qualify MinerU only as optional difficult-document worker if rights/security/resource gates pass;
5. keep a fallback/second-parser policy for disagreement.

## Required formats

PDF, DOC/DOCX, PPT/PPTX, XLS/XLSX/CSV, HTML, TXT/Markdown, common images; expand formats based on admitted donor support and tests.

## Arabic P0 tests

- Arabic-only;
- English-only;
- mixed Arabic/English;
- RTL tables;
- Arabic/Western numerals;
- rotated/scanned pages;
- poor scans;
- decimals/units/dates;
- charts/formulas.

## Exit

Gomrey Source IR preserves structural/page/region provenance and benchmarked parser quality. No “100% OCR accuracy” claim; 100% unit accounting remains the reliability contract.

---

# P07 — Web, YouTube/media and connectors

## Web

Adopt Crawl4AI-class acquisition for bounded page/site ingestion including rendered content where required, semantic DOM, tables/images/linked docs, optional sitemap/domain crawl and retrieval snapshots.

## YouTube/video

Use subtitles where available, but full mode also supports audio transcription, scenes/keyframes, visual OCR/VLM and timestamp alignment. Transcript-only is explicitly degraded.

## Connectors

Prioritize reuse from SurfSense/Onyx CE/Open Notebook as permitted:

- local files/folder watch;
- Google Drive/Docs/Sheets/Slides;
- GitHub;
- Notion/SharePoint/Dropbox/OneDrive or other high-demand sources;
- YouTube;
- web/RSS;
- additional connectors by demand.

Every connector supports incremental sync, tombstones, revision identity, rate-limit/backoff, credential isolation, OAuth/token refresh and revocation where applicable, and ACL/permission resynchronization where available. Network loss or partial sync never silently upgrades stale data to fresh truth: checkpoints, stale markers, resumable cursors and conflict/reconciliation states are explicit.

## Exit

At least one file, one web, one video and one synced connector source all normalize into the same Source IR/citation model.

---

# P08 — Retrieval Fabric and citation resolver

## Goal

Deliver better-than-vector-only RAG.

## Pipeline

- ACL/scope filter;
- exact/identifier/location retrieval;
- FTS/BM25/grep-style lexical retrieval;
- metadata/structural retrieval;
- dense semantic retrieval;
- visual/multimodal retrieval;
- optional graph/global-local retrieval;
- fusion;
- reranking;
- diversity/freshness/authority constraints;
- evidence resolution and sufficiency checks.

## Index rules

Indexes are rebuildable and sensitive. Missing vector/visual models cannot disable lexical/exact retrieval.

## Citations

Implement exact source-specific locators for PDF/document, web, video/audio, spreadsheet and image evidence.

## Exit

Frozen benchmark beats the Presenton/imported baseline and proves citation locators resolve to exact source positions.

---

# P09 — Decision Fabric, claim verification and abstention

## Goal

Use Jev-class typed decisions where they materially improve bounded choices, without granting them authority.

## Work

- deterministic provider;
- Decider/SemIf/Laya-class challenger adapters;
- calibration registry;
- provider/workload benchmark routing;
- abstention/OOD;
- disagreement policy;
- ingestion routing decisions;
- retrieval sufficiency/relevance decisions;
- claim-support classification;
- artifact-quality decisions.

## Verification

Combine probabilistic evidence with deterministic checks for numbers, dates, units, entities, ranges/cells, citation integrity and source revision.

## Exit

Default provider for each workload is justified by measured quality/calibration/resource evidence; unsupported claims are repaired, downgraded, or blocked.

---

# P10 — Notebook, research and Studio

## Goal

Deliver the human/agent knowledge workspace.

## Core UX

- notebooks/workspaces;
- source library and ingestion status;
- source viewer with citation jump;
- ask/search/research/deep research;
- evidence/contradiction viewer;
- selected-source context;
- notes and saved findings;
- source discovery/watch later where justified.

## Studio outputs

- report/brief;
- presentation;
- document;
- infographic;
- mind map/timeline;
- podcast/audio overview;
- quiz/flashcards where useful;
- structured agent result bundles.

Reuse Open Notebook/RAGFlow/SurfSense UI/workflow code when admitted instead of rebuilding common notebook/source patterns.

## Exit

A user can move from heterogeneous sources to cited answer/research and create an evidence-backed artifact without leaving Gomrey.

---

# P11 — Creation compiler and Gamma selective absorption

## Goal

Become materially better than Presenton while preserving working functionality.

## Work

- Narrative IR;
- Design IR;
- evidence-to-claim binding;
- skill/brand-driven generation;
- editable charts/tables/text/images;
- layout/overflow verifier;
- artifact transform between presentation/document/site/social/infographic where practical;
- selective Gamma module absorption only after exact authorized source admission and direct superiority test.

## Gamma rule

Do not perform a blind Gamma transplant. For each candidate module compare:

- quality;
- dependencies;
- architectural fit;
- security;
- maintenance cost;
- embedded third-party assets/rights;
- migration risk;
- Presenton/Gomrey incumbent.

Copy the better implementation, not the more famous one.

## Exit

Gomrey artifacts remain editable and verified, and at least the flagship presentation workflow materially exceeds the imported Presenton baseline on quality and evidence grounding.

---

# P12 — Agent platform: MCP, API and A2A

## Goal

Make Gomrey easiest to use from agents.

## Work

- MCP server with high-level + expert tools;
- MCP Tasks mapped to durable jobs;
- MCP resources and optional MCP Apps;
- OAuth/scopes/least privilege;
- structured typed errors/results;
- idempotent mutations;
- artifact expected-revision conflicts;
- conventional REST/SDK parity;
- Gomrey as authorized MCP client;
- A2A Agent Card and durable delegated tasks.

## Required end-to-end scenario

An external agent can create workspace, attach sources, wait for accountable ingestion, research, create a presentation, verify/repair it, export it and obtain the evidence report **without UI automation**.

## Exit

Protocol conformance, authz negative tests, retry/idempotency/concurrency tests and UI-vs-agent behavior parity all pass.

---

# P13 — Plugins, Skills and agent packs

## Goal

Make Gomrey extensible without creating an unbounded code-execution hole.

## Work

- plugin manifest/versioning;
- requested/granted capabilities;
- skills/templates/connectors/evaluators/MCP components;
- content-addressed/signed package path where practical;
- sandbox/bounded host APIs;
- update/uninstall/revocation;
- compatibility checks;
- plugin marketplace/catalog later;
- brand/format/domain skills;
- reusable agent packs.

## Exit

A third-party plugin can safely add a bounded source or creation capability without ambient access to unrelated workspace data/secrets.

---

# P14 — Collaboration, publishing and analytics

## Goal

Close the major commercial-product gaps after core quality is proven.

## Work

- multi-user workspaces;
- comments/review;
- artifact version history;
- realtime editing only if justified by product/complexity tradeoff;
- sharing/roles;
- publish links/sites/custom domain path;
- view/engagement analytics;
- brand libraries;
- organization policy/admin;
- audit/history.

## Exit

Team workflows and publish/analytics permissions are secure and do not bypass artifact/source ACLs.

---

# P15 — Gomrey Arena, reliability and security hardening

## Goal

Prove “best” instead of declaring it.

## Benchmark families

- EnterpriseRAG-style enterprise document questions;
- ViDoRe-style visual document retrieval;
- RAGChecker-style retrieval/generation diagnostics;
- Gomrey-specific large source and creation tasks.

## Gomrey torture suites

- 1k/5k/10k page accounting;
- kill/restart at multiple stages;
- needle at first/middle/final units;
- Arabic/English mixed OCR;
- complex tables/formulas/charts;
- YouTube transcript vs visual questions;
- multi-page web questions;
- spreadsheet numeric questions;
- contradictory sources;
- stale/updated connector data;
- permission leakage;
- prompt injection;
- citation-locator correctness;
- artifact overflow/brand/editability;
- agent retry/concurrency;
- plugin permission escalation.

## Competitive arena

Use matched prompts/sources to compare against current relevant products where terms/access permit. Record date, model/product versions and source-access differences.

## Exit

No known critical security/reliability gap; default retrieval/parser/model routes are benchmark-backed; flagship workflows meet frozen release targets.

---

# P16 — Release, operations and GA

## Goal

Ship a maintainable product rather than a research demo.

## Work

- reproducible release builds and dev/staging/production promotion rules;
- migrations/backup/restore;
- crash recovery;
- upgrade/rollback;
- plugin/model-pack update path;
- provider/model/prompt/config registry with exact runtime identity, compatibility, deprecation and rollback;
- production evaluation and drift detection for parser/OCR/retrieval/reranking/decision/generation defaults, with benchmark-freshness and rollback triggers;
- durable queue admission, tenant/global quotas, priority, fairness, backpressure, starvation prevention, dead-letter/reconciliation paths and load shedding;
- observability/redaction with defined SLIs/SLOs, alerting, health probes and actionable dashboards;
- incident response, security escalation, on-call/runbook ownership and post-incident evidence preservation;
- capacity planning and graceful degraded modes for provider outage, accelerator loss, storage pressure and dependency failure;
- profile-specific availability/recovery targets, process supervision, restart/failover strategy and explicit single-point-of-failure inventory for any server/hosted deployment claim;
- storage operations: database/blob integrity checks, backup verification/restore drills, corruption/partial-write recovery, WAL/compaction/vacuum or equivalent maintenance where applicable;
- usage metering and entitlement accounting, when monetized: idempotent usage events, quota reconciliation, plan/feature enforcement and billing state kept separate from security authorization;
- support diagnostics;
- administrator operations: tenant lifecycle, account recovery, support access, privileged-action approval/audit and no silent impersonation;
- deployment profiles: local desktop/self-hosted/server as selected;
- supported client matrix: browser versions, Windows/macOS/Linux desktop profiles, responsive/mobile-web behavior where claimed, DPI/font/export compatibility and accessibility qualification;
- secrets/key management plus TLS/transport-security qualification and encryption-at-rest/key-custody tests for supported deployment profiles;
- authentication/identity qualification for the declared product profile: session revocation, service principals, MFA/WebAuthn and enterprise OIDC/SAML/SCIM only where claimed, with negative tenant-isolation tests;
- content-safety and abuse controls with explicit policy boundaries, unsafe-source handling, generated-artifact checks and appeal/override authority where product policy requires it;
- privacy/retention/deletion controls;
- data governance: classification/PII boundaries, residency policy, retention schedules, access/export/delete requests, legal-hold behavior, derived-index deletion and backup/tombstone semantics;
- offline/network-partition qualification for each claimed local/sync profile: stale-state visibility, reconnect reconciliation, conflict behavior and no hidden remote correctness dependency;
- source-content rights/terms and redistribution/export controls verified through acquisition, derived artifacts, sharing and public publishing;
- SBOM/notices/license bundle;
- disaster recovery and data portability;
- performance/cost/resource envelopes;
- documentation and onboarding;
- release signing where applicable.

## Exit

Fresh-install -> migrate/restore -> ingest -> research -> create -> agent/API -> export/publish -> upgrade/rollback paths are all proven on supported profiles. Release qualification also proves the declared client matrix, queue overload/backpressure behavior, SLO/alert/incident paths, provider/model rollback, data-governance lifecycle, privileged admin boundaries, safety/abuse policy, and drift-triggered rollback on frozen fixtures.

---

# 4. Definition of Done for every implementation grain

A grain is not done until applicable items are proven:

- exact scope and donor/source identities recorded;
- code/tests/docs in English;
- deterministic tests pass;
- security/provenance review passes;
- Jev-class review evidence recorded when required/available;
- no unresolved material review findings;
- benchmark regression evaluated when behavior/model/retrieval changes;
- agent/API contract updated for core capabilities;
- permission/idempotency/error semantics tested;
- exact candidate CI green;
- migration/rollback impact known;
- post-merge verification on canonical main;
- evidence bound to exact commit/revision.

# 5. “Best ever” success model

Gomrey is not considered best because it has the most features. It wins only if it simultaneously improves:

- source coverage and ingestion reliability;
- retrieval recall/precision and visual understanding;
- citation correctness and claim faithfulness;
- abstention when evidence is insufficient;
- artifact design/editability;
- large-job resumability;
- Arabic/multilingual quality;
- agent ease-of-use and protocol correctness;
- privacy/local-first capability;
- extensibility without permission leakage;
- time-to-result and resource efficiency.

These dimensions become measurable release gates in P15 rather than marketing adjectives.
