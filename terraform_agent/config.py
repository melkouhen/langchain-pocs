from pathlib import Path


class Config:
    """Centralized configuration for the Terraform agent system.

    Manages all paths (project root, work directory, docs, prompts) and model
    configuration (embedding model, review model, main LLM model).

    Attributes:
        PROJECT_ROOT: Base directory of the project
        WORK_DIR: Directory for agent output and generated files
        DOCS_DIR: Directory containing documentation and best practices
        PROMPTS_DIR: Directory containing prompt templates
        EMBEDDING_MODEL: Name of the embedding model for ChromaDB
        REVIEW_MODEL_NAME: Name of the LLM model used for validation/review
        AGENT_MODEL: Name of the main Claude model for the agent
    """

    PROJECT_ROOT: Path
    WORK_DIR: Path
    DOCS_DIR: Path
    PROMPTS_DIR: Path
    EMBEDDING_MODEL: str
    REVIEW_MODEL_NAME: str
    AGENT_MODEL: str

    def __init__(self, base_dir: Path | None = None) -> None:
        """Initialize configuration with project paths and model names.

        Args:
            base_dir: Base directory for the project. Defaults to current working directory.
        """
        if base_dir is None:
            base_dir = Path.cwd()

        self.PROJECT_ROOT = base_dir
        self.WORK_DIR = self.PROJECT_ROOT / "work"
        self.DOCS_DIR = self.PROJECT_ROOT / "docs"
        self.PROMPTS_DIR = self.PROJECT_ROOT / "prompts"

        self.EMBEDDING_MODEL = "nomic-embed-text"
        self.REVIEW_MODEL_NAME = "qwen2.5-coder:7b-instruct"
        self.AGENT_MODEL = "claude-haiku-4-5-20251001"
