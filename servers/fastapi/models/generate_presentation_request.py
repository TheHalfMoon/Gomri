from typing import List, Literal, Optional
from pydantic import BaseModel, Field

from enums.tone import Tone
from enums.verbosity import Verbosity


class EvidenceBundleInput(BaseModel):
    """The evidence a caller supplies to ground a deck in its sources."""

    bundle_id: str = Field(..., description="Stable identity of the bundle")
    query: str = Field(..., description="The question the evidence answers")
    source_revisions: List[dict] = Field(
        default_factory=list,
        description="The exact source revisions the spans came from",
    )
    spans: List[dict] = Field(
        default_factory=list,
        description="The evidence spans, each with a citation_id, text and locator",
    )
    retrieval_identities: List[str] = Field(
        default_factory=list, description="Identities of the retrievers used"
    )
    contradictions: Optional[List[dict]] = Field(
        default=None, description="Known contradictions between spans"
    )
    omissions: Optional[List[dict]] = Field(
        default=None, description="Sources deliberately left out, with reasons"
    )
    dropped_without_reason: int = Field(
        default=0,
        description="Candidates dropped without a reason. Must be zero.",
    )


class GeneratePresentationRequest(BaseModel):
    content: str = Field(..., description="The content for generating the presentation")
    slides_markdown: Optional[List[str]] = Field(
        default=None, description="The markdown for the slides"
    )
    instructions: Optional[str] = Field(
        default=None, description="The instruction for generating the presentation"
    )
    tone: Tone = Field(default=Tone.DEFAULT, description="The tone to use for the text")
    verbosity: Verbosity = Field(
        default=Verbosity.STANDARD, description="How verbose the presentation should be"
    )
    web_search: bool = Field(default=False, description="Whether to enable web search")
    n_slides: Optional[int] = Field(
        default=None,
        description="Number of slides to generate. If omitted, model auto-detects slide count.",
    )
    language: Optional[str] = Field(
        default=None,
        description="Language for the presentation. If omitted, model auto-detects language.",
    )
    template: str = Field(
        default="general", description="Template to use for the presentation"
    )
    include_table_of_contents: bool = Field(
        default=False, description="Whether to include a table of contents"
    )
    include_title_slide: bool = Field(
        default=True, description="Whether to include a title slide"
    )
    files: Optional[List[str]] = Field(
        default=None, description="Files to use for the presentation"
    )
    export_as: Literal["pptx", "pdf"] = Field(
        default="pptx", description="Export format"
    )
    trigger_webhook: bool = Field(
        default=False, description="Whether to trigger subscribed webhooks"
    )
    evidence_bundle: Optional[EvidenceBundleInput] = Field(
        default=None,
        description=(
            "Optional evidence to ground the deck in. When present, every slide "
            "is bound to resolvable citation locators and unresolved or "
            "contradictory claims are surfaced explicitly."
        ),
    )
    source_ir: Optional[dict] = Field(
        default=None,
        description=(
            "The assembled source IR the evidence locators resolve against. "
            "Required whenever evidence_bundle is supplied."
        ),
    )


class GenerateSmartPresentationRequest(BaseModel):
    content: str = Field(default="", description="Prompt for the presentation")
    n_slides: Optional[int] = Field(default=None, ge=1)
    language: Optional[str] = None
    instructions: Optional[str] = None
    tone: Tone = Tone.DEFAULT
    verbosity: Verbosity = Verbosity.STANDARD
    web_search: bool = False
    include_table_of_contents: bool = False
    include_title_slide: bool = True
    files: Optional[List[str]] = Field(
        default=None,
        description="Previously uploaded Presenton file paths",
    )
    community_design_ids: Optional[List[int]] = None
    export_as: Literal["pptx", "pdf"] = "pptx"
