import shutil
from datetime import datetime
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

from .config import Config
from .prompts import PromptManager
from .knowledge_base import KnowledgeBase
from .tools import TerraformValidator, TerraformReviewer


class TerraformAgent:
    def __init__(
        self,
        config: Config,
        prompts: PromptManager,
        knowledge_base: KnowledgeBase,
    ):
        self.config = config
        self.prompts = prompts
        self.knowledge_base = knowledge_base

        print("🤖 Setting up agent...")

        # Initialize tools
        validator = TerraformValidator(config, prompts)
        reviewer = TerraformReviewer(config, prompts, knowledge_base)

        tools = [
            knowledge_base.search,
            validator.get_tool(),
            reviewer.get_tool(),
        ]

        # Create agent
        backend = FilesystemBackend(root_dir=config.PROJECT_ROOT, virtual_mode=False)
        self.agent = create_deep_agent(
            model=init_chat_model(model=config.AGENT_MODEL),
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
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": self.prompts.user}]}
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
