import assert from "node:assert/strict";
import test from "node:test";
import { checkContracts, loadSchemas, validateValue } from "./validate-contracts.mjs";

const HEX = "0123456789abcdef".repeat(4);
const WHEN = "2026-10-07T00:00:00Z";
const TENANT = "tenant-1";
const WORKSPACE = "workspace-1";

const VALID = {
  Workspace: { workspace_id: "w-1", tenant_id: TENANT, name: "Research", created_at: WHEN, revision: 1, status: "active" },
  Principal: { principal_id: "p-1", tenant_id: TENANT, kind: "agent", created_at: WHEN, status: "active" },
  CapabilityGrant: {
    grant_id: "g-1", tenant_id: TENANT, workspace_id: WORKSPACE, principal_id: "p-1",
    scopes: ["sources.read", "knowledge.search"], granted_by: "p-0", created_at: WHEN, status: "active",
  },
  SourceArtifact: {
    source_id: "s-1", tenant_id: TENANT, workspace_id: WORKSPACE, source_type: "pdf",
    original_digest: { algorithm: "sha256", value: HEX }, revision: 1, created_at: WHEN,
  },
  SourceUnit: { source_id: "s-1", source_unit_id: "u-1", tenant_id: TENANT, workspace_id: WORKSPACE, unit_kind: "page", state: "verified" },
  EvidenceSpan: {
    span_id: "e-1", source_id: "s-1", source_unit_id: "u-1", tenant_id: TENANT, workspace_id: WORKSPACE,
    extracted_digest: HEX, producer_identity: "docling-worker-1",
  },
  SourceSnapshot: {
    snapshot_id: "n-1", source_id: "s-1", tenant_id: TENANT, workspace_id: WORKSPACE,
    acquired_at: WHEN, content_digest: HEX, revision: 2,
  },
  IngestionManifest: {
    manifest_id: "m-1", source_id: "s-1", tenant_id: TENANT, workspace_id: WORKSPACE,
    declared_units: 10, accounted_units: 10, silent_drop_count: 0, status: "complete",
  },
  EvidenceBundle: {
    bundle_id: "b-1", tenant_id: TENANT, workspace_id: WORKSPACE,
    source_revisions: [{ source_id: "s-1", revision: 2 }], spans: ["e-1"],
    bundle_digest: HEX, verification_state: "verified", freshness_at: WHEN,
  },
  Claim: {
    claim_id: "c-1", tenant_id: TENANT, workspace_id: WORKSPACE, bundle_id: "b-1",
    text: "Revenue grew 12 percent in Q3.", support_state: "SUPPORTED",
  },
  Citation: {
    citation_id: "t-1", tenant_id: TENANT, workspace_id: WORKSPACE,
    source_id: "s-1", source_unit_id: "u-1", locator: { page: 4 },
  },
  Job: {
    job_id: "j-1", tenant_id: TENANT, workspace_id: WORKSPACE, kind: "ingest",
    input_baseline: "s-1@2", idempotency_key: "k-1", status: "running", created_at: WHEN,
  },
  StageAttempt: {
    job_id: "j-1", stage: "parse", attempt: 1, tenant_id: TENANT, workspace_id: WORKSPACE,
    status: "checkpointed", started_at: WHEN,
  },
  ArtifactBaseline: {
    baseline_id: "a-0", artifact_id: "a-1", revision: 3, tenant_id: TENANT, workspace_id: WORKSPACE,
    content_digest: HEX, created_at: WHEN,
  },
  DecisionRequest: {
    request_id: "d-1", tenant_id: TENANT, workspace_id: WORKSPACE, workload_kind: "retrieval-relevance",
    state_digest: HEX, question: "Is this span relevant?", answer_family: "BOOLEAN",
    privacy_mode: "local", consequence_class: "low",
  },
  DecisionResult: {
    request_id: "d-1", tenant_id: TENANT, workspace_id: WORKSPACE, provider_identity: "deterministic-rules",
    model_revision: "rules-1", selected_value: "yes", data_boundary: "local", created_at: WHEN,
  },
  Artifact: {
    artifact_id: "a-1", tenant_id: TENANT, workspace_id: WORKSPACE, artifact_type: "presentation",
    title: "Board update", current_revision: 3, created_at: WHEN, status: "draft",
  },
  ArtifactRevision: {
    artifact_id: "a-1", revision: 3, tenant_id: TENANT, workspace_id: WORKSPACE,
    content_digest: HEX, verification_state: "verifying", created_at: WHEN,
  },
  NarrativeIR: {
    narrative_id: "r-1", artifact_id: "a-1", revision: 3, tenant_id: TENANT, workspace_id: WORKSPACE,
    sections: [{ heading: "Summary", text: "Growth continued.", claim_ids: ["c-1"] }],
  },
  DesignIR: {
    design_id: "x-1", artifact_id: "a-1", revision: 3, tenant_id: TENANT, workspace_id: WORKSPACE, layout: "title-body",
  },
  Plugin: {
    plugin_id: "pl-1", publisher: "Gomrey", version: "1.0.0", content_digest: HEX, status: "installed",
  },
  Skill: { skill_id: "k-1", tenant_id: TENANT, name: "board-report", version: "1.2.0" },
  ConnectorIdentity: {
    connector_id: "o-1", provider: "drive", tenant_id: TENANT, workspace_id: WORKSPACE,
    credential_handle: "vault:ref:drive-1", scope: "read", status: "connected",
  },
};

