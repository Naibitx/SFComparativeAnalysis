import os
from pathlib import Path
from dotenv import load_dotenv

from app.integrations.openrouter_assistant import OpenRouterAssistant


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH, override=True)


def require_key(value: str | None, name: str) -> str:
    if not value or not value.strip():
        raise ValueError(f"{name} is missing or empty in backend/.env")
    return value.strip()


OPENROUTER_API_KEY = require_key(
    os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY"),
    "OPENROUTER_API_KEY or OPENAI_API_KEY",
)


ASSISTANT_CONFIG = {
    "chatgpt": {
        "name": "ChatGPT",
        "model": os.getenv("OPENROUTER_CHATGPT_MODEL", "openai/gpt-4o-mini"),
    },
    "gemini": {
        "name": "Google Gemini",
        "model": os.getenv("OPENROUTER_GEMINI_MODEL", "google/gemini-2.0-flash-001"),
    },
    "grok": {
        "name": "Grok",
        "model": os.getenv("OPENROUTER_GROK_MODEL", "x-ai/grok-2-1212"),
    },
    "copilot": {
        "name": "GitHub Copilot",
        "model": os.getenv("OPENROUTER_COPILOT_MODEL", "openai/gpt-4o"),
    },
    "claude": {
        "name": "Anthropic Claude",
        "model": os.getenv("OPENROUTER_CLAUDE_MODEL", "anthropic/claude-sonnet-4.6"),
    },
}


def get_assistant_client(assistant_key: str):
    key = assistant_key.lower().strip()

    if key not in ASSISTANT_CONFIG:
        raise ValueError(f"Unknown assistant key: {assistant_key}")

    config = ASSISTANT_CONFIG[key]

    return OpenRouterAssistant(
        api_key=OPENROUTER_API_KEY,
        model_version=config["model"],
        name=config["name"],
    )