from typing import Protocol

from PIL import Image

from app.domain.processing_options import BackgroundRemovalOptions


class BackgroundRemover(Protocol):
    def remove(self, image: Image.Image, options: BackgroundRemovalOptions) -> Image.Image:
        ...
