import shutil
from datetime import datetime
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

from .config import Config
from .prompts import PromptManager
from .knowledge_base import KnowledgeBase
from .tools import init_tools, search_knowledge_base, validate_and_fix_code, review_and_fix_code


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
    agent: object

    def __init__(
        self,
        config: Config,
        prompts: PromptManager,
        knowledge_base: KnowledgeBase,
    ) -> None:
        """Initialize the Terraform agent with all required components.

        Sets up the DeepAgent with three tools:
        1. Knowledge base search for retrieving best practices
        2. Terraform validator for syntax checking and fixes
        3. Code reviewer for best practices compliance

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

        tools = [
            search_knowledge_base,
            validate_and_fix_code,
            review_and_fix_code,
        ]

        # Create agent with prompt caching enabled
        backend = FilesystemBackend(root_dir=config.PROJECT_ROOT, virtual_mode=False)
        chat_model = ChatAnthropic(
            model=config.AGENT_MODEL,
            cache_control_tokens=True,
        )
        self.agent = create_deep_agent(
            model=chat_model,
            backend=backend,
            tools=tools,
        )

        print(f"  ✓ System prompt loaded ({len(prompts.system)} chars)")
        print(f"  ✓ User prompt loaded ({len(prompts.user)} chars)")
        print(f"  ✓ Agent created with tools:")
        print(f"    - search (knowledge base)")
        print(f"    - validate_and_fix_code")
        print(f"    - review_and_fix_code")

    def run(self) -> str:
        """Execute the agent to generate and validate Terraform code.

        Performs the following steps:
        1. Cleans and prepares the work directory
        2. Invokes the agent with the user prompt
        3. Handles any errors that occur during execution
        4. Returns the agent's final output

        Returns:
            The agent's response content as a string, containing generated
            Terraform code and validation/review results
        """
        print("🛠️  Preparing workspace...")

        # Clean and create work directory
        if self.config.WORK_DIR.exists():
            shutil.rmtree(self.config.WORK_DIR)
            print(f"  ✓ Cleaned existing work directory")

        self.config.WORK_DIR.mkdir(exist_ok=True)
        print(f"  ✓ Created fresh work directory: {self.config.WORK_DIR}")

        print("\n🚀 Starting Terraform Code Generation Agent")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        print("\n📝 Agent is running...")
        print(
            "    (Agent will autonomously call: search, validate_and_fix_code, review_and_fix_code)"
        )
        print("-" * 80)

        try:
            # Build messages with cache control on system prompt
            messages = [
                SystemMessage(
                    content=self.prompts.system,
                    cache_control={"type": "ephemeral"}
                ),
                HumanMessage(content=self.prompts.user),
            ]

            result = self.agent.invoke(
                {"messages": messages}
            )

            agent_output = result["messages"][-1].content
            overall_status = "✅ SUCCESS"

        except Exception as e:
            overall_status = "❌ FAILED"
            agent_output = str(e)
            print(f"\n❌ Agent Error: {e}")
            import traceback

            traceback.print_exc()

        print(overall_status)
        print("-" * 80)

        return agent_output
