import io
import os
import zipfile

import pytest
from PIL import Image

from enums.export_format import (
    DOCUMENT_EXPORT_FORMATS,
    EXPORT_FORMATS,
    IMAGE_EXPORT_FORMATS,
    is_document_export_format,
    is_image_export_format,
)
from models.image_export_options import ImageExportOptions
from services.image_export_service import (
    ARCHIVE_MEDIA_TYPE,
    IMAGE_FILE_EXTENSIONS,
    IMAGE_MEDIA_TYPES,
    MAX_ARCHIVE_ENTRIES,
    ImageExportBudgetError,
    ImageExportValidationError,
    build_image_archive,
)


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
JPEG_SIGNATURE = b"\xff\xd8\xff"
WEBP_SIGNATURE = b"RIFF"


def _png_bytes(width: int, height: int, colour: tuple[int, int, int]) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (width, height), colour).save(buffer, format="PNG")
    return buffer.getvalue()


def _rgba_png_bytes(width: int, height: int, colour: tuple[int, int, int, int]) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGBA", (width, height), colour).save(buffer, format="PNG")
    return buffer.getvalue()


def _write_donor_archive(path: str, entries: dict[str, bytes]) -> str:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, payload in entries.items():
            archive.writestr(name, payload)
    return path


def _read_archive(path: str) -> dict[str, bytes]:
    with zipfile.ZipFile(path, "r") as archive:
        return {info.filename: archive.read(info) for info in archive.infolist()}


# ---------------------------------------------------------------------------
# Format contract
# ---------------------------------------------------------------------------


def test_export_formats_cover_documents_and_images():
    assert DOCUMENT_EXPORT_FORMATS == frozenset({"pptx", "pdf"})
    assert IMAGE_EXPORT_FORMATS == frozenset({"png", "jpeg", "webp"})
    assert EXPORT_FORMATS == frozenset({"pptx", "pdf", "png", "jpeg", "webp"})


def test_image_and_document_format_predicates_are_disjoint():
    for export_as in EXPORT_FORMATS:
        assert not (
            is_image_export_format(export_as) and is_document_export_format(export_as)
        )
    assert is_image_export_format("png")
    assert is_document_export_format("pdf")
    assert not is_image_export_format("pdf")
    assert not is_document_export_format("webp")


def test_image_export_options_reject_unknown_format():
    with pytest.raises(ValueError):
        ImageExportOptions(format="gif")


def test_image_export_options_reject_unsupported_packaging():
    with pytest.raises(ValueError):
        ImageExportOptions(packaging="individual")


def test_image_export_options_reject_quality_for_lossless_png():
    with pytest.raises(ValueError):
        ImageExportOptions(format="png", quality=80)


def test_image_export_options_accept_quality_for_lossy_formats():
    assert ImageExportOptions(format="jpeg", quality=75).quality == 75
    assert ImageExportOptions(format="webp", quality=75).quality == 75


def test_image_export_options_reject_invalid_background():
    with pytest.raises(ValueError):
        ImageExportOptions(background="not-a-colour")
    with pytest.raises(ValueError):
        ImageExportOptions(background="#12345")


def test_image_export_options_normalise_background():
    assert ImageExportOptions(background="#FFF").background == "#ffffff"
    assert ImageExportOptions(background="#0a141E").resolved_background_rgb() == (
        10,
        20,
        30,
    )


def test_image_export_options_reject_out_of_range_width_and_quality():
    with pytest.raises(ValueError):
        ImageExportOptions(width=10)
    with pytest.raises(ValueError):
        ImageExportOptions(width=100_000)
    with pytest.raises(ValueError):
        ImageExportOptions(format="jpeg", quality=0)
    with pytest.raises(ValueError):
        ImageExportOptions(format="jpeg", quality=101)


# ---------------------------------------------------------------------------
# Archive layout
# ---------------------------------------------------------------------------


def test_png_export_packs_slides_with_deterministic_names(tmp_path):
    donor = _write_donor_archive(
        str(tmp_path / "rendered.zip"),
        {
            "slide_001.png": _png_bytes(1280, 720, (10, 20, 30)),
            "slide_002.png": _png_bytes(1280, 720, (40, 50, 60)),
        },
    )

    archive = build_image_archive(
        donor,
        options=ImageExportOptions(format="png"),
        output_directory=str(tmp_path / "out"),
        archive_basename="quarterly-review",
    )

    assert archive.media_type == ARCHIVE_MEDIA_TYPE
    assert archive.image_format == "png"
    assert archive.entry_count == 2
    assert [entry.filename for entry in archive.entries] == [
        "slide_01.png",
        "slide_02.png",
    ]
    assert os.path.basename(archive.path) == "quarterly-review_png.zip"

    packed = _read_archive(archive.path)
    assert sorted(packed) == ["slide_01.png", "slide_02.png"]


