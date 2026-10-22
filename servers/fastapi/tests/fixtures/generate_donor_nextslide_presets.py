#!/usr/bin/env python3
"""Regenerate the donor style-preset fixture used by the theme legibility tests.

Usage::

    python generate_donor_nextslide_presets.py \
        --donor-style-presets /path/to/0xRafie/nextslide/STYLE_PRESETS.md \
        --output donor_nextslide_presets.json

The generator is deterministic: it performs no network access and no random
selection, so re-running it against the same donor file reproduces the fixture
byte for byte.

Provenance
----------
Donor  : 0xRafie/nextslide @ 90a46f933b3056d27460400c915ef268a9ec3f56
License: MIT, Copyright (c) 2026 Danish Rafie Ekaputra
Scope  : colour custom properties (``--ns-*``) of the donor's 18 style presets.

The fixture exists because the donor's own mandatory design rules specify a
4.5:1 minimum text contrast, yet its shipped presets violate that rule on 10 of
54 text-on-background pairs. That makes the presets a realistic *negative*
fixture for Gomrey's contrast linter.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
from typing import Any

DONOR_REPOSITORY = "https://github.com/0xRafie/nextslide"
DONOR_REVISION = "90a46f933b3056d27460400c915ef268a9ec3f56"
DONOR_LICENSE = "MIT — Copyright (c) 2026 Danish Rafie Ekaputra"

COLOR_TOKENS = (
    "--ns-bg",
    "--ns-bg-alt",
    "--ns-text",
    "--ns-text-muted",
    "--ns-primary",
    "--ns-secondary",
    "--ns-accent",
)

_PRESET_BLOCK = re.compile(
    r"##\s*Preset\s+(\d+):\s*([^\n]+)\n(.*?)```css\s*:root\s*\{(.*?)\}\s*```",
    re.S,
)
_CUSTOM_PROPERTY = re.compile(r"(--ns-[a-z0-9-]+)\s*:\s*([^;]+);")
_HEX_VALUE = re.compile(r"^#[0-9a-fA-F]{6}$")


def extract_presets(style_presets_text: str) -> list[dict[str, Any]]:
    presets: list[dict[str, Any]] = []
    for number, name, _middle, body in _PRESET_BLOCK.findall(style_presets_text):
        tokens: dict[str, str] = {}
        for token, raw_value in _CUSTOM_PROPERTY.findall(body):
            if token not in COLOR_TOKENS:
                continue
            value = raw_value.strip()
            if not _HEX_VALUE.match(value):
                continue
            tokens[token] = value.lower()
        if len(tokens) >= 5:
            presets.append(
                {
                    "preset_number": int(number),
                    "name": name.strip(),
                    "tokens": dict(sorted(tokens.items())),
                }
            )
    return presets


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--donor-style-presets", required=True)
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args()

    source = pathlib.Path(arguments.donor_style_presets)
    presets = extract_presets(source.read_text(encoding="utf-8"))

    payload = {
        "source": {
            "repository": DONOR_REPOSITORY,
            "revision": DONOR_REVISION,
            "license": DONOR_LICENSE,
            "source_path": "STYLE_PRESETS.md",
            "extracted": "colour custom properties (--ns-*) of each preset :root block",
        },
        "presets": presets,
    }

    destination = pathlib.Path(arguments.output)
    destination.write_text(
        json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )
    print(f"wrote {destination} with {len(presets)} presets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
