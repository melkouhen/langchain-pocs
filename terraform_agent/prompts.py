from .config import Config


class PromptManager:
    """Manages loading and caching of prompt templates from markdown files.

    Loads prompt templates from the prompts directory, caches them in memory
    to avoid repeated disk reads, and provides convenient properties for
    accessing common prompts.

    Attributes:
        config: Configuration object containing paths
        _cache: Internal dictionary caching loaded prompt templates
    """

    config: Config
    _cache: dict[str, str]

    def __init__(self, config: Config) -> None:
        """Initialize the prompt manager with a configuration.

        Args:
            config: Configuration object with path to prompts directory
        """
        self.config = config
        self._cache = {}

    def load(self, filename: str) -> str:
        """Load a prompt template from a markdown file.

        Reads the file from the prompts directory and caches the result.
        Raises FileNotFoundError if the file does not exist.

        Args:
            filename: Name of the prompt file (e.g., 'terraform-system.md')

        Returns:
            Content of the prompt file as a string

        Raises:
            FileNotFoundError: If the prompt file does not exist
        """
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
        """System prompt for configuring the agent's behavior and role.

        Returns:
            System prompt template from terraform-system.md
        """
        return self.load("terraform-system.md")

    @property
    def user(self) -> str:
        """User prompt describing the task for the agent.

        Returns:
            User prompt template from terraform-user.md
        """
        return self.load("terraform-user.md")

    @property
    def validate(self) -> str:
        """Prompt template for terraform validation error analysis and fixes.

        Returns:
            Validation prompt template from terraform-validate.md
        """
        return self.load("terraform-validate.md")

    @property
    def review(self) -> str:
        """Prompt template for comprehensive code review against best practices.

        Returns:
            Review prompt template from terraform-review.md
        """
        return self.load("terraform-review.md")

    @property
    def response_compliant(self) -> str:
        """Response template for code compliant with best practices.

        Returns:
            Compliant response template from review-response-compliant.md
        """
        return self.load("review-response-compliant.md")

    @property
    def response_with_fixes(self) -> str:
        """Response template for code with suggested fixes.

        Returns:
            Response with fixes template from review-response-with-fixes.md
        """
        return self.load("review-response-with-fixes.md")
