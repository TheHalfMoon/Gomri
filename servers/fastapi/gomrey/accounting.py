"""Source-unit accounting: the no-silent-loss ledger (P04-G2).

Every declared unit must end in an explicit terminal state — verified,
uncertain, failed, skipped (with reason), or duplicate (of a canonical
unit). Anything else is a silent drop, and silent drops fail loudly.

The ledger is pure deterministic logic with snapshot/restore so a
killed worker resumes without losing completed marks or double-counting.
Persistence behind CanonicalStore arrives in a later grain; the rules
here are what any backend must enforce.
"""

from dataclasses import dataclass, field

TERMINAL_STATES = frozenset({"verified", "uncertain", "failed", "skipped", "duplicate"})


@dataclass
class UnknownUnit(Exception):
    unit_id: str


@dataclass
class DuplicateDeclaration(Exception):
    unit_id: str


@dataclass
class UnitLedger:
    """Account for every declared source unit exactly once."""

    declared: list[str] = field(default_factory=list)
    _states: dict[str, str] = field(default_factory=dict)
    _skip_reasons: dict[str, str] = field(default_factory=dict)
    _duplicate_of: dict[str, str] = field(default_factory=dict)

    def declare(self, unit_ids: list[str]) -> None:
        seen = set(self.declared)
        for unit_id in unit_ids:
            if unit_id in seen:
                raise DuplicateDeclaration(unit_id)
            seen.add(unit_id)
            self.declared.append(unit_id)
            self._states.setdefault(unit_id, "declared")

    def mark(self, unit_id: str, state: str, reason: str = "", canonical_id: str = "") -> None:
        if unit_id not in self._states:
            raise UnknownUnit(unit_id)
        if state not in TERMINAL_STATES:
            raise ValueError(f"not a terminal state: {state}")
        if state == "skipped" and not reason:
            raise ValueError("skipped units require a reason")
        if state == "duplicate" and not canonical_id:
            raise ValueError("duplicate units require a canonical unit id")
        self._states[unit_id] = state
        if reason:
            self._skip_reasons[unit_id] = reason
        if canonical_id:
            self._duplicate_of[unit_id] = canonical_id

    def counts(self) -> dict[str, int]:
        tally: dict[str, int] = {state: 0 for state in TERMINAL_STATES}
        tally["declared_total"] = len(self.declared)
        for unit_id in self.declared:
            state = self._states[unit_id]
            if state in tally:
                tally[state] += 1
        accounted = sum(tally[state] for state in TERMINAL_STATES)
        tally["accounted_units"] = accounted
        tally["silent_drops"] = len(self.declared) - accounted
        return tally

    def status(self) -> str:
        tally = self.counts()
        if tally["silent_drops"] > 0:
            return "incomplete"
        if tally["failed"] > 0 or tally["uncertain"] > 0:
            return "partial"
        return "complete"

    def unaccounted(self) -> list[str]:
        return [unit_id for unit_id in self.declared if self._states[unit_id] not in TERMINAL_STATES]

    def snapshot(self) -> dict[str, object]:
        """Opaque resume snapshot: declared order plus terminal marks."""
        return {
            "declared": list(self.declared),
            "states": dict(self._states),
            "skip_reasons": dict(self._skip_reasons),
            "duplicate_of": dict(self._duplicate_of),
        }

    @classmethod
    def restore(cls, snapshot: dict[str, object]) -> "UnitLedger":
        ledger = cls()
        declared = snapshot.get("declared", [])
        states = snapshot.get("states", {})
        if not isinstance(declared, list) or not isinstance(states, dict):
            raise ValueError("invalid ledger snapshot")
        ledger.declared = list(declared)
        ledger._states = {str(unit): str(state) for unit, state in states.items()}
        unknown = [unit for unit in ledger._states if unit not in set(ledger.declared)]
        if unknown:
            raise ValueError(f"snapshot marks undeclared units: {unknown[:3]}")
        skip_reasons = snapshot.get("skip_reasons", {})
        duplicate_of = snapshot.get("duplicate_of", {})
        ledger._skip_reasons = dict(skip_reasons) if isinstance(skip_reasons, dict) else {}
        ledger._duplicate_of = dict(duplicate_of) if isinstance(duplicate_of, dict) else {}
        return ledger
