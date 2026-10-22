# W12 — export fidelity: implementation evidence

**Mission:** Issue #77, wave `W12`.
**Branch:** `feature/rea/w12-export-fidelity`
**Base:** canonical `main` @ `5f299a7a6174ad3a1180f827778db5f4400a4d71` — W12 depends on nothing.
**Design:** `evidence/W12_EXPORT_FIDELITY_DESIGN.md` (1 281 lines, produced by a fresh-context subagent)
**Date (UTC):** 2026-10-22

---

## 1. What this grain delivers

Gomrey exported PPTX and PDF through an external package and **imported** PPTX back to JSON — and
there was **no test anywhere** that exercised either path. The design's single most important
measurement was that the round trip *can* be exercised deterministically:

```text
deck JSON → pptx-from-json → PPTX → pptx-to-json → JSON
```

**Browser-free.** No Chromium, no ImageMagick, no LibreOffice — 59 ms and 15 ms. That is what makes
a fidelity harness possible on CI at all, because the production export path is browser-bound.

W12 delivers that harness: eight synthetic decks, a **measured** expectations file, and a check
that fails with a behaviour-change notice when the export core's behaviour moves.

## 2. What the design measured, and what the harness confirms

The design surveyed the round trip and recorded what survives and what does not. The harness
**re-measured all of it** and pinned the results.

### Preserved (measured, pinned)

| Fact | Where |
|---|---|
| run text | `expectations/v1.json → decks[*].text_runs` |
| font family, bold, italic, colour, size | `decks[*].run_families` |
| position and size, **exactly in px** | `decks[*].positions` |
| paragraph alignment | `decks[*].alignments` |
| the PPTX package part list (notes slides, charts, media, slide count) | `decks[*].pptx_package` |

### Altered or dropped (measured, pinned as the current behaviour)

| Fact | Measured result |
|---|---|
| `vertical_alignment: "middle"` | comes back as `top` |
| `line_height: 1.2` | comes back as `0.07` |
| bullets | inlined as literal text (`"1. numbered"`, `"• justified"`) |
| N paragraphs | collapse into one element and one run joined by `\n` |
| autoshape `type` | ignored — an ellipse comes back as a rectangle polygon |
| `rotation`, `stroke.opacity`, `level`, chart axis titles, table spans/borders/heights | dropped |
| `decorative` | always `true` |
| **speaker notes** | **written to `ppt/notesSlides/notesSlide1.xml` but never re-imported** — the re-imported JSON has no `notes` key at all |

That last one is the harness's highest-value assertion, and it is **two-sided**: the note reached
the archive *and* it did not come back. If a future export core closes either side, the harness
produces a visible behaviour-change notice instead of a silent change.

## 3. The expectations are measured, not guessed

`expectations/v1.json` is produced by `measure.mjs`, which runs the real round trip over the
committed decks and records what came back. The harness then checks that a later run still
produces the same facts.

Regenerating the expectations is a **deliberate act** that means the export core's behaviour
changed, and the diff has to be reviewed. That is the whole point of a fidelity harness: it pins
behaviour so that a change is *visible*.

The expectations are pinned to `export_core_version: "1.0.34"`, and the harness asserts the
runtime matches. A third-party bump therefore cannot silently change what the harness means.

## 4. The fixtures

Eight synthetic decks, one per fidelity concern, all generated deterministically by
`generator.mjs` (no random source, no timestamp, so regeneration is byte-identical):

| Deck | Concern |
|---|---|
| `01-text-runs-fonts` | two runs, three fonts, bold/italic/underline/letter-spacing, fill and stroke |
| `02-alignment-bullets` | alignment, vertical alignment, numbered and default bullets, outline level, line height |
| `03-table` | a 2×2 table with a header fill |
| `04-vectors` | an autoshape with a stroke and a rotation, plus a connector |
| `05-chart` | a bar chart, two datasets, categories, title, legend, axis titles |
| `06-fills-and-background` | fill opacity, stroke opacity, a non-default background |
| `07-speaker-notes` | a slide-level note |
| `08-adversarial` | a 2 000-character run in a 40×20 box, a missing font family, a zero-size shape, right-to-left + emoji, an empty slide |

Every deck is synthetic. No real user data, no production output, no donor material, no
credential. `PROVENANCE.md` records the source, licence, creation date and regeneration command,
as `config/fixture-policy.json` requires.

### One fixture deviates from the design, and why

The design proposed a **picture** fixture. The picture shape's model is **not documented** in the
export-core type declarations, and every plausible construction throws
`Cannot read properties of undefined (reading 'path')`:

```text
data-nested      -> FAILED
top-level-path   -> FAILED
image-key        -> FAILED
```

Pinning that failure as an expectation would have encoded *our own misuse of an undocumented
shape* as a fact about the product. The fixture was therefore replaced with one covering the
constructs that **are** constructible, and the picture gap is recorded here as an open item. This
is the same discipline the W3 wave used: never pin a behaviour you have not verified.

## 5. What the harness does NOT assert, and why

- **The PPTX bytes.** Two runs of the same deck differ: the archive carries a UUID file name and
  wall-clock ZIP timestamps. The re-imported JSON and the package part list **are** deterministic,
  and those are what is pinned.
- **Rendered pixels.** The production export path is browser-bound; this harness is the
  deterministic tier beneath it. Pixel-level fidelity is a separate tier and is not claimed.
