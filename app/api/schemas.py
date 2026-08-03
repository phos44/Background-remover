from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class ModelInfo(BaseModel):
    id: str
    title: str
    description: str


class ModelsResponse(BaseModel):
    models: list[ModelInfo]
    default_model: str