def test_exporting_the_same_deck_in_two_formats_keeps_two_archives(tmp_path):
    donor = _write_donor_archive(
        str(tmp_path / "rendered.zip"),
        {"slide_001.png": _png_bytes(64, 36, (10, 20, 30))},
    )
    output_directory = str(tmp_path / "out")

    png_archive = build_image_archive(
        donor,
        options=ImageExportOptions(format="png"),
        output_directory=output_directory,
        archive_basename="quarterly-review",
    )
    jpeg_archive = build_image_archive(
        donor,
        options=ImageExportOptions(format="jpeg"),
        output_directory=output_directory,
        archive_basename="quarterly-review",
    )

    assert png_archive.path != jpeg_archive.path
    assert os.path.isfile(png_archive.path)
    assert os.path.isfile(jpeg_archive.path)
    assert os.path.basename(png_archive.path) == "quarterly-review_png.zip"
    assert os.path.basename(jpeg_archive.path) == "quarterly-review_jpeg.zip"


def test_png_export_preserves_rendered_bytes_losslessly(tmp_path):
    source = _png_bytes(1280, 720, (11, 22, 33))
    donor = _write_donor_archive(
        str(tmp_path / "rendered.zip"), {"slide_001.png": source}
    )

    archive = build_image_archive(
        donor,
        options=ImageExportOptions(format="png"),
        output_directory=str(tmp_path / "out"),
        archive_basename="lossless",
    )

    packed = _read_archive(archive.path)
    assert packed["slide_01.png"] == source
    with Image.open(io.BytesIO(packed["slide_01.png"])) as image:
        assert image.size == (1280, 720)
        assert image.format == "PNG"


def test_slide_order_follows_the_numeric_slide_index(tmp_path):
    donor = _write_donor_archive(
        str(tmp_path / "rendered.zip"),
        {
            "slide_010.png": _png_bytes(64, 36, (1, 1, 1)),
            "slide_002.png": _png_bytes(64, 36, (2, 2, 2)),
            "slide_001.png": _png_bytes(64, 36, (3, 3, 3)),
        },
    )

    archive = build_image_archive(
        donor,
        options=ImageExportOptions(format="png"),
        output_directory=str(tmp_path / "out"),
        archive_basename="ordered",
    )

    assert [entry.filename for entry in archive.entries] == [
        "slide_01.png",
        "slide_02.png",
        "slide_03.png",
    ]
    packed = _read_archive(archive.path)
    with Image.open(io.BytesIO(packed["slide_01.png"])) as image:
        assert image.getpixel((0, 0)) == (3, 3, 3)
    with Image.open(io.BytesIO(packed["slide_02.png"])) as image:
        assert image.getpixel((0, 0)) == (2, 2, 2)
    with Image.open(io.BytesIO(packed["slide_03.png"])) as image:
        assert image.getpixel((0, 0)) == (1, 1, 1)


def test_export_reports_the_slide_dimensions_it_produced(tmp_path):
    donor = _write_donor_archive(
        str(tmp_path / "rendered.zip"),
        {"slide_001.png": _png_bytes(1280, 720, (10, 20, 30))},
    )

    archive = build_image_archive(
        donor,
        options=ImageExportOptions(format="png"),
        output_directory=str(tmp_path / "out"),
        archive_basename="dimensions",
    )

    entry = archive.entries[0]
    assert (entry.width, entry.height) == (1280, 720)
    assert entry.media_type == IMAGE_MEDIA_TYPES["png"]
    assert entry.size_bytes > 0


# ---------------------------------------------------------------------------
# Format conversion
# ---------------------------------------------------------------------------


