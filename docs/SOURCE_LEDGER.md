# Gomrey Source and Donor Ledger

**Status:** FOUNDATION PLAN  
**Date:** 2026-10-05  
**Rule:** reuse mature implementation before native rebuild, but never inherit donor architecture, authority, licensing assumptions, or hidden dependencies by accident.

## 1. Adoption modes

- `COPY_FULL_BASE` — import a working product/repository as the initial executable foundation, preserve history/provenance where practical, then adapt behind Gomrey contracts.
- `COPY_BOUNDED` — copy only the smallest useful implementation/test slice.
- `ADAPT` — use donor implementation as the close basis behind Gomrey-owned interfaces.
- `DEPEND` — pinned package/runtime dependency.
- `WORKER` — isolated process with bounded filesystem/network/resource authority.
- `MODEL_PACK` — separately versioned model/tokenizer/calibration artifacts.
- `REFERENCE` — architecture/UX/test behavior only; do not copy runtime code.
- `BENCHMARK_ONLY` — comparator/evaluation input only.
- `DEFER` — useful candidate, but no adoption until a measured need exists.

No donor becomes canonical merely because it is available. Before copied/adapted material lands, record exact revision, exact paths, controlling terms or separate permission basis, embedded/transitive material, notices, modifications, tests, security placement, update strategy, and exit strategy.

## 2. Primary executable foundation

### Presenton

- Repository: `presenton/presenton`
- Planning/execution anchor reverified 2026-10-05: `e158a014cc1e29da0a27fe539db08dcbcea5c69d`
- Commit tree: `dbf6834b8519e25f4dfd936dc8c099ce17b9e96e`
- Commit timestamp: `2026-10-02T18:49:27Z`
- Public license observed: Apache-2.0; exact LICENSE blob `5566576249c0c99a84455b2fc8454e03a9b18e20` (11,340 bytes)
- Required NOTICE boundary: exact NOTICE blob `ba5df534c4549ed7459a34667a506baa5cbd5fea` (1,274,338 bytes); preserve the donor NOTICE through P01 and audit embedded/transitive entries before selective removal or repackaging
- Mode: `COPY_FULL_BASE`
- Intended value:
  - Next.js product UI;
  - FastAPI backend;
  - presentation generation;
  - editor/layout/template surfaces;
  - editable PPTX/PDF export;
  - local and hosted model provider adapters;
  - Electron/self-hosted paths;
  - REST and existing MCP foundation.
- Rule: import first, prove parity, then replace weak subsystems incrementally. Do not rewrite working presentation/editor/export paths simply to make them “Gomrey native.”

### Gamma authorized source

- Source: founder-authorized Gamma source code, archive/repository not yet supplied to this repository.
- Mode: `COPY_BOUNDED / ADAPT` after exact source bytes are available.
- Candidate value:
  - card/editor UX;
  - artifact responsiveness;
  - themes and design workflows;
  - document/site/social creation;
  - collaboration/publishing/analytics behavior;
  - other modules only where direct comparison proves them stronger than the Presenton-derived path.
- Gate: **no Gamma code is copied until an exact source snapshot, permission scope, third-party/asset boundary, and provenance record exist.** A public `gamma.app` URL is not a source archive.

## 3. Knowledge/RAG donors

### RAGFlow

- Repository: `infiniflow/ragflow`
- Planning anchor observed: `2400ca8eb51432b1d304266d0de9ca232d9b53fa`
- Mode: `COPY_BOUNDED / ADAPT`
- Candidate value:
  - ingestion pipeline architecture;
  - large-document/lazy processing patterns;
  - lexical/BM25 and semantic retrieval;
  - agentic RAG;
  - dataset/knowledge management;
  - knowledge compilation patterns (graph/tree/page-index-style projections);
  - connector/incremental ingestion behavior.
- Rule: RAGFlow is an engine donor, not the Gomrey data model or UI authority.

### Open Notebook

