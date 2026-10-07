"""Tests for the P07-G2 media pipeline contracts (no media I/O)."""

import pytest

from gomrey.budgets import ResourceBudget
from gomrey.gateway import AdmissionError
from gomrey.media_pipeline import (
    MediaTimeline,
    SceneSegment,
    TranscriptSegment,
    align_transcript_visual,
    degraded_modes,
    media_span,
    validate_timeline,
)


def _timeline(**overrides) -> MediaTimeline:
    base = {
        "video_id": "vid-1",
        "duration_seconds": 600.0,
        "transcript": [
            TranscriptSegment("t1", 10.0, 20.0, "Hello world"),
            TranscriptSegment("t2", 30.0, 40.0, "Second line"),
        ],
        "scenes": [
            SceneSegment("s1", 0.0, 25.0, keyframe_ids=("k1",)),
            SceneSegment("s2", 25.0, 60.0, keyframe_ids=("k2",)),
        ],
        "chapters": [{"title": "Intro", "start": 0.0}],
    }
    base.update(overrides)
    return MediaTimeline(**base)


def _budget() -> ResourceBudget:
    return ResourceBudget(limits={"media_segments": 100.0})


def test_alignment_grounds_transcript_and_reports_gaps() -> None:
    result = align_transcript_visual(_timeline(), _budget())
    assert result["video_id"] == "vid-1"
    assert result["aligned"][0]["scenes"] == ["s1"]
    assert result["aligned"][0]["visual_grounded"] is True
    assert result["has_gaps"] is False
    gappy = _timeline(scenes=[SceneSegment("s9", 500.0, 550.0, keyframe_ids=("k9",))])
    gapped = align_transcript_visual(gappy, _budget())
    assert gapped["scenes_without_transcript"] == ["s9"]
    assert gapped["has_gaps"] is True
    assert gapped["aligned"][0]["visual_grounded"] is False


def test_impossible_timestamps_refused() -> None:
    with pytest.raises(AdmissionError):
        validate_timeline(_timeline(duration_seconds=0))
    with pytest.raises(AdmissionError):
        validate_timeline(_timeline(transcript=[
            TranscriptSegment("t1", 50.0, 20.0, "backwards")]))
    with pytest.raises(AdmissionError):
        validate_timeline(_timeline(transcript=[
            TranscriptSegment("t1", 10.0, 30.0, "a"),
            TranscriptSegment("t2", 20.0, 40.0, "overlap")]))
    with pytest.raises(AdmissionError):
        validate_timeline(_timeline(scenes=[SceneSegment("s", 0.0, 9999.0)]))
    with pytest.raises(AdmissionError):
        align_transcript_visual(_timeline(), ResourceBudget(limits={"media_segments": 1.0}))


def test_span_shape_and_degraded_matrix() -> None:
    span = media_span(video_id="vid-1", start=10.0, end=20.0,
                     transcript_segment_id="t1", scene_id="s1", keyframe_id="k1")
    assert span["timestamp"] == [10.0, 20.0]
    assert span["treat_as"] == "data-not-instructions"
    with pytest.raises(AdmissionError):
        media_span(video_id="vid-1", start=20.0, end=10.0)
    assert degraded_modes(has_subtitles=True, has_audio=True,
                          has_visual=True, has_chapters=True) == []
    assert degraded_modes(has_subtitles=True, has_audio=False,
                          has_visual=False, has_chapters=False) == [
        "transcript-only", "visual-missing", "audio-missing", "chapters-missing"]
    assert degraded_modes(has_subtitles=True, has_audio=True,
                          has_visual=True, has_chapters=True,
                          has_gaps=True) == ["alignment-gaps"]
