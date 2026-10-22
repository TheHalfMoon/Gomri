"""Gomrey image export.

The slide renderer (the vendored ``@presenton/export-core`` runtime) owns
*rendering*: it paints every slide in a browser and packs one PNG per slide into
a ZIP archive. This module owns the *image* half of the Gomrey export contract:

* it decides the archive layout (deterministic file names, slide order),
* it converts between image formats when the caller asks for something other
  than PNG,
* it enforces the export budget, and
* it refuses malformed, hostile, or over-budget input instead of writing a
  half-formed artifact.

The module is deliberately free of FastAPI and database dependencies: it takes
paths and plain options and returns a typed result, so it can be exercised
without a running application.
"""

import io
import os
import re
import uuid
import zipfile
from dataclasses import dataclass
from typing import Optional

from PIL import Image, UnidentifiedImageError

from enums.export_format import IMAGE_EXPORT_FORMATS
from models.image_export_options import (
    ImageExportOptions,
    MAX_IMAGE_WIDTH,
    MIN_IMAGE_WIDTH,
)


ARCHIVE_MEDIA_TYPE = "application/zip"

IMAGE_MEDIA_TYPES: dict[str, str] = {
    "png": "image/png",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
}

IMAGE_FILE_EXTENSIONS: dict[str, str] = {
    "png": ".png",
    "jpeg": ".jpg",
    "webp": ".webp",
}

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

MAX_ARCHIVE_ENTRIES = 200
MAX_IMAGE_BYTES = 64 * 1024 * 1024
MAX_ARCHIVE_BYTES = 512 * 1024 * 1024
MAX_IMAGE_PIXELS = 64_000_000

# The renderer names its slides `slide_001.png`, `slide_002.png`, … and the
# Gomrey archive keeps that convention so the renderer's own output and the
# Gomrey archive describe the same slides with the same names.
_SLIDE_INDEX_PATTERN = re.compile(r"^slide[_-]?(\d+)$", re.IGNORECASE)
_SLIDE_NAME_DIGITS = 3
_SAFE_FILENAME = re.compile(r"^[A-Za-z0-9._-]+$")


class ImageExportError(Exception):
    """Base error for Gomrey image export failures."""


class ImageExportValidationError(ImageExportError):
    """The rendered archive violated the Gomrey image export contract."""


class ImageExportBudgetError(ImageExportError):
    """The rendered archive exceeded a Gomrey image export budget."""


@dataclass(frozen=True)
class ImageArchiveEntry:
    """One exported slide image."""

    filename: str
    media_type: str
    width: int
    height: int
    size_bytes: int


@dataclass(frozen=True)
class ImageArchive:
    """The packaged result of a Gomrey image export."""

    path: str
    media_type: str
    image_format: str
    entry_count: int
    entries: tuple[ImageArchiveEntry, ...]


def _slide_sort_key(name: str) -> tuple[int, int, str]:
    """Order archive entries by slide index.

    Slides are the files the renderer named ``slide_<index>``. They come first,
    in numeric order, which is the render order. Anything else is appended
    afterwards in lexical order so the result stays deterministic.
    """
    stem = os.path.splitext(name)[0]
    match = _SLIDE_INDEX_PATTERN.match(stem)
    if match:
        return (0, int(match.group(1)), stem)
    return (1, 0, stem)


def _validate_entry_name(name: str) -> str:
    """Reject archive entries that could escape the extraction directory."""
    if not name or name != name.strip():
        raise ImageExportValidationError("Rendered archive contains an invalid entry name")
    if name.startswith("/") or name.startswith("\\"):
        raise ImageExportValidationError(
            "Rendered archive contains an absolute entry name"
        )
    if ":" in name:
        raise ImageExportValidationError(
            "Rendered archive contains an entry name with a drive prefix"
        )
    normalized = name.replace("\\", "/")
    if "/" in normalized:
        raise ImageExportValidationError(
            "Rendered archive contains a nested entry name"
        )
    if any(segment == ".." for segment in normalized.split("/")):
        raise ImageExportValidationError(
            "Rendered archive contains an entry name that escapes the archive"
        )
    if not _SAFE_FILENAME.match(os.path.basename(normalized)):
        raise ImageExportValidationError(
            "Rendered archive contains an entry name with unsupported characters"
        )
    return normalized


