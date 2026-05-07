from pathlib import Path


class Config:
    def __init__(self, base_dir: Path | None = None):
        if base_dir is None:
            base_dir = Path.cwd()

        self.PROJECT_ROOT = base_dir
        self.WORK_DIR = self.PROJECT_ROOT / "work"
        self.DOCS_DIR = self.PROJECT_ROOT / "docs"
        self.PROMPTS_DIR = self.PROJECT_ROOT / "prompts"

        self.EMBEDDING_MODEL = "nomic-embed-text"
        self.REVIEW_MODEL_NAME = "qwen2.5-coder:7b-instruct"
        self.AGENT_MODEL = "claude-haiku-4-5-20251001"
