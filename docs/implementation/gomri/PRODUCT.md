# PRODUCT — Gomri

## Thesis

Gomri turns user-supplied sources, ideas and structured data into **beautiful presentations whose meaning and objects remain editable**. It is an AI-era slide product, not a screenshot exporter, a paid API wrapper or a generic Canva clone. It should ultimately compete with Gamma/Beautiful.ai while retaining stronger source traceability, safe targeted edits and honest editable PowerPoint export.

## Target workflow

1. User starts a project from prompt and authorized local file(s); deterministic offline fixtures are sufficient for testing.
2. Gomri extracts citations/claims, proposes an outline and identifies claims needing evidence.
3. User selects or approves 8–12 slides, a role-based theme and layout.
4. Editor displays native text/chart/table/image/shape objects; the user can change content without re-generating the entire deck.
5. User selects one element and asks an agent to shorten, translate, restyle or restructure. It previews the exact diff and preserves source numbers and unrelated objects.
6. User commits with revision-safe protection, can Undo, then exports native PPTX/PDF/images. A format cannot silently claim to preserve unsupported objects.
7. User can reopen the project/deck and inspect source attribution.

## Defining differentiators

- **Trustworthy:** source/citation/number/unit preservation, abstention and provenance receipt.
- **Beautiful:** four semantic layout families plus refinable freeform visual editor; visually tested Arabic/English.
- **Editable:** real Office text/chart/table/notes fidelity where promised, never all-slide bitmap stand-in.
- **Agent-native:** narrow read/selection/typed patch/undo/write authorization; no arbitrary deck overwrite.
- **Affordable/private:** zero unapproved paid cloud spend, deterministic local path, explicit provider opt-in.

## MVP success criteria

One 8–12 slide synthetic source -> approved outline -> editable deck -> scoped edit -> Undo -> PPTX journey in a real Windows browser/desktop session. Two-owner isolation and two-client race tests pass on disposable test infrastructure. Native objects and citations match source or are explicitly and completely receipted as unsupported. Exact-head CI and independent security/Code Review pass.

**Not the MVP:** 85 formats, massive template/stock asset library, live cloud collaboration, native iOS/Android app, full social scheduling, custom paid APIs, automatic GPU inpainting/video, and full parity against private vendor code.

## Product trade-offs

Keep the Presenton-derived editor and exporter as the default base. Prefer the smallest legally admissible source copy from the owner-controlled Ninerr/Skilit and qualified public donors. Any alternative editor/exporter must **prove** measurable improvement over baseline on synthetic fixtures before replacing code.

The founder decides product scope and authorizes merges/releases; agent roles autonomously execute **only the currently safety-qualified phase**. Reviews are evidence, not approval by themselves.
