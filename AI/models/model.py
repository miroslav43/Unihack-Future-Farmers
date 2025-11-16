import os
from agno.models.base import Model
from agno.models.google import Gemini
from agno.models.openrouter import OpenRouter

# Gemini model class for Google's Generative AI models.

#     Vertex AI:
#     - You will need Google Cloud credentials to use the Vertex AI API. Run `gcloud auth application-default login` to set credentials.
#     - Set `vertexai` to `True` to use the Vertex AI API.
#     - Set your `project_id` (or set `GOOGLE_CLOUD_PROJECT` environment variable) and `location` (optional).
#     - Set `http_options` (optional) to configure the HTTP options.

#     Based on https://googleapis.github.io/python-genai/

def get_gemini_model(
            id: str = os.getenv("MODEL_ID", "gemini-2.0-flash-001"),
            name: str = os.getenv("MODEL_NAME", "Gemini"),
            provider: str = os.getenv("MODEL_PROVIDER", "Google"),
            api_key: str = os.getenv("MODEL_OPENAI_API_KEY"),
            vertexai: bool = os.getenv("MODEL_VERTEX_AI", False),
            project_id: str = os.getenv("MODEL_PROJECT_ID", "your-project-id"),
            location: str = os.getenv("MODEL_LOCATION", "us-central1")
            ) -> Model:
    
    return Gemini(
        id=id,
        name=name,
        provider=provider,
        api_key=api_key,
        vertexai=vertexai,
        project_id=project_id,
        location=location
    )

def get_openrouter_model(
                id: str = os.getenv("MODEL_ID", "gpt-5-mini"),
                api_key: str = os.getenv("OPENAI_API_KEY")
                ) -> Model:
    
    return OpenRouter(
        id=id,
        api_key=api_key,
        max_tokens=10000
    )
    