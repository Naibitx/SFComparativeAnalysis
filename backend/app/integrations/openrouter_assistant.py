import re
import time
from openai import OpenAI


class OpenRouterAssistant:
    def __init__(self, api_key: str, model_version: str, name: str):
        if not api_key or not api_key.strip():
            raise ValueError("OPENROUTER_API_KEY must not be empty.")

        self.name = name
        self.model = model_version
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key.strip(),
            default_headers={
                "HTTP-Referer": "http://localhost:5173",
                "X-OpenRouter-Title": "SF Comparative Analysis",
            },
        )

    def generate_code(self, prompt: str, language: str = "Python") -> dict:
        full_prompt = f"""
Return ONLY valid {language} code.
Do not include markdown.
Do not include explanations.
Do not wrap the response in triple backticks.

Task:
{prompt}
"""

        start = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a code generation assistant. Return only valid {language} code.",
                    },
                    {
                        "role": "user",
                        "content": full_prompt,
                    },
                ],
                temperature=0.2,
                max_tokens=1800,
            )

            text = response.choices[0].message.content or ""
            code = self._clean_code(text)

            usage = getattr(response, "usage", None)
            tokens_used = getattr(usage, "total_tokens", None) if usage else None

            return {
                "code": code,
                "tokens_used": tokens_used,
                "latency_ms": int((time.time() - start) * 1000),
            }

        except Exception as exc:
            return {
                "code": f"# Generation failed for {self.name}: {exc}\nprint('Generation failed')",
                "tokens_used": None,
                "latency_ms": int((time.time() - start) * 1000),
            }

    def _clean_code(self, text: str) -> str:
        text = text.strip()

        fenced = re.search(
            r"```(?:python|javascript|php|java|cpp|c\+\+)?\s*(.*?)```",
            text,
            re.DOTALL | re.IGNORECASE,
        )

        if fenced:
            return fenced.group(1).strip()

        return text