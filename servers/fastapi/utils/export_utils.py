import logging
import os
import uuid
from typing import Literal, Optional
from urllib.parse import urlencode

from fastapi import HTTPException
from pathvalidate import sanitize_filename

from enums.export_format import (
    EXPORT_FORMATS,
    ExportFormat,
    is_image_export_format,
)
from models.image_export_options import ImageExportOptions
from models.presentation_and_path import PresentationAndPath
from services.export_task_service import EXPORT_TASK_SERVICE
from services.image_export_service import (
    ImageExportError,
    build_image_archive,
)
from utils.asset_directory_utils import get_exports_directory
from utils.filename_utils import safe_export_basename
from utils.runtime_limits import log_memory


LOGGER = logging.getLogger(__name__)

# The slide renderer always paints PNG. JPEG and WebP exports reuse that render
# and re-encode it, so PNG is the single rendering path for every image format.
RENDERED_IMAGE_FORMAT: Literal["png"] = "png"


def _get_next_public_url() -> str:
    return (os.getenv("NEXT_PUBLIC_URL") or "").strip() or "http://127.0.0.1"


def _get_next_public_fastapi_url() -> str | None:
    value = (os.getenv("NEXT_PUBLIC_FAST_API") or "").strip()
    return value or None


def _build_presentation_export_url(
    presentation_id: uuid.UUID, cookie_header: str | None = None
) -> tuple[str, str | None]:
    params = {"id": str(presentation_id)}
    fastapi_url = _get_next_public_fastapi_url()
    if fastapi_url:
        params["fastapiUrl"] = fastapi_url
    export_url = f"{_get_next_public_url().rstrip('/')}/pdf-maker?{urlencode(params)}"
    if cookie_header:
        export_url = f"{export_url}#{urlencode({'exportCookie': cookie_header})}"
    return (
        export_url,
        fastapi_url,
    )


def _image_archive_basename(title: str) -> str:
    name = (title or "").strip() or "presentation"
    return safe_export_basename(sanitize_filename(name))


def _remove_intermediate(path: str) -> None:
    try:
        if path and os.path.isfile(path):
            os.remove(path)
    except OSError as exc:
        LOGGER.warning(
            "presentation.export.images.intermediate_cleanup_failed path=%s error=%s",
            path,
            exc,
        )


def _resolve_image_options(
    export_as: ExportFormat,
    image_options: Optional[ImageExportOptions],
) -> ImageExportOptions:
    """Resolve the effective image options for an export request.

    ``export_as`` is the format the caller asked for and it wins. The options
    object is re-validated through the model rather than copied, so a
    combination the model refuses can never reach the encoder.
    """
    options = image_options or ImageExportOptions()
    if options.format == export_as:
        return options
    return ImageExportOptions.model_validate(
        {**options.model_dump(), "format": export_as}
    )


async def _export_presentation_as_images(
    presentation_id: uuid.UUID,
    title: str,
    options: ImageExportOptions,
    cookie_header: str | None,
) -> PresentationAndPath:
    """Render the deck and package the slides as a Gomrey image archive.

    The slide renderer produces a PNG-per-slide ZIP. That rendered archive is an
    intermediate: it is re-encoded into the requested format and replaced by a
    Gomrey-owned archive with deterministic entry names, and the intermediate is
    removed so only one downloadable artifact survives.
    """
    export_url, fastapi_url = _build_presentation_export_url(
        presentation_id, cookie_header
    )
    rendered = await EXPORT_TASK_SERVICE.export_from_url(
        url=export_url,
        title=_image_archive_basename(title),
        export_as=RENDERED_IMAGE_FORMAT,
        fastapi_url=fastapi_url,
        cookie_header=cookie_header,
    )

    rendered_path = rendered.path
    try:
        archive = build_image_archive(
            rendered_path,
            options=options,
            output_directory=get_exports_directory(),
            archive_basename=_image_archive_basename(title),
        )
    except ImageExportError as exc:
        _remove_intermediate(rendered_path)
        raise HTTPException(
            status_code=500,
            detail=f"Image export failed: {exc}",
        ) from exc
    except Exception:
        _remove_intermediate(rendered_path)
        raise

    if os.path.abspath(rendered_path) != os.path.abspath(archive.path):
        _remove_intermediate(rendered_path)

    LOGGER.info(
        "presentation.export.images",
        presentation_id=str(presentation_id),
        image_format=options.format,
        entry_count=archive.entry_count,
        first_entry=archive.entries[0].filename if archive.entries else None,
    )

    return PresentationAndPath(
        presentation_id=presentation_id,
        path=archive.path,
    )


async def export_presentation(
    presentation_id: uuid.UUID,
    title: str,
    export_as: ExportFormat,
    cookie_header: str | None = None,
    image_options: Optional[ImageExportOptions] = None,
) -> PresentationAndPath:
    log_memory(
        LOGGER,
        "presentation.export.start",
        presentation_id=str(presentation_id),
        export_as=export_as,
    )
    if export_as not in EXPORT_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported export format: {export_as}",
        )

    if is_image_export_format(export_as):
        try:
            options = _resolve_image_options(export_as, image_options)
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image export options: {exc}",
            ) from exc
        result = await _export_presentation_as_images(
            presentation_id,
            title,
            options,
            cookie_header,
        )
        log_memory(
            LOGGER,
            "presentation.export.finish",
            presentation_id=str(presentation_id),
            export_as=export_as,
        )
        return result

    export_url, fastapi_url = _build_presentation_export_url(
        presentation_id, cookie_header
    )
    name = (title or "").strip() or str(uuid.uuid4())
    export_result = await EXPORT_TASK_SERVICE.export_from_url(
        url=export_url,
        title=safe_export_basename(sanitize_filename(name)),
        export_as=export_as,
        fastapi_url=fastapi_url,
        cookie_header=cookie_header,
    )
    log_memory(
        LOGGER,
        "presentation.export.finish",
        presentation_id=str(presentation_id),
        export_as=export_as,
    )
    return PresentationAndPath(
        presentation_id=presentation_id,
        path=export_result.path,
    )
