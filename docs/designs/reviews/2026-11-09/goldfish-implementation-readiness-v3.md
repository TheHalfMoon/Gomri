# EGM Goldfish — Independent Implementation Readiness, Plan v3

**Evidence:** isolated OpenCode model session (opencode/deepseek-v4.1-flash-free), attached only design_v3.md, no code execution or access, no edits. This is a genuine independent reviewer perspective but not the complete official Google EGM orchestrator. It explicitly states the controlling contract was not attached and labels its content unverified.

**Scope of this review:** I read only `design_v3.md`; the P0 contract and write-path audit were not supplied, so their contents are **UNVERIFIED**. I ran no tests, builds, or code inspection, and make no claims about actual behavior.

## Verdict

| Scope | Verdict | Basis |
|---|---|---|
| **P0a** (read-only tracing) | **GO**, narrowly | Bounded, no writes, necessary precondition. Conditions below are procedural, not blocking. |
| **P0b** (isolated synthetic qualification) | **CONDITIONAL** | Correct intent, but isolation is asserted, not specified; several tests can write outside a disposable boundary. |
| **P1/P2** (design freeze or build) | **NO-GO** | The document simultaneously forbids and describes implementation, and the data/write contracts P1/P2 depend on are undefined. Paper-only refinement may continue. |

## Residual contradictory permissions

1. **Header vs §7.** §0 says “P1 preview and P2 production writes NOT AUTHORIZED,” but §7 Phase 1 lists files to “change in a feature PR” and §7 Phase 2 says “minimally extend” production files and names new paths (`gomri-ai-edit/patch.ts`, `slide_edit_transaction.py`). Those are code writes. “P2 production writes” is never defined as *user-data* writes versus *source-code* writes, so both readings survive.
2. **P0b vs §0.** §0 allows P0b “builds and safety tests”; §0 also says P0 phases “never change … production code or main.” A “production build” and PR-#88 checkout change the working tree and caches. No worktree isolation is stated.
3. **P0a vs P0b.** §7 Phase 0a forbids “installs, builds, runtime tests,” while §7 Phase 0b requires full test suites, TypeScript, production build, and Windows E2E. Sequential, but the transition criterion is only “P0a exit,” which is subjective.
4. **Fixture ladder.** Four different 30-deck triggers: §3 G1 (“after one qualified native PPTX journey”), §7 P1 (“only after P3”), §7 P3 (“then expand to 30 after P2”), §7 P4 (“only after P3”).
5. **Proof chicken-and-egg.** §7 P1 permits new modules “ONLY after proving the existing Template V2 helper cannot meet the requirement,” but P0b forbids feature code and P1 is unauthorized. No phase is authorized to perform that proof.
6. **Speaker notes.** §7 P0b requires a “speaker-note roundtrip”; §7 P3 says the canonical notes field is **UNKNOWN** until P0a. A blocked result is allowed, but no blocked-result acceptance is defined.

## Missing test isolation

§7 P0b says “disposable test infrastructure” and “no live-user-data mutation,” but never specifies: ephemeral database/schema, tenant/workspace fixture IDs, object-store and queue isolation, provider-key unsetting, network egress denial, seed/reset, teardown, or a preflight assertion that no real tenant exists. “Full FastAPI/Next.js/root tests” has no include/exclude list; E2E smoke can write local profiles and persistent storage. The two-client concurrency and role-revocation tests need a named harness, clock control, and idempotency-key reset.

## Unauthorized write risks

- Production build and package installs write artifacts, caches, and possibly postinstall output.
- Export tests may enqueue jobs or write shared storage (§7 P0b, §7 P3).
- Role-revocation testing may mutate a shared identity provider.
- Checking out PR #88 to “compare exact head with main” alters the working tree unless a worktree is mandated.
- Listing exact candidate paths invites creation before the reuse proof.

## Unclear data and ownership contracts

§5 requires a “versioned, small typed metadata envelope,” stable `slideId`/`sourceId`, digest, revision CAS, and rollback, but supplies no schema ID/version, canonicalization rule, digest algorithm, idempotency-key scope, storage/transaction boundary, or 409/412 body. §2 confirms only `component_id` and `citation_ids`; stability of `slideId`/`sourceId` is unproven. Ownership is ambiguous between the Template V2 editor, the adapter, and `contracts/v1`; “owner” in the P0a exit could mean code owner, data owner, or tenant owner. §0’s clause that the unseen contract “overrides any ambiguous permissions” is unexercisable and creates a permission bypass.

## Acceptance methods

P0a’s “source-verified” has no checklist, artifact format, or reviewer sign-off. P0b’s “honest pass/fail/blocked” has no evidence schema, per-grain list, or independent verifier. P1’s “RTL readable” and “no clipping” lack font/OS matrix, minimum size, and tolerance. P2’s gate omits the 409/412 codes and the CAS test harness. §5 mentions rollback tests for a future DesignIR v2, but no phase accepts them.

## Five smallest fixes

1. **Add one permission matrix** at the top of §7: phase × {read, build, test-write, source-write, user-data-write, merge}. Delete contradictory verbs (“change in a feature PR,” “minimally extend,” “builds”) or mark them explicitly “not authorized.”
2. **Write a one-page P0b isolation contract**: disposable worktree at pinned SHA, ephemeral DB/schema, isolated queue/object store, provider keys unset, egress denied, seed/teardown, preflight “no real tenant” assertion, and suite include/exclude lists.
3. **Define the metadata/CAS contract** in §5: schema ID/version/owner, digest canonicalization, idempotency scope, transaction boundary, tenant/workspace derivation, 409/412 bodies, notes field, and export-auth checkpoints. Mark unknowns as blocking.
4. **Fix the fixture ladder** to one sequence (8 decks at P1; 30 only after P3 exit) and add a measurable oracle for clipping/readability and the negative-control count.
5. **Make the controlling contract reviewable**: attach it, or state that no unseen document grants permission, and require P0a to emit a named route/owner/export matrix with a pass checklist.