test("every contract accepts its valid fixture", async () => {
  const { manifest, schemas } = await loadSchemas();
  assert.equal(manifest.schemas.length, 23);
  for (const entry of manifest.schemas) {
    const fixture = VALID[entry.name];
    assert.ok(fixture, `missing valid fixture for ${entry.name}`);
    const errors = validateValue(structuredClone(fixture), schemas[entry.name], schemas[entry.name]);
    assert.deepEqual(errors, [], `${entry.name} rejected its valid fixture: ${errors.join("; ")}`);
  }
});

test("contracts reject invalid records with precise errors", async () => {
  const { schemas } = await loadSchemas();
  const cases = [
    ["Workspace", {}, "missing required property workspace_id"],
    ["Workspace", { ...VALID.Workspace, status: "archived" }, "must be one of"],
    ["CapabilityGrant", { ...VALID.CapabilityGrant, scopes: ["not a scope!!"] }, "does not match pattern"],
    ["SourceArtifact", { ...VALID.SourceArtifact, original_digest: { algorithm: "md5", value: HEX } }, "must be one of"],
    ["IngestionManifest", { ...VALID.IngestionManifest, silent_drop_count: 1 }, "above maximum"],
    ["Claim", { ...VALID.Claim, support_state: "MAYBE" }, "must be one of"],
    ["Citation", { ...VALID.Citation, locator: { page: 0 } }, "below minimum"],
    ["Job", { ...VALID.Job, extra: true }, "additional property extra is not allowed"],
    ["DecisionRequest", { ...VALID.DecisionRequest, answer_family: "VIBES" }, "must be one of"],
    ["ArtifactRevision", { ...VALID.ArtifactRevision, content_digest: "xyz" }, "does not match pattern"],
    ["Plugin", { ...VALID.Plugin, version: "v1" }, "does not match pattern"],
    ["ConnectorIdentity", { ...VALID.ConnectorIdentity, credential_handle: "" }, "shorter than minLength"],
  ];
  for (const [name, record, fragment] of cases) {
    const errors = validateValue(record, schemas[name], schemas[name]);
    assert.ok(errors.length > 0, `${name} accepted an invalid record`);
    assert.ok(errors.some((message) => message.includes(fragment)), `${name}: no error contains ${fragment}: ${errors.join("; ")}`);
  }
});

test("durable records carry tenant and workspace identity", async () => {
  const { manifest, schemas } = await loadSchemas();
  // Workspace is the tenant-owned scope itself; Principal is tenant-level;
  // Plugin is a global catalog package whose install state is tracked per
  // workspace through CapabilityGrant scopes and Plugin.status.
  const exempt = new Set(["Workspace", "Principal", "Plugin"]);
  // Skill definitions are tenant-global and bound to a workspace at install
  // time, so workspace_id stays optional while tenant_id is mandatory.
  const workspaceOptional = new Set(["Skill"]);
  for (const entry of manifest.schemas) {
    if (exempt.has(entry.name)) continue;
    const required = schemas[entry.name].required ?? [];
    assert.ok(required.includes("tenant_id"), `${entry.name} must require tenant_id`);
    if (workspaceOptional.has(entry.name)) continue;
    assert.ok(required.includes("workspace_id"), `${entry.name} must require workspace_id`);
  }
});

