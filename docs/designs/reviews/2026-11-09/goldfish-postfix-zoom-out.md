# Fresh post-resolution EGM Goldfish Zoom Out

**Actual independent new OpenCode session** on Elephant v2 (`bee29b8`), model `opencode/deepseek-v4.1-flash-free`, no source code access, conditional verdict. This is not official orchestrator output.

**Verdict: CONDITIONAL — GO for P0 only, after its scope is tightened. Do not authorize Phase 1 preview or Phase 2 writes.**

## Remaining blockers

1. **Section 0 contradicts itself and §7 on what P0 is.** The binding gate says “only P0 read-only code tracing and controlled negative tests may proceed,” yet §0 Z2 authorizes “one non-persisting headline-hero preview,” which is Phase 1 work. §7 Phase 0 also orders full pytest/node/root suites, TypeScript, production build, Windows manual journey, and a gate of “one editable deck journey OR explicit NOT READY.” Builds and a journey are not read-only tracing. §0 Z4 further allows “safe main-only preview experiments” if #88 fails. That is three different P0 scopes.
2. **P1 is gated on P3 artifacts.** §7 Phase 1 requires “visual and no-silent-loss checks” on eight fixtures, but the export-fidelity/RTL tests it would rely on are “not present on main until qualified/merged” (§7 Phase 3) and live in #88 (§2). Dependency inversion.
3. **G2 has no verified target representation.** §2 says DesignIR v1 lacks a rich scene graph; §6 refuses to put the 12×12 grid into v1; §5 defers a “versioned, small typed metadata envelope” and possible DesignIR v2 with no schema, migration owner, or rollback test. Four SmartLayout families therefore have no proven encoding. Blocks P1, not P0.
4. **Speaker notes have no owner or route.** G3/G5 and §9 require notes preservation; §10 question 4 admits it is unknown. F2’s export-delivery authorization appears in §9 but not in the Phase 3 gate.

## Newly added bloat

- §7 Phase 1 lists a **30-fixture** test module while §0 Z3, G1, and the Phase 1 gate all say **8 first**. Whether “fixtures” means decks or unit cases is undefined; as written it restores the benchmark bloat Z3 cut.
- §7 Phase 2 still names `servers/fastapi/gomrey/slide_edit_transaction.py` plus new `patch.ts`/`verify.ts`, despite §0 Z1’s “no automatic new service” and the “NOT DEFAULT” label. Listing a path is de facto scope.
- §7 Phase 5’s “30 matched prompts” and blinded competitor comparison depend on “when legitimate authorized competitor access exists” — an unproven resource presented as a release stage.

## Conflicts

- §0 F3/F4 require consistent CAS/Undo, but §7 Phase 2 only inspects the legacy route and conditional new files; no verified route signature exists (§2, §10 q3).
- §0 Z1 requires atomic content-plus-revision update, while §2 admits ArtifactRevision v1 “does not establish a deployed atomic compare-and-swap endpoint.” That is a requirement, not a design.
- §4 excludes a new editor state store, but §5’s metadata envelope risks creating a second authority unless explicitly bounded.

## Unproven assumptions

- #88’s reported 55/148/15 tests are valid at exact head (§2 says unverified).
- Main’s Template V2 helpers suffice or fail for G2 (§10 q1) — deliberately unresolved.
- Server session context can supply principal/tenant/workspace to the legacy route (§0 F2, §5) — P0 must prove it.
- “Zero silent loss” is measurable without the component-ID-to-OOXML mapping F7 requires but P3 owns.

## Actions

1. Split §7 Phase 0 into P0a (read-only trace plus two-client stale-write and foreign-owner negative tests) and P0b (builds/manual journey), or explicitly authorize P0b; delete §0 Z4’s preview allowance and reconcile §0 Z2 with the binding gate.
2. Fix the 8-vs-30 count in §7 Phase 1 and remove export/RTL no-loss checks from the P1 gate until #88 or P3 artifacts are qualified.
3. Strike `slide_edit_transaction.py` and the DesignIR v2/envelope language until P0’s route map proves the legacy v1 route cannot do atomic CAS; require schema, migration, and rollback tests for any envelope.
4. Add speaker-notes route/owner to P0’s route map and F2 export-delivery authorization to the Phase 3 gate.
5. Define P0 exit as: exact heads, commands, exits, and skips recorded; both negative tests executed; “NOT READY” accepted; no Phase 1 code until then.
