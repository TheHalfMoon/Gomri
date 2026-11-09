---
name: beautiful-ai-slide-elements
description: Model reference for Beautiful.ai slides, one document per slide element - the fields each template's root element and its nested elements expect in states[0], allowed values, limits and pitfalls. Use when building or editing a slide model for create_slide or update_slide, before rendering it with render_slide.
---

# Beautiful.ai slide elements

A slide is rendered by a tree of elements, and the slide model mirrors that tree: `states[0].primary` is the model of the template's root element, and every element the root nests reads its own part of that model (an item of `items[]`, a `childElement`, a text block, a media slot). This skill documents, per element, what that part must contain. The documents are in `elements/<Element>.md` (served as `beautiful-ai://skills/slide-elements/elements/<Element>.md`).

How to use it:

1. Start with `Slide.md`: the slide model as a whole (`template_id`, `states[0]` and its keys, the `layout` object).
2. Find the template in the table below and read its root element's document, then the documents in "Also read" for the parts you are going to write.
3. Read the building blocks the first time you write them: `TextElement.md` (every text field is a `{ blocks: [...] }` object), `ContentElement.md` with `Picture.md` / `Icon.md` (every image, logo or icon slot is a `content_type` + `content_value` pair), `CollectionElement.md` (every `items[]` array), `Header.md` and `SideBarContainer.md` (the header and the side tray that most templates allow).
4. Build the model, render it (`render_slide`, or the save tools with `render: true`) and fix what the render reports before saving. When a document leaves you unsure of a template's shape, a real model of it (`get_slide_examples`) or its `defaultData` (`list_slide_templates`) settles it.

Every document has the same shape, in the order you need it: where the model lives, a minimal example, the pitfalls, the rules and limits, and last, under "Full reference", the complete field tables and the nested elements. The first four sections are what you need to write the element; read the full reference for a field the example does not show, or for its exact values and units.

The documents describe the current model. Stored slides (`get_slide`) also carry computed caches (text `blockBounds`, `textStyles`, …) and bookkeeping fields: never author those, the documents say which fields are yours to write (`get_slide_examples` returns its examples without them).

## Templates and their elements

| Template id | Root element | Also read |
|---|---|---|
| `action-number` | `ActionNumber.md` | |
| `agenda` | `Agenda.md` | `TextList.md` |
| `arrow_bars` | `ArrowBars.md` | |
| `authoring` | `AuthoringCanvas.md` | `AuthoringElementContainer.md`, then per element: `AuthoringShapeElement.md`, `AuthoringPathElement.md`, `AuthoringContentElement.md`, `AuthoringVideo.md` |
| `big-numbers` | `BigNumbers.md` | |
| `calendar-month`, `calendar-week` | `Calendar.md` | `VerticalTaskLists.md` (the week view) |
| `compare_circles` | `CompareBubble.md` | `CompareValuesCollection.md` |
| `compare_horizontal_bars` | `CompareHorizontalBar.md` | `CompareValuesCollection.md` |
| `compare_radial_bars` | `CompareRadialBar.md` | `CompareValuesCollection.md`, `RadialBarInfographic.md` (the ring) |
| `compare_vertical_bars` | `CompareVerticalBar.md` | `CompareValuesCollection.md` |
| `compare_vertical_pictograph` | `CompareVerticalPictograph.md` | `CompareValuesCollection.md`, `PictorialCharts.md` (the icon grid) |
| `connection_diagram` | `ConnectionDiagram.md` | `TextAndImage.md` |
| `contactus` | `ContactInfo.md` | |
| `countdown` | `Countdown.md` | |
| `cycle_diagram` | `CycleDiagram.md` | |
| `dashboard`, `chart_line`, `chart_column`, `chart_bar`, `chart_area`, `chart_waterfall`, `chart_pie`, `table-v2` | `Dashboard.md` | `GridLayoutContainer.md`, `LayoutContainerItem.md`, then per cell: `Chart.md`, `PieChart.md`, `Statistic.md`, `RadialBarInfographic.md`, `RadialBarChart.md`, `Table.md`, `TextAndImage.md` |
| `flow_chart` | `NodeDiagram.md` | `CalloutsCanvas.md`, `ConnectorGroup.md` |
| `gantt_chart` | `GanttChart.md` | |
| `headline2`, `section` | `Headline.md` | `TextFrame.md`, `PhotoCollage.md` (the images) |
| `horizontal-funnel` | `HorizontalFunnel.md` | `Ornament.md` |
| `horizontal-task-list` | `HorizontalTaskLists.md` | |
| `hub_and_spoke` | `HubAndSpoke.md` | `ContentItem.md`, `ConnectorGroup.md` |
| `image`, `collage` | `PhotoCollage.md` | `GridLayoutContainer.md`, `LayoutContainerItem.md`, `TextAndImage.md` (the cells) |
| `journey` | `Journey.md` | |
| `kanban` | `VerticalTaskLists.md` | |
| `logogrid` | `LogoGrid.md` | |
| `orgchart` | `OrgChart.md` | |
| `product_laptop` | `ProductScreenshot.md` | `TextList.md` |
| `pyramid`, `funnel` | `Pyramid.md` | |
| `radial_bar_chart` | `RadialBarChart.md` | |
| `roi_calculator` | `ROICalculator.md` | |
| `sequence`, `gears`, `puzzle` | `Sequence.md` | |
| `slicechart` | `SliceChart.md` | `Ornament.md` |
| `slidePlaceholder` | `SlidePlaceholder.md` | |
| `stackDiagram` | `StackDiagram.md` | `GridLayoutContainer.md`, `LayoutContainerItem.md`, `TextAndImage.md` |
| `step_boxes` | `ProcessDiagramBoxes.md` | `ProcessDiagram.md` |
| `step_chevrons` | `ProcessDiagramChevrons.md` | `ProcessDiagram.md`, `Ornament.md` |
| `step_circular` | `IconCircle.md` | `ContentItem.md`, `ConnectorGroup.md` |
| `swot_diagram` | `SwotDiagram.md` | |
| `target` | `Target.md` | `CalloutsCanvas.md` (annotations) |
| `team` | `Team.md` | |
| `text`, `long_bio` | `TextSlide.md` | |
| `textBoxGrid` | `TextBoxGrid.md` | `Ornament.md` |
| `textgrid_carousel` | `ImageCarousel.md` | `PhotoCollage.md`, `GridLayoutContainer.md`, `TextAndImage.md` (the cells) |
| `textgrid_photos` | `PhotoTextList.md` | |
| `textgrid_vertical_icons` | `IconTextGrid.md` | |
| `textlist` | `TextList.md` | |
| `thermometer` | `Thermometer.md` | `CalloutsCanvas.md` (annotations) |
| `timeline` | `Timeline.md` | `ContentItem.md` (the milestones), `ConnectorGroup.md`, `CalloutsCanvas.md` (annotations) |
| `timer` | `Timer.md` | |
| `title` | `PresentationTitle.md` | `TextFrame.md` |
| `user_testimonial` | `UserTestimonial.md` | |
| `vennDiagram` | `VennDiagram.md` | |
| `video` | `Video.md` | |
| `visual_percentage` | `PictorialCharts.md` | |
| `web-view` | `WebView.md` | |
| `wordCloud` | `WordCloudElement.md` | |
| `world_map` | `WorldMap.md` | |
| `xygraph` | `XYGraph.md` | `CalloutsCanvas.md` (annotations) |