def test_jpeg_export_produces_decodable_jpeg_slides(tmp_path):
    donor = _write_donor_archive(
        str(tmp_path / "rendered.zip"),
        {"slide_001.png": _png_bytes(1280, 720, (10, 20, 30))},
    )

    archive = build_image_archive(
        donor,
        options=ImageExportOptions(format="jpeg", quality=85),
        output_directory=str(tmp_path / "out"),
        archive_basename="photos",
    )

    assert archive.image_format == "jpeg"
    assert archive.entries[0].filename == "slide_01.jpg"
    assert archive.entries[0].media_type == "image/jpeg"

    packed = _read_archive(archive.path)
    payload = packed["slide_01.jpg"]
    assert payload.startswith(JPEG_SIGNATURE)
    with Image.open(io.BytesIO(payload)) as image:
        assert image.format == "JPEG"
        assert image.size == (1280, 720)
        assert image.mode == "RGB"


def test_webp_export_produces_decodable_webp_slides(tmp_path):
    donor = _write_donor_archive(
        str(tmp_path / "rendered.zip"),
        {"slide_001.png": _png_bytes(1280, 720, (10, 20, 30))},
    )

    archive = build_image_archive(
        donor,
        options=ImageExportOptions(format="webp", quality=80),
        output_directory=str(tmp_path / "out"),
        archive_basename="web",
    )

    assert archive.image_format == "webp"
    assert archive.entries[0].filename == "slide_01.webp"
    assert archive.entries[0].media_type == "image/webp"

    packed = _read_archive(archive.path)
    payload = packed["slide_01.webp"]
    assert payload.startswith(WEBP_SIGNATURE)
    assert payload[8:12] == b"WEBP"
    with Image.open(io.BytesIO(payload)) as image:
        assert image.format == "WEBP"
        assert image.size == (1280, 720)


def test_exported_slide_keeps_the_rendered_pixel_content(tmp_path):
    donor = _write_donor_archive(
        str(tmp_path / "rendered.zip"),
        {"slide_001.png": _png_bytes(1280, 720, (200, 40, 60))},
    )

    archive = build_image_archive(
        donor,
        options=ImageExportOptions(format="jpeg", quality=95),
        output_directory=str(tmp_path / "out"),
        archive_basename="pixels",
    )

    packed = _read_archive(archive.path)
    with Image.open(io.BytesIO(packed["slide_01.jpg"])) as image:
        red, green, blue = image.getpixel((640, 360))
    assert abs(red - 200) <= 3
    assert abs(green - 40) <= 3
    assert abs(blue - 60) <= 3


def test_jpeg_export_flattens_transparency_onto_the_requested_background(tmp_path):
    donor = _write_donor_archive(
        str(tmp_path / "rendered.zip"),
        {"slide_001.png": _rgba_png_bytes(64, 36, (0, 0, 0, 0))},
    )

    archive = build_image_archive(
        donor,
        options=ImageExportOptions(format="jpeg", background="#00ff00"),
        output_directory=str(tmp_path / "out"),
        archive_basename="flattened",
    )

    packed = _read_archive(archive.path)
    with Image.open(io.BytesIO(packed["slide_01.jpg"])) as image:
        assert image.mode == "RGB"
        red, green, blue = image.getpixel((32, 18))
    assert abs(green - 255) <= 3
    assert red <= 3
    assert blue <= 3


def test_resized_export_preserves_the_slide_aspect_ratio(tmp_path):
    donor = _write_donor_archive(
        str(tmp_path / "rendered.zip"),
        {"slide_001.png": _png_bytes(1280, 720, (10, 20, 30))},
    )

    archive = build_image_archive(
        donor,
        options=ImageExportOptions(format="png", width=640),
        output_directory=str(tmp_path / "out"),
        archive_basename="resized",
    )

    entry = archive.entries[0]
    assert (entry.width, entry.height) == (640, 360)

    packed = _read_archive(archive.path)
    with Image.open(io.BytesIO(packed["slide_01.png"])) as image:
        assert image.size == (640, 360)


def test_resized_jpeg_export_preserves_the_slide_aspect_ratio(tmp_path):
    donor = _write_donor_archive(
        str(tmp_path / "rendered.zip"),
        {"slide_001.png": _png_bytes(1280, 720, (10, 20, 30))},
    )

    archive = build_image_archive(
        donor,
        options=ImageExportOptions(format="jpeg", width=1920),
        output_directory=str(tmp_path / "out"),
        archive_basename="resized-jpeg",
    )

    assert (archive.entries[0].width, archive.entries[0].height) == (1920, 1080)


# ---------------------------------------------------------------------------
# Rejections
# ---------------------------------------------------------------------------


