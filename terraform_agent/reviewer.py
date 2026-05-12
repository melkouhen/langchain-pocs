"""Code review module for Terraform configurations.

This module provides functionality to review Terraform code against best practices,
identify security issues, compliance problems, and code quality concerns.
"""

import logging
import time
import glob
from pathlib import Path
from langchain_ollama import ChatOllama

from .config import Config
from .knowledge_base import KnowledgeBase
from .prompts import PromptManager

logger = logging.getLogger(__name__)


class TerraformReviewer:
    """Performs comprehensive code reviews of Terraform configurations.

    Uses a knowledge base of best practices and an LLM model to analyze
    Terraform code for security, compliance, and quality issues.

    Attributes:
        config: Configuration object with paths and model settings
        knowledge_base: ChromaDB knowledge base with best practices
        prompts: Prompt manager for loading review templates
        review_model: LLM model for code analysis
    """

    def __init__(
        self,
        config: Config,
        knowledge_base: KnowledgeBase,
        prompts: PromptManager
    ) -> None:
        """Initialize the Terraform reviewer.

        Args:
            config: Configuration object
            knowledge_base: Knowledge base instance
            prompts: Prompt manager instance
        """
        self.config = config
        self.knowledge_base = knowledge_base
        self.prompts = prompts
        self.review_model = ChatOllama(model=config.REVIEW_MODEL_NAME)

        logger.info(f"TerraformReviewer initialized with model: {config.REVIEW_MODEL_NAME}")

    def retrieve_best_practices(
        self,
        query: str = "terraform best practices",
        top_k: int = 5
    ) -> str:
        """Retrieve relevant best practices from knowledge base.

        Args:
            query: Search query for best practices
            top_k: Number of documents to retrieve

        Returns:
            String containing best practices documentation
        """
        logger.info(f"Searching knowledge base with query: '{query}'")

        best_practices = self.knowledge_base.search(
            query,
            k=top_k,
            summarize=False
        )

        if not best_practices:
            logger.warning("No documents found in knowledge base")
            return "No best practices found."

        logger.info(f"Retrieved {len(best_practices)} chars of best practices")
        return best_practices

    def read_terraform_files(self, path: str) -> tuple[str, int]:
        """Read all .tf files from a directory.

        Args:
            path: Directory path containing Terraform files

        Returns:
            Tuple of (concatenated_content, file_count)
        """
        tf_files = glob.glob(f"{path}/*.tf")

        if not tf_files:
            logger.warning(f"No .tf files found in {path}")
            return "", 0

        logger.info(f"Found {len(tf_files)} .tf files")

        code_content = ""
        for tf_file in tf_files:
            logger.debug(f"Reading {tf_file}")
            with open(tf_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
                code_content += f"\n\n# File: {Path(tf_file).name}\n{file_content}"

        # Limit content size for model
        if len(code_content) > self.config.MAX_TF_CONTENT_CHARS:
            logger.warning(
                f"Code content truncated from {len(code_content)} "
                f"to {self.config.MAX_TF_CONTENT_CHARS} chars"
            )
            code_content = (
                code_content[:self.config.MAX_TF_CONTENT_CHARS] +
                "\n\n[... content truncated ...]"
            )

        logger.info(
            f"Total code to review: {len(code_content)} bytes "
            f"across {len(tf_files)} files"
        )

        return code_content, len(tf_files)

    def execute_review(
        self,
        best_practices: str,
        code_content: str,
        path: str
    ) -> str:
        """Execute code review using LLM model.

        Args:
            best_practices: Best practices documentation
            code_content: Terraform code to analyze
            path: Directory path for context

        Returns:
            Review response from model
        """
        logger.info("Preparing review prompt")

        review_prompt = self.prompts.review.format(
            best_practices=best_practices,
            code_content=code_content,
            root_folder=path
        )

        logger.info(f"Running code review with {self.config.REVIEW_MODEL_NAME}")
        logger.info(f"Prompt size: {len(review_prompt)} chars")

        start_time = time.time()
        review_response = str(self.review_model.invoke(review_prompt).content)
        elapsed = time.time() - start_time

        logger.info(f"Code review completed in {elapsed:.2f}s")
        logger.info(f"Response length: {len(review_response)} chars")

        return review_response

    def format_result(
        self,
        review_response: str,
        num_files: int,
        path: str
    ) -> str:
        """Format the review result with appropriate template.

        Args:
            review_response: Raw response from review model
            num_files: Number of files analyzed
            path: Directory path

        Returns:
            Formatted review summary
        """
        has_issues = "CRITIQUE" in review_response or "MAJEUR" in review_response

        if has_issues:
            logger.warning("Issues found during review")

            if "### Code Corrigé" in review_response:
                logger.info("Fixed code provided in response")
                return self.prompts.response_with_fixes.format(
                    num_files=num_files,
                    review_response=review_response,
                    root_folder=path
                )
            else:
                return review_response
        else:
            logger.info("Code is compliant with best practices")
            return self.prompts.response_compliant.format(
                num_files=num_files,
                review_response=review_response
            )

    def review(
        self,
        path: str,
        query: str = "terraform best practices",
        verbose: bool = True
    ) -> str:
        """Perform complete code review of Terraform configuration.

        This is the main entry point for code reviews. It orchestrates:
        1. Retrieving best practices from knowledge base
        2. Reading Terraform files
        3. Executing LLM-based review
        4. Formatting results

        Args:
            path: Directory containing Terraform files
            query: Query for best practices search
            verbose: Show detailed progress logs

        Returns:
            Formatted review report
        """
        start_time = time.time()

        if verbose:
            logger.info("=" * 80)
            logger.info(f"Starting code review for: {path}")
            logger.info("=" * 80)

        # Step 1: Retrieve best practices
        if verbose:
            print("📚 Step 1: Retrieving best practices...")

        best_practices = self.retrieve_best_practices(query=query)

        if verbose:
            print(f"  ✓ Retrieved {len(best_practices)} chars\n")

        # Step 2: Read Terraform files
        if verbose:
            print("📖 Step 2: Reading Terraform files...")

        code_content, num_files = self.read_terraform_files(path)

        if num_files == 0:
            return "⚠️  No .tf files found in directory"

        if verbose:
            print(f"  ✓ Read {num_files} files ({len(code_content)} chars)\n")

        # Step 3: Execute review
        if verbose:
            print("🤖 Step 3: Executing code review...")

        review_response = self.execute_review(best_practices, code_content, path)

        if verbose:
            print("  ✓ Review completed\n")

        # Step 4: Format result
        if verbose:
            print("📝 Step 4: Formatting results...")

        result = self.format_result(review_response, num_files, path)

        elapsed = time.time() - start_time

        if verbose:
            logger.info("=" * 80)
            logger.info(f"Code review completed in {elapsed:.2f}s")
            logger.info("=" * 80)

        return result

    def quick_scan(self, path: str) -> dict:
        """Perform quick scan to get code statistics without full review.

        Args:
            path: Directory containing Terraform files

        Returns:
            Dictionary with code statistics
        """
        tf_files = list(Path(path).glob("*.tf"))

        resources = []
        variables = []
        outputs = []

        for tf_file in tf_files:
            content = tf_file.read_text()

            resources.extend([
                line for line in content.split('\n')
                if line.strip().startswith('resource ')
            ])
            variables.extend([
                line for line in content.split('\n')
                if line.strip().startswith('variable ')
            ])
            outputs.extend([
                line for line in content.split('\n')
                if line.strip().startswith('output ')
            ])

        return {
            'path': path,
            'files': len(tf_files),
            'resources': len(resources),
            'variables': len(variables),
            'outputs': len(outputs),
            'total_lines': sum(len(f.read_text().split('\n')) for f in tf_files)
        }
