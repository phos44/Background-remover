from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import Response
from starlette import status

from app.api.schemas import HealthResponse, ModelInfo, ModelsResponse
from app.core.config import Settings, get_settings
from app.domain.exceptions import ImageValidationError
from app.domain.image_validator import ImageValidator
from app.domain.processing_options import BackgroundRemovalOptions
from app.infrastructure.rembg_background_remover import RembgBackgroundRemover
from app.services.background_service import BackgroundRemovalService

router = APIRouter()

MODEL_CATALOG = {
    "isnet-general-use": ModelInfo(
        id="isnet-general-use",
        title="Универсальный",
        description="Лучший баланс качества для предметов, людей и смешанных сцен.",
    ),
    "isnet-anime": ModelInfo(
        id="isnet-anime",
        title="Иллюстрации",
        description="Лучше подходит для рисунков, маскотов, аниме и плоской графики.",
    ),
    "birefnet-general-lite": ModelInfo(
        id="birefnet-general-lite",
        title="Максимальное качество",
        description="Более сильная модель для сложных границ, работает медленнее.",
    ),
    "u2net": ModelInfo(
        id="u2net",
        title="Быстрый режим",
        description="Стабильный baseline с умеренным потреблением CPU.",
    ),
}


def get_background_service(
    config: Settings = Depends(get_settings),
    model: Annotated[str | None, Query(description="rembg model id")] = None,
) -> BackgroundRemovalService:
    model_name = model or config.rembg_model
    if model_name not in MODEL_CATALOG:
        raise ImageValidationError(
            f"Unsupported model: {model_name}",
            status.HTTP_400_BAD_REQUEST,
        )

    validator = ImageValidator(
        max_size_bytes=config.max_image_size_mb * 1024 * 1024,
        max_pixels=config.max_image_pixels,
    )
    remover = RembgBackgroundRemover(model_name=model_name)
    return BackgroundRemovalService(validator=validator, remover=remover)


@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/models", response_model=ModelsResponse, tags=["background"])
async def models(config: Settings = Depends(get_settings)) -> ModelsResponse:
    default_model = config.rembg_model
    if default_model not in MODEL_CATALOG:
        default_model = "isnet-general-use"
    return ModelsResponse(models=list(MODEL_CATALOG.values()), default_model=default_model)


@router.post(
    "/remove-background",
    response_class=Response,
    responses={
        200: {"content": {"image/png": {}}},
        400: {"description": "Invalid request or unsupported image"},
        413: {"description": "Image exceeds configured limits"},
        415: {"description": "Unsupported media type"},
        500: {"description": "Unexpected processing error"},
    },
    tags=["background"],
)
async def remove_background(
    image: UploadFile = File(...),
    alpha_matting: Annotated[
        bool,
        Query(description="Refine transparent edges using alpha matting"),
    ] = False,
    post_process_mask: Annotated[
        bool,
        Query(description="Apply mask post-processing"),
    ] = True,
    service: BackgroundRemovalService = Depends(get_background_service),
) -> Response:
    options = BackgroundRemovalOptions(
        alpha_matting=alpha_matting,
        post_process_mask=post_process_mask,
    )
    result = await service.remove(image, options)
    return Response(
        content=result,
        media_type="image/png",
        headers={"Content-Disposition": 'attachment; filename="background-removed.png"'},
    )
