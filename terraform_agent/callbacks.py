"""LangChain callbacks for structured Terraform workflow tracking.

This module provides callback handlers that track the execution phases
of the Terraform generation workflow in a structured, non-intrusive way.
"""

import logging
import time
from typing import Any, Dict, List, Optional
from datetime import datetime

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

logger = logging.getLogger(__name__)


class TerraformPhaseCallback(BaseCallbackHandler):
    """Callback handler that tracks Terraform generation phases.

    This callback monitors tool calls and LLM invocations to detect
    and report on the different phases of Terraform code generation:

    - PLANNING: Knowledge base search
    - GENERATION: Code generation via LLM
    - VALIDATION: terraform init/validate/plan
    - REVIEW: Code review and compliance checks

    The callback maintains structured execution logs and can generate
    detailed reports without parsing text or making assumptions.
    """

    def __init__(self, verbose: bool = True):
        """Initialize the callback handler.

        Args:
            verbose: Whether to print phase transitions to stdout
        """
        super().__init__()
        self.verbose = verbose
        self.execution_log: List[Dict[str, Any]] = []
        self.current_phase: Optional[str] = None
        self.phase_start_time: Optional[float] = None
        self.tool_results: Dict[str, Any] = {}
        self.session_start_time = time.time()

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        **kwargs: Any,
    ) -> None:
        """Called when a tool starts executing.

        Args:
            serialized: Tool metadata
            input_str: Tool input
            **kwargs: Additional arguments
        """
        tool_name = serialized.get("name", "unknown")

        # Detect phase based on tool
        phase = self._detect_phase(tool_name)

        if phase and phase != self.current_phase:
            self._end_current_phase()
            self._start_new_phase(phase, tool_name)

        if self.verbose:
            print(f"   → Calling {tool_name}")

        logger.debug(f"Tool started: {tool_name}")

    def on_tool_end(
        self,
        output: str,
        **kwargs: Any,
    ) -> None:
        """Called when a tool finishes executing.

        Args:
            output: Tool output (can be str or ToolMessage)
            **kwargs: Additional arguments
        """
        tool_name = kwargs.get("name", "unknown")

        # Convert output to string if it's a ToolMessage
        output_str = str(output) if not isinstance(output, str) else output

        # Store tool result for reporting
        self.tool_results[tool_name] = {
            "output": output_str,
            "success": "✅" in output_str or "successful" in output_str.lower(),
            "timestamp": datetime.now().isoformat(),
        }

        if self.verbose:
            status = "✅" if self.tool_results[tool_name]["success"] else "❌"
            print(f"   {status} {tool_name} completed")

        logger.debug(f"Tool ended: {tool_name}")

    def on_tool_error(
        self,
        error: Exception,
        **kwargs: Any,
    ) -> None:
        """Called when a tool encounters an error.

        Args:
            error: The exception that occurred
            **kwargs: Additional arguments
        """
        tool_name = kwargs.get("name", "unknown")

        self.tool_results[tool_name] = {
            "error": str(error),
            "success": False,
            "timestamp": datetime.now().isoformat(),
        }

        if self.verbose:
            print(f"   ❌ {tool_name} failed: {error}")

        logger.error(f"Tool error in {tool_name}: {error}")

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        **kwargs: Any,
    ) -> None:
        """Called when LLM starts generating.

        Args:
            serialized: LLM metadata
            prompts: Input prompts
            **kwargs: Additional arguments
        """
        # If we haven't started a phase yet, this is generation
        if not self.current_phase:
            self._start_new_phase("GENERATION", "llm")

        logger.debug("LLM generation started")

    def on_llm_end(
        self,
        response: LLMResult,
        **kwargs: Any,
    ) -> None:
        """Called when LLM finishes generating.

        Args:
            response: LLM response
            **kwargs: Additional arguments
        """
        logger.debug("LLM generation completed")

    def _detect_phase(self, tool_name: str) -> Optional[str]:
        """Detect workflow phase based on tool name.

        Args:
            tool_name: Name of the tool being called

        Returns:
            Phase name or None if tool doesn't indicate a phase change
        """
        phase_map = {
            "search_knowledge_base": "PLANNING",
            "load_module_spec": "PLANNING",
            "terraform_init": "VALIDATION",
            "terraform_validate": "VALIDATION",
            "terraform_plan": "VALIDATION",
            "review_and_fix_code": "CODE_REVIEW",
        }
        return phase_map.get(tool_name)

    def _start_new_phase(self, phase: str, trigger: str) -> None:
        """Start a new phase.

        Args:
            phase: Phase name
            trigger: What triggered the phase (tool name or 'llm')
        """
        self.current_phase = phase
        self.phase_start_time = time.time()

        if self.verbose:
            emoji_map = {
                "PLANNING": "📋",
                "GENERATION": "🔧",
                "VALIDATION": "✅",
                "CODE_REVIEW": "🔍",
            }
            emoji = emoji_map.get(phase, "📌")
            print(f"\n{'=' * 80}")
            print(f"{emoji} PHASE: {phase}")
            print(f"{'=' * 80}")

        logger.info(f"Phase started: {phase} (triggered by {trigger})")

    def _end_current_phase(self) -> None:
        """End the current phase and log it."""
        if self.current_phase and self.phase_start_time:
            duration = time.time() - self.phase_start_time

            self.execution_log.append({
                "phase": self.current_phase,
                "duration_seconds": round(duration, 2),
                "timestamp": datetime.now().isoformat(),
            })

            if self.verbose:
                print(f"\n   Phase completed in {duration:.2f}s")

            logger.info(f"Phase ended: {self.current_phase} ({duration:.2f}s)")

    def finalize(self) -> None:
        """Finalize the execution and end the current phase."""
        self._end_current_phase()

        total_duration = time.time() - self.session_start_time

        if self.verbose:
            self._print_summary(total_duration)

    def _print_summary(self, total_duration: float) -> None:
        """Print execution summary.

        Args:
            total_duration: Total execution time in seconds
        """
        print(f"\n{'=' * 80}")
        print(f"📊 EXECUTION SUMMARY")
        print(f"{'=' * 80}")

        print(f"\n{'Phase':<20} {'Duration':<15} {'Status':<10}")
        print("-" * 50)

        for entry in self.execution_log:
            phase = entry["phase"]
            duration = f"{entry['duration_seconds']:.2f}s"
            status = "✅"
            print(f"{phase:<20} {duration:<15} {status:<10}")

        print(f"\n{'Total':<20} {total_duration:.2f}s")

        # Tool execution summary
        print(f"\n🔧 Tool Execution Summary:")
        for tool_name, result in self.tool_results.items():
            status = "✅" if result.get("success") else "❌"
            print(f"   {status} {tool_name}")

        print(f"\n{'=' * 80}")

    def get_report(self) -> Dict[str, Any]:
        """Get structured execution report.

        Returns:
            Dictionary with execution log and tool results
        """
        return {
            "execution_log": self.execution_log,
            "tool_results": self.tool_results,
            "total_duration_seconds": round(time.time() - self.session_start_time, 2),
            "timestamp": datetime.now().isoformat(),
        }


