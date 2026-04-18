import time
from typing import Optional
import google.generativeai as genai
from google.api_core import exceptions
from base_assistant import BaseAssistant

class GeminiAssistant(BaseAssistant):
    """Concrete implementation of the Gemini AI assistant."""

    def __init__(self, api_key: str, model_version: str = "gemini-1.5-pro"):
        super().__init__(api_key, model_version)
        # Configure the Google AI SDK
        genai.configure(api_key=self._api_key)
        self._model = genai.GenerativeModel(model_version)

    @property
    def name(self) -> str:
        return "Gemini Pro"

    @property
    def provider(self) -> str:
        return "Google"

    def generate_code(
        self,
        prompt: str,
        language: str = "python",
        context: Optional[str] = None,
    ) -> dict:
        system_prompt = (
            f"You are an expert {language} developer. "
            "Return only the code with a brief explanation. "
            "Format your response exactly as:\nCODE:\n<code>\nEXPLANATION:\n<explanation>"
        )
        user_message = f"{context}\n\n{prompt}" if context else prompt

        try:
            start_time = time.time()
            # Generate content using the SDK
            response = self._model.generate_content(f"{system_prompt}\n\n{user_message}")
            latency_ms = (time.time() - start_time) * 1000

            content = response.text
            code, explanation = self._parse_gemini_response(content)

            return self._base_response(
                language=language,
                code=code,
                explanation=explanation,
                tokens_used=response.usage_metadata.total_token_count if response.usage_metadata else None,
                latency_ms=round(latency_ms, 2)
            )

        except Exception as e:
            return self.handle_error(e)

    def handle_error(self, raw_error: Exception | dict) -> dict:
        """Translates Google API exceptions into standardized error dicts."""
        if isinstance(raw_error, exceptions.Unauthenticated):
            return self._base_error("auth_error", "Invalid API Key", retryable=False)
        if isinstance(raw_error, exceptions.ResourceExhausted):
            return self._base_error("rate_limit", "Quota exceeded", retryable=True)
        if isinstance(raw_error, exceptions.InvalidArgument):
            return self._base_error("invalid_request", str(raw_error), retryable=False)
        
        return self._base_error("unknown_error", str(raw_error), retryable=False)

    def _parse_gemini_response(self, content: str) -> tuple[str, str]:
        """Helper to split code and explanation based on the system prompt format."""
        if "CODE:" in content and "EXPLANATION:" in content:
            parts = content.split("EXPLANATION:")
            explanation = parts[1].strip()
            code = parts[0].replace("CODE:", "").strip()
            return code, explanation
        return content.strip(), ""