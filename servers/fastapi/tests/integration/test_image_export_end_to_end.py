"""End-to-end Gomrey image export.

This is not a mocked export. It runs the real slide renderer (the vendored
``@presenton/export-core`` runtime driving a real Chromium), over a real HTTP
server, and then runs the real Gomrey image export service over the rendered
archive. Everything asserted here is observed from the produced bytes.

The test is skipped, honestly and with a precise reason, when the local
execution environment cannot run the renderer (no Node runtime, no export
package, or no Chromium). A skip is never reported as a pass.
"""

import http.server
import io
import os
import socket
import threading
import uuid
import zipfile
from pathlib import Path

import pytest
from PIL import Image

_REPO_ROOT = Path(__file__).resolve().parents[4]
_EXPORT_ROOT = _REPO_ROOT / "presentation-export"
_PUPPETEER_CACHE = Path.home() / ".cache" / "puppeteer"

os.environ["EXPORT_PACKAGE_ROOT"] = str(_EXPORT_ROOT)
if _PUPPETEER_CACHE.is_dir():
    os.environ.setdefault("PUPPETEER_CACHE_DIR", str(_PUPPETEER_CACHE))

from models.image_export_options import ImageExportOptions  # noqa: E402
from services.image_export_service import build_image_archive  # noqa: E402
from utils import export_utils  # noqa: E402


SLIDE_WIDTH = 1280
SLIDE_HEIGHT = 720

SLIDES = [
    ("Gomrey", "#0b1020", "#ffffff", "ltr"),
    ("Quarterly review", "#102a3b", "#7fd1ff", "ltr"),
    ("مرحبا بالعالم", "#1b1030", "#ffd166", "rtl"),
    ("Gomrey混合 script", "#10231b", "#a3ffb5", "rtl"),
]


def _slide_html(title: str, background: str, colour: str, direction: str) -> str:
    return f"""
    <div class="main-slide" style="
        width: {SLIDE_WIDTH}px;
        height: {SLIDE_HEIGHT}px;
        background: {background};
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    ">
      <div class="slide-export-inner" style="width: {SLIDE_WIDTH}px; height: {SLIDE_HEIGHT}px; display: flex; align-items: center; justify-content: center;">
        <h1 dir="{direction}" style="
          color: {colour};
          font-family: Arial, 'Helvetica Neue', sans-serif;
          font-size: 72px;
          margin: 0;
          text-align: center;
        ">{title}</h1>
      </div>
    </div>
    """


def _deck_html() -> str:
    slides = "".join(
        _slide_html(*slide) for slide in SLIDES
    )
    return f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <style>
      html, body {{ margin: 0; padding: 0; background: #000; }}
      #presentation-slides-wrapper {{
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: 0;
        margin: 0;
        padding: 0;
      }}
    </style>
  </head>
  <body>
    <div id="presentation-slides-wrapper">{slides}</div>
  </body>
