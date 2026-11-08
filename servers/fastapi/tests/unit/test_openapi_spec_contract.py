import json
from pathlib import Path

from api.main import app


SPEC_PATH = Path(__file__).resolve().parents[2] / "openai_spec.json"


def test_committed_openapi_spec_matches_the_live_application():
    """The MCP server publishes the committed spec, so it must not drift.

    ``servers/fastapi/mcp_server.py`` builds its tool schemas from the
    committed ``openai_spec.json`` rather than from the running application.
    When the application contract changes and the spec is not regenerated, the
    MCP tools keep advertising the old contract with no error anywhere. This
    test turns that silent drift into a failure.
    """
    committed = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    live = app.openapi()

    assert committed == live, (
        "servers/fastapi/openai_spec.json is out of date. "
        "Regenerate it with: "
        "cd servers/fastapi && PYTHONPATH=. python scripts/generate_openapi_spec.py"
    )


def test_openapi_spec_advertises_the_image_export_formats():
    committed = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    schemas = committed["components"]["schemas"]

    assert schemas["ImageExportOptions"]["properties"]["format"]["enum"] == [
        "png",
        "jpeg",
        "webp",
    ]

    for request_schema in (
        "GeneratePresentationRequest",
        "GenerateSmartPresentationRequest",
        "EditPresentationRequest",
    ):
        properties = schemas[request_schema]["properties"]
        assert properties["export_as"]["enum"] == [
            "pptx",
            "pdf",
            "png",
            "jpeg",
            "webp",
        ]
        assert "image_export" in properties
