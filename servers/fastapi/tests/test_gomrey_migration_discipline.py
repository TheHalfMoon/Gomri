"""Migration-discipline tests for the imported alembic chain (P03-G3).

DB-free: migration files are parsed with ast, never executed. The rules
lock the discipline the product depends on:

- exactly one head (no branches);
- one continuous chain from a single root (every down_revision resolves);
- every file declares revision and down_revision assignments;
- additive-only: no drop_table or drop_column calls inside any upgrade()
  function (downgrade() reversals are standard alembic practice and are
  out of scope for this check).

Destructive storage changes require a new governed migration grain that
updates this policy first. Legacy databases are handled by the stamp path
covered in tests/unit/test_migrations.py.
"""

import ast
from pathlib import Path

VERSIONS_DIR = Path(__file__).resolve().parents[1] / "alembic" / "versions"

FORBIDDEN_CALLS = {"drop_table", "drop_column"}

# Exact grandfathered exceptions in the imported donor chain. Each entry
# names the revision and the reason it predates Gomrey migration discipline.
# New destructive upgrades require a governed migration grain that extends
# this map explicitly; anything else fails.
ADDITIVE_EXCEPTIONS = {
    "026c0ba8b35c": "imported donor consolidation of access_tokens into the unified api_keys table",
    "d0a2b4c6e8f1": "imported donor username-only provider_settings rebuild dropping the email column",
}


def load_revisions():
    revisions = {}
    for path in sorted(VERSIONS_DIR.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        revision = down_revision = None
        found = set()
        for node in ast.walk(tree):
            target_id = None
            value = None
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                target = node.targets[0]
                if isinstance(target, ast.Name):
                    target_id = target.id
                    value = node.value
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                target_id = node.target.id
                value = node.value
            if target_id in {"revision", "down_revision"}:
                found.add(target_id)
                if isinstance(value, ast.Constant):
                    if target_id == "revision":
                        revision = value.value
                    else:
                        down_revision = value.value
        calls = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "upgrade":
                for child in ast.walk(node):
                    if (
                        isinstance(child, ast.Call)
                        and isinstance(child.func, ast.Attribute)
                        and child.func.attr in FORBIDDEN_CALLS
                    ):
                        calls.add(child.func.attr)
        revisions[path.name] = {
            "revision": revision,
            "down_revision": down_revision,
            "declared": found,
            "forbidden": calls,
        }
    return revisions


def test_every_migration_declares_revision_and_parent() -> None:
    revisions = load_revisions()
    assert len(revisions) > 0
    for name, info in revisions.items():
        assert info["declared"] == {"revision", "down_revision"}, name
        assert isinstance(info["revision"], str) and info["revision"], name


def test_chain_has_single_root_and_single_head() -> None:
    revisions = load_revisions()
    by_revision = {info["revision"]: name for name, info in revisions.items()}
    assert len(by_revision) == len(revisions), "duplicate revision ids"
    children: dict[str, list[str]] = {}
    roots = []
    for name, info in revisions.items():
        parent = info["down_revision"]
        if parent is None:
            roots.append(name)
        else:
            assert parent in by_revision, f"{name} has unresolvable parent {parent}"
            children.setdefault(parent, []).append(name)
    assert len(roots) == 1, f"expected one root, found {roots}"
    heads = [name for name in revisions if info_of(revisions, name) not in children]
    assert len(heads) == 1, f"expected one head, found {heads}"


def info_of(revisions, name):
    return revisions[name]["revision"]


def test_chain_is_additive_only() -> None:
    revisions = load_revisions()
    for name, info in revisions.items():
        if info["revision"] in ADDITIVE_EXCEPTIONS:
            continue
        assert not info["forbidden"], f"{name} calls {sorted(info['forbidden'])}"


def test_additive_exceptions_stay_exact() -> None:
    revisions = load_revisions()
    known = {info["revision"] for info in revisions.values()}
    for revision, reason in ADDITIVE_EXCEPTIONS.items():
        assert revision in known, f"stale exception {revision}"
        assert isinstance(reason, str) and reason, revision
