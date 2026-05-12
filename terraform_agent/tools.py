import subprocess
import glob
import os
import logging
import time
from pathlib import Path
from functools import wraps
from langchain_ollama import ChatOllama
from langchain_core.tools import tool

from .config import Config
from .prompts import PromptManager
from .knowledge_base import KnowledgeBase
from .model_router import ModelRouter

logger = logging.getLogger(__name__)

# Global instances for tools
_config: Config | None = None
_prompts: PromptManager | None = None
_knowledge_base: KnowledgeBase | None = None
_review_model: ChatOllama | None = None
_model_router: ModelRouter | None = None


def init_tools(config: Config, prompts: PromptManager, knowledge_base: KnowledgeBase, model_router: ModelRouter | None = None) -> None:
    """Initialize global instances needed by tools.

    Args:
        config: Configuration object
        prompts: PromptManager instance
        knowledge_base: KnowledgeBase instance
        model_router: Optional ModelRouter for flexible LLM backend selection
    """
    global _config, _prompts, _knowledge_base, _review_model, _model_router
    logger.info("Initializing tools with config, prompts, and knowledge base")
    _config = config
    _prompts = prompts
    _knowledge_base = knowledge_base
    _model_router = model_router
    _review_model = ChatOllama(model=config.REVIEW_MODEL_NAME)
    logger.info(f"Tools initialized - Review model: {config.REVIEW_MODEL_NAME}")
    if model_router:
        logger.info(f"Model router enabled - Ollama tasks: {config.USE_OLLAMA_FOR}")


def _validate_terraform_path(path: str) -> Path:
    """Validate that a path is within the work directory and safe to use.

    Args:
        path: Path to validate

    Returns:
        Resolved Path object

    Raises:
        ValueError: If path is outside work directory or invalid
    """
    if _config is None:
        raise RuntimeError("Tools not initialized - call init_tools() first")

    try:
        resolved = Path(path).resolve()
        work_dir = _config.WORK_DIR.resolve()

        if not resolved.is_relative_to(work_dir):
            raise ValueError(f"Path outside work directory: {path}")

        return resolved
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Invalid path: {path} - {e}")


def validate_work_dir_path(func):
    """Decorator to validate that path parameter is within work directory.

    Applies _validate_terraform_path to the first argument (path).
    Returns error string if validation fails.
    """
    @wraps(func)
    def wrapper(path: str) -> str:
        try:
            validated_path = _validate_terraform_path(path)
        except ValueError as e:
            logger.error(f"Path validation failed in {func.__name__}: {e}")
            return f"❌ ERROR: {e}"
        return func(str(validated_path))
    return wrapper


def _check_dev_environment(path: str) -> str | None:
    """Check if path is in dev environment.

    Args:
        path: Path to check

    Returns:
        Error message if not dev environment, None otherwise
    """
    if path.endswith("/dev") or "/dev/" in path:
        return None

    environment = "prod" if path.endswith("/prod") or "/prod/" in path else "unknown"
    logger.warning(f"Terraform command blocked: path is in {environment} environment")
    return f"❌ ERROR: Terraform commands only allowed in dev environment (path: {path})"


def _check_terraform_initialized(path: str) -> str | None:
    """Check if terraform has been initialized in the given path.

    Args:
        path: Path to check

    Returns:
        Error message if not initialized, None otherwise
    """
    terraform_dir = Path(path) / ".terraform"
    if not terraform_dir.exists():
        logger.warning(f"Terraform not initialized at {path} (.terraform/ missing)")
        return "❌ ERROR: Run terraform_init first (.terraform/ directory missing)"
    return None


def _log_to_file(level: str, context: str, message: str, path: str) -> None:
    """Log message to terraform_logs.error file.

    Args:
        level: Log level (INIT_ERROR, SYNTAX_ERROR, PLAN_ERROR, REVIEW_CRITICAL, etc.)
        context: Context of the log (terraform_init, terraform_validate, etc.)
        message: Log message
        path: Working directory path where log file should be created
    """
    from datetime import datetime

    try:
        log_file = Path(path) / "terraform_logs.error"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] [{context}] {message}\n"

        # Create or append to log file
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

        logger.debug(f"Logged to {log_file}: {log_entry.strip()}")
    except (OSError, IOError) as e:
        logger.warning(f"Failed to write to terraform_logs.error: {e}")


