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
def validate_and_fix_code(path: str) -> str:
    """Executes terraform init, validate and plan on generated code (dev environment only).

    Args:
        path: folder where the code is generated
    """
    if _prompts is None or _review_model is None or _config is None:
        return "⚠️ Error: Tools not initialized"

    if _config.ENVIRONMENT != "dev":
        return f"⚠️ Terraform validation skipped: running in {_config.ENVIRONMENT} environment (only dev environment executes terraform init, validate and plan)"

    try:
        # Step 1: Run terraform init
        init_result = subprocess.run(
            ["terraform", "init"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=60,
        )

        init_output = init_result.stdout or init_result.stderr

        if init_result.returncode != 0:
            return f"❌ Error during terraform init:\n{init_output}"

        # Step 2: Run terraform validate
        validate_result = subprocess.run(
            ["terraform", "validate"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        validate_output = validate_result.stdout or validate_result.stderr

        if validate_result.returncode != 0:
            error_message = validate_output

            prompt = _prompts.validate.format(
                error_message=error_message, root_folder=path
            )

            correction = _review_model.invoke(prompt).content
            return f"❌ Errors detected:\n\n📋 terraform validate output:\n{error_message}\n\n💡 Suggested fixes:\n{correction}"

        # Step 3: Run terraform plan
        plan_result = subprocess.run(
            ["terraform", "plan", "-no-color"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=60,
        )

        plan_output = plan_result.stdout or plan_result.stderr

        if plan_result.returncode != 0:
            return f"❌ Error during terraform plan:\n{plan_output}"
        else:
            return f"✅ Terraform validation successful\n\n📋 terraform init output:\n{init_output}\n\n📋 terraform validate output:\n{validate_output}\n\n📋 terraform plan output:\n{plan_output}"

    except FileNotFoundError:
        return "⚠️ Error: terraform is not installed or not accessible in PATH"
    except subprocess.TimeoutExpired:
        return "⚠️ Error: terraform init, validate or plan exceeded timeout"
    except (OSError, ValueError) as e:
        return f"⚠️ Error during validation: {str(e)}"


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
        review_response = _review_model.invoke(review_prompt).content

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


