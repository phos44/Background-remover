from io import BytesIO

from PIL import Image, UnidentifiedImageError
from starlette import status

from app.domain.exceptions import ImageValidationError


class ImageValidator:
    allowed_content_types = {"image/jpeg", "image/png", "image/webp"}
    allowed_formats = {"JPEG", "PNG", "WEBP"}

    def __init__(self, max_size_bytes: int, max_pixels: int) -> None:
        self.max_size_bytes = max_size_bytes
        self.max_pixels = max_pixels

    def validate_upload_metadata(self, content_type: str | None, size: int) -> None:
        if content_type not in self.allowed_content_types:
            raise ImageValidationError(
                "Only JPEG, PNG and WEBP images are supported",
                status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            )
        if size > self.max_size_bytes:
            raise ImageValidationError(
                "Image exceeds the configured file size limit",
                status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )

    def validate_image_bytes(self, payload: bytes) -> Image.Image:
        if not payload:
            raise ImageValidationError("Uploaded file is empty")

        try:
            image = Image.open(BytesIO(payload))
            image.verify()
            image = Image.open(BytesIO(payload))
        except (UnidentifiedImageError, OSError) as exc:
            raise ImageValidationError("Uploaded file is not a valid image") from exc

        if image.format not in self.allowed_formats:
            raise ImageValidationError(
                "Only JPEG, PNG and WEBP images are supported",
                status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            )

        width, height = image.size
        if width * height > self.max_pixels:
            raise ImageValidationError(
                "Image exceeds the configured resolution limit",
                status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )

        return image.convert("RGBA")

