import asyncio
import uuid

import pytest
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from pydantic import ValidationError
from starlette.requests import Request

from api.v1.ppt.endpoints.presentation import (
    PRESENTATION_ROUTER,
    export_existing_presentation,
)
from models.generate_presentation_request import (
    GeneratePresentationRequest,
    GenerateSmartPresentationRequest,
)
from models.image_export_options import ImageExportOptions
from models.presentation_and_path import PresentationAndPath
from models.presentation_from_template import EditPresentationRequest


class _FakeAsyncSession:
    def __init__(self, presentation):
        self._presentation = presentation

    async def get(self, _model, key):
        if key == self._presentation.id:
            return self._presentation
        return None


class _FakePresentation:
    def __init__(self):
        self.id = uuid.uuid4()
        self.title = "Quarterly review"


def _request() -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/v1/ppt/presentation/export",
            "headers": [(b"host", b"gomrey.example.com")],
        }
    )


def _openapi_export_schema() -> dict:
    app = FastAPI()
    app.include_router(PRESENTATION_ROUTER)
    schema = get_openapi(title="gomrey", version="0.1.0", routes=app.routes)
    export_path = next(
        path for path in schema["paths"] if path.endswith("/export")
    )
    body_ref = schema["paths"][export_path]["post"]["requestBody"]["content"][
        "application/json"
    ]["schema"]["$ref"]
    return schema["components"]["schemas"][body_ref.split("/")[-1]]


# ---------------------------------------------------------------------------
# Public API contract
# ---------------------------------------------------------------------------


def test_export_endpoint_advertises_the_image_formats():
    schema = _openapi_export_schema()
    export_as = schema["properties"]["export_as"]
    assert export_as["enum"] == ["pptx", "pdf", "png", "jpeg", "webp"]


def test_export_endpoint_advertises_the_image_export_options():
    schema = _openapi_export_schema()
    assert "image_export" in schema["properties"]


def test_generate_request_accepts_image_formats():
    for export_as in ("png", "jpeg", "webp"):
        request = GeneratePresentationRequest(content="hello", export_as=export_as)
        assert request.export_as == export_as


def test_generate_request_rejects_unknown_formats():
    with pytest.raises(ValidationError):
        GeneratePresentationRequest(content="hello", export_as="gif")


def test_generate_request_carries_image_export_options():
    request = GeneratePresentationRequest(
        content="hello",
        export_as="jpeg",
        image_export={"format": "jpeg", "quality": 70, "width": 1920},
    )
    assert request.image_export == ImageExportOptions(
        format="jpeg", quality=70, width=1920
    )


def test_generate_request_rejects_image_options_that_conflict_with_the_format():
    with pytest.raises(ValidationError):
        GeneratePresentationRequest(
            content="hello",
            export_as="png",
            image_export={"format": "png", "quality": 80},
        )


def test_smart_generate_request_accepts_image_formats():
    request = GenerateSmartPresentationRequest(content="hello", export_as="webp")
    assert request.export_as == "webp"


def test_edit_request_accepts_image_formats():
    request = EditPresentationRequest(
        presentation_id=uuid.uuid4(),
        slides=[],
        export_as="png",
        image_export={"format": "png"},
    )
    assert request.export_as == "png"
    assert request.image_export is not None


# ---------------------------------------------------------------------------
# Route behaviour
# ---------------------------------------------------------------------------


def test_export_route_forwards_the_image_export_options(monkeypatch):
    presentation = _FakePresentation()
    captured: dict = {}

    async def _fake_export_presentation(
        presentation_id,
        title,
        export_as,
        cookie_header=None,
        image_options=None,
    ):
        captured["presentation_id"] = presentation_id
        captured["export_as"] = export_as
        captured["image_options"] = image_options
        return PresentationAndPath(
            presentation_id=presentation_id,
            path="/tmp/exports/quarterly-review.zip",
        )

    monkeypatch.setattr(
        "api.v1.ppt.endpoints.presentation.export_presentation",
        _fake_export_presentation,
    )

    options = ImageExportOptions(format="webp", quality=70)
    response = asyncio.run(
        export_existing_presentation(
            id=presentation.id,
            request_http=_request(),
            export_as="webp",
            image_export=options,
            sql_session=_FakeAsyncSession(presentation),
        )
    )

    assert captured["export_as"] == "webp"
    assert captured["image_options"] is options
    assert response.path == "/tmp/exports/quarterly-review.zip"
    assert response.edit_path == f"/presentation?id={presentation.id}"


def test_export_route_reports_a_missing_presentation():
    from fastapi import HTTPException

    presentation = _FakePresentation()

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            export_existing_presentation(
                id=uuid.uuid4(),
                request_http=_request(),
                export_as="png",
                image_export=None,
                sql_session=_FakeAsyncSession(presentation),
            )
        )

    assert error.value.status_code == 404
