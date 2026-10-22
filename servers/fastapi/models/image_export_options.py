from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


ImageFormat = Literal["png", "jpeg", "webp"]

ImagePackaging = Literal["zip"]

MIN_IMAGE_WIDTH = 320
MAX_IMAGE_WIDTH = 7680
MIN_IMAGE_QUALITY = 1
MAX_IMAGE_QUALITY = 100
DEFAULT_IMAGE_BACKGROUND = "#ffffff"


class ImageExportOptions(BaseModel):
    """Options that control the Gomrey image export.

    The slide renderer always produces one PNG per slide. These options describe
    what the resulting archive should look like: the image format, the output
    resolution, the encoder quality for lossy formats, and the background used
    when a format cannot carry an alpha channel.
    """

    format: ImageFormat = Field(
        default="png",
        description="Image format of every slide in the exported archive.",
    )
    packaging: ImagePackaging = Field(
        default="zip",
        description="How the exported slides are packaged for download.",
    )
    width: Optional[int] = Field(
        default=None,
        ge=MIN_IMAGE_WIDTH,
        le=MAX_IMAGE_WIDTH,
        description=(
            "Target pixel width of every exported slide. The height is derived "
            "from the slide aspect ratio so the output never distorts."
        ),
    )
    quality: Optional[int] = Field(
        default=None,
        ge=MIN_IMAGE_QUALITY,
        le=MAX_IMAGE_QUALITY,
        description=(
            "Encoder quality for lossy formats (JPEG, WebP). PNG is lossless and "
            "rejects this option."
        ),
    )
    background: str = Field(
        default=DEFAULT_IMAGE_BACKGROUND,
        description=(
            "Background colour used to flatten transparency for formats that "
            "cannot carry an alpha channel (JPEG)."
        ),
    )

    @field_validator("background")
    @classmethod
    def _validate_background(cls, value: str) -> str:
        normalized = (value or "").strip().lower()
        if not normalized.startswith("#"):
            raise ValueError("background must be a hex colour such as #ffffff")
        digits = normalized[1:]
        if len(digits) not in (3, 6) or any(
            character not in "0123456789abcdef" for character in digits
        ):
            raise ValueError("background must be a hex colour such as #ffffff")
        if len(digits) == 3:
            digits = "".join(character * 2 for character in digits)
        return f"#{digits}"

    @model_validator(mode="after")
    def _validate_format_options(self) -> "ImageExportOptions":
        if self.quality is not None and self.format == "png":
            raise ValueError(
                "quality is not supported for PNG image export because PNG is lossless"
            )
        return self

    def resolved_background_rgb(self) -> tuple[int, int, int]:
        digits = self.background.lstrip("#")
        return (
            int(digits[0:2], 16),
            int(digits[2:4], 16),
            int(digits[4:6], 16),
        )
