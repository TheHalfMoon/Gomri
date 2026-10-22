from typing import Literal


ExportFormat = Literal["pptx", "pdf", "png", "jpeg", "webp"]

IMAGE_EXPORT_FORMATS: frozenset[str] = frozenset({"png", "jpeg", "webp"})

EXPORT_FORMATS: frozenset[str] = frozenset({"pptx", "pdf", "png", "jpeg", "webp"})

DOCUMENT_EXPORT_FORMATS: frozenset[str] = EXPORT_FORMATS - IMAGE_EXPORT_FORMATS


def is_image_export_format(export_as: str) -> bool:
    """True when the export format produces images rather than a document."""
    return export_as in IMAGE_EXPORT_FORMATS
