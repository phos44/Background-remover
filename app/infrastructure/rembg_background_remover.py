from PIL import Image

from app.domain.exceptions import ImageProcessingError
from app.domain.ports import BackgroundRemover
from app.domain.processing_options import BackgroundRemovalOptions
from app.infrastructure.image_preprocessor import prepare_for_inference


class RembgBackgroundRemover(BackgroundRemover):
    _sessions: dict[str, object] = {}

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def remove(self, image: Image.Image, options: BackgroundRemovalOptions) -> Image.Image:
        try:
            from rembg import remove

            session = self._get_session()
            prepared = prepare_for_inference(image)
            result = remove(
                prepared,
                session=session,
                alpha_matting=options.alpha_matting,
                alpha_matting_foreground_threshold=options.alpha_matting_foreground_threshold,
                alpha_matting_background_threshold=options.alpha_matting_background_threshold,
                alpha_matting_erode_size=options.alpha_matting_erode_size,
                post_process_mask=options.post_process_mask,
            )
            return result.convert("RGBA")
        except Exception as exc:
            raise ImageProcessingError() from exc

    def _get_session(self) -> object:
        if self.model_name not in self._sessions:
            from rembg import new_session

            self._sessions[self.model_name] = new_session(self.model_name)
        return self._sessions[self.model_name]
