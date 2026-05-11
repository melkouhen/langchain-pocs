"""LLM-based evaluator for the Terraform generation agent.

Scores each run against 5 weighted criteria using Claude as judge,
returning a structured EvaluationResult with per-criterion scores and commentary.
"""

from __future__ import annotations

import glob
import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

EVAL_MODEL = "claude-haiku-4-5-20251001"

# (key, display name, weight)
CRITERIA: list[tuple[str, str, float]] = [
    ("pipeline_respect",     "Respect du Pipeline",       0.30),
    ("code_quality",         "Qualité du Code Terraform", 0.25),
    ("terraform_validation", "Validation Terraform",      0.20),
    ("code_review",          "Revue de Code",             0.15),
    ("documentation",        "Documentation",             0.10),
]

_SYSTEM = (
    "You are an expert evaluator for a Terraform code generation agent. "
    "Evaluate objectively. Return only the JSON asked — no prose, no markdown fences."
)

_PROMPT = """\
## Task given to the agent
{task}

## Agent final response (first 3 000 chars)
{agent_output}

## Generated Terraform files
{tf_content}

## terraform validate result
{validation_result}

---

Score the agent output on these 5 criteria (0–5, decimals allowed):

1. **pipeline_respect** (weight 30%) — Did the agent search the knowledge base, produce a plan, generate code, run terraform_validate, and run review_and_fix_code? Full pipeline = 5; each missing step costs ~1 point.
2. **code_quality** (weight 25%) — Proper file split (main.tf / variables.tf / outputs.tf / providers.tf), documented variables with descriptions, modularity, KISS.
3. **terraform_validation** (weight 20%) — Does terraform validate pass cleanly? Were errors corrected before the final answer? No .tf files = 0.
4. **code_review** (weight 15%) — CRITICAL / MAJOR / MINOR classification present, critical issues fixed, major issues addressed.
5. **documentation** (weight 10%) — Comments explain the non-obvious only (not boilerplate). Decisions are justified. Not over-commented.

Return exactly this JSON object (no other text):
{{
  "scores": {{
    "pipeline_respect":     {{"score": <0-5>, "observations": "<one sentence>"}},
    "code_quality":         {{"score": <0-5>, "observations": "<one sentence>"}},
    "terraform_validation": {{"score": <0-5>, "observations": "<one sentence>"}},
    "code_review":          {{"score": <0-5>, "observations": "<one sentence>"}},
    "documentation":        {{"score": <0-5>, "observations": "<one sentence>"}}
  }},
  "strengths":    ["<strength 1>", "<strength 2>"],
  "improvements": ["<improvement 1>", "<improvement 2>"],
  "summary": "<one sentence overall assessment>"
}}
"""


@dataclass
class CriteriaScore:
    key: str
    name: str
    weight: float
    score: float
    observations: str


@dataclass
class EvaluationResult:
    test_case_id: str
    test_case_name: str
    timestamp: str
    agent_success: bool
    terraform_valid: bool
    files_found: list[str]
    criteria_scores: list[CriteriaScore]
    weighted_score: float
    quality_label: str
    strengths: list[str]
    improvements: list[str]
    summary: str

    def to_dict(self) -> dict:
        return asdict(self)


def _quality_label(score: float) -> str:
    if score >= 4.5:
        return "EXCELLENT"
    if score >= 3.5:
        return "BON"
    if score >= 2.5:
        return "ACCEPTABLE"
    if score >= 1.5:
        return "A AMELIORER"
    return "INSUFFISANT"


def _collect_tf_files(work_dir: Path) -> list[str]:
    return [
        str(Path(f).relative_to(work_dir))
        for f in sorted(glob.glob(str(work_dir / "**" / "*.tf"), recursive=True))
    ]


def _read_tf_content(work_dir: Path, max_chars: int = 8000) -> str:
    parts: list[str] = []
    total = 0
    for tf_file in sorted(glob.glob(str(work_dir / "**" / "*.tf"), recursive=True)):
        rel = str(Path(tf_file).relative_to(work_dir))
        content = Path(tf_file).read_text()
        chunk = f"--- {rel} ---\n{content}"
        if total + len(chunk) > max_chars:
            parts.append(f"--- {rel} --- [truncated — content limit reached]")
            break
        parts.append(chunk)
        total += len(chunk)
    return "\n\n".join(parts) if parts else "(no .tf files found)"


def _run_terraform_validate(work_dir: Path) -> tuple[bool, str]:
    """Try terraform validate in the dev env directory (needs .terraform/ to exist)."""
    dev_path = work_dir / "envs" / "dev"
    if not dev_path.exists():
        candidates = list(work_dir.rglob("*.tf"))
        if not candidates:
            return False, "No .tf files found in work directory"
        dev_path = candidates[0].parent

    if not (dev_path / ".terraform").exists():
        return False, "terraform init not yet run (.terraform/ missing) — skipping validate"

    try:
        result = subprocess.run(
            ["terraform", "validate"],
            cwd=str(dev_path),
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = (result.stdout or result.stderr).strip()
        return result.returncode == 0, output
    except FileNotFoundError:
        return False, "terraform binary not found in PATH"
    except subprocess.TimeoutExpired:
        return False, "terraform validate timed out (>30 s)"


def evaluate(
    test_case_id: str,
    test_case_name: str,
    task_prompt: str,
    agent_output: str,
    work_dir: Path,
    agent_success: bool,
) -> EvaluationResult:
    timestamp = datetime.now().isoformat()
    files_found = _collect_tf_files(work_dir)
    tf_content = _read_tf_content(work_dir)
    tf_valid, validation_output = _run_terraform_validate(work_dir)

    validation_result = (
        f"PASSED\n{validation_output}" if tf_valid else f"FAILED\n{validation_output}"
    )

    model = ChatAnthropic(model=EVAL_MODEL, temperature=0)
    prompt = _PROMPT.format(
        task=task_prompt,
        agent_output=agent_output[:3000],
        tf_content=tf_content,
        validation_result=validation_result,
    )

    response = model.invoke(
        [
            SystemMessage(content=_SYSTEM),
            HumanMessage(content=prompt),
        ]
    )
    raw = str(response.content).strip()

    start = raw.find("{")
    end = raw.rfind("}") + 1
    data: dict = json.loads(raw[start:end])

    criteria_scores: list[CriteriaScore] = []
    weighted_score = 0.0
    names = {key: name for key, name, _ in CRITERIA}

    for key, _, weight in CRITERIA:
        entry = data["scores"].get(key, {})
        score = float(entry.get("score", 0))
        criteria_scores.append(
            CriteriaScore(
                key=key,
                name=names[key],
                weight=weight,
                score=score,
                observations=entry.get("observations", ""),
            )
        )
        weighted_score += score * weight

    return EvaluationResult(
        test_case_id=test_case_id,
        test_case_name=test_case_name,
        timestamp=timestamp,
        agent_success=agent_success,
        terraform_valid=tf_valid,
        files_found=files_found,
        criteria_scores=criteria_scores,
        weighted_score=round(weighted_score, 2),
        quality_label=_quality_label(weighted_score),
        strengths=data.get("strengths", []),
        improvements=data.get("improvements", []),
        summary=data.get("summary", ""),
    )
