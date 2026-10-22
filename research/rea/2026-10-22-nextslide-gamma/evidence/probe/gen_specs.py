#!/usr/bin/env python3
"""
PROBE SPEC GENERATOR — synthetic deck content: "Ocean Plastic Reduction: 2026 Strategy".
Builds 3 variants of the SAME content with different presets and layout mixes.
Emits spec_*.json for build_deck.py
"""
import json
import os
import sys

OUT = os.path.dirname(os.path.abspath(__file__))

# A tiny inline SVG (data URI) so the deck fetches NOTHING remote and the
# PPTX exporter embeds a real image instead of a dead URL.
SVG = (
    "data:image/svg+xml;base64,"
    "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MDAiIGhlaWdodD0iMjUwIj4"
    "<defs+PC9kZWZzPg=="
)
# build a real valid svg properly
import base64
_svg = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600">'
    '<rect width="800" height="600" fill="#0b3d5c"/>'
    '<circle cx="400" cy="300" r="180" fill="#0e7490" opacity="0.85"/>'
    '<path d="M0 430 Q200 380 400 430 T800 430 L800 600 L0 600 Z" fill="#155e75"/>'
    '<text x="400" y="300" font-family="sans-serif" font-size="46" fill="#e0f2fe" '
    'text-anchor="middle">11M tonnes / yr</text></svg>'
)
IMG = "data:image/svg+xml;base64," + base64.b64encode(_svg.encode()).decode()


def T(content, role, x, y, w, h, size, face, color, bold=False, align="left", valign="middle"):
    """Text element for slide-data JSON (sizes in POINTS)."""
    return {
        "type": "text", "content": content, "role": role,
        "position": {"x": x, "y": y, "w": w, "h": h},
        "style": {"fontSize": size, "fontFace": face, "bold": bold,
                  "color": color, "align": align, "valign": valign},
    }


def h1(text, delay="", align=None):
    a = f' style="text-align:{align}"' if align else ""
    return f'        <h1 class="animate-fade-up {delay}"{a}>{text}</h1>'


def p(text, cls="", delay=""):
    return f'        <p class="{cls} animate-fade-up {delay}">{text}</p>'


# --------------------------------------------------------------------------
# SLIDE BODY BUILDERS  (each returns (html, elements))
# --------------------------------------------------------------------------

def s_title(t, sub, meta, face, color, muted, bg):
    html = "\n".join([
        h1(t),
        p(sub, "subtitle", "delay-200"),
        p(meta, "meta", "delay-400"),
    ])
    els = [
        T(t, "title", "10%", "28%", "80%", "22%", 44, face, color, True, "center"),
        T(sub, "subtitle", "15%", "55%", "70%", "12%", 24, "Inter", muted, False, "center"),
        T(meta, "caption", "20%", "70%", "60%", "8%", 16, "Inter", muted, False, "center"),
    ]
    return html, els


def s_content(head, body, face, color, muted):
    html = "\n".join([h1(head), p(body, "", "delay-200")])
    els = [
        T(head, "title", "5%", "8%", "90%", "12%", 36, face, color, True),
        T(body, "body", "5%", "24%", "75%", "34%", 20, "Inter", color),
    ]
    return html, els


def s_section(head, sub, face, color, muted):
    html = "\n".join([h1(head), p(sub, "subtitle", "delay-200")])
    els = [
        T(head, "title", "15%", "35%", "70%", "20%", 40, face, color, True, "center"),
        T(sub, "subtitle", "25%", "58%", "50%", "10%", 22, "Inter", muted, False, "center"),
    ]
    return html, els


def s_bullets(head, items, face, color, muted):
    lis = "\n".join(
        f'          <li class="animate-fade-up delay-{100*(i+1)}">{t}</li>'
        for i, t in enumerate(items)
    )
    html = f'        <h1 class="animate-fade-up">{head}</h1>\n        <ul class="ns-bullets">\n{lis}\n        </ul>'
    els = [T(head, "title", "5%", "8%", "90%", "12%", 36, face, color, True)]
    for i, t in enumerate(items):
        els.append(T(t, "body", "5%", f"{26 + i*11}%", "72%", "9%", 22, "Inter", color))
    return html, els


