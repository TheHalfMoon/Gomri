# Gomrey Agent Platform

**Status:** FOUNDATION PLAN  
**Principle:** Gomrey must be the easiest high-quality creation and knowledge system for agents to use, not merely a human application with an API bolted on later.

## 1. Protocol posture

Gomrey is simultaneously:

- an MCP server exposing knowledge, creation, verification, export, publishing, connector, and plugin capabilities;
- an MCP client/orchestrator able to call authorized external MCP servers;
- an A2A-capable specialist agent for delegation from other agent systems;
- a conventional REST/SDK platform for environments that do not speak MCP/A2A;
- a plugin/skill host with explicit capability boundaries.

All protocol adapters call the same Gomrey domain services. They do not implement parallel business logic.

## 2. MCP baseline

Implementation targets the then-current final MCP specification selected by the implementation grain. At foundation time, the planning target is MCP `2026-07-28` semantics, including stateless core behavior and the Tasks extension for long-running tool work where supported.

Do not hard-code deprecated protocol features into Gomrey architecture. Compatibility shims may exist at edges.

## 3. Tool design rules

Every agent tool must have:

- stable name and versioned schema;
- narrow purpose;
- typed input and output;
- bounded payloads;
- permission scopes;
- explicit workspace/artifact/source identity;
- idempotency key for mutations;
- expected revision/precondition for concurrent edits where applicable;
- structured error codes and retryability classification;
- audit receipt;
- cancellation/deadline semantics for long work.

Do not return only prose such as “done.” Return durable identifiers and structured verification state.

## 4. High-level tools first

Agents should not need to understand Gomrey internals to achieve common goals.

Primary high-level tools:

```text
gomrey.workspace.create
gomrey.sources.add
gomrey.sources.connect
gomrey.research
gomrey.ask
gomrey.create
gomrey.improve
gomrey.verify
gomrey.export
gomrey.publish
```

Example conceptual call:

```text
gomrey.create(
  artifact_type="presentation",
  goal="Board update",
  source_scope={...},
  skill="executive-board",
  evidence_policy="strict",
  constraints={"slides": 18}
)
```

The high-level tool may orchestrate many internal stages but returns a single durable task/artifact handle.

## 5. Expert tools

Expert agents can use lower-level primitives:

### Sources

```text
gomrey.sources.add_file
gomrey.sources.add_url
gomrey.sources.add_youtube
gomrey.sources.add_image
gomrey.sources.sync
gomrey.sources.get
gomrey.sources.status
gomrey.sources.remove
```

### Knowledge

```text
gomrey.search
gomrey.retrieve
gomrey.ask
gomrey.research
gomrey.deep_research
gomrey.find_evidence
gomrey.compare_sources
gomrey.verify_claim
gomrey.get_citation
```

### Artifact inspection/editing

```text
gomrey.artifact.get
gomrey.artifact.diff
gomrey.artifact.branch
gomrey.artifact.merge
gomrey.presentation.inspect
gomrey.slide.get
gomrey.slide.add
gomrey.slide.delete
gomrey.slide.reorder
gomrey.slide.rewrite
gomrey.slide.relayout
gomrey.element.add
gomrey.element.update
gomrey.element.delete
gomrey.chart.create
gomrey.chart.update
```

### Verification

```text
gomrey.verify_artifact
gomrey.verify_slide
gomrey.verify_claim
gomrey.verify_citations
gomrey.check_numeric_integrity
gomrey.check_source_coverage
gomrey.check_layout
gomrey.check_brand
```

### Export/publish

```text
gomrey.export_pptx
gomrey.export_pdf
gomrey.export_docx
gomrey.export_html
gomrey.export_images
gomrey.publish
gomrey.unpublish
gomrey.get_share_link
```

## 6. Long-running work and MCP Tasks

Operations such as crawling a site, ingesting 10,000 pages, transcribing a long video, deep research, or creating a complex deck are durable Gomrey jobs.

