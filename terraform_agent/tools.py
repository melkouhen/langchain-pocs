import subprocess
import glob
import os
import logging
import time
from langchain_ollama import ChatOllama
from langchain_core.tools import tool

from .config import Config
from .prompts import PromptManager
from .knowledge_base import KnowledgeBase

# Configure logger
logger = logging.getLogger(__name__)

# Global instances for tools
_config: Config | None = None
_prompts: PromptManager | None = None
_knowledge_base: KnowledgeBase | None = None
_review_model: ChatOllama | None = None


def init_tools(config: Config, prompts: PromptManager, knowledge_base: KnowledgeBase) -> None:
    """Initialize global instances needed by tools.

    Args:
        config: Configuration object
        prompts: PromptManager instance
        knowledge_base: KnowledgeBase instance
    """
    global _config, _prompts, _knowledge_base, _review_model
    logger.info("Initializing tools with config, prompts, and knowledge base")
    _config = config
    _prompts = prompts
    _knowledge_base = knowledge_base
    _review_model = ChatOllama(model=config.REVIEW_MODEL_NAME)
    logger.info(f"Tools initialized - Review model: {config.REVIEW_MODEL_NAME}")


# ============================================================================
# EXTRACTED TOOLS (decorated at module level)
# ============================================================================

@tool
def search_knowledge_base(query: str) -> str:
    """Search the knowledge base for Terraform best practices.

    Args:
        query: Search query for finding relevant best practices

    Returns:
        Relevant best practices from knowledge base
    """
    logger.debug(f"search_knowledge_base called with query: {query}")

    if _knowledge_base is None:
        logger.error("Knowledge base not initialized")
        return "⚠️ Error: Knowledge base not initialized"

    logger.info(f"Searching knowledge base for: {query}")
    start_time = time.time()
    result = _knowledge_base.search(query)
    elapsed = time.time() - start_time
    logger.info(f"Knowledge base search completed in {elapsed:.2f}s")

    return result


@tool
def load_module_spec(file_path: str) -> str:
    """Load the specification of a Terraform module from a file.

    Args:
        file_path: Path to the module specification file (e.g., docs/terraform-module.md)

    Returns:
        Complete module specification with variables, outputs, and usage examples
    """
    logger.debug(f"load_module_spec called with file_path: {file_path}")

    if _config is None:
        logger.error("Config not initialized")
        return "⚠️ Error: Config not initialized"

    try:
        full_path = _config.PROJECT_ROOT / file_path
        logger.info(f"Loading module spec from: {full_path}")

        if not full_path.exists():
            logger.warning(f"Module spec file not found: {full_path}")
            return f"⚠️ Error: Module spec file not found: {full_path}"

        content = full_path.read_text()
        logger.info(f"Module spec loaded successfully ({len(content)} bytes)")
        return content

    except (OSError, ValueError) as e:
        logger.error(f"Error reading module spec: {str(e)}")
        return f"⚠️ Error reading module spec: {str(e)}"


