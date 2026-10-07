"""Durable job kernel: state machine, idempotency, checkpoints, retries.

Pure deterministic logic with no database and no network. Persistence
arrives in later grains behind the CanonicalStore seam; this module
defines the rules that any backend must enforce:

- closed state machine with explicit legal transitions;
- idempotency keys memoize results: replays return the stored outcome
  instead of re-executing non-idempotent effects;
- checkpoints are opaque tokens capturing completed stages, so a job can
  resume without restarting from zero;
- failures classify as transient (bounded retry with deterministic
  backoff) or permanent (no retry);
- cancellation and deadlines are explicit states, not silent stops.
"""

from dataclasses import dataclass, field

TERMINAL_STATES = frozenset({"complete", "partial", "failed", "cancelled"})

LEGAL_TRANSITIONS: dict[str, frozenset[str]] = {
    "queued": frozenset({"running", "cancelled"}),
    "running": frozenset({"checkpointed", "complete", "partial", "failed", "cancelled"}),
    "checkpointed": frozenset({"running", "failed", "cancelled"}),
    "suspended": frozenset({"running", "cancelled"}),
    "complete": frozenset(),
    "partial": frozenset(),
    "failed": frozenset(),
    "cancelled": frozenset(),
}

TRANSIENT_ERRORS = frozenset({
    "timeout",
    "rate_limited",
    "worker_crashed",
    "connection_reset",
    "service_unavailable",
})


@dataclass
class IllegalTransition(Exception):
    job_id: str
    from_state: str
    to_state: str


def transition(job_id: str, from_state: str, to_state: str) -> str:
    """Return to_state when legal, else raise IllegalTransition."""
    allowed = LEGAL_TRANSITIONS.get(from_state)
    if allowed is None:
        raise IllegalTransition(job_id, from_state, to_state)
    if to_state not in allowed:
        raise IllegalTransition(job_id, from_state, to_state)
    return to_state


def classify_failure(error_code: str) -> str:
    """Classify a failure as transient (retryable) or permanent."""
    return "transient" if error_code in TRANSIENT_ERRORS else "permanent"


def backoff_seconds(attempt: int, base: float = 1.0, cap: float = 300.0, factor: float = 2.0) -> float:
    """Deterministic exponential backoff without jitter (testability first)."""
    if attempt < 1:
        raise ValueError("attempt starts at 1")
    return min(cap, base * (factor ** (attempt - 1)))


def should_retry(error_code: str, attempt: int, max_attempts: int) -> bool:
    """Retry only transient failures within the bounded attempt budget."""
    return classify_failure(error_code) == "transient" and attempt < max_attempts


@dataclass
class IdempotencyLedger:
    """Memoize mutation outcomes by idempotency key.

    The first claim wins; replays observe the stored outcome. Unknown
    outcomes stay unknown until reconciled by a later grain — they are
    never silently upgraded to success.
    """

    _outcomes: dict[str, str] = field(default_factory=dict)

    def claim(self, key: str) -> bool:
        """Return True when this call owns the key, False on replay."""
        if key in self._outcomes:
            return False
        self._outcomes[key] = "unknown"
        return True

    def record(self, key: str, outcome: str) -> None:
        if key not in self._outcomes:
            raise KeyError(f"idempotency key was never claimed: {key}")
        if outcome not in {"success", "failed", "unknown"}:
            raise ValueError(f"invalid outcome: {outcome}")
        self._outcomes[key] = outcome

    def outcome(self, key: str) -> str:
        return self._outcomes.get(key, "unknown")


@dataclass
class DurableJob:
    """In-memory durable job with stage checkpoints."""

    job_id: str
    stages: list[str]
    completed: list[str] = field(default_factory=list)
    state: str = "queued"
    attempts: int = 0

    def start(self) -> None:
        self.state = transition(self.job_id, self.state, "running")

    def complete_stage(self, stage: str) -> None:
        if self.state not in {"running", "checkpointed"}:
            raise IllegalTransition(self.job_id, self.state, "checkpointed")
        if stage not in self.stages:
            raise ValueError(f"unknown stage: {stage}")
        if stage not in self.completed:
            self.completed.append(stage)
        self.state = "checkpointed"

    def checkpoint_token(self) -> str:
        """Opaque resume token: ordered completed stages joined by unit separator."""
        return "\x1f".join(self.completed)

    def restore(self, token: str) -> None:
        """Resume from a checkpoint token without redoing completed stages."""
        wanted = [stage for stage in token.split("\x1f") if stage] if token else []
        unknown = [stage for stage in wanted if stage not in self.stages]
        if unknown:
            raise ValueError(f"checkpoint references unknown stages: {unknown}")
        self.completed = list(wanted)
        if self.state == "checkpointed":
            self.state = transition(self.job_id, self.state, "running")

    def pending_stages(self) -> list[str]:
        return [stage for stage in self.stages if stage not in self.completed]

    def finish(self, complete: bool = True) -> None:
        self.state = transition(self.job_id, self.state, "complete" if complete else "partial")

    def fail(self) -> None:
        self.state = transition(self.job_id, self.state, "failed")

    def cancel(self) -> None:
        self.state = transition(self.job_id, self.state, "cancelled")

    def is_expired(self, now_iso: str, deadline_iso: str | None) -> bool:
        """Deadline comparison on ISO-8601 strings (lexicographic = chronological)."""
        if deadline_iso is None:
            return False
        return now_iso > deadline_iso