</html>
"""


class _DeckHandler(http.server.BaseHTTPRequestHandler):
    deck_html = ""

    def do_GET(self):  # noqa: N802 - http.server API
        payload = self.deck_html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *_args):
        return


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def _renderer_prerequisites() -> str | None:
    """Return the precise reason the renderer cannot run, or None."""
    if not (_EXPORT_ROOT / "runner.mjs").is_file():
        return (
            "the export runtime is not installed; run "
            "scripts/sync-presentation-export.cjs"
        )
    if not (
        _EXPORT_ROOT / "node_modules" / "@presenton" / "export-core" / "dist" / "index.js"
    ).is_file():
        return "the @presenton/export-core package is not installed"
    if not (_PUPPETEER_CACHE.is_dir() and any(_PUPPETEER_CACHE.iterdir())):
        return "no Chromium build is present in the local Puppeteer cache"
    if os.system("node --version >/dev/null 2>&1") != 0:
        return "the Node.js runtime is not available on PATH"
    return None


@pytest.fixture
def deck_server():
    _DeckHandler.deck_html = _deck_html()
    port = _free_port()
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), _DeckHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}/pdf-maker"
    finally:
        server.shutdown()
        server.server_close()


@pytest.fixture
def export_environment(tmp_path, monkeypatch):
    app_data = tmp_path / "app_data"
    temp_directory = tmp_path / "temp"
    app_data.mkdir(parents=True, exist_ok=True)
    temp_directory.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("APP_DATA_DIRECTORY", str(app_data))
    monkeypatch.setenv("TEMP_DIRECTORY", str(temp_directory))
    return app_data


@pytest.fixture
def rendered_archive(deck_server, export_environment, monkeypatch):
    blocker = _renderer_prerequisites()
    if blocker:
        pytest.skip(f"E2E_NOT_EXECUTED: {blocker}")

    def _fake_export_url(presentation_id, cookie_header=None):
        return deck_server, None

    monkeypatch.setattr(
        export_utils, "_build_presentation_export_url", _fake_export_url
    )

    import asyncio

    return asyncio.run(
        export_utils.export_presentation(
            uuid.uuid4(),
            "Gomrey image export",
            "png",
        )
    )


def _packed_entries(archive_path: str) -> dict[str, bytes]:
    with zipfile.ZipFile(archive_path, "r") as archive:
        return {info.filename: archive.read(info) for info in archive.infolist()}


def test_end_to_end_png_export_renders_every_slide(rendered_archive):
    path = Path(rendered_archive.path)
    assert path.is_file()
    assert path.suffix == ".zip"

    entries = _packed_entries(str(path))
    assert len(entries) == len(SLIDES)
    assert sorted(entries) == [
        "slide_001.png",
        "slide_002.png",
        "slide_003.png",
        "slide_004.png",
    ]


def test_end_to_end_png_export_keeps_the_slide_canvas_size(rendered_archive):
    entries = _packed_entries(rendered_archive.path)
    for payload in entries.values():
        assert payload.startswith(b"\x89PNG\r\n\x1a\n")
        with Image.open(io.BytesIO(payload)) as image:
            assert image.format == "PNG"
            assert image.size == (SLIDE_WIDTH, SLIDE_HEIGHT)


def test_end_to_end_png_export_renders_distinct_slide_content(rendered_archive):
    entries = _packed_entries(rendered_archive.path)
    colours = set()
    for payload in entries.values():
        with Image.open(io.BytesIO(payload)) as image:
            colours.add(image.convert("RGB").getpixel((5, 5)))
    assert len(colours) == len(SLIDES)


def test_end_to_end_export_removes_the_rendered_intermediate(
    rendered_archive, export_environment
):
    exports_dir = export_environment / "exports"
    leftovers = [
        path
        for path in exports_dir.rglob("*")
        if path.is_file() and path.name != Path(rendered_archive.path).name
    ]
    assert leftovers == []


def test_end_to_end_jpeg_export_converts_the_rendered_slides(
    rendered_archive, export_environment
):
    entries = _packed_entries(rendered_archive.path)
    source = entries["slide_001.png"]

    archive = build_image_archive(
        rendered_archive.path,
        options=ImageExportOptions(format="jpeg", quality=85),
        output_directory=str(export_environment / "exports"),
        archive_basename="gomrey-images",
    )

    assert archive.image_format == "jpeg"
    assert archive.entry_count == len(SLIDES)
    assert [entry.filename for entry in archive.entries] == [
        "slide_001.jpg",
        "slide_002.jpg",
        "slide_003.jpg",
        "slide_004.jpg",
    ]

    converted = _packed_entries(archive.path)
    payload = converted["slide_001.jpg"]
    assert payload.startswith(b"\xff\xd8\xff")
    with Image.open(io.BytesIO(payload)) as image:
        assert image.format == "JPEG"
        assert image.size == (SLIDE_WIDTH, SLIDE_HEIGHT)


def test_end_to_end_webp_export_converts_the_rendered_slides(
    rendered_archive, export_environment
):
    archive = build_image_archive(
        rendered_archive.path,
        options=ImageExportOptions(format="webp", quality=80),
        output_directory=str(export_environment / "exports"),
        archive_basename="gomrey-images",
    )

    assert archive.image_format == "webp"
    converted = _packed_entries(archive.path)
    payload = converted["slide_004.webp"]
    assert payload[:4] == b"RIFF"
    assert payload[8:12] == b"WEBP"
    with Image.open(io.BytesIO(payload)) as image:
        assert image.format == "WEBP"
        assert image.size == (SLIDE_WIDTH, SLIDE_HEIGHT)


def test_end_to_end_resized_export_preserves_the_slide_aspect_ratio(
    rendered_archive, export_environment
):
    archive = build_image_archive(
        rendered_archive.path,
        options=ImageExportOptions(format="png", width=640),
        output_directory=str(export_environment / "exports"),
        archive_basename="gomrey-images",
    )

    assert (archive.entries[0].width, archive.entries[0].height) == (640, 360)
