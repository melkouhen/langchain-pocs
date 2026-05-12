from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TestCase:
    id: str
    name: str
    prompt: str


def _load_prompt(filename: str) -> str:
    """Load prompt content from user_prompts directory."""
    prompt_path = Path(__file__).parent.parent / "user_prompts" / filename
    return prompt_path.read_text(encoding="utf-8")


TEST_CASES: list[TestCase] = [
    TestCase(
        id="tc01",
        name="Simple GCS Bucket",
        prompt=_load_prompt("1-bucket.md"),
    ), 
    TestCase(
        id="tc02",
        name="Simple Service Cloud Run",
        prompt=_load_prompt("2-cloudrun.md"),
    )
]