- **The re-imported JSON as Gomrey's own model.** `pptx-to-json` returns its own shape, which is
  *not* `RawSlideLayouts`; the harness pins the facts it measures rather than asserting a
  compatibility that does not exist.

## 6. The runtime is not committed, and a skip is never a pass

`presentation-export/` is gitignored. It is materialised by `npm run sync:presentation-export`,
which fetches a **public release tarball** — free, no account, no paid service.

On a checkout without it, every deck case reports a **real skip with its reason**:

```text
﹣ the round trip preserves what it is expected to preserve: 08-adversarial
  # EF-RUNTIME-ABSENT: run `npm run sync:presentation-export` to materialise the export runtime
ℹ tests 15
ℹ pass 3
ℹ skipped 12
```

Verified by hiding the runtime and running the harness. A skip is never counted as a pass, and
the reason names the condition.

## 7. The Node version problem, and the CI job

The export core declares `engines.node >= 22.12.0`. **Every existing CI job pins Node 20**, where
the export tasks cannot run. Installing under Node 20 works, but *running* the tasks does not.

So the harness reports `EF-NODE-VERSION` rather than failing in a confusing way, and a dedicated
CI job was added that pins **Node 22** and materialises the runtime:

```yaml
  test-export-fidelity:
    name: Test export fidelity
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: servers/nextjs
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22"          # the export core requires >= 22.12.0
          cache: npm
          cache-dependency-path: servers/nextjs/package-lock.json
      - run: npm ci
      - run: npm run sync:presentation-export
      - run: npm run check:presentation-export
      - run: node --test tests/export-fidelity.test.mjs
```

The existing `test-nextjs` job is untouched. On Node 20 the harness skips with a reason; on the
dedicated job it runs for real. **No existing CI gate was removed or weakened.**

## 8. Files

| File | Change | Lines |
|---|---|---|
| `servers/nextjs/tests/fixtures/export-fidelity/roundtrip.mjs` | **added** — the round trip, the ZIP reader, the fact extraction | 250 |
| `servers/nextjs/tests/fixtures/export-fidelity/generator.mjs` | **added** — the deterministic deck generator | 240 |
| `servers/nextjs/tests/fixtures/export-fidelity/measure.mjs` | **added** — writes the measured expectations | 90 |
| `servers/nextjs/tests/fixtures/export-fidelity/decks/*.json` | **added** — eight synthetic decks | ~13 KB total |
| `servers/nextjs/tests/fixtures/export-fidelity/expectations/v1.json` | **added** — the measured expectations | 700 |
| `servers/nextjs/tests/fixtures/export-fidelity/PROVENANCE.md` | **added** — fixture policy record | 60 |
| `servers/nextjs/tests/fixtures/export-fidelity/README.md` | **added** — what is pinned and what is not | 60 |
| `servers/nextjs/tests/export-fidelity.test.mjs` | **added** — the harness | 220 |
| `.github/workflows/test-all.yml` | **modified** — the Node 22 job | +33 |
| `package.json` | **modified** — `test:export-fidelity` | +1 |

## 9. Gate results on this revision

| Gate | Command | Result |
|---|---|---|
| Next.js unit | `npm test` | **88 pass / 0 fail** (73 baseline + 15 harness) |
| Repository tooling | `npm test` (root) | 48 pass / 0 fail |
| FastAPI | `uv run --locked python -m pytest -q` | 1125 passed (unchanged) |
| Export-fidelity harness | `node --test tests/export-fidelity.test.mjs` | **15 pass / 0 fail** |
| Fixture policy | `node scripts/check-fixtures.mjs` | OK |
| Secret scan | `node scripts/scan-secrets.mjs` | OK |
| Workflow parse | `yaml.safe_load` | OK — `test-export-fidelity` registered |

## 10. What is still open for W12

| Item | State |
|---|---|
| The **browser tier** — the production path that actually produces the PPTX | **Not exercised.** It needs Chromium and the `/pdf-maker` route. The design's Tier B is env-gated and is not delivered here. |
| The re-imported JSON being consumable as Gomrey's own `RawSlideLayouts` | **Not delivered.** The export core returns its own shape; the harness pins the facts it measures instead of asserting a compatibility that does not exist. |
| `pptx_font_utils.py` being on the import path | **Not delivered.** It is a separate font-substitution utility; folding it in would confound the measurement. |
| The picture fixture | **Not delivered** — the shape's model is undocumented and could not be constructed without guessing. |
| `<a:pPr rtl="1">` surviving a PPTX round trip | **Not delivered.** The reader is in the external export core. **This is also the W13 wave's open item**, and the two waves meet here: W13 fixes the *direction* that goes in, and W12 measures what comes *out*. |
| The export core's undocumented `shape_type` values | **Recorded, not fixed.** Only `textbox`, `autoshape`, `connector`, `table`, `chart` were exercised here; the sweep found others that silently produce zero elements. |

## 11. Non-fabrication record

- No paid service, hosted model, funded compute or product account was used. The export runtime is
  a **public release tarball** fetched by the repository's own existing script.
- No login, paywall, CAPTCHA, rate limit or access control was defeated.
- No credential, secret or user data was collected.
- Every fixture is synthetic and its provenance is recorded.
- The expectations were **measured**, not hand-written.
