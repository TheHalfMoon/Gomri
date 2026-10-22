from typing import Literal


ExportFormat = Literal["pptx", "pdf", "png", "jpeg", "webp"]

DOCUMENT_EXPORT_FORMATS: frozenset[str] = frozenset({"pptx", "pdf"})

IMAGE_EXPORT_FORMATS: frozenset[str] = frozenset({"png", "jpeg", "webp"})

EXPORT_FORMATS: frozenset[str] = DOCUMENT_EXPORT_FORMATS | IMAGE_EXPORT_FORMATS


def is_image_export_format(export_as: str) -> bool:
    """True when the export format produces images rather than a document."""
    return export_as in IMAGE_EXPORT_FORMATS


def is_document_export_format(export_as: str) -> bool:
    """True when the export format produces a single document file."""
    return export_as in DOCUMENT_EXPORT_FORMATS
