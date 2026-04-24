import re
import time
from anthropic import Anthropic


class ClaudeAssistant:
    def __init__(self, api_key: str, model_version: str):
        self.name = "Anthropic Claude"
        self.provider = "Anthropic"
        self.model = model_version
        self.client = Anthropic(api_key=api_key)

    def generate_code(self, prompt: str, language: str = "Python") -> dict:
        full_prompt = f"""
You are participating in a coding-assistant benchmark.

Your job is to solve ONLY the benchmark task below.

Return ONLY valid {language} code.
Do NOT use any AI SDKs.
Do NOT call Anthropic, OpenAI, Gemini, Grok, or OpenRouter inside the generated code.
Do NOT write poems or unrelated examples.
Do NOT include markdown or explanations.
Do NOT wrap code in triple backticks.

Task:
{prompt}
"""

        start = time.time()

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1800,
                temperature=0.2,
                messages=[
                    {
                        "role": "user",
                        "content": full_prompt,
                    }
                ],
            )

            text = ""

            for block in message.content:
                if getattr(block, "type", None) == "text":
                    text += block.text

            cleaned_code = self._clean_code(text)

            end = time.time()

            return {
                "code": cleaned_code,
                "tokens_used": None,
                "latency_ms": int((end - start) * 1000),
            }

        except Exception as e:
            return {
                "code": f"# Claude error: {str(e)}\nprint('Claude failed')",
                "tokens_used": None,
                "latency_ms": None,
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


