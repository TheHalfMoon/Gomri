# Beautiful.ai Deep REA — 02: Published Slide Model and Layout Engine Constraints

Date: 2026-11-09. Evidence: vendor-authored public Apache-2.0 Markdown source in beautifulai/claude-plugin at a3f771432c0d2c43f13c56a92d34ee9fa932855a. The documents describe the actual **external schema**, not the private renderer implementation. Companion: ../../registry/beautiful-ai-template-model-map-2026-11-09.csv (73 named template IDs; 59 root element docs).

## A. Data model: verified public conventions

The public Slide.md defines:
- template_id: selector for template element type, defaults and capabilities.
- template_version, version=10, migrationVersion=10.03, textStylesVersion=2.
- hasBeenEdited: when false and a Brand Kit default slide is configured, the theme may replace the authored model.
- layout: header position, tray position, footer, background, decoration.
- states[0]: template-specific tree with primary, optional header and tray.
- metadata: isGenerating, slidePrompt, generateError, wasAiGenerated, needsLayoutProcessing.
- slide_notes: presenter notes.
- server-owned fields: id, presentationId, timestamps, _changeId and library item identity; not authored by tools.

A new document missing migrationVersion or textStylesVersion is NOT equivalent to leaving the current version unchanged. The app can execute migrations or legacy font-size mappings and change the input. The docs warn that outdated migration on modern Dashboard data can destroy child elements.

Source: https://github.com/beautifulai/claude-plugin/blob/main/skills/beautiful-ai-slide-elements/elements/Slide.md

## B. BaseElement and rendering lifecycle

BaseElement is the abstract parent of slide elements. Children may bind to their own submodel or share their parent model; named elements get structural IDs. Collection entries can have stored IDs. Schema default merge, migration and derived layout/cache fields are part of the described lifecycle.

Derived values such as blockBounds, textStyles, calculatedWidth, topSpace and bottomSpace are recomputed by the layout engine. They are not canonical source fields. An agent copying them from an existing deck can cause stale sizing behavior. Every element provides isFit, and root false can cause editor refusal.

Gomri should keep canonical semantic IDs, typed edit operations and immutable source references in its own Deck IR. Derived layout caches must never overwrite source-of-truth charts, tables, media rights or text.

Source: https://github.com/beautifulai/claude-plugin/blob/main/skills/beautiful-ai-slide-elements/elements/BaseElement.md

## C. The real public 12 by 12 dashboard model

The Dashboard and GridLayoutContainer references show:
- default cols=12, rows=12, gridLayout.cells as x, y, width, height.
- primary.items[i] is the content belonging to gridLayout.cells[i].
- childElement holds typed content; componentType can be Chart, PieChart, Table, Statistic, RadialBar and TextAndImage.
- with gutter enabled there are 10 px gaps between units.
- extra items beyond matching cells may be silently removed; missing items may become placeholder cells.
- cells outside bounds can become invisible and overlapping cells may escape detection.
- layoutEngineType values include flex, dashboard, stack_diagram, fixed, preserve-aspect, single_cell, custom, headline and sidebar.
- a chart_line or table-v2 template can be the same Dashboard root model with one full-size cell.

This is a genuine, actionable behavioral specification from the published source, not a screenshot-level guess.

Sources:
https://github.com/beautifulai/claude-plugin/blob/main/skills/beautiful-ai-slide-elements/elements/GridLayoutContainer.md
https://github.com/beautifulai/claude-plugin/blob/main/skills/beautiful-ai-slide-elements/elements/Dashboard.md

### Gomri design proposal, not Beautiful.ai's own schema

    DashboardNode:
      columns = 12, rows = 12
      cells = [ { cellId, x, y, spanX, spanY, childElementId } ]
      children = typed native slide elements
      constraints = noOverlap, noOverflow, noSilentDataLoss
      revision = stable revision ID

Unlike the described normalization that may drop extra items, Gomri should fail loudly, offer a suggested repair, then apply only after validation. This is an explicit opportunity to exceed Beautiful.ai robustness.

