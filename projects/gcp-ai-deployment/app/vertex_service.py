from google import genai
from google.genai import types

from app.settings import Settings


class VertexGenerationService:
    """Small adapter that keeps the Vertex AI SDK outside the API layer."""

    def __init__(self, settings: Settings) -> None:
        if not settings.google_cloud_project:
            raise ValueError("GOOGLE_CLOUD_PROJECT is required")

        self.model = settings.vertex_model
        self.client = genai.Client(
            vertexai=True,
            project=settings.google_cloud_project,
            location=settings.google_cloud_location,
            http_options=types.HttpOptions(timeout=settings.request_timeout_seconds * 1000),
        )

    def generate(
        self,
        prompt: str,
        temperature: float,
        max_output_tokens: int,
    ) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            ),
        )
        if not response.text:
            raise RuntimeError("Vertex AI returned an empty response")
        return response.text.strip()