def _parse_terraform_error(error_output: str) -> str:
    """Parse terraform error with LLM to extract actionable information.

    Uses model_router to parse with Ollama or Claude depending on configuration.

    Args:
        error_output: Raw error output from terraform command

    Returns:
        Parsed error summary with root cause and suggested fix
    """
    if _model_router is None:
        # No model router - return raw error
        return error_output

    try:
        logger.info("Parsing terraform error with LLM")

        prompt = f"""Parse this Terraform error and provide:
1. Error type (syntax/provider/resource/validation)
2. Root cause (one sentence)
3. Suggested fix (one sentence)

Keep response concise and actionable.

Error:
{error_output[:1000]}

Parsed error:"""

        parsed = _model_router.invoke("parsing", prompt)
        logger.info(f"Error parsing completed: {len(error_output)} → {len(parsed)} chars")
        return parsed

    except Exception as e:
        logger.warning(f"Error parsing failed: {e}, returning raw error")
        return error_output




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
    result = _knowledge_base.search(query)
    preview = result[:50].replace('\n', ' ') if result else '(empty)'
    logger.info(f"Knowledge base search completed - preview: {preview}...")

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
@validate_work_dir_path
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

    # Check environment
    if error := _check_dev_environment(path):
        return error

    logger.info(f"Running terraform init at {path}")

    try:
        logger.debug("Executing: terraform init")
        start_time = time.time()

        init_result = subprocess.run(
            ["rtk", "terraform", "init"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=60,
        )

        elapsed = time.time() - start_time
        init_output = init_result.stdout or init_result.stderr

        if init_result.returncode != 0:
            logger.error(f"terraform init failed (exit code {init_result.returncode}) after {elapsed:.2f}s")
            logger.error(f"Init output: {init_output[:500]}")  # Show first 500 chars in ERROR log
            _log_to_file("INIT_ERROR", "terraform_init", f"Failed with exit code {init_result.returncode}: {init_output[:200]}", path)
            return f"❌ ERROR: terraform init failed:\n{init_output}"

        logger.info(f"terraform init successful in {elapsed:.2f}s")
        _log_to_file("INIT_SUCCESS", "terraform_init", f"Initialization successful in {elapsed:.2f}s", path)
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
@validate_work_dir_path
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

    # Check environment
    if error := _check_dev_environment(path):
        return error

    # Check terraform is initialized
    if error := _check_terraform_initialized(path):
        return error

    logger.info(f"Running terraform validate at {path}")

    try:
        logger.debug("Executing: terraform validate")
        start_time = time.time()

        validate_result = subprocess.run(
            ["rtk", "terraform", "validate"],
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

            # Parse error with LLM for better insights
            parsed_error = _parse_terraform_error(validate_output)

            _log_to_file("SYNTAX_ERROR", "terraform_validate", f"Validation failed: {validate_output[:200]}", path)
            return f"❌ ERROR: terraform validate failed. Fix the code syntax errors and re-run terraform_validate.\n\n{parsed_error}"

        logger.info(f"terraform validate successful in {elapsed:.2f}s")
        _log_to_file("VALIDATE_SUCCESS", "terraform_validate", f"Validation successful in {elapsed:.2f}s", path)
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
@validate_work_dir_path
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

    # Check environment
    if error := _check_dev_environment(path):
        return error

    # Check terraform is initialized
    if error := _check_terraform_initialized(path):
        return error

    logger.info(f"Running terraform plan at {path}")

    try:
        logger.debug("Executing: terraform plan -no-color")
        start_time = time.time()

        plan_result = subprocess.run(
            ["rtk", "terraform", "plan", "-no-color"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=60,
        )

        elapsed = time.time() - start_time
        plan_output = plan_result.stdout or plan_result.stderr

        if plan_result.returncode != 0:
            logger.error(f"terraform plan failed (exit code {plan_result.returncode}) after {elapsed:.2f}s")
            logger.debug(f"Plan output: {plan_output[:500]}...")
            _log_to_file("PLAN_ERROR", "terraform_plan", f"Plan failed: {plan_output[:200]}", path)
            return f"❌ ERROR: terraform plan failed:\n{plan_output}"

        logger.info(f"terraform plan successful in {elapsed:.2f}s")
        _log_to_file("PLAN_SUCCESS", "terraform_plan", f"Plan successful in {elapsed:.2f}s", path)
        max_chars = _config.MAX_PLAN_OUTPUT_CHARS
        truncated = plan_output[:max_chars] + "\n...[truncated]" if len(plan_output) > max_chars else plan_output
        return f"✅ terraform plan successful\n\n{truncated}"

    except FileNotFoundError:
        logger.error("terraform is not installed or not accessible in PATH")
        return "❌ ERROR: terraform is not installed or not accessible in PATH"
    except subprocess.TimeoutExpired:
        logger.error("terraform plan exceeded timeout (60s)")
        return "❌ ERROR: terraform plan exceeded timeout"
    except (OSError, ValueError) as e:
        logger.error(f"Exception during plan: {str(e)}")
        return f"❌ ERROR: during plan: {str(e)}"


def _retrieve_best_practices() -> str:
    """Retrieve Terraform best practices from knowledge base.

    Returns:
        String containing relevant best practices for code review
    """
    if _knowledge_base is None:
        logger.error("Knowledge base not initialized")
        return ""

    logger.debug("Retrieving best practices from knowledge base")
    best_practices = _knowledge_base.search(
        "Terraform best practices security standards naming conventions modules"
    )
    preview = best_practices[:50].replace('\n', ' ') if best_practices else '(empty)'
    logger.debug(f"Retrieved {len(best_practices)} characters - preview: {preview}...")
    return best_practices


def _read_terraform_files(path: str) -> tuple[str, int]:
    """Read all Terraform files in directory.

    Args:
        path: Directory path to scan for .tf files

    Returns:
        Tuple of (concatenated file contents, number of files)
    """
    logger.debug("Reading Terraform files")
    tf_files = sorted(glob.glob(path + "/**/*.tf", recursive=True))
    logger.info(f"Found {len(tf_files)} Terraform files")

    if not tf_files:
        logger.warning(f"No .tf files found in {path}")
        return "", 0

    code_content = ""
    for file_path in tf_files:
        with open(file_path, "r") as tf_file:
            file_name = os.path.basename(file_path)
            file_content = tf_file.read()
            code_content += f"\n\n--- {file_name} ---\n{file_content}"
            logger.debug(f"Loaded {file_name}: {len(file_content)} bytes")

    logger.info(f"Total code to review: {len(code_content)} bytes across {len(tf_files)} files")
    return code_content, len(tf_files)


def _execute_code_review(best_practices: str, code_content: str, path: str) -> str:
    """Execute code review with LLM model.

    Args:
        best_practices: Best practices documentation from knowledge base
        code_content: Terraform code to review
        path: Root folder path for context

    Returns:
        Review response from model
    """
    if _prompts is None or _review_model is None or _config is None:
        logger.error("Review components not initialized")
        return ""

    logger.debug("Preparing review prompt")
    review_prompt = _prompts.review.format(
        best_practices=best_practices,
        code_content=code_content,
        root_folder=path
    )
    logger.debug(f"Review prompt prepared: {len(review_prompt)} bytes")

    logger.info(f"Running code review with {_config.REVIEW_MODEL_NAME}")
    review_start = time.time()
    review_response = str(_review_model.invoke(review_prompt).content)
    review_elapsed = time.time() - review_start
    logger.info(f"Code review completed in {review_elapsed:.2f}s, response length: {len(review_response)} bytes")

    return review_response


def _format_review_result(review_response: str, num_files: int, path: str) -> str:
    """Parse review response and format final result.

    Args:
        review_response: Raw response from review model
        num_files: Number of files reviewed
        path: Root folder path

    Returns:
        Formatted review summary
    """
    if _prompts is None:
        logger.error("Prompts not initialized")
        return review_response

    logger.debug("Parsing review response")

    # Check if issues were found
    if "CRITIQUE" in review_response or "MAJEUR" in review_response:
        logger.warning("Issues found during review (CRITIQUE or MAJEUR)")
        if "### Code Corrigé" in review_response:
            logger.info("Fixed code found in response")
            return _prompts.response_with_fixes.format(
                num_files=num_files,
                review_response=review_response,
                root_folder=path,
            )
        else:
            logger.info("No fixed code provided, returning review response")
            return review_response
    else:
        logger.info("Code is compliant with best practices")
        return _prompts.response_compliant.format(
            num_files=num_files,
            review_response=review_response,
        )


@tool
@validate_work_dir_path
def review_and_fix_code(path: str) -> str:
    """Performs comprehensive code review against best practices.

    Process:
    1. Retrieves Terraform best practices from knowledge base
    2. Reads and analyzes generated Terraform code
    3. Executes LLM-based code review
    4. Formats results with compliance status and fixes

    Args:
        path: folder where the code is generated

    Returns:
        Formatted review summary with findings and fixes
    """
    logger.debug(f"review_and_fix_code called with path: {path}")

    if _knowledge_base is None or _prompts is None or _review_model is None:
        logger.error("Tools not fully initialized")
        return "⚠️ Error: Tools not initialized"

    try:
        logger.info(f"Starting code review at {path}")
        start_time = time.time()

        # Step 1: Retrieve best practices
        best_practices = _retrieve_best_practices()

        # Step 2: Read Terraform files
        code_content, num_files = _read_terraform_files(path)
        if num_files == 0:
            return "⚠️ Review: No .tf files found in directory"

        # Step 3-4: Execute review with model
        review_response = _execute_code_review(best_practices, code_content, path)

        # Step 5: Format result
        result_summary = _format_review_result(review_response, num_files, path)

        # Log review results
        if "CRITIQUE" in review_response or "MAJEUR" in review_response:
            if "CRITIQUE" in review_response:
                _log_to_file("REVIEW_CRITICAL", "review_and_fix_code", "Critical issues found in code review", path)
            if "MAJEUR" in review_response:
                _log_to_file("REVIEW_MAJOR", "review_and_fix_code", "Major issues found in code review", path)
        else:
            _log_to_file("REVIEW_SUCCESS", "review_and_fix_code", f"Code review passed - {num_files} files analyzed", path)

        elapsed = time.time() - start_time
        logger.info(f"Code review and fix completed in {elapsed:.2f}s")

        return result_summary

    except FileNotFoundError as e:
        logger.error(f"File not found during review: {e}")
        return f"⚠️ Error: File not found: {e}"
    except (OSError, ValueError) as e:
        logger.error(f"Exception during review: {str(e)}")
        return f"⚠️ Error during review: {str(e)}"


