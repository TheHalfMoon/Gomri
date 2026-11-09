---
name: beautiful-ai-slide-design
description: Design guidelines for Beautiful.ai slides - what makes a slide look good, how to keep it from being dull or empty, and the checks to run on a rendered slide before saving it. Use whenever you build, change or review a slide in Beautiful.ai.
---

# Beautiful.ai slide design guidelines

A slide is judged on its rendered image. Build for the picture, not for the model: the model is only right when the render looks right. These guidelines say what "looks right" means and how to get there with the templates and elements available.

## Not dull: give every slide something to look at

- Do not be shy with images. A slide made only of text looks dull; a fitting picture makes it look designed. When the content allows it and a suitable image can be obtained from the source the user chose (the editing skill says to ask once per task: their own images uploaded with `create_upload_url` and saved with `save_image_asset`, or `generate_image_asset` for the workspace's Team Assets, the web, stock photos or AI), add one: a side tray (`left_tray` / `right_tray`) next to a list, a process or a table; an image cell in a dashboard next to a chart or statistics; a background photo on a section break (`headline2`, `section`) or on a title slide when the user asks for one (a new deck's title slide stays simple, see the presentation building skill); the photo slots of `team`, `textgrid_photos`, `user_testimonial`. Pick an image that matches the slide's subject and the deck's style (photo vs. illustration, color mood), not a generic stock cliché.
- Use the built-in icons (`list_icons`) when a photo is not available or would be too much: an icon per item on lists (`textgrid_vertical_icons`), steps (`step_chevrons`, `step_circular`), hub-and-spoke nodes, statistics; they follow the theme's icon style and colors, so they always fit. Keep one icon per idea and a consistent level of detail across the set.
- Prefer templates with a visual structure over plain text when the content has one: steps become a process diagram, a comparison becomes compare bars or a stack diagram, numbers become statistics or a chart, a date series a timeline. Reserve `text` / `textlist` for content that really is prose or a list.
- Use the theme's colors: a colored tray or dashboard cell (`cellColor` with an accent or `background_accent`), a colored background on a section break, a highlighted item (`hilited`, `color`) for the one thing the audience should notice. One or two accents per slide; not every cell a different color.
- Exceptions: data-dense slides (a full table, a chart with many series, a dashboard already at 4+ cells) and slides that are mostly a single big visual do not need a decorative image; adding one would crowd them. And never add a picture that is not available: do not invent asset ids, do not leave `__generateImage` objects behind hoping for the best.

## Not empty: fill the canvas

Large empty areas look unfinished. The renderer scales text to the space it has, so a slide with little content gets big text and still large gaps. Fix it by changing the layout, not by padding the content with filler text.

- Few items: pick a template that is built for few items (1 statistic -> `action-number`; 2–3 points -> `textBoxGrid` in one row, `stackDiagram` or `headline2`; 2 values -> `compare_circles`), or give the slide a second element: a side tray with an image or a short takeaway, a second cell in a dashboard, a header with a subtitle line.
- Short text: a `textlist` with three short bullets fills better with an image tray and one column than with two columns; a lone paragraph is a `headline2` or `text` with an image, not a list.
- Dashboards: cells should fill the 12x12 grid with no unused rows or columns; a single small chart in a big cell gets a text cell under it or a statistic beside it. Charts with few categories want a narrower cell, not a full-width one.
- Trays: a tray takes 300–470 px of a 1280 px slide; use it when the main element has fewer than ~4 items or is naturally narrow (a short list, a quote, a single number); drop it when the main element needs the width (a wide table, a long timeline, a chart with many categories).
- Headers: most templates have one; a slide without a header and with little content looks empty. Use the header for the title and, when it helps, a one-line subtitle (a `body` block after the `heading`).

## Not crowded: leave room to breathe

The opposite failure. Crowded slides are the result of too much content for the template, not of the template.

- Every text readable at a glance: no overflow, no clipping, no ellipsis, nothing scaled down to tiny print, labels (axis, data, legend, column headers, step captions) not touching each other.
- Shorten before squeezing: trim wording, drop non-essential labels or secondary text, reduce item count or split the content over two slides (only when the user asks for a split; otherwise say that a split would help). Respect the item counts in the templates skill.
- Keep gutters: a dashboard with `showGutter` and a few cells looks calmer than many edge-to-edge cells; a list with sub-bullets on every item is a wall of text, keep sub-bullets to the items that need them.

## Coherent and consistent

- Balance: elements aligned and evenly spaced; nothing squeezed into a corner, nothing leaving a big gap on one side; an image tray on the side that balances the header position.
- Contrast: text readable against what is behind it (background color or image, cell color, chart bars). Light text on light images and dark text on dark cells are the most common render failures; change the `cellColor`, add a backdrop, or pick a different image.
- Consistency with the deck: same title style, capitalization, number formats, label tone and icon style as the neighboring slides; slides of the same template with their content structured the same way. Look at the neighbors before building. Consistency is in the style, not in the look: the deck should not read as one slide repeated (see "Varied across the deck").
- Titles as takeaways where the deck does it: "Revenue grew 40% in Q3" over "Q3 revenue"; mirror the deck's convention.
- Text style: short, parallel phrasing across items (all nouns, or all verbs), numbers formatted alike, no trailing periods on fragments.

## Varied across the deck

A deck is judged as a whole too, and the most common complaint about a generated one is that its slides all look alike: the same template slide after slide, the same layout, the same picture turning up again. Every slide can pass the checks above and the deck still look like one slide repeated. The user expects variety without asking for it, so build it in from the start rather than waiting to be told.

- Two neighboring slides on the same template are fine when their content calls for it (two lists in a row within one section, two charts of related series); what makes a deck dull is many slides that look identical. Keep a template from running three or more slides in a row or taking more than about a third of the deck: take the alternative the templates skill lists for that content (a bullet list next to an icon list or text boxes, chevrons next to a circular process, a dashboard of statistics next to big numbers, a list next to a two-column comparison) or restructure one of them (two of its points become a statistic, its steps a timeline). And when a template does repeat, make the two slides look different: the other tray side or no tray, the other header position, a colored background on one, a different kind of visual.
- Vary the kind of visual as well: a photo tray on one slide, icons on the next, a chart or a colored cell on the one after. A deck where every slide has the same right-hand photo tray is as monotonous as one with no pictures.
- A picture appears on one slide only. Every slide that gets a picture gets its own, chosen for its subject (a `generate_image_asset` call or another of the user's files per slide); the same photo on two slides looks like a mistake, the title slide's picture included. A logo is the one asset that may repeat.

## Checklist before saving

Run it on the rendered image after your last edit; fix and render again when something fails (at most 3 attempts, then save the best working version and tell the user what remains):

1. Rendered without errors and visibly shows the requested change.
2. Every piece of text readable: nothing overflowing, clipped, truncated, overlapping or too small; good contrast against its background.
3. Not crowded: text blocks and labels have breathing room; the slide does not look dense.
4. Not empty: no large unused area; the content fills the canvas in a balanced way.
5. Not dull: the slide has a visual (image, icon, chart, colored element) unless it is data-dense by nature.
6. Coherent: balanced layout, aligned and evenly spaced elements, theme colors, new content matching the style of the existing content and the deck.
7. Varied: in a deck, not identical to the slide before it (the same template with the same layout), not the third slide in a row on one template, and no picture that is already on another slide of the deck.
