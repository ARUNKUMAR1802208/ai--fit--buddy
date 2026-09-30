from .config import settings


class AIConfigurationError(RuntimeError):
    pass


_client = None


def get_client():
    global _client
    if settings.mock_ai:
        raise AIConfigurationError("Mock AI mode is enabled; no Gemini client is available.")
    if not settings.gemini_api_key:
        raise AIConfigurationError(
            "GEMINI_API_KEY is not configured. Add it to the .env file and restart the server."
        )
    if _client is None:
        try:
            from google import genai
        except ImportError as exc:
            raise AIConfigurationError(
                "google-genai is not installed. Run: pip install -r requirements.txt"
            ) from exc
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client