@tool
def terraform_init(path: str) -> str:
    """Initialize a Terraform working directory.

    Runs 'terraform init' to download providers and prepare the working directory.

    Args:
        path: folder where the code is generated
    """

    logger.debug(f"terraform_init called with path: {path}")

    if _config is None:
        logger.error("Config not initialized")
        return "⚠️ Error: Tools not initialized"

    environment = "dev" if path.endswith("/dev") or "/dev/" in path else "prod"
    logger.info(f"Running terraform init in {environment} environment at {path}")

    if environment != "dev":
        logger.warning(f"Skipping terraform init: running in {environment} environment (only dev allowed)")
        return f"❌ ERROR: Terraform init skipped: running in {environment} environment (only dev environment executes terraform commands)"

    try:
        logger.debug("Executing: terraform init")
        start_time = time.time()

        init_result = subprocess.run(
            ["terraform", "init"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=60,
        )

        elapsed = time.time() - start_time
        init_output = init_result.stdout or init_result.stderr

        if init_result.returncode != 0:
            logger.error(f"terraform init failed (exit code {init_result.returncode}) after {elapsed:.2f}s")
            logger.debug(f"Init output: {init_output}")
            return f"❌ ERROR: terraform init failed:\n{init_output}"

        logger.info(f"terraform init successful in {elapsed:.2f}s")
        return f"✅ terraform init successful"

    except FileNotFoundError:
        logger.error("terraform is not installed or not accessible in PATH")
        return "❌ ERROR: terraform is not installed or not accessible in PATH"
    except subprocess.TimeoutExpired:
        logger.error("terraform init exceeded timeout (60s)")
        return "❌ ERROR: terraform init exceeded timeout"
    except (OSError, ValueError) as e:
        logger.error(f"Exception during init: {str(e)}")
        return f"❌ ERROR: during init: {str(e)}"


@tool
def terraform_validate(path: str) -> str:
    """Validate Terraform configuration files.

    Runs 'terraform validate' to check syntax and configuration validity.

    Args:
        path: folder where the code is generated
    """
    logger.debug(f"terraform_validate called with path: {path}")

    if _prompts is None or _review_model is None or _config is None:
        logger.error("Tools not fully initialized")
        return "⚠️ Error: Tools not initialized"

    environment = "dev" if path.endswith("/dev") or "/dev/" in path else "prod"
    logger.info(f"Running terraform validate in {environment} environment at {path}")

    if environment != "dev":
        logger.warning(f"Skipping terraform validate: running in {environment} environment (only dev allowed)")
        return f"❌ ERROR: Terraform validate skipped: running in {environment} environment (only dev environment executes terraform commands)"

    try:
        logger.debug("Executing: terraform validate")
        start_time = time.time()

        validate_result = subprocess.run(
            ["terraform", "validate"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        elapsed = time.time() - start_time
        validate_output = validate_result.stdout or validate_result.stderr

        if validate_result.returncode != 0:
            logger.error(f"terraform validate failed (exit code {validate_result.returncode}) after {elapsed:.2f}s")
            logger.debug(f"Validation output: {validate_output}")
            return f"❌ ERROR: terraform validate failed. Fix the code and re-run terraform_init + terraform_validate.\n\n{validate_output}"

        logger.info(f"terraform validate successful in {elapsed:.2f}s")
        return f"✅ terraform validate successful"

    except FileNotFoundError:
        logger.error("terraform is not installed or not accessible in PATH")
        return "❌ ERROR: terraform is not installed or not accessible in PATH"
    except subprocess.TimeoutExpired:
        logger.error("terraform validate exceeded timeout (30s)")
        return "❌ ERROR: terraform validate exceeded timeout"
    except (OSError, ValueError) as e:
        logger.error(f"Exception during validate: {str(e)}")
        return f"❌ ERROR: during validate: {str(e)}"


@tool
def terraform_plan(path: str) -> str:
    """Generate a Terraform execution plan.

    Runs 'terraform plan' to preview infrastructure changes.

    Args:
        path: folder where the code is generated
    """
    logger.debug(f"terraform_plan called with path: {path}")

    if _config is None:
        logger.error("Config not initialized")
        return "⚠️ Error: Tools not initialized"

    environment = "dev" if path.endswith("/dev") or "/dev/" in path else "prod"
    logger.info(f"Running terraform plan in {environment} environment at {path}")

    if environment != "dev":
        logger.warning(f"Skipping terraform plan: running in {environment} environment (only dev allowed)")
        return f"❌ ERROR: Terraform plan skipped: running in {environment} environment (only dev environment executes terraform commands)"

    try:
        logger.debug("Executing: terraform plan -no-color")
        start_time = time.time()

        plan_result = subprocess.run(
            ["terraform", "plan", "-no-color"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=60,
        )

        elapsed = time.time() - start_time
        plan_output = plan_result.stdout or plan_result.stderr

        if plan_result.returncode != 0:
            logger.error(f"terraform plan failed (exit code {plan_result.returncode}) after {elapsed:.2f}s")
            logger.debug(f"Plan output: {plan_output[:500]}...")  # Log first 500 chars
            return f"❌ ERROR: terraform plan failed:\n{plan_output}"

        logger.info(f"terraform plan successful in {elapsed:.2f}s")
        return f"✅ terraform plan successful"

    except FileNotFoundError:
        logger.error("terraform is not installed or not accessible in PATH")
        return "❌ ERROR: terraform is not installed or not accessible in PATH"
    except subprocess.TimeoutExpired:
        logger.error("terraform plan exceeded timeout (60s)")
        return "❌ ERROR: terraform plan exceeded timeout"
    except (OSError, ValueError) as e:
        logger.error(f"Exception during plan: {str(e)}")
        return f"❌ ERROR: during plan: {str(e)}"


@tool
def review_and_fix_code(path: str) -> str:
    """Performs comprehensive code review against best practices.

    Process:
    1. Retrieves Terraform best practices from knowledge base
    2. Analyzes generated code for compliance
    3. Identifies major issues and applies fixes if necessary

    Args:
        path: folder where the code is generated
    """
    logger.debug(f"review_and_fix_code called with path: {path}")

    if _knowledge_base is None or _prompts is None or _review_model is None:
        logger.error("Tools not fully initialized")
        return "⚠️ Error: Tools not initialized"

    try:
        logger.info(f"Starting code review at {path}")
        start_time = time.time()

        # Step 1: Retrieve best practices from knowledge base
        logger.debug("Step 1: Retrieving best practices from knowledge base")
        best_practices = _knowledge_base.search(
            "Terraform best practices security standards naming conventions modules"
        )
        logger.debug(f"Retrieved {len(best_practices)} characters of best practices")

        # Step 2: Read all generated Terraform files
        logger.debug("Step 2: Reading Terraform files")
        tf_files = sorted(glob.glob(path + "/**/*.tf", recursive=True))
        logger.info(f"Found {len(tf_files)} Terraform files")

        if not tf_files:
            logger.warning(f"No .tf files found in {path}")
            return "⚠️ Review: No .tf files found in directory"

        code_content = ""
        for file_path in tf_files:
            with open(file_path, "r") as f:
                file_name = os.path.basename(file_path)
                file_content = f.read()
                code_content += f"\n\n--- {file_name} ---\n{file_content}"
                logger.debug(f"Loaded {file_name}: {len(file_content)} bytes")

        logger.info(f"Total code to review: {len(code_content)} bytes across {len(tf_files)} files")

        # Step 3: Use template from markdown file
        logger.debug("Step 3: Preparing review prompt")
        review_prompt = _prompts.review.format(
            best_practices=best_practices, code_content=code_content
        )
        logger.debug(f"Review prompt prepared: {len(review_prompt)} bytes")

        # Step 4: Execute review with model
        logger.info(f"Step 4: Running code review with {_config.REVIEW_MODEL_NAME if _config else 'unknown model'}")
        review_start = time.time()
        review_response = str(_review_model.invoke(review_prompt).content)
        review_elapsed = time.time() - review_start
        logger.info(f"Code review completed in {review_elapsed:.2f}s, response length: {len(review_response)} bytes")

        # Step 5: Parse response and apply fixes if needed
        logger.debug("Step 5: Parsing review response")
        if "CRITIQUE" in review_response or "MAJEUR" in review_response:
            logger.warning("Issues found during review (CRITIQUE or MAJEUR)")
            if "### Code Corrigé" in review_response:
                logger.info("Fixed code found in response")
                result_summary = _prompts.response_with_fixes.format(
                    num_files=len(tf_files),
                    review_response=review_response,
                    root_folder=path,
                )
            else:
                logger.info("No fixed code provided, returning review response")
                result_summary = review_response
        else:
            logger.info("Code is compliant with best practices")
            result_summary = _prompts.response_compliant.format(
                num_files=len(tf_files),
                review_response=review_response,
            )

        elapsed = time.time() - start_time
        logger.info(f"Code review and fix completed in {elapsed:.2f}s")

        return result_summary

    except FileNotFoundError as e:
        logger.error(f"File not found during review: {e}")
        return f"⚠️ Error: File not found: {e}"
    except (OSError, ValueError) as e:
        logger.error(f"Exception during review: {str(e)}")
        return f"⚠️ Error during review: {str(e)}"


