from typing import List, Optional
from pydantic import BaseModel
import uuid

from enums.export_format import ExportFormat
from models.image_export_options import ImageExportOptions


class SlideContentUpdate(BaseModel):
    index: int
    content: dict


class EditPresentationRequest(BaseModel):
    presentation_id: uuid.UUID
    slides: List[SlideContentUpdate]
    export_as: ExportFormat = "pptx"
    image_export: Optional[ImageExportOptions] = None