When the MCP host supports Tasks, a tool call may return a task handle. The task status maps to the Gomrey Job Engine and supports polling/cancellation without keeping one fragile connection open.

Task progress exposes useful structured metrics, for example:

```text
source_units_total
source_units_accounted
verified
uncertain
failed
current_stage
percent
estimated_work_remaining (optional, never a correctness claim)
warnings[]
```

A task result references durable output artifacts/evidence; the full private content does not need to be repeated in every poll.

## 7. MCP resources

Read-heavy stable objects should be available as resource-style surfaces where supported, including:

- workspace metadata;
- source manifests;
- source-unit/evidence locators;
- artifact revisions;
- verification reports;
- plugin/skill manifests;
- benchmark/evaluation summaries.

Authorization is re-evaluated on access; knowing a resource URI does not grant access.

## 8. MCP Apps

Where supported by host clients, Gomrey can expose interactive MCP Apps for high-value visual workflows such as:

- presentation preview;
- source/citation viewer;
- slide picker;
- approval screen;
- artifact diff/review;
- ingestion progress with unresolved-page drill-down.

App actions use the same audited tool/capability path. The embedded UI does not bypass agent-host consent or Gomrey permissions.

## 9. A2A specialist agent

Gomrey publishes an A2A Agent Card describing capabilities such as:

```text
research
deep-research
document-understanding
multimodal-source-analysis
evidence-verification
presentation-generation
document/report-generation
visual-design
artifact-editing
export/publishing
```

A2A tasks map to Gomrey durable jobs. The agent may return intermediate status, artifacts, evidence summaries, and explicit blockers/abstentions.

A2A does not grant arbitrary workspace access. Delegation carries an authenticated principal and explicit scope.

## 10. Agent-safe mutation model

Every mutable artifact carries a revision identity. Mutations accept:

```text
artifact_id
expected_revision
idempotency_key
operation payload
```

Outcomes include:

- applied with new revision;
- idempotent replay of an already-applied operation;
- conflict/stale revision;
- policy denial;
- validation failure;
- unknown outcome requiring reconciliation.

This prevents duplicate slides/decks when an agent retries after timeout and prevents silent overwrite when multiple agents edit concurrently.

## 11. Parallel agent work

Gomrey may support lightweight artifact branches:

```text
main
  agent/research
  agent/design
  agent/citations
```

Branches are semantic artifact revisions, not necessarily Git branches. Merge computes a structured diff and surfaces conflicts such as competing edits to the same slide/element or evidence link.

No automatic merge is allowed when semantics conflict materially.

## 12. Agent result format

Agent-facing responses should favor typed summaries such as:

```json
{
  "artifact_id": "...",
  "revision": 7,
  "status": "NEEDS_REPAIR",
  "sources": 87,
  "claims": 144,
  "verified_claims": 142,
  "unresolved_claims": 2,
  "broken_citations": 0,
  "warnings": [],
  "exports": []
}
```

The exact schema will be versioned. Human-readable summaries are additional convenience, not the contract.

## 13. Permissions/scopes

Initial capability families:

```text
workspace.read
workspace.admin
sources.read
sources.write
sources.connect
knowledge.search
knowledge.research
artifact.read
artifact.create
artifact.edit
artifact.export
artifact.publish
plugins.read
plugins.install
connectors.manage
approvals.respond
```

Tokens/grants are least-privilege and workspace-scoped where possible.

## 14. Approval policy

Typical default posture:

- read/search/research within granted sources — automatic;
- draft/create/edit inside workspace — automatic under granted scope;
- connector authorization/credential change — explicit policy/approval;
- publish publicly or send externally — approval-capable;
- destructive source/workspace deletion — approval-capable;
- plugin installation with new permissions — explicit grant.

Approval rules remain configurable by workspace policy.

## 15. Gomrey as MCP client

Gomrey can use authorized external MCP servers for research and artifact workflows.

Examples:

