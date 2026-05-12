"""Model router for flexible LLM backend selection.

Provides a unified interface to switch between Claude (Anthropic) and Ollama models
based on configuration, with automatic fallback handling.
"""

import logging
from typing import Literal
from langchain_core.messages import BaseMessage
from langchain_ollama import ChatOllama
from langchain_anthropic import ChatAnthropic

logger = logging.getLogger(__name__)


ModelType = Literal["summarization", "parsing", "review"]


class ModelRouter:
    """Routes LLM calls to appropriate backend (Claude or Ollama).

    Provides unified interface with automatic fallback from Ollama to Claude
    if local model is unavailable.

    Attributes:
        use_ollama_for: Set of task types to route to Ollama
        ollama_models: Mapping of task types to Ollama model names
        claude_model: Claude model name for fallback
        _ollama_available: Cached availability status
    """

    def __init__(
        self,
        use_ollama_for: set[ModelType],
        ollama_models: dict[ModelType, str],
        claude_model: str,
    ):
        """Initialize model router with configuration.

        Args:
            use_ollama_for: Set of task types to use Ollama for (e.g. {"summarization", "parsing"})
            ollama_models: Mapping of task types to Ollama model names
            claude_model: Claude model name for fallback
        """
        self.use_ollama_for = use_ollama_for
        self.ollama_models = ollama_models
        self.claude_model = claude_model
        self._ollama_available: bool | None = None

    def _check_ollama_available(self) -> bool:
        """Check if Ollama is available and responsive.

        Returns:
            True if Ollama is available, False otherwise
        """
        if self._ollama_available is not None:
            return self._ollama_available

        try:
            # Try to create a client and list models
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            self._ollama_available = response.status_code == 200
            logger.info(f"Ollama availability check: {self._ollama_available}")
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            self._ollama_available = False

        return self._ollama_available

    def get_model(self, task_type: ModelType, fallback: bool = True) -> ChatOllama | ChatAnthropic:
        """Get appropriate model for task type.

        Args:
            task_type: Type of task (summarization, parsing, review)
            fallback: Whether to fallback to Claude if Ollama unavailable

        Returns:
            Configured LLM instance (ChatOllama or ChatAnthropic)
        """
        # Check if we should use Ollama for this task
        should_use_ollama = task_type in self.use_ollama_for

        # If Ollama requested, check availability
        if should_use_ollama:
            if self._check_ollama_available():
                model_name = self.ollama_models.get(task_type)
                if model_name:
                    logger.info(f"Using Ollama model '{model_name}' for {task_type}")
                    return ChatOllama(model=model_name, temperature=0)

            if not fallback:
                raise RuntimeError(f"Ollama not available for {task_type} and fallback disabled")

            logger.warning(f"Ollama unavailable for {task_type}, falling back to Claude")

        # Use Claude (either by choice or as fallback)
        logger.info(f"Using Claude model '{self.claude_model}' for {task_type}")
        return ChatAnthropic(model=self.claude_model, temperature=0)

    def invoke(self, task_type: ModelType, prompt: str | list[BaseMessage]) -> str:
        """Invoke model with prompt and return response.

        Args:
            task_type: Type of task to perform
            prompt: Prompt string or list of messages

        Returns:
            Model response content as string
        """
        model = self.get_model(task_type)
        response = model.invoke(prompt)
        return str(response.content)