def _read_bounded(archive: zipfile.ZipFile, info: zipfile.ZipInfo) -> bytes:
    """Read one archive member, refusing anything over the per-image budget."""
    if info.file_size > MAX_IMAGE_BYTES:
        raise ImageExportBudgetError(
            f"Rendered slide exceeds the {MAX_IMAGE_BYTES} byte image budget"
        )
    with archive.open(info, "r") as handle:
        payload = handle.read(MAX_IMAGE_BYTES + 1)
    if len(payload) > MAX_IMAGE_BYTES:
        raise ImageExportBudgetError(
            f"Rendered slide exceeds the {MAX_IMAGE_BYTES} byte image budget"
        )
    return payload


def _open_image(payload: bytes) -> Image.Image:
    """Decode a rendered slide, refusing anything that is not a complete image."""
    if not payload.startswith(PNG_SIGNATURE):
        raise ImageExportValidationError(
            "Rendered archive contains an entry that is not a PNG slide"
        )
    try:
        image = Image.open(io.BytesIO(payload))
        width, height = image.size
        if width <= 0 or height <= 0:
            raise ImageExportValidationError(
                "Rendered archive contains a PNG slide with no pixels"
            )
        if width * height > MAX_IMAGE_PIXELS:
            raise ImageExportBudgetError(
                f"Rendered slide exceeds the {MAX_IMAGE_PIXELS} pixel budget"
            )
        # Pillow decodes lazily. Force the decode so a truncated or corrupt
        # slide is refused here instead of being written into the archive.
        image.load()
    except ImageExportBudgetError:
        raise
    except ImageExportValidationError:
        raise
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ImageExportValidationError(
            "Rendered archive contains an unreadable PNG slide"
        ) from exc
    return image


def _has_alpha(image: Image.Image) -> bool:
    """True when the image carries transparency."""
    return image.mode in ("RGBA", "LA") or (
        image.mode == "P" and "transparency" in image.info
    )


def _resize(image: Image.Image, target_width: Optional[int]) -> Image.Image:
    if target_width is None or target_width == image.width:
        return image
    if target_width < MIN_IMAGE_WIDTH or target_width > MAX_IMAGE_WIDTH:
        raise ImageExportValidationError(
            f"Target width must be between {MIN_IMAGE_WIDTH} and {MAX_IMAGE_WIDTH} pixels"
        )
    target_height = max(1, round(image.height * target_width / image.width))
    return image.resize((target_width, target_height), Image.Resampling.LANCZOS)


def _flatten(image: Image.Image, background: tuple[int, int, int]) -> Image.Image:
    """Composite an image onto an opaque background, dropping the alpha channel."""
    if not _has_alpha(image):
        return image.convert("RGB")
    canvas = Image.new("RGB", image.size, background)
    rgba = image.convert("RGBA")
    canvas.paste(rgba, mask=rgba.getchannel("A"))
    return canvas


def _encode(
    image: Image.Image,
    image_format: str,
    options: ImageExportOptions,
) -> bytes:
    buffer = io.BytesIO()
    if image_format == "png":
        image.save(buffer, format="PNG", optimize=True)
    elif image_format == "jpeg":
        _flatten(image, options.resolved_background_rgb()).save(
            buffer,
            format="JPEG",
            quality=options.quality if options.quality is not None else 90,
            subsampling=0,
        )
    elif image_format == "webp":
        if _has_alpha(image):
            image = image.convert("RGBA")
        elif image.mode != "RGB":
            image = image.convert("RGB")
        image.save(
            buffer,
            format="WEBP",
            quality=options.quality if options.quality is not None else 90,
        )
    else:
        raise ImageExportValidationError(
            f"Unsupported image export format: {image_format}"
        )
    return buffer.getvalue()


