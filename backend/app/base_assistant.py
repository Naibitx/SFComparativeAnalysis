"""
base_assistant.py
-----------------
Abstract base class that defines the common interface all AI coding assistants
must implement in the comparative analysis project.
 
Supported assistants: ChatGPT, CoPilot, Gemini, Grok, Claude
"""
 
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
 
 
class BaseAssistant(ABC):
    """
    Abstract base class for all AI coding assistants.
 
    Every concrete assistant (ChatGPT, CoPilot, Gemini, Grok, Claude) must
    subclass this and implement every @abstractmethod.
 
    Response format (returned by generate_code)
    """
 
    def __init__(self, api_key: str, model_version: str = ""):
        """
        Parameters
        ----------
        api_key : str
            Credential used to authenticate with the provider's API.
        model_version : str, optional
            Specific model string (e.g. "gpt-4o", "gemini-1.5-pro").
        """
        if not api_key:
            raise ValueError("api_key must not be empty.")
        self._api_key = api_key
        self.model_version = model_version
 
    # Identity — must be defined as class-level attributes by subclasses

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable assistant name, e.g. 'Claude', 'ChatGPT'."""
 
    @property
    @abstractmethod
    def provider(self) -> str:
        """Company behind the assistant, e.g. 'Anthropic', 'OpenAI'."""
 
    # Core capabilities — must be implemented by every subclass
 
    @abstractmethod
    def generate_code(
        self,
        prompt: str,
        language: str = "python",
        context: Optional[str] = None,
    ) -> dict:
        """
        Generate code from a natural-language prompt.
 
        Returns a response dict matching the format documented in the class
        docstring.
        """
 
    @abstractmethod
    def handle_error(self, raw_error: Exception | dict) -> dict:
        """
        Translate a provider-specific error into the standardised error dict
        documented in the class docstring.
        """
 
    # Shared helpers available to all subclasses

 
    def _base_response(self, language: str, code: str, explanation: str = "",
                       tokens_used: Optional[int] = None,
                       latency_ms: Optional[float] = None) -> dict:
        """Build a populated response dict."""
        return {
            "assistant":   self.name,
            "language":    language,
            "code":        code,
            "explanation": explanation,
            "tokens_used": tokens_used,
            "latency_ms":  latency_ms,
            "timestamp":   datetime.utcnow().isoformat() + "Z",
        }
 
    def _base_error(self, error_type: str, message: str,
                    retryable: bool = False) -> dict:
        """Build a populated error dict."""
        return {
            "assistant":  self.name,
            "error_type": error_type,
            "message":    message,
            "retryable":  retryable,
            "timestamp":  datetime.utcnow().isoformat() + "Z",
        }
 
    def __repr__(self) -> str:
        model = f" ({self.model_version})" if self.model_version else ""
        return f"<{self.__class__.__name__}{model}>"