- Repository: `lfnovo/open-notebook`
- Planning anchor observed: `315d5255af2a5132aada41c94d5c3c5dc8e837aa` (v1.15.0 release commit observed 2026-10-04)
- Mode: `COPY_BOUNDED / ADAPT`
- Candidate value:
  - notebook/source UX;
  - heterogeneous source ingestion;
  - citations/context selection;
  - podcast/studio workflows;
  - provider plumbing;
  - durable worker failure/retry semantics.
- Rule: copy source/notebook workflows where they are better than rebuilding them; keep Gomrey Source IR and evidence semantics authoritative.

### SurfSense

- Repository: `MODSetter/SurfSense`
- Planning anchor observed: `7fb479c361414e1ffd180860eb0b5eb5afb0c4e3`
- Mode: `COPY_BOUNDED / ADAPT`
- Candidate value:
  - connectors;
  - Google Drive/YouTube/web source integration;
  - browser extension patterns;
  - MCP integration;
  - live web research.

### Onyx Community Edition

- Repository: `onyx-dot-app/onyx`
- Planning anchor observed: `f5c518f663038c3ef713b8830b81e1a0a92bfb44`
- Public CE license observed: MIT
- Mode: `COPY_BOUNDED / REFERENCE`
- Candidate value:
  - connector lifecycle;
  - incremental indexing;
  - hybrid/agentic retrieval;
  - permission-aware source/search architecture;
  - deep research and agent actions.
- Rule: enterprise-only code/features are not assumed reusable under CE terms. Exact path licensing must be checked before copying.

## 4. Document/OCR/media donors

### Docling

- Repository: `docling-project/docling`
- Planning anchor observed: `eda5b5fc86d10b2b79a900ff3e69fc159d5f6014`
- Mode: `DEPEND / WORKER / COPY_BOUNDED adapters`
- Role: default structured document parser and normalization comparator.

### PaddleOCR

- Repository: `PaddlePaddle/PaddleOCR`
- Mode: `DEPEND / WORKER`
- Role: multilingual OCR, scanned documents, tables/layout/formulas/charts, Arabic/English qualification candidate.

### MinerU

- Repository: `opendatalab/MinerU`
- Mode: `WORKER / BENCHMARK_ONLY` until exact current terms and service obligations are recorded.
- Role: difficult visual/layout-heavy document fallback and comparator.

### Crawl4AI

- Repository: `unclecode/crawl4ai`
- Planning anchor observed: `e5d2e786d1a101225f3f6a3e6fd344d76eeb13af`
- Mode: `DEPEND / COPY_BOUNDED`
- Role: website crawling, JavaScript pages, clean structured/LLM-ready extraction.

### YouTube/video/audio stack

Candidate components:

- `yt-dlp/yt-dlp` — media/subtitle acquisition where lawful and permitted by source/user rights;
- `SYSTRAN/faster-whisper` and/or `ggml-org/whisper.cpp` — transcription;
- `Breakthrough/PySceneDetect` — scene/keyframe segmentation.

Mode: `DEPEND / WORKER`.  
Rule: a YouTube source is multimodal. Transcript-only ingestion is an explicit degraded mode, not the full source representation.

## 5. Multimodal retrieval/graph candidates

### RAG-Anything / LightRAG

- Repositories: `HKUDS/RAG-Anything`, `HKUDS/LightRAG`
- Mode: `ADAPT / BENCHMARK_ONLY`
- Candidate value: multimodal entity/relationship extraction and graph/global-local retrieval.
- Gate: graph machinery is adopted only where Gomrey benchmarks show measurable gain over simpler lexical+dense+rerank retrieval.

### Embedding/reranking model packs

Candidate families include Qwen3 embedding/reranker and Qwen3-VL embedding/reranker paths.

Mode: `MODEL_PACK / BENCHMARK_ONLY` until exact model revision, artifact digest, model/data license, resource profile, calibration/evaluation, and local/runtime compatibility are qualified.