def _slide_filename(index: int, total: int, extension: str) -> str:
    digits = max(_SLIDE_NAME_DIGITS, len(str(total)))
    return f"slide_{index:0{digits}d}{extension}"


def _archive_path(
    output_directory: str,
    archive_basename: str,
    image_format: str,
) -> str:
    """A unique archive path.

    The title alone is not unique: two presentations can share a title, and two
    exports of one presentation can run at the same time. The unique suffix
    keeps every export a separate artifact.
    """
    return os.path.join(
        output_directory,
        f"{archive_basename}_{image_format}_{uuid.uuid4().hex[:8]}.zip",
    )


def build_image_archive(
    rendered_archive_path: str,
    options: ImageExportOptions,
    output_directory: str,
    archive_basename: str,
) -> ImageArchive:
    """Convert a rendered PNG slide archive into a Gomrey image export.

    ``rendered_archive_path`` is the ZIP produced by the slide renderer. The
    result is a new archive in ``output_directory`` whose entries are ordered by
    slide index, named deterministically, and encoded in the requested format.
    """
    if options.format not in IMAGE_EXPORT_FORMATS:
        raise ImageExportValidationError(
            f"Unsupported image export format: {options.format}"
        )
    if not os.path.isfile(rendered_archive_path):
        raise ImageExportValidationError(
            "Rendered slide archive was not produced by the export runtime"
        )

    os.makedirs(output_directory, exist_ok=True)
    final_path = _archive_path(output_directory, archive_basename, options.format)
    staging_path = f"{final_path}.part"

    extension = IMAGE_FILE_EXTENSIONS[options.format]
    media_type = IMAGE_MEDIA_TYPES[options.format]
    entries: list[ImageArchiveEntry] = []

    try:
        with zipfile.ZipFile(rendered_archive_path, "r") as archive:
            members = [info for info in archive.infolist() if not info.is_dir()]
            if not members:
                raise ImageExportValidationError(
                    "Rendered slide archive contains no slides"
                )
            if len(members) > MAX_ARCHIVE_ENTRIES:
                raise ImageExportBudgetError(
                    f"Rendered archive exceeds the {MAX_ARCHIVE_ENTRIES} slide budget"
                )
            total_declared = sum(info.file_size for info in members)
            if total_declared > MAX_ARCHIVE_BYTES:
                raise ImageExportBudgetError(
                    f"Rendered archive exceeds the {MAX_ARCHIVE_BYTES} byte budget"
                )

            ordered = sorted(members, key=lambda item: _slide_sort_key(item.filename))
            total = len(ordered)
            with zipfile.ZipFile(staging_path, "w", compression=zipfile.ZIP_STORED) as out:
                for position, info in enumerate(ordered, start=1):
                    _validate_entry_name(info.filename)
                    payload = _read_bounded(archive, info)
                    image = _open_image(payload)
                    if options.format == "png" and options.width is None:
                        # PNG is already the rendered format: keep the renderer
                        # bytes exactly as produced instead of re-encoding them.
                        encoded = payload
                        width, height = image.width, image.height
                    else:
                        resized = _resize(image, options.width)
                        encoded = _encode(resized, options.format, options)
                        width, height = resized.width, resized.height
                    filename = _slide_filename(position, total, extension)
                    out.writestr(filename, encoded)
                    entries.append(
                        ImageArchiveEntry(
                            filename=filename,
                            media_type=media_type,
                            width=width,
                            height=height,
                            size_bytes=len(encoded),
                        )
                    )

        # Publish the finished archive atomically so a downloader never sees a
        # half-written ZIP and a concurrent export never truncates this one.
        os.replace(staging_path, final_path)
    except BaseException:
        try:
            if os.path.isfile(staging_path):
                os.remove(staging_path)
        except OSError:
            pass
        raise

    return ImageArchive(
        path=final_path,
        media_type=ARCHIVE_MEDIA_TYPE,
        image_format=options.format,
        entry_count=len(entries),
        entries=tuple(entries),
    )