test("manifest lists every schema file exactly once", async () => {
  const errors = await checkContracts();
  assert.deepEqual(errors, []);
});

test("validator implements the documented keyword subset", () => {
  const root = { $defs: { id: { type: "string", minLength: 2 } } };
  assert.deepEqual(validateValue("ab", { $ref: "#/$defs/id" }, root), []);
  assert.ok(validateValue("a", { $ref: "#/$defs/id" }, root).length > 0);
  assert.ok(validateValue("x", { type: "string", unsupportedKeyword: true }, {}).some((message) => message.includes("unsupported keyword")));
  assert.ok(validateValue("x", { $ref: "other.json#/$defs/id" }, root).some((message) => message.includes("only local")));
  assert.deepEqual(validateValue("b", { anyOf: [{ const: "a" }, { const: "b" }] }, {}), []);
  assert.ok(validateValue("c", { anyOf: [{ const: "a" }, { const: "b" }] }, {}).length > 0);
  assert.deepEqual(validateValue("a", { oneOf: [{ const: "a" }, { type: "string" }] }, {}).length, 1);
  assert.ok(validateValue("2026-10-07", { type: "string", format: "date-time" }, {}).length > 0);
});

test("narrative sections may carry citation locators and an evidence status", async () => {
  const { schemas } = await loadSchemas();
  const documentLocator = {
    kind: "document",
    citation_id: "cite-0123456789abcdef",
    source_id: "s-1",
    unit_id: "u-1",
    page_no: 4,
  };
  const record = {
    ...VALID.NarrativeIR,
    verification_scope: { gated: ["numbers", "dates"], not_gated: ["units", "entities"] },
    sections: [
      {
        heading: "Summary",
        text: "Growth continued.",
        claim_ids: ["c-1"],
        citation_locators: [documentLocator],
        evidence_status: "grounded",
      },
    ],
  };
  assert.deepEqual(validateValue(record, schemas.NarrativeIR, schemas.NarrativeIR), []);
});

test("a citation locator must carry the fields its source family requires", async () => {
  const { schemas } = await loadSchemas();
  const base = {
    kind: "document",
    citation_id: "cite-0123456789abcdef",
    source_id: "s-1",
    unit_id: "u-1",
  };
  const withoutPage = {
    ...VALID.NarrativeIR,
    sections: [
      {
        heading: "Summary",
        text: "Growth continued.",
        citation_locators: [base],
        evidence_status: "grounded",
      },
    ],
  };
  const errors = validateValue(withoutPage, schemas.NarrativeIR, schemas.NarrativeIR);
  assert.ok(errors.length > 0, "a document locator without page_no must be rejected");
  assert.ok(
    errors.some((message) => message.includes("oneOf")),
    `no error reports the per-kind requirement: ${errors.join("; ")}`,
  );

  const webLocator = { ...base, kind: "web", canonical_url: "https://example.test/a", retrieved_at: WHEN };
  const web = {
    ...VALID.NarrativeIR,
    sections: [
      {
        heading: "Summary",
        text: "Growth continued.",
        citation_locators: [webLocator],
        evidence_status: "grounded",
      },
    ],
  };
  assert.deepEqual(validateValue(web, schemas.NarrativeIR, schemas.NarrativeIR), []);
});

test("an unknown evidence status is rejected", async () => {
  const { schemas } = await loadSchemas();
  const record = {
    ...VALID.NarrativeIR,
    sections: [
      { heading: "Summary", text: "Growth continued.", evidence_status: "probably-fine" },
    ],
  };
  const errors = validateValue(record, schemas.NarrativeIR, schemas.NarrativeIR);
  assert.ok(errors.length > 0);
  assert.ok(errors.some((message) => message.includes("must be one of")), errors.join("; "));
});

test("a narrative section may not carry an undeclared property", async () => {
  const { schemas } = await loadSchemas();
  const record = {
    ...VALID.NarrativeIR,
    sections: [
      { heading: "Summary", text: "Growth continued.", confidence: 0.9 },
    ],
  };
  const errors = validateValue(record, schemas.NarrativeIR, schemas.NarrativeIR);
  assert.ok(errors.length > 0);
  assert.ok(
    errors.some((message) => message.includes("additional property confidence is not allowed")),
    errors.join("; "),
  );
});
