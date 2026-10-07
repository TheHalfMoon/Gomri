"""Deterministic tests for source-unit accounting (P04-G2)."""

import random

import pytest

from gomrey.accounting import (
    DuplicateDeclaration,
    UnitLedger,
    UnknownUnit,
)


def test_duplicate_declaration_fails_loudly() -> None:
    ledger = UnitLedger()
    ledger.declare(["u-1", "u-2"])
    with pytest.raises(DuplicateDeclaration):
        ledger.declare(["u-2", "u-3"])


def test_unknown_unit_and_bad_marks_rejected() -> None:
    ledger = UnitLedger()
    ledger.declare(["u-1"])
    with pytest.raises(UnknownUnit):
        ledger.mark("ghost", "verified")
    with pytest.raises(ValueError):
        ledger.mark("u-1", "verified-ish")
    with pytest.raises(ValueError):
        ledger.mark("u-1", "skipped")
    with pytest.raises(ValueError):
        ledger.mark("u-1", "duplicate")


def test_status_flow_incomplete_partial_complete() -> None:
    ledger = UnitLedger()
    ledger.declare(["u-1", "u-2", "u-3"])
    assert ledger.status() == "incomplete"
    assert ledger.unaccounted() == ["u-1", "u-2", "u-3"]
    ledger.mark("u-1", "verified")
    ledger.mark("u-2", "failed")
    ledger.mark("u-3", "skipped", reason="blank page")
    assert ledger.status() == "partial"
    tally = ledger.counts()
    assert tally["accounted_units"] == 3
    assert tally["silent_drops"] == 0


def test_duplicates_reference_canonical_units() -> None:
    ledger = UnitLedger()
    ledger.declare(["u-1", "u-2"])
    ledger.mark("u-1", "verified")
    ledger.mark("u-2", "duplicate", canonical_id="u-1")
    assert ledger.status() == "complete"


def test_snapshot_restore_round_trip() -> None:
    ledger = UnitLedger()
    ledger.declare(["u-1", "u-2"])
    ledger.mark("u-1", "verified")
    snapshot = ledger.snapshot()
    restored = UnitLedger.restore(snapshot)
    assert restored.counts() == ledger.counts()
    assert restored.unaccounted() == ["u-2"]
    with pytest.raises(ValueError):
        UnitLedger.restore({"declared": ["u-1"], "states": {"ghost": "verified"}})
    with pytest.raises(ValueError):
        UnitLedger.restore({"declared": "nope", "states": {}})


def test_thousand_unit_kill_restart_torture() -> None:
    rng = random.Random(20261007)
    units = [f"unit-{index:04d}" for index in range(1000)]
    ledger = UnitLedger()
    ledger.declare(units)
    order = units[:]
    rng.shuffle(order)
    cursor = 0
    restarts = 0
    while cursor < len(order):
        chunk = order[cursor : cursor + rng.randint(1, 50)]
        for unit_id in chunk:
            roll = rng.random()
            if roll < 0.90:
                ledger.mark(unit_id, "verified")
            elif roll < 0.94:
                ledger.mark(unit_id, "uncertain")
            elif roll < 0.97:
                ledger.mark(unit_id, "failed")
            elif roll < 0.99:
                ledger.mark(unit_id, "skipped", reason="unparseable scan")
            else:
                ledger.mark(unit_id, "duplicate", canonical_id=order[0])
        cursor += len(chunk)
        # Simulate a kill after every chunk: snapshot, rebuild, resume.
        ledger = UnitLedger.restore(ledger.snapshot())
        restarts += 1
    tally = ledger.counts()
    assert tally["accounted_units"] == 1000
    assert tally["silent_drops"] == 0
    assert tally["verified"] > 800
    assert ledger.status() == "partial"
    assert ledger.unaccounted() == []
    assert restarts > 10
