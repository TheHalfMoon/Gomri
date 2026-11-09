# Footer

`Footer` renders the 50 px strip across the bottom of the slide with the theme's logo, footer message and
slide number. Everything it shows comes from the presentation theme (`logo`, `logo_dark`, `footerMessage`,
`showLogo`, `showMessage`, `showPageNum`, `logoPosition`, `logoScale`, `logoOffset`); the slide model can only
override those switches per slide. `CanvasElement` creates it when the footer is enabled for the slide (see
`layout.showFooter` in `Slide.md`); it is never a template's root element.

## Model location

- `states[0].footer` (an empty `{}` is created when the footer shows and the key is missing).
- Whether the footer shows at all is decided by `layout.showFooter` on the slide, not by this object.

## Minimal example

Theme footer forced on, with the slide number but without the message:

```json
{
  "layout": { "showFooter": "on" },
  "states": [ { "footer": { "showPageNumOverride": true, "showMessageOverride": false } } ]
}
```

In the common case write nothing: `layout.showFooter: "theme"` and no `states[0].footer`.

## Pitfalls

- `states[0].footer` alone does nothing: the footer is switched on by `layout.showFooter`.
- `layout.showFooter: true` / `false` (booleans in old slides) are not `"on"` / `"off"`; they behave like
  `"theme"`.
- `showFooter: "on"` is ignored while `elementTextBlockPosition` is `"tray"`.
- `showLogoOverride: true` cannot show a logo the theme does not have, and `logoTypeOverride` has no effect
  unless the theme has both logo variants.

## Rules and limits

- Shown when all of these hold: the template's `allowFooter` is true (false only for `title`, `ppt-slide`,
  `slidePlaceholder`, `ai-generation`); `layout.elementTextBlockPosition` is not `"tray"`;
  `layout.trayLayout` is not `bottom_tray`; and `layout.showFooter` resolves to on: `"on"` → shown, `"off"` →
  hidden, `"theme"` / absent → shown only when the theme's `showFooterByDefault` is `true` **and** the template's
  `preventDefaultFooter` is `false`. `preventDefaultFooter` is true for the headline / image family
  (`headline2`, `section`, `headline`, `chapter`, `headline_image`, `picture_headline_right`, `image`,
  `collage`, `picture_picture`, `text_text`, `culturegrid`, `aboutUs`, `contactus`): those show a footer only
  with `showFooter: "on"`. Most built-in themes have `showFooterByDefault: false`, so `"theme"` usually means no
  footer.
- Geometry: full canvas width, 50 px high, anchored to the bottom of the canvas (it overlaps a full-bleed
  side tray). The primary element gives up 40 px at the bottom only when it reserves footer space (the
  default for every element; `PhotoCollage` and `Headline` do not when they are full-bleed without gutters,
  so there the footer is drawn over the image).
- Logo scale: logos with aspect ratio < 1.5 fill the footer height; wider logos are capped at 100 px width;
  both multiplied by the theme's `logoScale`.
- `_migrate_10_02` of `CanvasElement` sets `showFooter: "off"` on `authoring` (classic) slides, which draw
  their own footer.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

All fields are optional per-slide overrides of theme settings; an absent field means "as the theme says".

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `showMessageOverride` | boolean | default: theme `showMessage` | Show / hide the theme's footer message on this slide. |
| `showPageNumOverride` | boolean | default: theme `showPageNum` | Show / hide the slide number. The number is computed at render time (skipped slides show "X" in the editor). |
| `showLogoOverride` | boolean | default: theme `showLogo` | Show / hide the theme logo. Has no effect when the theme has no logo at all. |
| `logoPositionOverride` | string | `"left"`, `"right"`; default: theme `logoPosition` or `"left"` | Side of the logo; the slide number takes the opposite side, the message is centred. |
| `logoTypeOverride` | string | `"light"`, `"dark"`; default (absent): picked from the background colour (`logo_dark` on dark or image backgrounds when the theme has one) | Which theme logo variant to use. Only meaningful when the theme defines both `logo` and `logo_dark`. The editor can also store `"auto"`, but any stored value bypasses the automatic choice and anything other than `"dark"` loads the light logo: omit the field for automatic. |
| `overrideStyle` | string | `"auto"` (default), `"light"`, `"dark"` | Which background the footer assumes it sits on, to pick contrasting text / logo colours: `"auto"` asks the primary element for its background colour; `"light"` / `"dark"` force a light / dark background. |
| `color` | – | found in old examples | Not read by the v10 footer. Do not write. |

Plus the common fields, see `BaseElement.md` (none matter here).

### Nested elements

- `message` -> `FooterMessage` (a non-editable `TextElement` showing the theme's `footerMessage`); no model.
- `slideNum` -> `TextElement` showing the slide index + 1; no model (the value is recomputed on every render).
- The logo is an `<img>` drawn by the footer itself, with a white frame behind it on non-light backgrounds
  when the theme has no dark logo variant.
