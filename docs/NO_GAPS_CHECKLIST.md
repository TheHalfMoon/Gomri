# Gomrey No-Gaps Program Checklist

**Status:** FOUNDATION PLAN  
**Purpose:** prevent a strong-looking roadmap from omitting a production-critical system.

Every row must eventually resolve to `NOT_APPLICABLE`, `PLANNED`, `IMPLEMENTED`, `QUALIFIED`, or `BLOCKED` with evidence. A missing row is not allowed to become an implicit assumption.

| Domain | Required coverage | Primary phase |
|---|---|---|
| Repository foundation | contribution rules, CI, branch/merge policy, secrets rules, provenance | P00-P02 |
| Donor governance | exact revisions, licenses/permissions, notices, transitive assets, update/exit strategy | P00+ |
| Presenton base | import, build parity, tests, editor, generation, export, MCP/API | P01 |
| Gamma donor | exact authorized archive, selective module admission, third-party boundary | P11 |
| Product identity | naming, packages, containers, docs, legal notices, branding separation | P02 |
| Identity/auth | users, agents, service principals, sessions/tokens, OAuth | P03/P12/P14 |
| Workspace/org | workspace ownership, roles, sharing, quotas/policies | P03/P14 |
| Authorization | scopes, ACLs, connector inheritance, plugin permissions, approvals | P05/P12/P13 |
| Secrets | encrypted storage/handles, redaction, rotation/revocation, no prompt exposure | P05/P16 |
| Canonical storage | metadata DB, migrations, transactions, source/artifact revisions | P03 |
| Blob storage | content addressing, immutable inputs/assets, cleanup/retention | P03/P16 |
| Backup/restore | manifests, integrity checks, compatibility, disaster recovery | P16 |
| Data portability | export/import, user ownership, deletion/tombstone semantics | P16 |
| Durable jobs | stage identity, checkpoints, retry, cancellation, reconciliation | P04 |
| Idempotency | tool/API/job mutation keys, duplicate suppression | P04/P12 |
| Concurrency | optimistic revisions, artifact/source conflicts, agent retries | P04/P12 |
| Resource budgets | CPU/RAM/GPU/time/network/token/source limits | P04/P05/P12 |
| Source gateway | MIME, hostile input, archive bombs, active content, quarantine | P05 |
| Network security | SSRF, DNS rebinding, redirects, egress policy, proxies | P05 |
| Filesystem security | path traversal, bounded mounts, temp cleanup, permissions | P05 |
| Prompt injection/taint | untrusted source marking, propagation, no trust laundering | P05/P08/P12 |
| PDF/document parsing | native/scanned/mixed, page accounting, structure/provenance | P06 |
| Office formats | DOCX/PPTX/XLSX and legacy formats where qualified | P06 |
| OCR | multilingual, Arabic/English, rotation, poor scans, confidence/uncertainty | P06 |
| Tables | structure, merged cells, numeric integrity, citations to cells/ranges | P06/P08/P09 |
| Charts/figures | extraction/visual indexing, captions, source regions | P06/P08 |
| Formulas/code | preservation/recognition, source coordinates | P06 |
| Images | OCR/VLM, regions, metadata, visual retrieval | P06/P08 |
| Web acquisition | static/JS pages, snapshots, DOM sections, screenshots | P07 |
| Website crawl | sitemap/domain scope, depth/budget, dedupe, robots/policy | P07 |
| Web freshness | retrieval timestamp, digest, recrawl/change detection | P07 |
| YouTube | metadata, captions, audio transcript, scenes/keyframes, timestamps | P07 |
| Generic audio | transcription, language, timestamps, failure/uncertainty | P07 |
| Generic video | scene/keyframe/visual text + transcript alignment | P07 |
| Local files/watch | folders, change/delete sync, permissions | P07 |
| Drive/Docs | initial + incremental sync, revisions, ACL mapping | P07 |
| Enterprise connectors | Notion/SharePoint/Dropbox/etc. by demand and admission | P07/P14 |
| Connector lifecycle | credentials, cursors, rate limits, tombstones, stale state | P07 |
| Exact retrieval | IDs, page/time/range/source locators | P08 |
| Lexical retrieval | FTS/BM25/grep-style, language/tokenization behavior | P08 |
| Dense retrieval | embedding abstraction, model packs, rebuildability | P08 |
| Visual retrieval | page/image/video embeddings and multimodal queries | P08 |
| Graph retrieval | optional, benchmark-gated, explainable edges | P08 |
| Fusion/reranking | deterministic fusion + reranker identity/benchmark | P08 |
| Metadata filters | source/date/type/ACL/workspace/user filters | P08 |
| Retrieval sufficiency | continue/retrieve/abstain decision | P08/P09 |
| Contradictions | detection, preservation, surfacing, no forced single truth | P08/P09 |
| Evidence bundles | exact source revisions, omissions, digest, permission scope | P08 |
| Citation resolver | PDF/web/video/spreadsheet/image exact locators | P08 |
| Jev build review | exact candidate, schema, decision output, evidence/nonclaim | P00+ |
| Decision Fabric | deterministic + typed model providers + router | P09 |
| Calibration | workload/model-specific profile, ECE/Brier/NLL/risk coverage | P09 |
| Abstention | unsupported/OOD/missing evidence, explicit user/agent state | P09 |
| Claim verification | support states, deterministic numeric/date/unit checks | P09 |
| Notebook UX | source list/viewer, cited chat, research, saved findings | P10 |
| Deep research | multi-step search/acquisition with bounded source admission | P10 |
| Studio outputs | report, deck, doc, infographic, audio/podcast, etc. | P10/P11 |
| Presentation generation | outline/narrative/design/layout/render | P01/P11 |
| Presentation editing | text/media/chart/layout editing, undo/history | P01/P11 |
| PPTX export | editable output, fonts/assets, fidelity | P01/P11 |
| PDF/image export | deterministic rendering and failure handling | P01/P11 |
| Document/report creation | editable semantic content, citations | P11 |
| Website creation | responsive output, assets, publish path | P11/P14 |
| Social/graphics | reusable artifact compiler, export formats | P11 |
| Narrative IR | source-grounded claims/sections across output types | P11 |
| Design IR | layout/tokens/components/brand semantics | P11 |
| Brand system | logos/fonts/colors/themes, rights, brand extraction/skills | P11/P13 |
| Layout QA | overflow, clipping, contrast, density, missing fonts/assets | P11/P15 |
| Accessibility | alt text, contrast, reading order, keyboard/UI where applicable | P11/P14/P15 |
| MCP server | tools/resources/tasks/apps where selected | P12 |
| MCP client | authorized external MCP use, taint/provenance, credential isolation | P12 |
| MCP auth | OAuth/current spec conformance, scopes, negative tests | P12 |
| MCP Tasks | durable job mapping, polling/update/cancel/result | P12 |
| A2A | Agent Card, delegated task lifecycle, auth/scope | P12 |
| REST/SDK | stable schemas, auth, parity with core tool surface | P12 |
| Structured errors | retryability, policy denial, stale revision, unknown outcome | P12 |
| Agent discoverability | tools, skills, limits, policies, supported artifacts | P12 |
| Agent concurrency | expected revisions, idempotency, branch/diff/merge | P12 |
| Plugin manifest | identity/version/compatibility/permissions/capabilities | P13 |
| Plugin sandbox | network/fs/secrets restrictions, audit, kill/timeout | P13 |
| Skills | narrative/design/evidence rules without hidden permission gain | P13 |
| Connectors as plugins | safe installation and credential grants | P13 |
| Agent packs | bounded multi-capability roles/workflows | P13 |
| Plugin updates | provenance, rollback, revocation, dependency compatibility | P13/P16 |
| Collaboration | sharing, roles, comments, history, conflict behavior | P14 |
| Realtime | explicit necessity gate, consistency/reconnect behavior if adopted | P14 |
| Publishing | public/private links, custom domains, revoke/unpublish | P14 |
| Analytics | viewer engagement, privacy, retention, permissions | P14 |
| Audit | source/agent/plugin/publish/approval events with redaction | P05/P12/P14 |
| Observability | metrics/traces/logs, secret/content redaction, health | P16 |
| Performance | cold/warm latency, throughput, resource profiles, large jobs | P15/P16 |
| Cost | hosted-provider optional budgets, no hidden mandatory paid service | P15/P16 |
| Offline/local | core workflows and declared degraded modes | P06-P16 |
| Security testing | SAST/dependencies/SBOM/hostile fixtures/authz/plugin attacks | P02/P05/P13/P15 |
| Supply chain | pinned artifacts, hashes/signatures, model/plugin provenance | P00/P13/P16 |
| Privacy | retention, telemetry policy, local/remote boundaries, deletion | P05/P16 |
| Licensing | code/model/data/asset/font notices and redistribution boundaries | P00/P16 |
| Benchmark framework | frozen datasets, reproducible configs, exact model/provider identity | P15 |
| RAG quality | recall/precision, faithfulness, citation correctness, hallucination | P15 |
| Visual retrieval | ViDoRe-style tests, charts/screenshots/pages | P15 |
| Arabic quality | OCR/retrieval/generation/citation across mixed-language fixtures | P06/P15 |
| Large-source reliability | 1k/5k/10k source-unit jobs, kill/restart, zero silent drops | P04/P15 |
| Competitive evaluation | matched prompts/sources, dated competitor/product versions | P15 |
| Release builds | reproducible installers/images/packages, signing where applicable | P16 |
| Upgrade/rollback | DB/schema/artifact/model/plugin compatibility | P16 |
| Diagnostics/support | safe support bundle, health checks, no secret dump | P16 |
| Documentation | user, admin, agent, plugin, self-host, security, provenance docs | P00-P16 |

## Final release rule

Gomrey cannot claim production readiness while any applicable checklist row is absent, silently deferred, or supported only by a marketing statement. Every applicable row needs an owner/phase and an evidence-backed terminal state.
