"""Budgets, progress events, and ambiguous-outcome reconciliation (P04-G3).

Pure deterministic logic with no database and no network:

- ResourceBudget: named caps (time, tokens, pages, network calls, output
  bytes) where exhaustion yields an explicit partial/blocked state rather
  than silent truncation.
- progress_event(): structured task metrics matching the MCP Tasks/Job
  Engine progress shape from AGENT_PLATFORM.md.
- reconcile(): unknown idempotency outcomes resolve only through an
  explicit idempotent re-check callback whose result is recorded; an
  unknown outcome is never upgraded to success by assumption.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Literal


@dataclass
class BudgetExhausted(Exception):
    budget: str
    limit: float
    consumed: float


@dataclass
class ResourceBudget:
    """Named consumption caps with explicit exhaustion."""

    limits: dict[str, float] = field(default_factory=dict)
    consumed: dict[str, float] = field(default_factory=dict)

    def spend(self, resource: str, amount: float) -> None:
        if amount < 0:
            raise ValueError("spend amount must be non-negative")
        limit = self.limits.get(resource)
        used = self.consumed.get(resource, 0.0) + amount
        if limit is not None and used > limit:
            raise BudgetExhausted(resource, limit, used)
        self.consumed[resource] = used

    def remaining(self, resource: str) -> float | None:
        limit = self.limits.get(resource)
        if limit is None:
            return None
        return max(0.0, limit - self.consumed.get(resource, 0.0))

    def exhausted(self) -> list[str]:
        return [
            resource
            for resource, limit in self.limits.items()
            if self.consumed.get(resource, 0.0) >= limit
        ]


def progress_event(
    *,
    job_id: str,
    stage: str,
    total: int,
    accounted: int,
    verified: int = 0,
    uncertain: int = 0,
    failed: int = 0,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    """Structured task progress; estimates are never correctness claims."""
    if total < 0 or accounted < 0 or accounted > total:
        raise ValueError("accounted must be within [0, total]")
    percent = 100.0 * accounted / total if total else 100.0
    return {
        "job_id": job_id,
        "current_stage": stage,
        "source_units_total": total,
        "source_units_accounted": accounted,
        "verified": verified,
        "uncertain": uncertain,
        "failed": failed,
        "percent": round(percent, 2),
        "warnings": list(warnings or []),
    }


ReconcileResult = Literal["success", "failed", "still_unknown"]


def reconcile(
    ledger: Any,
    key: str,
    recheck: Callable[[], ReconcileResult],
) -> str:
    """Resolve an unknown outcome only through an explicit re-check.

    The ledger must expose outcome(key) and record(key, outcome).
    A re-check returning still_unknown keeps the outcome unknown;
    success/failure is recorded from observed evidence, never assumed.
    """
    current = ledger.outcome(key)
    if current in {"success", "failed"}:
        return current
    observed = recheck()
    if observed == "still_unknown":
        return "unknown"
    ledger.record(key, observed)
    return observed
