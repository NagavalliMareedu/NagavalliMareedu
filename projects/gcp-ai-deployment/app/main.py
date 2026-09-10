import logging
import time
import uuid
from functools import lru_cache

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from app.settings import Settings, get_settings
from app.vertex_service import VertexGenerationService

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GCP AI Deployment API",
    version="1.0.0",
    description="Production-style Gemini API deployed through Vertex AI.",
)


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    max_output_tokens: int = Field(default=512, ge=1, le=2048)


class GenerateResponse(BaseModel):
    request_id: str
    model: str
    text: str
    latency_ms: int


@lru_cache
def get_generation_service() -> VertexGenerationService:
    return VertexGenerationService(get_settings())


@app.middleware("http")
async def add_request_context(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    started = time.perf_counter()
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    response.headers["x-response-time-ms"] = str(
        round((time.perf_counter() - started) * 1000)
    )
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "service": "gcp-ai-deployment-api"}


@app.post("/v1/generate", response_model=GenerateResponse)
def generate(
    payload: GenerateRequest,
    settings: Settings = Depends(get_settings),
    service: VertexGenerationService = Depends(get_generation_service),
) -> GenerateResponse:
    if len(payload.prompt) > settings.max_prompt_characters:
        raise HTTPException(status_code=422, detail="Prompt exceeds configured limit")

    request_id = str(uuid.uuid4())
    started = time.perf_counter()

    try:
        text = service.generate(
            prompt=payload.prompt,
            temperature=payload.temperature,
            max_output_tokens=payload.max_output_tokens,
        )
    except Exception as exc:
        logger.exception("generation_failed request_id=%s", request_id)
        raise HTTPException(
            status_code=502,
            detail="The model service is temporarily unavailable",
        ) from exc

    return GenerateResponse(
        request_id=request_id,
        model=settings.vertex_model,
        text=text,
        latency_ms=round((time.perf_counter() - started) * 1000),
    )