class DetailedTerraformCallback(TerraformPhaseCallback):
    """Extended callback with detailed security and best practices tracking.

    This callback extends the base phase tracking with additional
    checks for security compliance and best practices adherence.
    """

    def __init__(self, verbose: bool = True):
        """Initialize the detailed callback handler.

        Args:
            verbose: Whether to print detailed information
        """
        super().__init__(verbose)
        self.security_checks: Dict[str, bool] = {}
        self.bp_checks: Dict[str, bool] = {}

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Called when a tool finishes - extracts security/BP info.

        Args:
            output: Tool output
            **kwargs: Additional arguments
        """
        super().on_tool_end(output, **kwargs)

        tool_name = kwargs.get("name", "unknown")

        # Extract security checks from review output
        if tool_name == "review_and_fix_code":
            self._extract_checks(output)

    def _extract_checks(self, output: str) -> None:
        """Extract security and best practice checks from review output.

        Args:
            output: Review tool output (can be str or ToolMessage)
        """
        # Convert output to string if it's a ToolMessage
        output_str = str(output) if not isinstance(output, str) else output

        # Security checks
        self.security_checks = {
            "UBLA": "uniform_bucket_level_access" in output_str,
            "Public Access Prevention": "public_access_prevention" in output_str,
            "Encryption": "encryption" in output_str or "kms" in output_str.lower(),
            "Versioning": "versioning" in output_str,
            "Lifecycle Policies": "lifecycle" in output_str,
        }

        # Best practices checks
        self.bp_checks = {
            "Module Structure": "module" in output_str.lower(),
            "Variables Defined": "variable" in output_str or "var." in output_str,
            "Outputs Defined": "output" in output_str,
            "Documentation": "description" in output_str or "README" in output_str,
        }

    def _print_summary(self, total_duration: float) -> None:
        """Print execution summary with security/BP details.

        Args:
            total_duration: Total execution time in seconds
        """
        super()._print_summary(total_duration)

        # Print security checks if available
        if self.security_checks:
            print(f"\n🔒 Security Checks:")
            for check, passed in self.security_checks.items():
                status = "✅" if passed else "❌"
                print(f"   {status} {check}")

            score = sum(self.security_checks.values()) / len(self.security_checks) * 100
            print(f"\n   Security Score: {score:.0f}%")

        # Print best practices checks if available
        if self.bp_checks:
            print(f"\n📐 Best Practices Checks:")
            for check, passed in self.bp_checks.items():
                status = "✅" if passed else "❌"
                print(f"   {status} {check}")

            score = sum(self.bp_checks.values()) / len(self.bp_checks) * 100
            print(f"\n   Best Practices Score: {score:.0f}%")

        print(f"\n{'=' * 80}")

    def get_report(self) -> Dict[str, Any]:
        """Get detailed execution report with security/BP checks.

        Returns:
            Dictionary with execution log, tool results, and checks
        """
        report = super().get_report()
        report["security_checks"] = self.security_checks
        report["bp_checks"] = self.bp_checks

        if self.security_checks:
            report["security_score"] = sum(self.security_checks.values()) / len(self.security_checks) * 100

        if self.bp_checks:
            report["bp_score"] = sum(self.bp_checks.values()) / len(self.bp_checks) * 100

        return report