def s_two_column(head, lh, lb, rh, rb, face, color, muted):
    html = "\n".join([
        h1(head),
        '        <div class="ns-columns">',
        '          <div class="ns-col animate-fade-up delay-200">',
        f'            <h3>{lh}</h3>',
        f'            <p>{lb}</p>',
        '          </div>',
        '          <div class="ns-col animate-fade-up delay-400">',
        f'            <h3>{rh}</h3>',
        f'            <p>{rb}</p>',
        '          </div>',
        '        </div>',
    ])
    els = [
        T(head, "title", "5%", "6%", "90%", "12%", 36, face, color, True),
        T(lh, "label", "5%", "24%", "45%", "8%", 22, face, color, True),
        T(lb, "body", "5%", "33%", "45%", "34%", 20, "Inter", color),
        T(rh, "label", "52%", "24%", "45%", "8%", 22, face, color, True),
        T(rb, "body", "52%", "33%", "45%", "34%", 20, "Inter", color),
    ]
    return html, els


def s_chart(head, data, primary, face, color):
    rows = "\n".join(
        f'        <div class="ns-bar-row">\n'
        f'          <span class="ns-bar-label">{lbl}</span>\n'
        f'          <div class="ns-bar-track">\n'
        f'            <div class="ns-bar-fill animate-scale-x delay-{100*i}" style="--ns-bar-value: {pct}%">\n'
        f'              <span class="ns-bar-value">{val}</span>\n'
        f'            </div>\n'
        f'          </div>\n'
        f'        </div>'
        for i, (lbl, pct, val) in enumerate(data)
    )
    html = (
        f'        <h1 class="animate-fade-up">{head}</h1>\n'
        f'        <div class="ns-chart-container animate-fade-up delay-200">\n'
        f'          <div class="ns-chart ns-chart-bar-h">\n'
        f'            <h3 class="ns-chart-title">Annual plastic input by source</h3>\n'
        f'            <div class="ns-chart-body">\n{rows}\n            </div>\n'
        f'          </div>\n'
        f'        </div>'
    )
    els = [T(head, "title", "5%", "6%", "90%", "12%", 34, face, color, True)]
    els.append({
        "type": "chart", "chartType": "bar",
        "data": [{"label": lbl, "value": float(val.replace("M t", ""))} for lbl, _pct, val in data],
        "position": {"x": "10%", "y": "24%", "w": "80%", "h": "58%"},
        "style": {"barColor": primary, "labelColor": "#64748b"},
    })
    return html, els


def s_comparison(head, lh, lb, rh, rb, face, color, primary):
    html = "\n".join([
        h1(head, align="center"),
        '        <div class="ns-compare">',
        f'          <div class="ns-compare-card animate-scale-up delay-200">',
        f'            <h3>{lh}</h3>',
        f'            <p>{lb}</p>',
        '          </div>',
        f'          <div class="ns-compare-card animate-scale-up delay-400">',
        f'            <h3>{rh}</h3>',
        f'            <p>{rb}</p>',
        '          </div>',
        '        </div>',
    ])
    els = [
        T(head, "title", "5%", "6%", "90%", "12%", 34, face, color, True, "center"),
        T(lh, "label", "6%", "24%", "42%", "8%", 24, face, primary, True),
        T(lb, "body", "6%", "33%", "42%", "34%", 20, "Inter", color),
        T(rh, "label", "53%", "24%", "42%", "8%", 24, face, primary, True),
        T(rb, "body", "53%", "33%", "42%", "34%", 20, "Inter", color),
    ]
    return html, els


def s_quote(quote, attr, face, color, muted):
    html = "\n".join([
        '        <div class="ns-quote animate-fade-in duration-slow">',
        f'          <blockquote>{quote}</blockquote>',
        f'          <p class="ns-attribution animate-fade-up delay-400">{attr}</p>',
        '        </div>',
    ])
    els = [
        T(quote, "body", "15%", "30%", "70%", "26%", 32, face, color, False, "center"),
        T(attr, "caption", "30%", "60%", "40%", "8%", 18, "Inter", muted, False, "center"),
    ]
    return html, els


def s_timeline(head, items, face, color, muted):
    blocks = []
    els = [T(head, "title", "5%", "6%", "90%", "12%", 36, face, color, True)]
    for i, (date, title, desc) in enumerate(items):
        side = "fade-left" if i % 2 == 0 else "fade-right"
        blocks.append(
            f'          <div class="ns-timeline-item animate-{side} delay-{200*(i+1)}">\n'
            f'            <div class="ns-timeline-marker{" active" if i == len(items)-1 else ""}"></div>\n'
            f'            <div class="ns-timeline-content">\n'
            f'              <span class="ns-timeline-date">{date}</span>\n'
            f'              <h4 class="ns-timeline-title">{title}</h4>\n'
            f'              <p class="ns-timeline-desc">{desc}</p>\n'
            f'            </div>\n'
            f'          </div>'
        )
        els.append(T(f"{date} — {title}: {desc}", "body", "8%", f"{26+i*18}%", "84%", "12%", 16, "Inter", color))
    html = f'        <h1 class="animate-fade-up">{head}</h1>\n        <div class="ns-timeline">\n' + "\n".join(blocks) + "\n        </div>"
    return html, els


