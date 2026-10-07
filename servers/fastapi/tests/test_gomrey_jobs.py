"""Deterministic tests for the durable job kernel (P04-G1)."""

import pytest

from gomrey.jobs import (
    DurableJob,
    IdempotencyLedger,
    IllegalTransition,
    backoff_seconds,
    classify_failure,
    should_retry,
    transition,
)


def test_legal_transitions_pass_and_illegal_raise() -> None:
    assert transition("j-1", "queued", "running") == "running"
    with pytest.raises(IllegalTransition):
        transition("j-1", "queued", "complete")
    with pytest.raises(IllegalTransition):
        transition("j-1", "complete", "running")
    with pytest.raises(IllegalTransition):
        transition("j-1", "nope", "running")


def test_terminal_states_have_no_outgoing_transitions() -> None:
    for state in ("complete", "partial", "failed", "cancelled"):
        with pytest.raises(IllegalTransition):
            transition("j-1", state, "running")


def test_failure_classification_and_bounded_retry() -> None:
    assert classify_failure("timeout") == "transient"
    assert classify_failure("worker_crashed") == "transient"
    assert classify_failure("bad_input") == "permanent"
    assert classify_failure("auth_denied") == "permanent"
    assert should_retry("timeout", 1, 3) is True
    assert should_retry("timeout", 3, 3) is False
    assert should_retry("bad_input", 1, 3) is False


def test_backoff_is_deterministic_and_capped() -> None:
    assert backoff_seconds(1) == 1.0
    assert backoff_seconds(2) == 2.0
    assert backoff_seconds(3) == 4.0
    assert backoff_seconds(1) == backoff_seconds(1)
    assert backoff_seconds(100) == 300.0
    with pytest.raises(ValueError):
        backoff_seconds(0)


def test_idempotency_replay_returns_stored_outcome() -> None:
    ledger = IdempotencyLedger()
    assert ledger.claim("k-1") is True
    assert ledger.claim("k-1") is False
    assert ledger.outcome("k-1") == "unknown"
    ledger.record("k-1", "success")
    assert ledger.claim("k-1") is False
    assert ledger.outcome("k-1") == "success"
    assert ledger.outcome("never-claimed") == "unknown"
    with pytest.raises(KeyError):
        ledger.record("never-claimed", "success")
    with pytest.raises(ValueError):
        ledger.record("k-1", "maybe")


def test_job_checkpoint_resume_skips_completed_stages() -> None:
    job = DurableJob(job_id="j-1", stages=["parse", "index", "verify"])
    job.start()
    job.complete_stage("parse")
    token = job.checkpoint_token()
    resumed = DurableJob(job_id="j-1", stages=["parse", "index", "verify"])
    resumed.restore(token)
    assert resumed.pending_stages() == ["index", "verify"]
    resumed.start()
    resumed.complete_stage("index")
    resumed.complete_stage("verify")
    assert resumed.pending_stages() == []
    resumed.finish()
    assert resumed.state == "complete"


def test_job_cancel_and_deadline() -> None:
    job = DurableJob(job_id="j-1", stages=["parse"])
    job.cancel()
    assert job.state == "cancelled"
    with pytest.raises(IllegalTransition):
        job.start()
    assert job.is_expired("2026-10-08T00:00:00Z", "2026-10-07T00:00:00Z") is True
    assert job.is_expired("2026-10-06T00:00:00Z", "2026-10-07T00:00:00Z") is False
    assert job.is_expired("2026-10-08T00:00:00Z", None) is False


def test_checkpoint_rejects_unknown_stages() -> None:
    job = DurableJob(job_id="j-1", stages=["parse"])
    with pytest.raises(ValueError):
        job.restore("parse\x1fhack")
    with pytest.raises(ValueError):
        job.complete_stage("hack")