## 6. Jev-class decision candidates

### TypeSafe Jev

- Role: required build/review comparator where reproducible access is available; not a hidden runtime dependency.
- Mode: `BENCHMARK_ONLY / BUILD_REVIEW`.
- Rule: no claim that Jev was executed unless exact request/model/tool identity and output are captured in evidence.

### Mapika Decider

- Repository: `Mapika/decider`
- Public license observed: Apache-2.0
- Mode: `DEPEND / COPY_BOUNDED / MODEL_PACK / BENCHMARK_ONLY`
- Candidate value: one-pass typed choices/scores/yes-probability with calibrated probability outputs; GGUF/local runtime options.

### SemIf-style direct option scoring

- Mode: `COPY_BOUNDED / REFERENCE / BENCHMARK_ONLY`.
- Candidate value: direct option-logit scoring and calibration without free-form generation/parsing.

### Laya / other compact decision models

- Mode: `MODEL_PACK / BENCHMARK_ONLY`.
- Candidate value: compact local multilingual routing/classification/decision workloads.

Permanent rule: **Gomrey owns decision schemas, policy, calibration requirements, abstention behavior, provenance, and authority. Models are replaceable providers.**

## 7. Assets, model artifacts, datasets and generated-output rights

Code permission does not automatically grant rights to bundled or referenced non-code material. Admission treats these as separate identities and rights decisions:

- model weights, tokenizers, processors, calibration artifacts and runtimes;
- training/evaluation datasets and benchmark fixtures;
- fonts, icons, illustrations, photos, audio, video, templates, themes and stock assets;
- logos, trademarks, product names and brand kits;
- user-supplied source material and connector-acquired content;
- generated artifacts that embed, transform or redistribute third-party material.

A copied donor module may land while its bundled asset/model remains excluded. Public publishing/export must preserve required attribution and must not silently convert source-access permission into redistribution permission. Generated content does not erase third-party asset provenance, trademark constraints or source-rights restrictions.

MODEL_PACK admission requires exact model artifact digests plus separate code/runtime, weight, tokenizer/processor and model-data/license identities where applicable. Benchmark datasets are never assumed redistributable because their loader code is open source.

## 8. Founder-owned sibling donors

High-value internal sources include:

- `TheHalfMoon/MedOrigin` — SourceArtifact/EvidenceSpan/Document IR, provenance, abstention, evidence and document trust boundaries;
- `TheHalfMoon/Morize` — retrieval hierarchy, evidence graph, contradiction/supersession, rebuildable projections;
- `TheHalfMoon/Winds` — durable workflow identity, retry/reconciliation, resumability and exact artifact applicability;
- `TheHalfMoon/Inercative` — typed product/compiler architecture, design engine, tool/model routing;
- `TheHalfMoon/Orcel` — agent runtime/workflow/checkpoint patterns;
- `TheHalfMoon/kernux` — capability/policy boundary;
- `TheHalfMoon/Ascout` — review/evidence/verification discipline;
- `TheHalfMoon/SpecGrain` and `TheHalfMoon/Diffcipline` — bounded planning and proof-before-done process.

Mode: `ADAPT / COPY_BOUNDED / PROCESS_REFERENCE` based on the selected slice.

## 9. Source admission record

Every adopted slice must record:

```text
source_name
source_repository_or_archive
exact_revision_or_digest
source_paths
public_license
separate_permission_basis_if used
embedded/transitive code/assets/models
model_weight_tokenizer_runtime_rights
training_evaluation_dataset_rights
font_icon_media_template_brand_rights
generated_output_redistribution_or_publication_restrictions
notices/attribution
Gomrey_target_module
adoption_mode
why_reuse_beats_native
security/trust placement
network/filesystem/credential capabilities
tests/benchmarks
modifications
update strategy
rollback/exit strategy
review evidence
```

Permission expands what is possible; it does not remove provenance, third-party rights, security, benchmark, or exit requirements.
