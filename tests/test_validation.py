from io import BytesIO

import pytest
from PIL import Image

from app.domain.exceptions import ImageValidationError
from app.domain.image_validator import ImageValidator


def make_png(size=(64, 64)) -> bytes:
    image = Image.new("RGB", size, "white")
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def test_accepts_valid_png() -> None:
    validator = ImageValidator(max_size_bytes=1024 * 1024, max_pixels=1_000_000)

    image = validator.validate_image_bytes(make_png())

    assert image.mode == "RGBA"
    assert image.size == (64, 64)


def test_rejects_invalid_bytes() -> None:
    validator = ImageValidator(max_size_bytes=1024 * 1024, max_pixels=1_000_000)

    with pytest.raises(ImageValidationError):
        validator.validate_image_bytes(b"not an image")


def test_rejects_large_resolution() -> None:
    validator = ImageValidator(max_size_bytes=1024 * 1024, max_pixels=100)

    with pytest.raises(ImageValidationError):
        validator.validate_image_bytes(make_png(size=(32, 32)))

