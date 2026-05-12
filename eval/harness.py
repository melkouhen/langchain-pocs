"""Evaluation harness for the Terraform code generation agent.

Runs each test case through the agent, evaluates the generated code with an
LLM judge, and writes structured JSON results to eval/results/<timestamp>/.

Usage:
    python -m eval.harness                         # all test cases
    python -m eval.harness --test-id tc01          # single test case
    python -m eval.harness --results-dir /tmp/out  # custom output dir
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
print(f"Project root: {PROJECT_ROOT}")
sys.path.insert(0, str(PROJECT_ROOT))

from terraform_agent.generator import TerraformGenerator
from terraform_agent.config import Config
from terraform_agent.knowledge_base import KnowledgeBase
from terraform_agent.prompts import PromptManager

from .evaluator import EvaluationResult, evaluate
from .test_cases import TEST_CASES, TestCase


def _snapshot_tf_files(src: Path, dest: Path) -> None:
    """Copy only .tf and .terraform.lock.hcl files (skip .terraform/ provider binaries)."""
    for pattern in ("**/*.tf", "**/.terraform.lock.hcl"):
        for src_file in src.glob(pattern):
            rel = src_file.relative_to(src)
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, target)


def _run_test_case(
    test_case: TestCase,
    agent: TerraformGenerator,
    config: Config,
    run_dir: Path,
) -> EvaluationResult:
    print(f"\n{'='*72}")
    print(f"  {test_case.id}  —  {test_case.name}")
    print(f"{'='*72}")

    work_dir = config.WORK_DIR
    print(f"Work dir : {work_dir}")

    # Clear work/ for a clean run
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    agent_success = True
    try:
        agent_output = agent.run(user_prompt=test_case.prompt)
    except Exception as exc:
        agent_output = str(exc)
        agent_success = False
        print(f"  Agent error: {exc}")

    # Evaluate on the live work_dir so terraform validate can use .terraform/
    result = evaluate(
        test_case_id=test_case.id,
        test_case_name=test_case.name,
        task_prompt=test_case.prompt,
        agent_output=agent_output,
        work_dir=work_dir,
        agent_success=agent_success,
    )

    # Save .tf snapshot (no provider binaries) + evaluation report
    snapshot_dir = run_dir / test_case.id
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    _snapshot_tf_files(work_dir, snapshot_dir / "work")
    (snapshot_dir / "evaluation.json").write_text(
        json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
    )

    # Print per-criterion bar chart
    print(f"\n  Score: {result.weighted_score:.2f}/5  [{result.quality_label}]")
    print(f"  TF valid: {'yes' if result.terraform_valid else 'no'} | Files: {len(result.files_found)}")
    for cs in result.criteria_scores:
        filled = round(cs.score)
        bar = "█" * filled + "░" * (5 - filled)
        pct = int(cs.weight * 100)
        print(f"  {bar}  {cs.score:.1f}/5  [{pct:2d}%]  {cs.name}")
    if result.summary:
        print(f"\n  {result.summary}")

    return result


def _print_summary(results: list[EvaluationResult]) -> None:
    print(f"\n{'='*72}")
    print("  SUMMARY")
    print(f"{'='*72}")
    print(f"  {'Name':<35} {'Score':>7}  {'Quality':<15} TF")
    print(f"  {'-'*60}")
    for r in results:
        tf_icon = "✅" if r.terraform_valid else "❌"
        print(
            f"  {r.test_case_name:<35} {r.weighted_score:>6.2f}/5"
            f"  {r.quality_label:<15} {tf_icon}"
        )
    if results:
        avg = sum(r.weighted_score for r in results) / len(results)
        print(f"  {'-'*60}")
        print(f"  {'Average':<35} {avg:>6.2f}/5")
    print()


def main() -> None:
    # Configure logging to display all logs to console
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    load_dotenv()

    parser = argparse.ArgumentParser(description="Terraform Agent Evaluation Harness")
    parser.add_argument("--test-id", help="Run only one test case (e.g. tc01)")
    parser.add_argument(
        "--results-dir",
        default="eval/results",
        help="Base directory for results (default: eval/results)",
    )
    args = parser.parse_args()

    cases = TEST_CASES
    if args.test_id:
        cases = [tc for tc in TEST_CASES if tc.id == args.test_id]
        if not cases:
            available = [tc.id for tc in TEST_CASES]
            print(f"Test case '{args.test_id}' not found. Available: {available}")
            sys.exit(1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = PROJECT_ROOT / args.results_dir / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    # Shared setup — KnowledgeBase init is expensive, do it once
    config = Config(base_dir=PROJECT_ROOT)
    prompts = PromptManager(config)
    kb = KnowledgeBase(config)
    agent = TerraformGenerator(config, prompts, kb)

    results: list[EvaluationResult] = []
    for tc in cases:
        result = _run_test_case(tc, agent, config, run_dir)
        results.append(result)

    _print_summary(results)

    report = {
        "timestamp": timestamp,
        "total_tests": len(results),
        "average_score": round(
            sum(r.weighted_score for r in results) / len(results), 2
        ) if results else 0.0,
        "results": [r.to_dict() for r in results],
    }
    (run_dir / "report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False)
    )
    print(f"Results saved → {run_dir}")


if __name__ == "__main__":
    main()
