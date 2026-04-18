""" Implementation of BaseAssistant for Google Gemini Pro """

import time
from typing import Optional
import google.generativeai as genai
from google.api_core import exceptions

from .base_assistant import BaseAssistant


class GeminiAssistant(BaseAssistant):

    def __init__(self, api_key: str, model_version: str = "gemini-1.5-pro"):
        super().__init__(api_key, model_version)
        genai.configure(api_key=api_key)
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
        system_instruction = (
            f"You are an expert {language} developer. "
            "Return only the code with a brief explanation. "
            "Format your response as:\nCODE:\n<code>\nEXPLANATION:\n<explanation>"
        )
        
        full_prompt = f"{system_instruction}\n\nContext: {context}\n\nTask: {prompt}" if context else f"{system_instruction}\n\nTask: {prompt}"

        try:
            start = time.time()
            # Gemini's generation call
            response = self._model.generate_content(full_prompt)
            latency_ms = (time.time() - start) * 1000

            content = response.text or ""
            code, explanation = self._parse_response(content)

            # Returns structured result for ExecutionEngine and MetricsCollector
            return self._base_response(
                language=language,
                code=code,
                explanation=explanation,
                # Gemini Pro 1.5 usage metadata
                tokens_used=response.usage_metadata.total_token_count if response.usage_metadata else None,
                latency_ms=round(latency_ms, 2),
            )

        except Exception as e:
            return self.handle_error(e)

    def handle_error(self, raw_error: Exception) -> dict:
        """ Standardized error mapping for Google API exceptions """
        error_map = {
            exceptions.Unauthenticated: ("auth_error", False),
            exceptions.ResourceExhausted: ("rate_limit", True),
            exceptions.InvalidArgument: ("invalid_request", False),
            exceptions.ServiceUnavailable: ("network_error", True),
        }

        for exc_type, (error_type, retryable) in error_map.items():
            if isinstance(raw_error, exc_type):
                return self._base_error(error_type, str(raw_error), retryable)

        return self._base_error("unknown", str(raw_error), retryable=False)

    def _parse_response(self, content: str) -> tuple[str, str]:
        code, explanation = "", ""
        if "CODE:" in content and "EXPLANATION:" in content:
            parts = content.split("EXPLANATION:")
            explanation = parts[1].strip()
            code = parts[0].replace("CODE:", "").strip()
        else:
            code = content.strip()
        return code, explanation