def test_export_rejects_a_missing_rendered_archive(tmp_path):
    with pytest.raises(ImageExportValidationError):
        build_image_archive(
            str(tmp_path / "does-not-exist.zip"),
            options=ImageExportOptions(format="png"),
            output_directory=str(tmp_path / "out"),
            archive_basename="missing",
        )


def test_export_rejects_an_empty_rendered_archive(tmp_path):
    donor = _write_donor_archive(str(tmp_path / "rendered.zip"), {})

    with pytest.raises(ImageExportValidationError):
        build_image_archive(
            donor,
            options=ImageExportOptions(format="png"),
            output_directory=str(tmp_path / "out"),
            archive_basename="empty",
        )


def test_export_rejects_entries_that_escape_the_archive(tmp_path):
    donor = _write_donor_archive(
        str(tmp_path / "rendered.zip"),
        {"../escape.png": _png_bytes(64, 36, (1, 2, 3))},
    )

    with pytest.raises(ImageExportValidationError):
        build_image_archive(
            donor,
            options=ImageExportOptions(format="png"),
            output_directory=str(tmp_path / "out"),
            archive_basename="escape",
        )
    assert not os.path.exists(str(tmp_path / "escape.png"))


def test_export_rejects_absolute_entry_names(tmp_path):
    donor = _write_donor_archive(
        str(tmp_path / "rendered.zip"),
        {"/etc/passwd.png": _png_bytes(64, 36, (1, 2, 3))},
    )

    with pytest.raises(ImageExportValidationError):
        build_image_archive(
            donor,
            options=ImageExportOptions(format="png"),
            output_directory=str(tmp_path / "out"),
            archive_basename="absolute",
        )


def test_export_rejects_nested_entry_paths(tmp_path):
    donor = _write_donor_archive(
        str(tmp_path / "rendered.zip"),
        {"nested/slide_001.png": _png_bytes(64, 36, (1, 2, 3))},
    )

    with pytest.raises(ImageExportValidationError):
        build_image_archive(
            donor,
            options=ImageExportOptions(format="png"),
            output_directory=str(tmp_path / "out"),
            archive_basename="nested",
        )


def test_export_rejects_entries_that_are_not_rendered_slides(tmp_path):
    donor = _write_donor_archive(
        str(tmp_path / "rendered.zip"),
        {"slide_001.jpg": JPEG_SIGNATURE + b"not a real jpeg"},
    )

    with pytest.raises(ImageExportValidationError):
        build_image_archive(
            donor,
            options=ImageExportOptions(format="png"),
            output_directory=str(tmp_path / "out"),
            archive_basename="not-a-slide",
        )


def test_export_rejects_a_corrupt_rendered_slide(tmp_path):
    donor = _write_donor_archive(
        str(tmp_path / "rendered.zip"),
        {"slide_001.png": PNG_SIGNATURE + b"corrupt payload"},
    )

    with pytest.raises(ImageExportValidationError):
        build_image_archive(
            donor,
            options=ImageExportOptions(format="png"),
            output_directory=str(tmp_path / "out"),
            archive_basename="corrupt",
        )


def test_export_enforces_the_slide_count_budget(tmp_path):
    entries = {
        f"slide_{index:04d}.png": _png_bytes(16, 9, (1, 2, 3))
        for index in range(MAX_ARCHIVE_ENTRIES + 1)
    }
    donor = _write_donor_archive(str(tmp_path / "rendered.zip"), entries)

    with pytest.raises(ImageExportBudgetError):
        build_image_archive(
            donor,
            options=ImageExportOptions(format="png"),
            output_directory=str(tmp_path / "out"),
            archive_basename="too-many",
        )


def test_export_refuses_an_unsupported_format(tmp_path):
    donor = _write_donor_archive(
        str(tmp_path / "rendered.zip"),
        {"slide_001.png": _png_bytes(64, 36, (1, 2, 3))},
    )
    options = ImageExportOptions(format="png").model_copy(update={"format": "gif"})

    with pytest.raises(ImageExportValidationError):
        build_image_archive(
            donor,
            options=options,
            output_directory=str(tmp_path / "out"),
            archive_basename="unsupported",
        )


def test_every_supported_image_format_has_a_media_type_and_extension():
    for image_format in IMAGE_EXPORT_FORMATS:
        assert image_format in IMAGE_MEDIA_TYPES
        assert image_format in IMAGE_FILE_EXTENSIONS
    assert IMAGE_FILE_EXTENSIONS["jpeg"] == ".jpg"