def s_image_left(head, body, alt, face, color):
    html = "\n".join([
        '        <div class="ns-split">',
        f'          <div class="ns-split-image animate-fade-in"><img src="{IMG}" alt="{alt}"></div>',
        '          <div class="ns-split-text">',
        f'            <h1 class="animate-fade-up delay-200">{head}</h1>',
        f'            <p class="animate-fade-up delay-400">{body}</p>',
        '          </div>',
        '        </div>',
    ])
    els = [
        {"type": "image", "src": IMG, "alt": alt,
         "position": {"x": "0%", "y": "0%", "w": "50%", "h": "100%"},
         "style": {"objectFit": "cover", "borderRadius": 0}},
        T(head, "title", "54%", "18%", "42%", "16%", 34, face, color, True),
        T(body, "body", "54%", "38%", "42%", "34%", 20, "Inter", color),
    ]
    return html, els


def s_image_right(head, body, alt, face, color):
    html = "\n".join([
        '        <div class="ns-split">',
        '          <div class="ns-split-text">',
        f'            <h1 class="animate-fade-up">{head}</h1>',
        f'            <p class="animate-fade-up delay-200">{body}</p>',
        '          </div>',
        f'          <div class="ns-split-image animate-fade-in delay-200"><img src="{IMG}" alt="{alt}"></div>',
        '        </div>',
    ])
    els = [
        T(head, "title", "4%", "18%", "42%", "16%", 34, face, color, True),
        T(body, "body", "4%", "38%", "42%", "34%", 20, "Inter", color),
        {"type": "image", "src": IMG, "alt": alt,
         "position": {"x": "50%", "y": "0%", "w": "50%", "h": "100%"},
         "style": {"objectFit": "cover", "borderRadius": 0}},
    ]
    return html, els


def s_blank_cards(head, cards, face, color, muted):
    inner = "\n".join(
        f'            <div class="ns-icon-card animate-fade-up delay-{100*(i+1)}">\n'
        f'              <div class="ns-icon">{icon}</div>\n'
        f'              <h4>{t}</h4>\n'
        f'              <p>{d}</p>\n'
        f'            </div>'
        for i, (icon, t, d) in enumerate(cards)
    )
    html = (
        f'        <h1 class="animate-fade-up">{head}</h1>\n'
        f'        <div class="ns-icon-grid">\n{inner}\n        </div>'
    )
    els = [T(head, "title", "5%", "6%", "90%", "12%", 36, face, color, True)]
    for i, (icon, t, d) in enumerate(cards):
        els.append(T(f"{icon} {t} — {d}", "body", f"{5+i*31}%", "26%", "29%", "22%", 16, "Inter", color))
    return html, els


def s_counter(head, face, color, muted, primary):
    """Slide that exercises the .animate-counter-up marker class."""
    html = "\n".join([
        h1(head),
        '        <div class="ns-metrics" style="margin-top: var(--ns-space-lg)">',
        '          <div class="ns-metric-card animate-fade-up">',
        '            <span class="ns-metric-value" data-target="11">0</span>',
        '            <span class="ns-metric-label">Million tonnes / year</span>',
        '          </div>',
        '          <div class="ns-metric-card animate-fade-up delay-100">',
        '            <span class="ns-metric-value animate-counter-up" data-target="73">73%</span>',
        '            <span class="ns-metric-label">Target reduction by 2030</span>',
        '          </div>',
        '        </div>',
    ])
    els = [
        T(head, "title", "5%", "8%", "90%", "12%", 36, face, color, True),
        T("11", "title", "8%", "30%", "40%", "18%", 44, face, color, True, "center"),
        T("73%", "title", "52%", "30%", "40%", "18%", 44, face, color, True, "center"),
    ]
    return html, els


