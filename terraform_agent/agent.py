import logging
from typing import TYPE_CHECKING
from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from phoenix.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor

from .config import Config
from .prompts import PromptManager
from .knowledge_base import KnowledgeBase
from .tools import init_tools, load_module_spec, search_knowledge_base, terraform_init, terraform_validate, terraform_plan, review_and_fix_code

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph

logger = logging.getLogger(__name__)

class TerraformAgent:
    """Orchestrates autonomous Terraform code generation and validation.

    Creates and manages a DeepAgent that can autonomously:
    1. Generate Terraform code based on requirements
    2. Search the knowledge base for best practices
    3. Validate generated code for syntax errors
    4. Review code compliance with best practices

    The agent operates in a controlled workspace (work/) and generates
    complete Terraform projects with supporting documentation.

    Attributes:
        config: Configuration object with paths and model names
        prompts: PromptManager instance for all prompt templates
        knowledge_base: KnowledgeBase instance for semantic search
        agent: The underlying DeepAgent instance
    """

    config: Config
    prompts: PromptManager
    knowledge_base: KnowledgeBase
    agent: "CompiledStateGraph"

    def __init__(
        self,
        config: Config,
        prompts: PromptManager,
        knowledge_base: KnowledgeBase,
    ) -> None:
        """Initialize the Terraform agent with all required components.

        Sets up the DeepAgent with six tools:
        1. Module spec loader for accessing Terraform module specifications
        2. Knowledge base search for retrieving best practices
        3. Terraform init for initializing working directory
        4. Terraform validate for syntax checking and fixes
        5. Terraform plan for previewing infrastructure changes
        6. Code reviewer for best practices compliance

        Args:
            config: Configuration object containing paths and model names
            prompts: PromptManager instance for accessing prompt templates
            knowledge_base: KnowledgeBase instance for semantic search capabilities
        """
        self.config = config
        self.prompts = prompts
        self.knowledge_base = knowledge_base

        print("🤖 Setting up agent...")

        # Initialize global tool instances
        init_tools(config, prompts, knowledge_base)

        # Initialize Phoenix tracing if enabled
        if config.PHOENIX_ENABLED:
            try:
                tracer_provider = register(
                    project_name=config.PHOENIX_PROJECT_NAME,
                    endpoint=config.PHOENIX_ENDPOINT,
                )
                LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
                logger.info(f"✓ Phoenix tracing enabled → {config.PHOENIX_ENDPOINT}")
                print(f"  ✓ Phoenix tracing enabled → {config.PHOENIX_ENDPOINT}")
            except Exception as e:
                logger.warning(f"Failed to initialize Phoenix: {e}")
                print(f"  ⚠️  Phoenix initialization failed: {e}")

        # Prepare tools list
        tools_list = [
            load_module_spec,
            search_knowledge_base,
            terraform_init,
            terraform_validate,
            terraform_plan,
            review_and_fix_code,
        ]

        # Create agent with prompt caching enabled
        backend = FilesystemBackend(root_dir=config.PROJECT_ROOT, virtual_mode=False)

        self.agent = create_deep_agent(
            model=config.AGENT_MODEL,
            backend=backend,
            tools=tools_list,
        )

        print(f"  ✓ System prompt loaded ({len(prompts.system)} chars)")
        print(f"  ✓ User prompt loaded ({len(prompts.user)} chars)")
        print(f"  ✓ Agent created with tools:")
        print(f"    - load_module_spec (module specifications)")
        print(f"    - search_knowledge_base (best practices)")
        print(f"    - terraform_init (initialize working directory)")
        print(f"    - terraform_validate (validate configuration)")
        print(f"    - terraform_plan (preview changes)")
        print(f"    - review_and_fix_code (code review)")

    def run(self, user_prompt: str | None = None) -> str:
        """Execute the agent to generate and validate Terraform code.

        Performs the following steps:
        1. Cleans and prepares the work directory
        2. Invokes the agent with the user prompt
        3. Handles any errors that occur during execution
        4. Returns the agent's final output

        Args:
            user_prompt: Optional custom user prompt. If not provided, uses the
                        default prompt from the prompt manager.

        Returns:
            The agent's response content as a string, containing generated
            Terraform code and validation/review results
        """
        print("🛠️  Preparing workspace...")
        print("\n🚀 Starting Terraform Code Generation Agent")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        print("\n📝 Agent is running...")
        print(
            "    (Agent will autonomously call: terraform_init, terraform_validate, terraform_plan, review_and_fix_code)"
        )
        print("-" * 80)

        try:
            # Build messages with cache control on system prompt
            prompt_content = user_prompt if user_prompt is not None else self.prompts.user
            messages = [
                SystemMessage(
                    content=[
                        {
                            "type": "text",
                            "text": self.prompts.system,
                            "cache_control": {"type": "ephemeral"},
                        }
                    ]
                ),
                HumanMessage(content=prompt_content),
            ]

            result = self.agent.invoke(
                {"messages": messages},
            )

            agent_output = result["messages"][-1].content
            overall_status = "✅ SUCCESS"
            logger.info("Agent execution completed successfully")

        except Exception as e:
            overall_status = "❌ FAILED"
            agent_output = str(e)
            logger.error(f"Agent execution failed: {e}", exc_info=True)
            print(f"\n❌ Agent Error: {e}")
            import traceback

            traceback.print_exc()

        print(overall_status)
        print("-" * 80)

        return agent_output
