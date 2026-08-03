from io import BytesIO

from fastapi import UploadFile
import structlog

from app.domain.image_validator import ImageValidator
from app.domain.ports import BackgroundRemover
from app.domain.processing_options import BackgroundRemovalOptions

logger = structlog.get_logger(__name__)


class BackgroundRemovalService:
    def __init__(self, validator: ImageValidator, remover: BackgroundRemover) -> None:
        self.validator = validator
        self.remover = remover

    async def remove(self, upload: UploadFile, options: BackgroundRemovalOptions) -> bytes:
        payload = await upload.read()
        self.validator.validate_upload_metadata(upload.content_type, len(payload))
        image = self.validator.validate_image_bytes(payload)

        logger.info(
            "remove_background_started",
            filename=upload.filename,
            content_type=upload.content_type,
            width=image.width,
            height=image.height,
        )
        result = self.remover.remove(image, options)
        output = BytesIO()
        result.save(output, format="PNG", optimize=True)
        logger.info("remove_background_finished", bytes=len(output.getvalue()))
        return output.getvalue()
