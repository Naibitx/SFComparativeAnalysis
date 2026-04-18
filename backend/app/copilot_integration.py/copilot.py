""" Implementation of BaseAssistant for GitHub CoPilot """

import time
from typing import Optional

import openai

from base_assistant import BaseAssistant


class CoPilotAssistant(BaseAssistant):

    def __init__(self, api_key: str, model_version: str = "gpt-4o"):
        super().__init__(api_key, model_version)
        self._client = openai.OpenAI(api_key=api_key)

    @property
    def name(self) -> str:
        return "CoPilot"

    @property
    def provider(self) -> str:
        return "GitHub / OpenAI"

    def generate_code(
        self,
        prompt: str,
        language: str = "python",
        context: Optional[str] = None,
    ) -> dict:
        system_prompt = (
            f"You are an expert {language} developer. "
            "Return only the code with a brief explanation. "
            "Format your response as:\nCODE:\n<code>\nEXPLANATION:\n<explanation>"
        )
        user_message = f"{context}\n\n{prompt}" if context else prompt

        try:
            start = time.time()
            response = self._client.chat.completions.create(
                model=self.model_version,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_message},
                ],
            )
            latency_ms = (time.time() - start) * 1000

            content = response.choices[0].message.content or ""
            code, explanation = self._parse_response(content)

            return self._base_response(
                language=language,
                code=code,
                explanation=explanation,
                tokens_used=response.usage.total_tokens if response.usage else None,
                latency_ms=round(latency_ms, 2),
            )

        except Exception as e:
            return self.handle_error(e)

    def handle_error(self, raw_error: Exception | dict) -> dict:
        error_map = {
            openai.AuthenticationError: ("auth_error",       False),
            openai.RateLimitError:      ("rate_limit",       True),
            openai.BadRequestError:     ("invalid_request",  False),
            openai.APIConnectionError:  ("network_error",    True),
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
        return code, explanations