## Building blocks

Shared by many roots; their documents are the reference for the fields they read wherever they appear.

- `Slide.md`: the whole slide model and its `layout` (header position, tray layout, footer, background).
- `Header.md` (`states[0].header`), `SideBarContainer.md` (`states[0].tray`, the side trays), `BottomTray.md` (the bottom tray and the element text block / attribution), `Footer.md`, `CanvasBackground.md` (`layout.backgroundColor` and friends).
- `BaseElement.md`: the fields every element reads; `CollectionElement.md`: how `items[]` work (ids, order, counts).
- `TextElement.md`: text blocks, text styles, list styles (bullets, numbers, checklists, icons); `TextFrame.md`: the framed text block of titles and headlines.
- `ContentElement.md`: a media slot and how `content_type` picks `Picture.md` (images and logos), `Icon.md` (built-in icons, see `list_icons`), `VideoElement.md`; `MediaElement.md`: the shared crop / scale / filter fields; `FramedMediaElement.md`: a media slot with a frame shape.
- `TextAndImage.md`: text with an optional image, used by dashboard cells, trays and several diagrams.
- `GridLayoutContainer.md` and `LayoutContainerItem.md`: the grid of cells behind dashboards, photo collages, stack diagrams and trays; the cell components `Chart.md`, `PieChart.md`, `Statistic.md`, `RadialBarInfographic.md`, `Table.md`.
- `CalloutsCanvas.md`: free-floating callouts and annotations (on flow charts, targets, thermometers, XY graphs, timelines and the slide itself), whose entries are described by `CalloutElement.md` (the shared contract and the `calloutType` table) and per type by `TextCallout.md`, `MarkerCallout.md` (bullet, numbered, lettered markers), `MediaCallout.md`, `MediaAndTextCallout.md`, `FlexCircleCallout.md` and `ShapeCallout.md` (boxes, diamonds, circles, pills); `AuthoringCanvas.md`: the free-form canvas, whose entries are `AuthoringElementContainer.md` (position, size, rotation, type) around one of `AuthoringShapeElement.md` (shapes and text boxes), `AuthoringPathElement.md` (lines and arrows), `AuthoringContentElement.md` (images and icons), `AuthoringVideo.md`, and the legacy `AuthoringSvgElement.md` / `AuthoringRadialBar.md`; `ConnectorGroup.md`: the connectors between items; `ContentItem.md`: the nodes (text with a dot, number, letter, icon or shape) of hub-and-spoke, icon circle and timeline diagrams.
- `Ornament.md`: the number / letter / icon badge on the items of step chevrons, slice charts, horizontal funnels and text box grids.
- `CompareValuesCollection.md`: the shared model of the five compare charts; `ProcessDiagram.md`: the shared model of the step diagrams.
