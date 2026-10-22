#!/usr/bin/env python3
"""
PROBE BUILDER — assembles a NextSlide deck by literally consuming the donor's
own source files (no re-implementation):

  donor/viewport-base.css        -> verbatim CSS
  donor/STYLE_PRESETS.md         -> :root block + <link> for a chosen preset
  donor/animation-library.md      -> base + selected @keyframes/.animate-* rules
  donor/html-template.md         -> the JavaScript controller, verbatim

Usage: build_deck.py <spec.json> <out.html>
"""
import json
import os
import re
import sys

DONOR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "donor")


def read(p):
    with open(os.path.join(DONOR, p), encoding="utf-8") as f:
        return f.read()


# ---------- parse STYLE_PRESETS.md ----------
def parse_presets(md):
    presets = {}
    # split on "## Preset N: Name"
    parts = re.split(r"\n## Preset (\d+): (.+)\n", md)
    # parts = [pre, num, name, body, num, name, body, ...]
    for i in range(1, len(parts) - 1, 3):
        num = int(parts[i])
        name = parts[i + 1].strip()
        body = parts[i + 2]
        css = re.search(r"```css\n(:root \{.*?\n\})\n```", body, re.S)
        link = re.search(r"```html\n(<link href=\"https://fonts\.googleapis\.com.*?)\n```", body, re.S)
        if not css:
            continue
        presets[num] = {
            "num": num,
            "name": name,
            "css": css.group(1),
            "link": link.group(1) if link else "",
            "slug": re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-"),
        }
    return presets


# ---------- parse animation-library.md ----------
def parse_animations(md):
    """Return (base_css, {name: css_block}, easing_css, delay_css, duration_css, reduced_css)"""
    blocks = re.findall(r"```css\n(.*?)\n```", md, re.S)
    # block 0 = animation base, 1 = easing, 2 = stagger delays, 3 = duration modifiers
    base = blocks[0]
    easing = blocks[1]
    delays = blocks[2]
    durations = blocks[3]
    reduced = None
    per = {}
    # find per-animation blocks by heading order
    heads = list(re.finditer(r"^### (\d+)\. (animate-[a-z-]+)", md, re.M))
    # map heading -> following css block
    for i, h in enumerate(heads):
        start = h.end()
        end = heads[i + 1].start() if i + 1 < len(heads) else len(md)
        seg = md[start:end]
        m = re.search(r"```css\n(.*?)\n```", seg, re.S)
        if m:
            per[h.group(2)] = m.group(1)
    # reduced-motion block lives in its own section
    rm = re.search(r"## Reduced Motion.*?```css\n(.*?)\n```", md, re.S)
    if rm:
        reduced = rm.group(1)
    return base, easing, delays, durations, reduced, per


# ---------- extract controller JS from html-template.md ----------
def extract_controller(md):
    m = re.search(r"## JavaScript Slide Controller.*?```javascript\n(.*?)\n```", md, re.S)
    if not m:
        raise SystemExit("controller not found")
    return m.group(1)


# ---------- HTML escape ----------
def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def main():
    spec_path, out_path = sys.argv[1], sys.argv[2]
    with open(spec_path, encoding="utf-8") as f:
        spec = json.load(f)

    presets = parse_presets(read("STYLE_PRESETS.md"))
    base, easing, delays, durations, reduced, per = parse_animations(read("animation-library.md"))
    viewport = read("viewport-base.css")
    controller = extract_controller(read("html-template.md"))

    pnum = int(spec["preset"])
    preset = presets[pnum]
    anims = spec.get("animations", ["fade-up"])
    missing = [a for a in anims if a not in per]
    if missing:
        raise SystemExit(f"FATAL: requested animation blocks not found in animation-library.md: {missing}")
    anim_css = "\n".join(per[a] for a in anims)
    # the animate-counter-up marker has no CSS block; emulate donor's intent by
    # using the documented emphasis-opacity exemption list verbatim
    emphasis_exempt = ".animate-pulse,\n.animate-glow,\n.animate-float,\n.animate-shimmer {\n  opacity: 1;\n}"

    slides_html = []
    slide_json = []
    for s in spec["slides"]:
        layout = s["layout"]
        cls = "slide active" if s is spec["slides"][0] else "slide"
        body = s.get("html", "")
        notes = s.get("notes", "")
        aside = f'\n  <aside class="notes">{esc(notes)}</aside>' if notes else ""
        slides_html.append(
            f'    <section class="{cls}" data-slide="{s["n"]}" data-layout="{layout}">\n'
            f'      <div class="slide-content">\n{body}\n      </div>{aside}\n'
            f'    </section>'
        )
        sd = {"layout": layout, "background": {"color": s.get("bg", "#ffffff")},
              "elements": s.get("elements", [])}
        if notes:
            sd["notes"] = notes
        slide_json.append(sd)

    meta = spec["meta"]
    data = {"meta": meta, "slides": slide_json}

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(meta["title"])}</title>

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  {preset["link"]}

  <style>
    /* 1. CSS Variables — from selected preset (STYLE_PRESETS.md) */
{preset["css"]}

    /* 2. Base CSS — full contents of viewport-base.css */
{viewport}

    /* 3. Animations — selected from animation-library.md */
{base}
{easing}
{delays}
{durations}
{emphasis_exempt}
{anim_css}

    /* 4. Reduced motion */
{reduced}

    /* 5. Custom styles */
{spec.get("custom_css", "")}
  </style>
</head>
<body>
  <div class="ns-deck">
    <div class="ns-progress"><div class="ns-progress-bar"></div></div>

{chr(10).join(slides_html)}

    <div class="ns-nav">
      <button class="ns-nav-prev" aria-label="Previous slide">&#8249;</button>
      <button class="ns-nav-next" aria-label="Next slide">&#8250;</button>
    </div>

    <div class="ns-counter">
      <span class="ns-current">1</span> / <span class="ns-total">{len(spec["slides"])}</span>
    </div>
  </div>

  <script type="application/json" id="slide-data">
{json.dumps(data, indent=2)}
  </script>

  <script>
{controller}
  </script>
</body>
</html>
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"wrote {out_path}  preset={pnum} '{preset['name']}'  slides={len(spec['slides'])}  bytes={len(html.encode())}")


if __name__ == "__main__":
    main()
