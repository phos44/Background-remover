from starlette import status


class ImageValidationError(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ImageProcessingError(Exception):
    def __init__(self, message: str = "Unable to process image") -> None:
        self.message = message
        super().__init__(message)