- Drive/Docs/Sheets;
- GitHub;
- search/browser tools;
- CRM/data warehouses;
- custom organization tools.

External tool outputs enter as untrusted observations with provenance. An MCP connection is not a trust upgrade.

Credential handling is server-side and capability-scoped; prompts/models do not receive raw connector secrets.

## 16. Plugin model

A Gomrey plugin may package:

```text
plugin.json
skills/
templates/
connectors/
evaluators/
mcp/
artifact-rules/
```

The manifest declares:

```text
plugin identity/version
publisher/provenance
compatible Gomrey versions
requested permissions
network destinations
filesystem scopes
secret handles
provided tools/resources/skills/templates
runtime/sandbox requirements
update channel
```

## 17. Plugin classes

### Source plugins

Examples: Google Drive, Notion, SharePoint, Dropbox, GitHub, Slack, YouTube, PubMed, arXiv, Salesforce.

### Creation plugins

Examples: consulting deck, board report, clinical evidence review, academic poster, Saudi government presentation, VC pitch, annual report.

### Agent packs

A pack can combine retrieval rules, skills, templates, evaluators, and bounded tools for a role such as financial analyst, competitive intelligence analyst, or evidence reviewer.

## 18. Skill contract

A skill can specify:

- audience/purpose;
- narrative grammar;
- visual language;
- layout preferences;
- chart/table preferences;
- brand/token rules;
- evidence/citation policy;
- verification requirements;
- examples and transformation rules.

Skills do not automatically gain network/filesystem/tool permissions.

## 19. Agent discoverability

Agents should be able to discover:

- available tools and their schemas;
- installed skills/plugins;
- workspace policies and allowed artifact/source types;
- supported export formats;
- long-task semantics;
- current provider/capability limitations;
- verification/evidence policies.

Do not require hidden prompt lore to use Gomrey correctly.

## 20. Error taxonomy

At minimum distinguish:

- invalid input/schema;
- unauthorized/forbidden;
- stale revision/conflict;
- transient provider/network failure;
- permanent source failure;
- resource budget exceeded;
- unsupported capability/format;
- unresolved/abstained decision;
- blocked pending approval;
- unknown outcome requiring reconciliation.

Agents need machine-readable retry guidance. “500 error” is not a sufficient platform contract.

## 21. Rate/resource budgets

Agent requests carry or resolve to bounded budgets for:

- time;
- tokens/model calls;
- network requests;
- pages/source units;
- CPU/RAM/GPU worker use;
- output artifacts/size;
- parallelism.

Budget exhaustion produces a truthful partial/blocking state rather than silent truncation.

## 22. Plugin/agent security

Controls include:

- signed/content-addressed package identity where feasible;
- explicit requested/granted permissions;
- no ambient secrets;
- domain allowlists for network-capable plugins;
- bounded filesystem mounts;
- plugin/tool call audit;
- prompt-injection/taint propagation;
- source ACL checks before retrieval disclosure;
- safe uninstall/revocation that invalidates dependent credentials/caches as required.

## 23. Conformance gates

Agent platform release gates include:

- MCP protocol conformance for selected spec version;
- Tasks lifecycle tests;
- OAuth/authz negative tests;
- idempotent retry tests;
- concurrent revision conflict tests;
- plugin permission escalation tests;
- connector/source ACL leakage tests;
- A2A task/cancellation tests;
- structured-result schema compatibility tests;
- human UI vs agent API behavior parity tests for core capabilities.

## 24. Success criterion

An external agent should be able to perform this entire workflow without UI automation:

```text
create workspace
 -> attach/connect heterogeneous sources
 -> wait for accountable ingestion
 -> research with evidence
 -> create editable presentation/report/site
 -> verify and repair claims/citations/layout
 -> export or request publish approval
 -> retrieve final artifact and evidence report
```

If an agent must click the web UI to complete a normal workflow, Gomrey has failed the agent-first requirement.