# --------------------------------------------------------------------------
# CONTENT MODEL (shared across variants)
# --------------------------------------------------------------------------
CONTENT = {
    "title": "Ocean Plastic Reduction",
    "subtitle": "2026 Strategy",
    "meta": "Global Marine Resilience Initiative · October 2026",
    "content_head": "The ocean absorbs 11 million tonnes of plastic annually",
    "content_body": ("Atmospheric and riverside leakage pushes an estimated 11 million tonnes of "
                     "plastic into the ocean every year — a figure projected to nearly triple by "
                     "2040 without intervention. The 2026 strategy concentrates on upstream "
                     "interception, where prevention costs a fraction of downstream cleanup."),
    "section_head": "Three Pillars",
    "section_sub": "Intercept, Innovate, Regenerate",
    "bullets_head": "Five commitments for 2026",
    "bullets": [
        "River interception at 1,400 high-load catchments worldwide",
        "Producer-funded reuse infrastructure in 12 coastal markets",
        "Single-use polymer phase-out in packaging and hospitality",
        "Open chemical-recycling feedstock contracts for PET and nylon",
        "Verified marine habitat restoration across 200,000 hectares",
    ],
    "twocol_head": "Where we are vs. where we need to be",
    "twocol_lh": "Today",
    "twocol_lb": ("Roughly 9% of ocean plastic is removed each year, concentrated in a handful "
                  "of high-visibility cleanup projects that rarely touch the highest-volume sources."),
    "twocol_rh": "2026 target",
    "twocol_rb": ("A 73% reduction in annual ocean-bound plastic by 2030, achieved through "
                  "upstream interception rather than post-hoc recovery."),
    "chart_head": "73% of ocean plastic traces to five river systems",
    "chart": [
        ("Ganges", 100, "2.0M t"),
        ("Nile", 78, "1.6M t"),
        ("Yangtze", 66, "1.3M t"),
        ("Mekong", 44, "0.9M t"),
        ("Other", 39, "0.8M t"),
    ],
    "comparison_head": "Prevention now, not cleanup later",
    "comparison_lh": "Cleanup first",
    "comparison_lb": ("Recovery happens after damage is done. Cost per tonne stays above $4,000 "
                      "and ecological benefit is local and short-lived."),
    "comparison_rh": "Prevention first",
    "comparison_rb": ("Intercepting at source prevents emission entirely. Cost per tonne falls "
                      "below $180 and avoided emissions compound every year."),
    "quote": "We cannot clean the ocean faster than we are polluting it.",
    "quote_attr": "— Marine Policy Review, 2026",
    "timeline_head": "The road to 2030",
    "timeline": [
        ("Q1 2026", "Baselines locked", "Audited plastic flow data published for 40 river basins."),
        ("Q3 2026", "Interception live", "1,400 catchment barriers reach full deployment."),
        ("Q1 2027", "Reuse at scale", "Reusable packaging available in 12 coastal markets."),
        ("Q4 2030", "73% reduction", "Verified year-on-year reduction against 2024 baseline."),
    ],
    "imageleft_head": "Plastic concentrates at river mouths",
    "imageleft_body": ("Riverine transport dominates: 80% of ocean-bound plastic enters through "
                       "a limited number of catchments, making interception the highest-leverage "
                       "intervention available."),
    "imageright_head": "Monitoring becomes the bottleneck",
    "imageright_body": ("Audit-grade measurement of plastic flows is now the limiting factor. "
                        "Without it, reduction targets cannot be independently verified."),
    "blank_head": "Three enablers, one deadline",
    "blank_cards": [
        ("🔒", "Reuse policy", "12 coastal markets by end of 2026"),
        ("📊", "Verified data", "40 audited river basins, open methodology"),
        ("💰", "Producer funding", "$1.8B committed over five years"),
    ],
    "counter_head": "The 2026 baseline",
    "closing_head": "Reduce at source, measure honestly",
    "closing_body": ("The 2026 strategy treats interception, reuse infrastructure and producer "
                     "funding as a single system. Progress is published quarterly against an "
                     "audited baseline, and every claim in this deck is traceable to a public "
                     "methodology."),
}


