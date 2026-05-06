# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Terraform code review and validation system built with LangChain and Anthropic's Claude API. It uses autonomous agents (via DeepChain) to generate, review, and validate Terraform infrastructure code with best-practice guidance.

**Key Focus Areas:**
- Terraform code review with best practices enforcement
- Terraform validation and auto-correction
- Autonomous agent-based Terraform code generation
- Vector store integration (ChromaDB) for documentation retrieval
- LangSmith integration for agent tracing and debugging

## Setup

### Dependencies
The project uses `uv` for dependency management. Install dependencies:
```bash
uv sync
```

### Environment Variables
Configure your `.env` file with:
- `ANTHROPIC_API_KEY`: Your Claude API key
- `LANGSMITH_TRACING`: Set to `true` to enable tracing
- `LANGSMITH_ENDPOINT`: LangSmith API endpoint
- `LANGCHAIN_API_KEY`: LangChain API key
- `LANGCHAIN_PROJECT`: Project name for organizing runs

The `.env` template is already present; update with your actual API keys.

## Key Commands

### Running Notebooks
```bash
# Run Jupyter notebooks directly
jupyter notebook

# Run a specific notebook in headless mode
jupyter nbconvert --to notebook --execute notebooks/deepchain-terraform-assistant.ipynb --output deepchain-output.ipynb
```

### Python Execution
```bash
# Run Python scripts with the virtual environment
uv run python <script.py>

# Execute code from the shell with project dependencies available
source .venv/bin/activate
python <script.py>
```

### Code Quality
```bash
# Format imports (isort is in dependencies)
uv run isort .

# Format code (consider adding black or ruff if needed)
```

## Architecture & Key Components

### Notebooks Directory
- **`deepchain-terraform-assistant.ipynb`**: Main notebook orchestrating the DeepChain agent for autonomous Terraform generation and validation. Flow: Load docs → Create vectorstore → Define tools → Setup agent → Run → Show results
- **`terraform-review.md`**: Terraform code review prompt template with best practices
- **`terraform-system.md`**, **`terraform-user.md`**: Prompt components for system role and user instructions
- **`terraform-evaluation.md`**: Evaluation criteria for Terraform code reviews
- **`terraform-validate.md`**: Validation workflow and rules
- **`langchain-anthropic.ipynb`**: Basic LangChain + Anthropic integration testing
- **`langchain-fibonnaci.ipynb`**: Example of LangChain agent usage

### Documentation Directory
- **`structure.md`**: Terraform project structuring best practices (reference material)
- **`cloud-storage.md`**: Cloud storage configuration patterns

### Vector Store
ChromaDB vector store is created during notebook execution and stored in `.vectorstore2/`. This enables semantic search over Terraform best practices documentation.

## Technology Stack

| Component | Purpose |
|-----------|---------|
| LangChain | Agent orchestration and tool chaining |
| langchain-anthropic | Claude API integration |
| langchain-chroma | ChromaDB vector store integration |
| DeepChain (via deepagents) | Autonomous agent with long-term planning |
| ChromaDB | Vector database for documentation retrieval |
| LangSmith | Agent tracing, debugging, and monitoring |
| LangChain Community | Extended integrations (Ollama, OpenAI) |

## Development Notes

### Adding New Notebooks
- Follow the pattern of existing notebooks for consistency
- Use markdown headers to organize cells logically
- Include docstrings explaining the notebook's purpose at the top
- Store vector data in `.vectorstore2/` for persistence

### Extending the Review System
- Modify prompts in `terraform-*.md` files to adjust review criteria
- Update `.vectorstore2/` by re-running the notebook if documentation changes
- Add new tools to the agent by extending the `tools` list in the main notebook

### Environment Setup for Development
The project targets **Python 3.14** (configured in `.python-version`). Ensure you're using this version:
```bash
python --version  # Should output 3.14.x
```

## Testing Terraform Code
The system accepts Terraform configuration files and returns:
1. Compliance analysis against best practices
2. Critical/major/minor issue classification
3. Proposed code corrections
4. Full corrected code (if issues found)

See `terraform-review.md` for the complete review prompt structure.
