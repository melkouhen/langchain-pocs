from pathlib import Path
import os


class Config:
    """Centralized configuration for the Terraform agent system.

    Manages all paths (project root, work directory, docs, prompts) and model
    configuration (embedding model, review model, main LLM model).

    Attributes:
        PROJECT_ROOT: Base directory of the project
        WORK_DIR: Directory for agent output and generated files
        RULES_DIR: Directory containing rule documentation and best practices
        PROMPTS_DIR: Directory containing prompt templates
        EMBEDDING_MODEL: Name of the embedding model for ChromaDB
        REVIEW_MODEL_NAME: Name of the LLM model used for validation/review
        AGENT_MODEL: Name of the main Claude model for the agent
        ENVIRONMENT: Execution environment ("dev", "prod", etc.)
        CHUNK_SIZE: Size of text chunks for vectorstore
        CHUNK_OVERLAP: Overlap between chunks to preserve context
        MAX_PLAN_OUTPUT_CHARS: Maximum characters for terraform plan output
        MAX_TF_CONTENT_CHARS: Maximum characters for .tf files in evaluation
    """

    PROJECT_ROOT: Path
    WORK_DIR: Path
    RULES_DIR: Path
    PROMPTS_DIR: Path
    EMBEDDING_MODEL: str
    REVIEW_MODEL_NAME: str
    AGENT_MODEL: str
    ENVIRONMENT: str
    PHOENIX_ENDPOINT: str
    PHOENIX_PROJECT_NAME: str
    PHOENIX_ENABLED: bool

    # Content processing constants
    CHUNK_SIZE: int
    CHUNK_OVERLAP: int
    MAX_PLAN_OUTPUT_CHARS: int
    MAX_TF_CONTENT_CHARS: int

    def __init__(self, base_dir: Path | None = None, environment: str = "dev") -> None:
        """Initialize configuration with project paths and model names.

        Args:
            base_dir: Base directory for the project. Defaults to current working directory.
            environment: Execution environment (default: "dev")
        """
        if base_dir is None:
            base_dir = Path.cwd()

        self.PROJECT_ROOT = base_dir
        self.WORK_DIR = self.PROJECT_ROOT / "work"
        self.RULES_DIR = self.PROJECT_ROOT / "rules"
        self.PROMPTS_DIR = self.PROJECT_ROOT / "prompts"

        self.EMBEDDING_MODEL = "nomic-embed-text"
        self.REVIEW_MODEL_NAME = "qwen2.5-coder:7b-instruct"
        self.AGENT_MODEL = "claude-haiku-4-5-20251001"
        self.ENVIRONMENT = environment

        self.PHOENIX_ENDPOINT = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006/v1/traces")
        self.PHOENIX_PROJECT_NAME = os.getenv("PHOENIX_PROJECT_NAME", "terraform-agent")
        self.PHOENIX_ENABLED = os.getenv("PHOENIX_ENABLED", "true").lower() == "true"

        # Content processing constants (centralized from various modules)
        self.CHUNK_SIZE = 1000  # Vectorstore: balance between context and granularity
        self.CHUNK_OVERLAP = 100  # Vectorstore: preserve context at chunk boundaries
        self.MAX_PLAN_OUTPUT_CHARS = 4000  # ~1000 tokens - prevent Claude context overflow in responses
        self.MAX_TF_CONTENT_CHARS = 8000  # ~2000 tokens - limit for qwen2.5-coder review model context
