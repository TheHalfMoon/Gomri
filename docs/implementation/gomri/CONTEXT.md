# Gomri — Ubiquitous Language

| Term | Definition | Avoid |
|---|---|---|
| **Deck** | Canonical ordered collection of slide content/metadata owned by one authorized workspace | Treating PDF/PPTX screenshot as canonical deck |
| **Slide** | One ordered editable presentation page with stable ID and components | Calling an exported flattened image a slide model |
| **Component** | Small editable shape/text/chart/table/image with stable canonical identity | "Element" when referring ambiguously to HTML DOM |
| **Selected target** | Explicit allowlisted current component IDs user/agent may change | Whole-deck overwrite as a scoped edit |
| **SourceIR** | Normalized user-authorized source records/digests with provenance | Raw web page markup treated as instructions |
| **NarrativeIR** | Evidence-grounded claims/outline/slide roles derived from SourceIR | Unchecked generated text |
| **SmartLayout** | Derived in-memory placement of existing canonical components by semantic roles | Second persistent editor or independent DesignIR database |
| **Revision** | Monotonic server-authoritative version controlling atomic slide/deck writes | Browser `JSON.stringify` fingerprint as distributed CAS |
| **Edit proposal** | Immutable typed candidate diff requiring authorization and, where needed, human confirmation | Executed write or unconstrained LLM prose |
| **Edit commit** | Single atomic owner-checked compare-and-swap of authorized patch + revision | UI-only "save" promise |
| **Undo** | A new revision restoring earlier canonical content while preserving intervening history | Rewriting or deleting an old revision |
| **Loss receipt** | Component/slide/format-specific record of unsupported or downgraded export capability | Silent rasterization or "mostly editable" claim |
| **Donor** | Pinned source repository/commit/file set admitted under license/permission and asset checks | Competitor website as downloadable private source |
| **E2E PASS** | Executed real-browser synthetic user journey with backend/OOXML assertions | Unit tests or screenshots without interaction |
| **OCR Delegation** | Alibaba CLI's local diff/rule extraction for an independent reviewer | Completed AI code review |
| **PStack phase** | One narrow red-test -> implementation -> independent-review milestone with explicit gate | Infinite autonomous rewrite |