## D. Classic freeform authoring

AuthoringCanvas.md describes an ordered array of absolutely positioned editable content: text boxes, shapes, icons, vector paths and embedded components. Array order can determine z-order; snap-to-10px grid is optional. Content can be placed outside a 1280x720 canvas without a universal containment check; auto-fit children can update dimensions and positions during render.

Gomri should retain Presenton's interactive freeform editor. Add a SmartLayout mode as an additional view of its typed scene graph rather than replacing the editor with Beautiful.ai templates.

Source: https://github.com/beautifulai/claude-plugin/blob/main/skills/beautiful-ai-slide-elements/elements/AuthoringCanvas.md

## E. Text, media, and version-sensitive data

TextElement.md uses rich-text blocks containing block IDs, type, textStyle, HTML text, optional list/indent, inline media and rich formatting. Auto-fit reduces size and can raise isFit=false, but merely fitting does not prove legibility or correct Arabic shaping. Images/icons use content_type + content_value and additional media crop/asset identifiers. Some animations exist in player but not exported still frames.

Important documented issues:
- stale __generateImage flags on existing assets can keep an infinite spinner;
- old model fields can be migrated differently than a new one;
- shared slide libraryItemId makes a reference, and editing can detach it into a standalone copy;
- hasBeenEdited=false may allow the current Brand Kit default slide to override the author's model;
- cached geometry/text should not be re-authored.

Sources:
https://github.com/beautifulai/claude-plugin/blob/main/skills/beautiful-ai-slide-elements/elements/TextElement.md
https://github.com/beautifulai/claude-plugin/blob/main/skills/beautiful-ai-slide-elements/elements/Picture.md
https://github.com/beautifulai/claude-plugin/blob/main/skills/beautiful-ai-slide-elements/elements/Slide.md

## F. Template taxonomy and design heuristics

The skill index maps 73 literal template IDs to 59 root element document names, extracted into a CSV. The source folder has 103 distinct element Markdown documents, NOT necessarily 103 templates. The rules choose layout based on semantic content and item count. Examples: dashboard/chart_line/chart_bar/chart_pie/table-v2 share Dashboard; authoring uses AuthoringCanvas; textlist uses TextList; flow_chart uses NodeDiagram; image carousels use ImageCarousel.

The public agent design skill discourages using one template more than a third of a deck, encourages a strong picture/icon where appropriate, requires good contrast and sufficiently large text, and recommends rendered visual verification.

Sources:
https://github.com/beautifulai/claude-plugin/blob/main/skills/beautiful-ai-slide-elements/SKILL.md
https://github.com/beautifulai/claude-plugin/blob/main/skills/beautiful-ai-slide-templates/SKILL.md
https://github.com/beautifulai/claude-plugin/blob/main/skills/beautiful-ai-slide-design/SKILL.md

## G. 12 negative tests for Gomri SmartLayout

| Test | Original source risk | Desired Gomri gate |
|---|---|---|
| L-01 | items more numerous than grid cells | reject, no silent deletion |
| L-02 | cell x/y outside valid grid | explicit error; no hidden objects |
| L-03 | grid cell overlap | flag intersection and repair preview |
| L-04 | text min font reached | reject unreadable shrink or offer reflow |
| L-05 | mixed Arabic/English with numerals | correct bidi in editor and PPTX |
| L-06 | missing schema/migration version | explicit migration, exact data preservation |
| L-07 | stale computed fields | recompute cache, never source-truth |
| L-08 | theme default replacement | require explicit confirmation if authored content changes |
| L-09 | shared slide reference edited | explain detach and copy-on-write |
| L-10 | out-of-frame freeform object | visible warning and correction |
| L-11 | chart values changed during layout switch | fail claim integrity |
| L-12 | missing image asset / stuck generation flag | recover or error; no indefinite spinner |

**Status:** this chapter is source inspection. It does NOT build Gomri SmartLayout or expose Beautiful.ai's private code.
