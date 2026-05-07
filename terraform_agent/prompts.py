from .config import Config


class PromptManager:
    def __init__(self, config: Config):
        self.config = config
        self._cache = {}

    def load(self, filename: str) -> str:
        if filename in self._cache:
            return self._cache[filename]

        filepath = self.config.PROMPTS_DIR / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Prompt file not found: {filepath}")

        content = filepath.read_text()
        self._cache[filename] = content
        return content

    @property
    def system(self) -> str:
        return self.load("terraform-system.md")

    @property
    def user(self) -> str:
        return self.load("terraform-user.md")

    @property
    def validate(self) -> str:
        return self.load("terraform-validate.md")

    @property
    def review(self) -> str:
        return self.load("terraform-review.md")

    @property
    def response_compliant(self) -> str:
        return self.load("review-response-compliant.md")

    @property
    def response_with_fixes(self) -> str:
        return self.load("review-response-with-fixes.md")