def build_slide(n, layout, kind, face, color, muted, primary, bg, notes):
    """kind selects the body builder; returns slide dict."""
    C = CONTENT
    if kind == "title":
        html, els = s_title(C["title"], C["subtitle"], C["meta"], face, color, muted, bg)
    elif kind == "content":
        html, els = s_content(C["content_head"], C["content_body"], face, color, muted)
    elif kind == "section":
        html, els = s_section(C["section_head"], C["section_sub"], face, color, muted)
    elif kind == "bullets":
        html, els = s_bullets(C["bullets_head"], C["bullets"], face, color, muted)
    elif kind == "two-column":
        html, els = s_two_column(C["twocol_head"], C["twocol_lh"], C["twocol_lb"],
                                 C["twocol_rh"], C["twocol_rb"], face, color, muted)
    elif kind == "chart":
        html, els = s_chart(C["chart_head"], C["chart"], primary, face, color)
    elif kind == "comparison":
        html, els = s_comparison(C["comparison_head"], C["comparison_lh"], C["comparison_lb"],
                                 C["comparison_rh"], C["comparison_rb"], face, color, primary)
    elif kind == "quote":
        html, els = s_quote(C["quote"], C["quote_attr"], face, color, muted)
    elif kind == "timeline":
        html, els = s_timeline(C["timeline_head"], C["timeline"], face, color, muted)
    elif kind == "image-left":
        html, els = s_image_left(C["imageleft_head"], C["imageleft_body"],
                                 "Ocean plastic concentration illustration", face, color)
    elif kind == "image-right":
        html, els = s_image_right(C["imageright_head"], C["imageright_body"],
                                  "Marine monitoring illustration", face, color)
    elif kind == "blank":
        html, els = s_blank_cards(C["blank_head"], C["blank_cards"], face, color, muted)
    elif kind == "counter":
        html, els = s_counter(C["counter_head"], face, color, muted, primary)
    else:  # closing (content layout)
        html, els = s_content(C["closing_head"], C["closing_body"], face, color, muted)
    return {"n": n, "layout": layout, "html": html, "elements": els,
            "bg": bg, "notes": notes}


def variant(name, preset_num, kinds, face, color, muted, primary, bg, title_suffix, anims):
    slides = []
    for i, (layout, kind) in enumerate(kinds, start=1):
        notes = f"Speaker note for slide {i} ({kind}). Expand with regional detail and cite the 2026 audit."
        slides.append(build_slide(i, layout, kind, face, color, muted, primary, bg, notes))
    spec = {
        "preset": preset_num,
        "animations": anims,
        "meta": {
            "title": f"Ocean Plastic Reduction: 2026 Strategy{title_suffix}",
            "author": "Gomrey Research Probe",
            "date": "2026-10-22",
            "theme": name,
            "slideWidth": 13.333,
            "slideHeight": 7.5,
        },
        "slides": slides,
    }
    p = os.path.join(OUT, f"spec_{name}.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2)
    print(f"wrote {p}  slides={len(slides)}  layouts={[k[0] for k in kinds]}")


ANIMS = ["animate-fade-up", "animate-fade-down", "animate-fade-left",
         "animate-fade-right", "animate-fade-in", "animate-scale-up",
         "animate-scale-down", "animate-scale-x", "animate-scale-y",
         "animate-blur-in", "animate-flip-x", "animate-flip-y",
         "animate-zoom-in", "animate-pop", "animate-rotate-in",
         "animate-slide-in-left", "animate-slide-in-right",
         "animate-typewriter", "animate-draw-line", "animate-pulse",
         "animate-glow", "animate-float", "animate-shimmer"]

if __name__ == "__main__":
    # Variant A — Corporate Pro (preset 2), light
    variant("corporate-pro", 2, [
        ("title", "title"), ("content", "content"), ("section", "section"),
        ("bullets", "bullets"), ("chart", "chart"), ("comparison", "comparison"),
        ("quote", "quote"), ("timeline", "timeline"), ("content", "closing"),
    ], "Sora", "#1e293b", "#475569", "#2563eb", "#ffffff", " — Corporate Pro", ANIMS)

    # Variant B — Midnight Pro (preset 16), dark
    variant("midnight-pro", 16, [
        ("title", "title"), ("two-column", "two-column"), ("section", "section"),
        ("chart", "chart"), ("image-left", "image-left"), ("image-right", "image-right"),
        ("blank", "blank"), ("counter", "counter"), ("content", "closing"),
    ], "Sora", "#e2e8f0", "#94a3b8", "#3b82f6", "#0f172a", " — Midnight Pro", ANIMS)

    # Variant C — Botanical (preset 14), light; includes a second chart-family slide
    variant("botanical", 14, [
        ("title", "title"), ("bullets", "bullets"), ("two-column", "two-column"),
        ("comparison", "comparison"), ("quote", "quote"), ("content", "closing"),
    ], "Cormorant Garamond", "#14532d", "#16a34a", "#15803d", "#f0fdf4",
        " — Botanical", ANIMS)
