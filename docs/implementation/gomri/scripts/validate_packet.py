#!/usr/bin/env python3
"""Read-only PStack packet integrity checker; Python stdlib only, no network."""

from __future__ import annotations

import argparse
import csv
import io
import json
import pathlib
import posixpath
import re
import subprocess
import sys


PREFIX = "docs/implementation/gomri/"


def git(repo: pathlib.Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo), *args],
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=pathlib.Path, default=pathlib.Path.cwd())
    parser.add_argument("--ref", default="HEAD", help="Exact SHA or fetched branch ref")
    parser.add_argument("--json-out", type=pathlib.Path, default=None)
    args = parser.parse_args()
    repo = args.repo.resolve()

    root = git(repo, "rev-parse", "--show-toplevel").strip()
    revision = git(repo, "rev-parse", args.ref).strip()
    tree = set(git(repo, "ls-tree", "-r", "--name-only", revision).splitlines())
    packet = sorted(x for x in tree if x.startswith(PREFIX) and x.endswith(".md"))
    extras = [
        "docs/designs/GOMRI_EGM_P0_EXECUTION_CONTRACT_2026-11-09.md",
        "docs/designs/GOMRI_EGM_P0B_ISOLATION_CONTRACT_2026-11-09.md",
        "docs/designs/GOMRI_EGM_CONVERGED_EDITOR_2026-11-09.md",
        "docs/designs/evidence/P0B_EXECUTION_LEDGER_2026-11-09.md",
    ]

    errors = []
    link_count = 0
    files_inspected = 0
    for path in packet + extras:
        if path not in tree:
            errors.append({"file": path, "type": "missing_packet_file"})
            continue
        content = git(repo, "show", f"{revision}:{path}")
        files_inspected += 1
        fence_count = len(re.findall("^" + chr(96) * 3, content, re.MULTILINE))
        if fence_count % 2 != 0:
            errors.append({"file": path, "type": "unbalanced_markdown_fence"})
        if chr(92) + chr(96) in content:
            errors.append({"file": path, "type": "escaped_markdown_code_span"})
        for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", content):
            target = match.group(1).split("#", 1)[0].split(" ", 1)[0]
            if not target or target.startswith(("https://", "http://", "mailto:", "#")):
                continue
            link_count += 1
            normalized = posixpath.normpath(
                posixpath.join(posixpath.dirname(path), target)
            )
            if normalized in tree:
                continue
            if target.endswith("/") and any(
                p.startswith(normalized.rstrip("/") + "/") for p in tree
            ):
                continue
            errors.append(
                {
                    "file": path,
                    "type": "missing_relative_link_target",
                    "target": target,
                    "resolved": normalized,
                }
            )

    required = [
        "README.md", "PRODUCT.md", "CLAUDE.md", "STATE.md",
        "CONTEXT.md", "ROADMAP.md", "ROLES.md", "AGENTS.md",
        "SOURCE_ADMISSION.csv", "DONOR_VERIFICATION.md",
        "QUALITY_AND_LOCAL_REVIEW.md", "OPUS_HANDOFF.md",
        "specs/_TEMPLATE.md",
    ] + [
        "specs/" + n
        for n in [
            "00-qualify-baseline.md", "01-evidence-to-deck.md",
            "02-smart-layout.md", "03-scoped-ai-edits.md",
            "04-pptx-roundtrip.md", "05-e2e-browser.md",
            "06-release-qualification.md", "07-adaptive-formats.md",
        ]
    ]
    for relative in required:
        if PREFIX + relative not in tree:
            errors.append({"type": "missing_required_file", "file": relative})

    csv_file = PREFIX + "SOURCE_ADMISSION.csv"
    donor_rows = 0
    if csv_file in tree:
        record = git(repo, "show", f"{revision}:{csv_file}")
        reader = csv.DictReader(io.StringIO(record))
        columns = set(reader.fieldnames or [])
        expected = {
            "phase", "donor_repository", "pinned_revision", "source_scope",
            "admission_mode", "gomri_destination",
            "rename_and_architecture_rule", "license_and_provenance_gate",
            "assets_or_model_boundary", "acceptance_or_hold", "owner_role",
        }
        if not expected.issubset(columns):
            errors.append({"type": "donor_csv_columns", "missing": sorted(expected-columns)})
        for line, row in enumerate(reader, 2):
            donor_rows += 1
            if None in row or any(value is None for value in row.values()):
                errors.append({"type": "donor_csv_bad_row", "line": line})
            if not row.get("donor_repository") or not row.get("admission_mode"):
                errors.append({"type": "donor_csv_missing_identity", "line": line})
        if donor_rows < 10:
            errors.append({"type": "donor_csv_incomplete", "found": donor_rows})

    roadmap_file = PREFIX + "ROADMAP.md"
    if roadmap_file in tree:
        roadmap = git(repo, "show", f"{revision}:{roadmap_file}")
        for i in range(8):
            if f"S{i:02d}" not in roadmap:
                errors.append({"type": "roadmap_missing_phase", "phase": i})
        if "S00" not in roadmap or "BLOCKED" not in roadmap:
            errors.append({"type": "roadmap_unstated_safety_gate"})

    roles_file = PREFIX + "ROLES.md"
    if roles_file in tree:
        roles = git(repo, "show", f"{revision}:{roles_file}")
        for i in range(11):
            if f"R{i}" not in roles:
                errors.append({"type": "role_not_declared", "role": f"R{i}"})

    result = {
        "ref": revision,
        "repo_root": root,
        "packet_markdown_files": len(packet),
        "files_inspected": files_inspected,
        "internal_markdown_links_checked": link_count,
        "source_admission_rows": donor_rows,
        "errors": errors,
        "status": "PASS" if not errors else "FAIL",
        "scope": "Documents, links and phase inventory only; not CI, legal clearance or runtime safety",
    }
    output = json.dumps(result, indent=2, ensure_ascii=False)
    print(output)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(output + "\n", encoding="utf-8")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
