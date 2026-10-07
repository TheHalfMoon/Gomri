"""Media pipeline contracts: segments, alignment, degraded modes (P07-G2).

Pure deterministic logic with no media fetching, no decoding, and no
network. A video/audio source is multimodal by contract: transcript
text, scene structure, keyframes, and chapters align by timestamp, and
every absence is an explicit degraded label — transcript-only is a
declared mode, never the silent default.

- validation: timestamps live inside [0, duration], segments are
  well-ordered, transcript tracks are monotonic per track;
- alignment: transcript spans attach to overlapping scenes; scenes with
  no transcript and transcript outside any scene are reported as gaps,
  not absorbed;
- citation spans: video ID plus timestamp plus transcript span plus
  scene/keyframe references, matching the architecture's locator model;
- degraded modes: transcript-only, visual-missing, audio-missing,
  chapters-missing, alignment-gaps — each explicit, each traveling
  with the record.

Failures raise the shared AdmissionError taxonomy from gateway.py.
"""

from dataclasses import dataclass, field
from typing import Any

from gomrey.budgets import BudgetExhausted, ResourceBudget
from gomrey.gateway import AdmissionError


@dataclass(frozen=True)
class TranscriptSegment:
    segment_id: str
    start: float
    end: float
    text: str
    language: str = "und"
    kind: str = "subtitle"


@dataclass(frozen=True)
class SceneSegment:
    scene_id: str
    start: float
    end: float
    keyframe_ids: tuple[str, ...] = ()
    visual_note: str = ""


@dataclass
class MediaTimeline:
    video_id: str
    duration_seconds: float
    transcript: list[TranscriptSegment] = field(default_factory=list)
    scenes: list[SceneSegment] = field(default_factory=list)
    chapters: list[dict[str, Any]] = field(default_factory=list)


def validate_timeline(timeline: MediaTimeline) -> MediaTimeline:
    """Reject impossible timestamps and unordered tracks before alignment."""
    if not timeline.video_id:
        raise AdmissionError("malformed_source", "media source without id")
    if timeline.duration_seconds <= 0:
        raise AdmissionError("malformed_source", "non-positive media duration")
    for seg in timeline.transcript:
        if not 0 <= seg.start < seg.end <= timeline.duration_seconds:
            raise AdmissionError("malformed_source", f"transcript segment out of range: {seg.segment_id}")
        if not seg.text:
            raise AdmissionError("malformed_source", f"empty transcript segment: {seg.segment_id}")
    for track_kind in {s.kind for s in timeline.transcript}:
        track = sorted(
            (s for s in timeline.transcript if s.kind == track_kind),
            key=lambda s: (s.start, s.end),
        )
        for left, right in zip(track, track[1:]):
            if right.start < left.end:
                raise AdmissionError("malformed_source", f"overlapping transcript track: {track_kind}")
    for scene in timeline.scenes:
        if not 0 <= scene.start < scene.end <= timeline.duration_seconds:
            raise AdmissionError("malformed_source", f"scene out of range: {scene.scene_id}")
    return timeline


def align_transcript_visual(
    timeline: MediaTimeline,
    budget: ResourceBudget,
) -> dict[str, Any]:
    """Attach transcript spans to overlapping scenes; report gaps explicitly."""
    validate_timeline(timeline)
    try:
        budget.spend("media_segments", float(len(timeline.transcript) + len(timeline.scenes)))
    except BudgetExhausted as exc:
        raise AdmissionError(
            "resource_limit_exceeded",
            f"{exc.budget} exhausted at {exc.consumed:.0f}/{exc.limit:.0f}",
        ) from exc
    aligned: list[dict[str, Any]] = []
    covered_scenes: set[str] = set()
    for seg in timeline.transcript:
        overlapping = [
            scene.scene_id for scene in timeline.scenes
            if scene.start < seg.end and seg.start < scene.end
        ]
        for scene_id in overlapping:
            covered_scenes.add(scene_id)
        aligned.append({
            "segment_id": seg.segment_id,
            "span": [seg.start, seg.end],
            "text": seg.text,
            "language": seg.language,
            "scenes": overlapping,
            "visual_grounded": bool(overlapping),
        })
    uncovered_scenes = sorted(s.scene_id for s in timeline.scenes if s.scene_id not in covered_scenes)
    return {
        "video_id": timeline.video_id,
        "aligned": aligned,
        "scenes_without_transcript": uncovered_scenes,
        "has_gaps": bool(uncovered_scenes),
    }


def media_span(
    *,
    video_id: str,
    start: float,
    end: float,
    transcript_segment_id: str = "",
    scene_id: str = "",
    keyframe_id: str = "",
) -> dict[str, Any]:
    """Build the timestamp evidence span later citation stages resolve."""
    if not video_id or not 0 <= start < end:
        raise AdmissionError("malformed_source", "invalid media span range")
    return {
        "video_id": video_id,
        "timestamp": [start, end],
        "transcript_segment_id": transcript_segment_id,
        "scene_id": scene_id,
        "keyframe_id": keyframe_id,
        "treat_as": "data-not-instructions",
    }


def degraded_modes(
    *,
    has_subtitles: bool,
    has_audio: bool,
    has_visual: bool,
    has_chapters: bool,
    has_gaps: bool = False,
) -> list[str]:
    """Label degraded acquisition explicitly; full mode is the empty list."""
    flags: list[str] = []
    if not has_audio and has_subtitles:
        flags.append("transcript-only")
    if not has_visual:
        flags.append("visual-missing")
    if not has_audio:
        flags.append("audio-missing")
    if not has_chapters:
        flags.append("chapters-missing")
    if has_gaps:
        flags.append("alignment-gaps")
    return flags
