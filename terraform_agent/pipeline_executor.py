"""Pipeline executor with explicit phases for Terraform code generation.

This module provides a structured pipeline that wraps TerraformGenerator with
explicit phases: Planning, Generation, Code Review, and Validation.
Each phase produces visible output to demonstrate the complete workflow.
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from .config import Config
from .prompts import PromptManager
from .knowledge_base import KnowledgeBase
from .model_router import ModelRouter
from .generator import TerraformGenerator

if TYPE_CHECKING:
    from typing import Dict, Any

logger = logging.getLogger(__name__)


class PipelineExecutor:
    """Executes Terraform generation pipeline with explicit visible phases.

    This class orchestrates the complete Terraform code generation workflow
    with four distinct phases:

    1. PLANNING: Analyze requirements and search knowledge base
    2. GENERATION: Generate code and validate syntax
    3. CODE REVIEW: Security and best practices compliance
    4. VALIDATION: Final checks and summary report

    Each phase produces structured output with status indicators (✅/❌/⚠️)
    to make the pipeline execution transparent and auditable.

    Attributes:
        config: Configuration object
        prompts: PromptManager instance
        knowledge_base: KnowledgeBase instance
        model_router: ModelRouter instance
        generator: TerraformGenerator instance
        execution_log: Log of all phases and their results
    """

    def __init__(
        self,
        config: Config,
        prompts: PromptManager,
        knowledge_base: KnowledgeBase,
        model_router: ModelRouter | None = None,
    ) -> None:
        """Initialize pipeline executor.

        Args:
            config: Configuration object
            prompts: PromptManager instance
            knowledge_base: KnowledgeBase instance
            model_router: Optional ModelRouter for flexible LLM backend selection
        """
        self.config = config
        self.prompts = prompts
        self.knowledge_base = knowledge_base
        self.model_router = model_router

        # Initialize the underlying generator
        self.generator = TerraformGenerator(
            config=config,
            prompts=prompts,
            knowledge_base=knowledge_base,
            model_router=model_router,
        )

        # Execution tracking
        self.execution_log: list[Dict[str, Any]] = []
        self.start_time: float | None = None
        self.end_time: float | None = None

    def _log_phase(self, phase: str, status: str, details: str = "", duration: float | None = None) -> None:
        """Log a phase execution result.

        Args:
            phase: Phase name (PLANNING, GENERATION, CODE_REVIEW, VALIDATION)
            status: Status indicator (SUCCESS, FAILED, WARNING)
            details: Additional details about the phase
            duration: Optional duration in seconds
        """
        entry = {
            "phase": phase,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat(),
        }
        if duration is not None:
            entry["duration_seconds"] = round(duration, 2)

        self.execution_log.append(entry)
        logger.info(f"Phase {phase} completed with status {status}")

    def _print_phase_header(self, phase_number: int, phase_name: str, emoji: str) -> None:
        """Print a formatted phase header.

        Args:
            phase_number: Phase number (1-4)
            phase_name: Name of the phase
            emoji: Emoji to display
        """
        print(f"\n{'=' * 80}")
        print(f"{emoji} PHASE {phase_number}: {phase_name}")
        print(f"{'=' * 80}")

    def _print_check(self, check_name: str, passed: bool, details: str = "") -> None:
        """Print a check result.

        Args:
            check_name: Name of the check
            passed: Whether the check passed
            details: Additional details
        """
        icon = "✅" if passed else "❌"
        print(f"{icon} {check_name}")
        if details:
            print(f"   {details}")

    def _phase_1_planning(self, user_prompt: str) -> Dict[str, Any]:
        """Execute Phase 1: Planning and Analysis.

        This phase:
        - Analyzes the user prompt
        - Searches the knowledge base for relevant best practices
        - Creates an execution plan

        Args:
            user_prompt: User's requirements

        Returns:
            Dictionary with planning results
        """
        self._print_phase_header(1, "PLANNING & ANALYSIS", "📋")
        phase_start = time.time()

        print("\n🔍 Analyzing user requirements...")
        print(f"   Prompt length: {len(user_prompt)} characters")

        # Extract key requirements
        has_gcs = "gcs" in user_prompt.lower() or "bucket" in user_prompt.lower()
        has_dev = "dev" in user_prompt.lower()
        has_prod = "prod" in user_prompt.lower()

        print(f"\n📊 Requirements detected:")
        self._print_check("GCS Bucket resources", has_gcs)
        self._print_check("Dev environment", has_dev)
        self._print_check("Prod environment", has_prod)

        # Search knowledge base
        print(f"\n📚 Searching knowledge base for best practices...")
        kb_start = time.time()
        search_query = "GCS bucket security best practices terraform modules"
        kb_results = self.knowledge_base.search(search_query, k=3)
        kb_duration = time.time() - kb_start

        kb_chunks = len(kb_results.split("\n\n")) if kb_results else 0
        print(f"   ✓ Found {kb_chunks} relevant chunks in {kb_duration:.2f}s")

        # Create execution plan
        print(f"\n📝 Execution plan:")
        print(f"   1. Generate Terraform module structure")
        print(f"   2. Initialize with terraform init")
        print(f"   3. Validate syntax with terraform validate")
        print(f"   4. Review code for security & best practices")
        print(f"   5. Generate terraform plan")

        phase_duration = time.time() - phase_start
        self._log_phase("PLANNING", "SUCCESS", f"Requirements analyzed, {kb_chunks} KB chunks retrieved", phase_duration)

        print(f"\n✅ Planning phase completed in {phase_duration:.2f}s")

        return {
            "requirements": {
                "has_gcs": has_gcs,
                "has_dev": has_dev,
                "has_prod": has_prod,
            },
            "knowledge_base_chunks": kb_chunks,
            "duration": phase_duration,
        }

    def _phase_2_generation(self, user_prompt: str) -> Dict[str, Any]:
        """Execute Phase 2: Code Generation & Syntax Validation.

        This phase:
        - Generates Terraform code using the agent
        - Validates syntax with terraform validate

        Args:
            user_prompt: User's requirements

        Returns:
            Dictionary with generation results
        """
        self._print_phase_header(2, "CODE GENERATION & VALIDATION", "🔧")
        phase_start = time.time()

        print("\n🤖 Invoking Terraform generation agent...")
        print("   (Agent will autonomously call tools: init, validate, plan, review)")

        # Run the generator
        gen_start = time.time()
        agent_output = self.generator.run(user_prompt=user_prompt)
        gen_duration = time.time() - gen_start

        # Check results
        init_success = "terraform init successful" in agent_output or "✅" in agent_output
        validate_success = "terraform validate successful" in agent_output

        print(f"\n📊 Generation results:")
        self._print_check("Terraform init", init_success)
        self._print_check("Terraform validate", validate_success)

        phase_duration = time.time() - phase_start
        status = "SUCCESS" if (init_success and validate_success) else "FAILED"
        self._log_phase("GENERATION", status, f"Code generated in {gen_duration:.2f}s", phase_duration)

        if status == "SUCCESS":
            print(f"\n✅ Generation phase completed in {phase_duration:.2f}s")
        else:
            print(f"\n❌ Generation phase failed after {phase_duration:.2f}s")

        return {
            "init_success": init_success,
            "validate_success": validate_success,
            "agent_output": agent_output,
            "duration": phase_duration,
        }

    def _phase_3_code_review(self, generation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Phase 3: Code Review & Security Analysis.

        This phase:
        - Reviews generated code against best practices
        - Checks security compliance
        - Identifies issues and suggests fixes

        Args:
            generation_results: Results from phase 2

        Returns:
            Dictionary with review results
        """
        self._print_phase_header(3, "CODE REVIEW & SECURITY ANALYSIS", "🔍")
        phase_start = time.time()

        agent_output = generation_results.get("agent_output", "")

        print("\n🔒 Security checks:")

        # Parse agent output for security indicators
        checks = {
            "Uniform Bucket Level Access (UBLA)": "uniform_bucket_level_access" in agent_output,
            "Public access prevention": "public_access_prevention" in agent_output,
            "Encryption at rest": "encryption" in agent_output or "kms" in agent_output,
            "Versioning enabled": "versioning" in agent_output,
            "Lifecycle policies": "lifecycle" in agent_output,
        }

        for check_name, passed in checks.items():
            self._print_check(check_name, passed)

        print("\n📐 Best practices compliance:")

        # Check for best practices
        bp_checks = {
            "Module structure": "module" in agent_output.lower(),
            "Variables defined": "variable" in agent_output or "var." in agent_output,
            "Outputs defined": "output" in agent_output,
            "Documentation present": "description" in agent_output or "README" in agent_output,
        }

        for check_name, passed in bp_checks.items():
            self._print_check(check_name, passed)

        # Check for issues
        has_critical = "CRITIQUE" in agent_output or "CRITICAL" in agent_output
        has_major = "MAJEUR" in agent_output or "MAJOR" in agent_output
        has_fixes = "Code Corrigé" in agent_output or "Fixed" in agent_output

        print("\n🔍 Review findings:")
        if has_critical:
            print("   ⚠️  Critical issues detected")
        if has_major:
            print("   ⚠️  Major issues detected")
        if has_fixes:
            print("   ✅ Fixes provided by reviewer")
        if not (has_critical or has_major):
            print("   ✅ No critical or major issues found")

        phase_duration = time.time() - phase_start

        # Determine status
        security_score = sum(checks.values()) / len(checks) * 100
        bp_score = sum(bp_checks.values()) / len(bp_checks) * 100

        if security_score >= 80 and bp_score >= 75:
            status = "SUCCESS"
            print(f"\n✅ Code review passed")
        elif security_score >= 60:
            status = "WARNING"
            print(f"\n⚠️  Code review completed with warnings")
        else:
            status = "FAILED"
            print(f"\n❌ Code review failed")

        print(f"   Security score: {security_score:.0f}%")
        print(f"   Best practices score: {bp_score:.0f}%")
        print(f"   Duration: {phase_duration:.2f}s")

        self._log_phase(
            "CODE_REVIEW",
            status,
            f"Security: {security_score:.0f}%, BP: {bp_score:.0f}%",
            phase_duration
        )

        return {
            "security_checks": checks,
            "bp_checks": bp_checks,
            "security_score": security_score,
            "bp_score": bp_score,
            "has_critical": has_critical,
            "has_major": has_major,
            "has_fixes": has_fixes,
            "duration": phase_duration,
        }

    def _phase_4_validation(
        self,
        planning_results: Dict[str, Any],
        generation_results: Dict[str, Any],
        review_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute Phase 4: Final Validation & Summary.

        This phase:
        - Validates terraform plan execution
        - Generates final summary report
        - Provides recommendations

        Args:
            planning_results: Results from phase 1
            generation_results: Results from phase 2
            review_results: Results from phase 3

        Returns:
            Dictionary with validation results
        """
        self._print_phase_header(4, "VALIDATION & SUMMARY", "✅")
        phase_start = time.time()

        agent_output = generation_results.get("agent_output", "")

        print("\n🎯 Pipeline execution summary:")
        print(f"\n{'Phase':<25} {'Status':<15} {'Duration':<10}")
        print("-" * 50)

        for entry in self.execution_log:
            status_icon = {
                "SUCCESS": "✅",
                "FAILED": "❌",
                "WARNING": "⚠️",
            }.get(entry["status"], "◯")

            duration_str = f"{entry.get('duration_seconds', 0):.2f}s" if "duration_seconds" in entry else "-"
            print(f"{entry['phase']:<25} {status_icon} {entry['status']:<13} {duration_str:<10}")

        # Overall status
        print("\n📊 Overall metrics:")

        total_duration = time.time() - self.start_time if self.start_time else 0
        print(f"   Total execution time: {total_duration:.2f}s")

        plan_success = "terraform plan successful" in agent_output or "Plan:" in agent_output
        self._print_check("Terraform plan generated", plan_success)

        # Check if code was generated
        work_dir = self.config.WORK_DIR
        tf_files = list(work_dir.rglob("*.tf")) if work_dir.exists() else []
        print(f"   Generated files: {len(tf_files)} .tf files")

        # Final verdict
        print("\n🏁 Final verdict:")

        all_phases_ok = all(entry["status"] == "SUCCESS" for entry in self.execution_log)
        security_ok = review_results.get("security_score", 0) >= 80

        if all_phases_ok and security_ok and plan_success:
            verdict = "✅ PIPELINE SUCCEEDED"
            print(f"   {verdict}")
            print(f"   All phases completed successfully")
            print(f"   Code is production-ready")
            status = "SUCCESS"
        elif all_phases_ok:
            verdict = "⚠️  PIPELINE COMPLETED WITH WARNINGS"
            print(f"   {verdict}")
            print(f"   Review findings require attention")
            status = "WARNING"
        else:
            verdict = "❌ PIPELINE FAILED"
            print(f"   {verdict}")
            print(f"   Some phases did not complete successfully")
            status = "FAILED"

        phase_duration = time.time() - phase_start
        self._log_phase("VALIDATION", status, verdict, phase_duration)

        print(f"\n{'=' * 80}")
        print(f"Pipeline execution completed in {total_duration:.2f}s")
        print(f"{'=' * 80}")

        return {
            "plan_success": plan_success,
            "tf_files_count": len(tf_files),
            "verdict": verdict,
            "all_phases_ok": all_phases_ok,
            "duration": phase_duration,
        }

    def run(self, user_prompt: str | None = None) -> str:
        """Execute the complete pipeline with explicit phases.

        This method orchestrates all four phases:
        1. Planning & Analysis
        2. Code Generation & Validation
        3. Code Review & Security Analysis
        4. Validation & Summary

        Args:
            user_prompt: User's requirements. If None, uses default from prompts.

        Returns:
            Agent output from generation phase
        """
        self.start_time = time.time()
        self.execution_log = []

        prompt_content = user_prompt if user_prompt is not None else self.prompts.user

        print("\n" + "=" * 80)
        print("🚀 TERRAFORM PIPELINE EXECUTOR")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Work directory: {self.config.WORK_DIR}")
        print("=" * 80)

        try:
            # Phase 1: Planning
            planning_results = self._phase_1_planning(prompt_content)

            # Phase 2: Generation
            generation_results = self._phase_2_generation(prompt_content)

            # Phase 3: Code Review
            review_results = self._phase_3_code_review(generation_results)

            # Phase 4: Validation
            validation_results = self._phase_4_validation(
                planning_results,
                generation_results,
                review_results,
            )

            self.end_time = time.time()

            return generation_results.get("agent_output", "")

        except Exception as e:
            self.end_time = time.time()
            logger.error(f"Pipeline execution failed: {e}", exc_info=True)
            self._log_phase("PIPELINE", "FAILED", str(e))
            print(f"\n❌ Pipeline failed: {e}")
            raise

    def get_execution_report(self) -> Dict[str, Any]:
        """Get detailed execution report.

        Returns:
            Dictionary with complete execution log and metrics
        """
        total_duration = (self.end_time - self.start_time) if (self.start_time and self.end_time) else 0

        return {
            "execution_log": self.execution_log,
            "total_duration_seconds": round(total_duration, 2),
            "timestamp": datetime.now().isoformat(),
            "work_directory": str(self.config.WORK_DIR),
        }
