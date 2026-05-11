import subprocess
import glob
import os
from langchain_ollama import ChatOllama
from langchain_core.tools import tool

from .config import Config
from .prompts import PromptManager
from .knowledge_base import KnowledgeBase

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
    _config = config
    _prompts = prompts
    _knowledge_base = knowledge_base
    _review_model = ChatOllama(model=config.REVIEW_MODEL_NAME)


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
    if _knowledge_base is None:
        return "⚠️ Error: Knowledge base not initialized"

    return _knowledge_base.search(query)


@tool
def load_module_spec(file_path: str) -> str:
    """Load the specification of a Terraform module from a file.

    Args:
        file_path: Path to the module specification file (e.g., docs/terraform-module.md)

    Returns:
        Complete module specification with variables, outputs, and usage examples
    """
    if _config is None:
        return "⚠️ Error: Config not initialized"

    try:
        full_path = _config.PROJECT_ROOT / file_path
        if not full_path.exists():
            return f"⚠️ Error: Module spec file not found: {full_path}"

        return full_path.read_text()
    except (OSError, ValueError) as e:
        return f"⚠️ Error reading module spec: {str(e)}"


@tool
def terraform_init(path: str) -> str:
    """Initialize a Terraform working directory.

    Runs 'terraform init' to download providers and prepare the working directory.

    Args:
        path: folder where the code is generated
    """
    if _config is None:
        return "⚠️ Error: Tools not initialized"

    environment = "dev" if path.endswith("/dev") or "/dev/" in path else "prod"
    if environment != "dev":
        return f"❌ ERROR: Terraform init skipped: running in {environment} environment (only dev environment executes terraform commands)"

    try:
        init_result = subprocess.run(
            ["terraform", "init"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=60,
        )

        init_output = init_result.stdout or init_result.stderr

        if init_result.returncode != 0:
            return f"❌ ERROR: terraform init failed:\n{init_output}"

        return f"✅ terraform init successful"

    except FileNotFoundError:
        return "❌ ERROR: terraform is not installed or not accessible in PATH"
    except subprocess.TimeoutExpired:
        return "❌ ERROR: terraform init exceeded timeout"
    except (OSError, ValueError) as e:
        return f"❌ ERROR: during init: {str(e)}"


@tool
def terraform_validate(path: str) -> str:
    """Validate Terraform configuration files.

    Runs 'terraform validate' to check syntax and configuration validity.

    Args:
        path: folder where the code is generated
    """
    if _prompts is None or _review_model is None or _config is None:
        return "⚠️ Error: Tools not initialized"

    environment = "dev" if path.endswith("/dev") or "/dev/" in path else "prod"
    if environment != "dev":
        return f"❌ ERROR: Terraform validate skipped: running in {environment} environment (only dev environment executes terraform commands)"

    try:
        validate_result = subprocess.run(
            ["terraform", "validate"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        validate_output = validate_result.stdout or validate_result.stderr

        if validate_result.returncode != 0:
            return f"❌ ERROR: terraform validate failed. Fix the code and re-run terraform_init + terraform_validate.\n\n{validate_output}"

        return f"✅ terraform validate successful"

    except FileNotFoundError:
        return "❌ ERROR: terraform is not installed or not accessible in PATH"
    except subprocess.TimeoutExpired:
        return "❌ ERROR: terraform validate exceeded timeout"
    except (OSError, ValueError) as e:
        return f"❌ ERROR: during validate: {str(e)}"


@tool
def terraform_plan(path: str) -> str:
    """Generate a Terraform execution plan.

    Runs 'terraform plan' to preview infrastructure changes.

    Args:
        path: folder where the code is generated
    """
    if _config is None:
        return "⚠️ Error: Tools not initialized"

    environment = "dev" if path.endswith("/dev") or "/dev/" in path else "prod"
    if environment != "dev":
        return f"❌ ERROR: Terraform plan skipped: running in {environment} environment (only dev environment executes terraform commands)"

    try:
        plan_result = subprocess.run(
            ["terraform", "plan", "-no-color"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=60,
        )

        plan_output = plan_result.stdout or plan_result.stderr

        if plan_result.returncode != 0:
            return f"❌ ERROR: terraform plan failed:\n{plan_output}"

        return f"✅ terraform plan successful"

    except FileNotFoundError:
        return "❌ ERROR: terraform is not installed or not accessible in PATH"
    except subprocess.TimeoutExpired:
        return "❌ ERROR: terraform plan exceeded timeout"
    except (OSError, ValueError) as e:
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
    if _knowledge_base is None or _prompts is None or _review_model is None:
        return "⚠️ Error: Tools not initialized"

    try:
        # Step 1: Retrieve best practices from knowledge base
        best_practices = _knowledge_base.search(
            "Terraform best practices security standards naming conventions modules"
        )

        # Step 2: Read all generated Terraform files
        tf_files = sorted(glob.glob(path + "/**/*.tf", recursive=True))

        if not tf_files:
            return "⚠️ Review: No .tf files found in directory"

        code_content = ""
        for file_path in tf_files:
            with open(file_path, "r") as f:
                file_name = os.path.basename(file_path)
                code_content += f"\n\n--- {file_name} ---\n{f.read()}"

        # Step 3: Use template from markdown file
        review_prompt = _prompts.review.format(
            best_practices=best_practices, code_content=code_content
        )

        # Step 4: Execute review with model
        review_response = str(_review_model.invoke(review_prompt).content)

        # Step 5: Parse response and apply fixes if needed
        if "CRITIQUE" in review_response or "MAJEUR" in review_response:
            if "### Code Corrigé" in review_response:
                result_summary = _prompts.response_with_fixes.format(
                    num_files=len(tf_files),
                    review_response=review_response,
                    root_folder=path,
                )
            else:
                result_summary = review_response
        else:
            result_summary = _prompts.response_compliant.format(
                num_files=len(tf_files),
                review_response=review_response,
            )

        return result_summary

    except FileNotFoundError as e:
        return f"⚠️ Error: File not found: {e}"
    except (OSError, ValueError) as e:
        return f"⚠️ Error during review: {str(e)}"


