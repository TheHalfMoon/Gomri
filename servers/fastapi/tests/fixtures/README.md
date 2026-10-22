# Test fixtures

Every directory here documents its source, licence, creation date and
generator, as required by `docs/FIXTURE_POLICY.md`.

## `donor_nextslide_presets.json`

| Field | Value |
|---|---|
| **Source** | `0xRafie/nextslide` @ `90a46f933b3056d27460400c915ef268a9ec3f56`, file `STYLE_PRESETS.md` |
| **Licence** | MIT — Copyright (c) 2026 Danish Rafie Ekaputra |
| **Extracted** | the colour custom properties (`--ns-bg`, `--ns-bg-alt`, `--ns-text`, `--ns-text-muted`, `--ns-primary`, `--ns-secondary`, `--ns-accent`) of each of the donor's 18 style presets |
| **Creation date (UTC)** | 2026-10-22 |
| **Generator** | `generate_donor_nextslide_presets.py` in this directory |
| **Seed** | none — the generator is fully deterministic (no network, no randomness) |
| **Regeneration** | `python generate_donor_nextslide_presets.py --donor-style-presets <path-to-donor>/STYLE_PRESETS.md --output donor_nextslide_presets.json` |

### Why this fixture exists

The donor's own mandatory design rules specify a **4.5:1 minimum text contrast
ratio**, yet its shipped presets violate that rule on **10 of the 54**
text-on-background pairs. Measured over the three text roles against the slide
background:

| Failing role | Failing presets | Count |
|---|---|---|
| `--ns-text-muted` | Asymmetric, Botanical, Creative Studio | **3** |
| `--ns-primary` | Minimal Clean, Soft Curves, Teal Serenity, Bento Grid, Retro 90s, Prism Glow | **6** |

This makes the presets a realistic **negative fixture**: a palette set that
looks entirely reasonable but fails an accessibility rule that the donor itself
declares mandatory. It is used by
`servers/fastapi/tests/unit/test_template_quality.py` to prove Gomrey's
contrast linter catches real violations rather than only synthetic ones.

No fixture in this directory contains real user secrets, private health or
business data, donor credentials or production dumps.
