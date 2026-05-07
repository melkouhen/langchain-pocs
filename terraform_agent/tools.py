import subprocess
import glob
import os
from langchain_ollama import ChatOllama
from langchain_core.tools import tool

from .config import Config
from .prompts import PromptManager
from .knowledge_base import KnowledgeBase


class TerraformValidator:
    """Tool for validating Terraform code and suggesting fixes.

    Uses the 'terraform validate' command to check for syntax errors and
    configuration issues. If errors are found, uses an LLM to analyze and
    suggest corrections based on the error messages.

    Attributes:
        config: Configuration object with model names
        prompts: PromptManager instance for validation prompts
        review_model: LLM model used for analyzing and fixing errors
    """

    def __init__(self, config: Config, prompts: PromptManager):
        """Initialize the Terraform validator with configuration and prompts.

        Args:
            config: Configuration object containing model names and paths
            prompts: PromptManager instance for accessing validation templates
        """
        self.config = config
        self.prompts = prompts
        self.review_model = ChatOllama(model=config.REVIEW_MODEL_NAME)

    def get_tool(self):
        """Return a LangChain tool for terraform validation.

        Returns:
            A LangChain @tool decorated function that can be used by agents
        """
        @tool
        def validate_and_fix_code(path: str) -> str:
            """
            Executes terraform validate on generated code.

            Args:
                path: folder where the code is generated
            """
            try:
                result = subprocess.run(
                    ["terraform", "validate"],
                    cwd=path,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode != 0:
                    error_message = result.stderr or result.stdout

                    prompt = self.prompts.validate.format(
                        error_message=error_message, root_folder=path
                    )

                    correction = self.review_model.invoke(prompt).content
                    return f"❌ Erreurs détectées:\n{error_message}\n\n💡 Corrections suggérées:\n{correction}"
                else:
                    return "✅ Terraform validate: succès - aucune erreur détectée"

            except FileNotFoundError:
                return "⚠️ Erreur: terraform n'est pas installé ou non accessible dans le PATH"
            except subprocess.TimeoutExpired:
                return "⚠️ Erreur: terraform validate a dépassé le timeout (30s)"
            except Exception as e:
                return f"⚠️ Erreur lors de la validation: {str(e)}"

        return validate_and_fix_code


class TerraformReviewer:
    """Tool for reviewing Terraform code against best practices.

    Performs comprehensive code reviews by:
    1. Retrieving relevant best practices from the knowledge base
    2. Reading all generated Terraform files
    3. Analyzing code compliance with best practices
    4. Identifying major issues and suggesting fixes if needed

    Attributes:
        config: Configuration object with model names and paths
        prompts: PromptManager instance for review prompts
        knowledge_base: KnowledgeBase instance for accessing best practices
        review_model: LLM model used for code analysis
    """

    def __init__(
        self, config: Config, prompts: PromptManager, knowledge_base: KnowledgeBase
    ):
        """Initialize the Terraform reviewer with dependencies.

        Args:
            config: Configuration object containing model names and paths
            prompts: PromptManager instance for accessing review templates
            knowledge_base: KnowledgeBase instance for accessing best practices
        """
        self.config = config
        self.prompts = prompts
        self.knowledge_base = knowledge_base
        self.review_model = ChatOllama(model=config.REVIEW_MODEL_NAME)

    def get_tool(self):
        """Return a LangChain tool for code review.

        Returns:
            A LangChain @tool decorated function that can be used by agents
        """
        @tool
        def review_and_fix_code(path: str) -> str:
            """
            Performs comprehensive code review against best practices.

            Process:
            1. Retrieves Terraform best practices from knowledge base
            2. Analyzes generated code for compliance
            3. Identifies major issues and applies fixes if necessary

            Args:
                path: folder where the code is generated
            """
            try:
                # Step 1: Retrieve best practices from knowledge base
                best_practices = self.knowledge_base.search(
                    "Terraform best practices security standards naming conventions modules"
                )

                # Step 2: Read all generated Terraform files
                tf_files = sorted(glob.glob(path + "/**/*.tf", recursive=True))

                if not tf_files:
                    return "⚠️ Revue: Aucun fichier .tf trouvé dans le répertoire"

                code_content = ""
                for file_path in tf_files:
                    with open(file_path, "r") as f:
                        file_name = os.path.basename(file_path)
                        code_content += f"\n\n--- {file_name} ---\n{f.read()}"

                # Step 3: Use template from markdown file
                review_prompt = self.prompts.review.format(
                    best_practices=best_practices, code_content=code_content
                )

                # Step 4: Execute review with model
                review_response = self.review_model.invoke(review_prompt).content

                # Step 5: Parse response and apply fixes if needed
                if "CRITIQUE" in review_response or "MAJEUR" in review_response:
                    if "### Code Corrigé" in review_response:
                        result_summary = self.prompts.response_with_fixes.format(
                            num_files=len(tf_files),
                            review_response=review_response,
                            root_folder=path,
                        )
                    else:
                        result_summary = review_response
                else:
                    result_summary = self.prompts.response_compliant.format(
                        num_files=len(tf_files),
                        review_response=review_response,
                    )

                return result_summary

            except FileNotFoundError as e:
                return f"⚠️ Erreur: Fichier non trouvé: {e}"
            except Exception as e:
                return f"⚠️ Erreur lors de la revue: {str(e)}"

        return review_and_fix_code
