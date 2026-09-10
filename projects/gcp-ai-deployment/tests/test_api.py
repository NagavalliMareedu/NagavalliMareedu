from fastapi.testclient import TestClient

from app.main import app, get_generation_service
from app.settings import Settings, get_settings


class FakeGenerationService:
    def generate(self, prompt: str, temperature: float, max_output_tokens: int) -> str:
        return f"Generated response for: {prompt}"


def test_settings() -> Settings:
    return Settings(
        google_cloud_project="test-project",
        vertex_model="gemini-test",
        max_prompt_characters=100,
    )


app.dependency_overrides[get_settings] = test_settings
app.dependency_overrides[get_generation_service] = FakeGenerationService
client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "x-request-id" in response.headers


def test_generate() -> None:
    response = client.post(
        "/v1/generate",
        json={"prompt": "What is Vertex AI?", "temperature": 0.1},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["model"] == "gemini-test"
    assert body["text"].startswith("Generated response")
    assert body["request_id"]


def test_prompt_limit() -> None:
    response = client.post("/v1/generate", json={"prompt": "x" * 101})
    assert response.status_code == 422
