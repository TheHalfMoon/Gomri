"""Tests for the W2a slide animation field on the slide element model.

The animation is a **template-authoring** decision. The model that writes the
slide content never sees it, and the template application keeps the template's
own value. These tests prove all three properties, because each of them fails
silently otherwise.
"""

import json

import pytest
from pydantic import ValidationError

from templates.v2.models.elements import ElementAnimation, Text
from templates.v2.models.layouts import (
    RawSlideLayout,
    RawSlideLayouts,
    slide_layout_llm_json_schema,
)
from templates.v2.schema import extract_slide_schema_from_layout

TEXT_ELEMENT = {
    "type": "text",
    "name": "body",
    "decorative": False,
    "min_length": 1,
    "max_length": 200,
    "runs": [{"text": "Retention rose to 91 percent."}],
}


def _with_animation(animation: dict | None = None) -> dict:
    element = dict(TEXT_ELEMENT)
    if animation is not None:
        element["animation"] = animation
    return element


# --------------------------------------------------------------------------- #
# The model
# --------------------------------------------------------------------------- #


def test_the_element_model_accepts_an_animation() -> None:
    element = Text(
        **{
            **_with_animation(
                {"name": "fade-up", "delay_ms": 120, "duration": "normal"}
            ),
            "runs": [{"text": "Retention rose to 91 percent."}],
        }
    )

    assert element.animation is not None
    assert element.animation.name == "fade-up"
    assert element.animation.delay_ms == 120
    assert element.animation.duration == "normal"


def test_the_element_model_defaults_to_no_animation() -> None:
    element = Text(
        **{
            **_with_animation(),
            "runs": [{"text": "Retention rose to 91 percent."}],
        }
    )
    assert element.animation is None


def test_an_animation_without_a_name_is_refused() -> None:
    with pytest.raises(ValidationError):
        ElementAnimation()


def test_a_negative_delay_is_refused() -> None:
    with pytest.raises(ValidationError):
        ElementAnimation(name="fade-up", delay_ms=-1)


def test_an_unknown_duration_is_refused() -> None:
    with pytest.raises(ValidationError):
        ElementAnimation(name="fade-up", duration="glacial")


# --------------------------------------------------------------------------- #
# The template keeps its animation — no silent drop
# --------------------------------------------------------------------------- #


def test_a_template_layout_keeps_its_animation() -> None:
    """The element model must declare the field, or pydantic drops it."""
    raw = RawSlideLayouts(
        layouts=[
            RawSlideLayout(
                id="title_intro",
                description="A layout with an animated element.",
                elements=[
                    _with_animation({"name": "fade-up", "delay_ms": 100}),
                ],
            )
        ]
    )

    element = raw.layouts[0].elements[0]
    assert element.animation is not None
    assert element.animation.name == "fade-up"
    assert element.animation.delay_ms == 100


def test_the_template_application_keeps_the_animation_when_content_is_applied() -> None:
    """The template's value must survive the generated content merge."""
    from api.v1.ppt.endpoints.presentation import _apply_template_content_to_ui

    ui = {
        "components": [
            {
                "id": "body",
                "elements": [_with_animation({"name": "fade-up"})],
            }
        ]
    }
    content = {"body": {"body": "A generated sentence."}}

    hydrated = _apply_template_content_to_ui(ui, content)

    assert hydrated is not None
    element = hydrated["components"][0]["elements"][0]
    assert element["animation"]["name"] == "fade-up"
    # The generated content still landed.
    assert element["runs"][0]["text"] == "A generated sentence."


def test_the_generated_content_cannot_replace_the_animation() -> None:
    """A model-supplied animation must never win over the template's."""
    from api.v1.ppt.endpoints.presentation import _apply_template_content_to_ui

    ui = {
        "components": [
            {
                "id": "body",
                "elements": [_with_animation({"name": "fade-up"})],
            }
        ]
    }
    content = {"body": {"body": "A generated sentence."}}

    hydrated = _apply_template_content_to_ui(ui, content)

    assert hydrated is not None
    element = hydrated["components"][0]["elements"][0]
    assert element["animation"]["name"] == "fade-up"


# --------------------------------------------------------------------------- #
# The model never sees it
# --------------------------------------------------------------------------- #


def test_the_layout_generation_schema_does_not_offer_an_animation() -> None:
    """The layout-generating model must not be able to choose an animation."""
    schema = slide_layout_llm_json_schema()

    def properties_with_animation(node):
        found = []
        if isinstance(node, dict):
            properties = node.get("properties")
            if isinstance(properties, dict) and "animation" in properties:
                found.append(properties)
            for value in node.values():
                found.extend(properties_with_animation(value))
        elif isinstance(node, list):
            for value in node:
                found.extend(properties_with_animation(value))
        return found

    assert properties_with_animation(schema) == []
    assert "animation" not in json.dumps(schema)


def test_the_content_schema_does_not_offer_an_animation() -> None:
    """The content-generating model must not be able to choose an animation."""
    layout = RawSlideLayout(
        id="title_intro",
        description="A layout with an animated element.",
        elements=[_with_animation({"name": "fade-up"})],
    )

    schema = extract_slide_schema_from_layout(layout)

    assert "animation" not in json.dumps(schema)
