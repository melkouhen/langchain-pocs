# CLAUDE.md — Terraform Agent Project Guide

## 🎯 Project Overview

**Terraform Code Review & Generation Agent** — An autonomous AI system that generates, validates, and improves Terraform infrastructure code following best practices.

**Status:** Production-ready ✅  
**Last Updated:** May 11, 2026  
**Active Development:** Yes

---

## 📋 Quick Reference

| Item | Value |
|------|-------|
| **Language** | Python 3.14 + Terraform HCL |
| **Package Manager** | uv (fast Python package manager) |
| **Main LLM** | Claude Haiku 4.5 (Anthropic API) |
| **Validation Model** | Ollama qwen2.5-coder:7b (local) |
| **Vector Store** | ChromaDB (semantic search) |
| **Agent Framework** | DeepAgents (autonomous planning) |
| **Infrastructure** | Google Cloud Storage (GCS) |

---

## 🏗️ Project Structure

### Core Components

**`terraform_agent/`** — Python agent implementation (624 lines)
- `agent.py` (147L) — DeepAgent orchestration
- `tools.py` (190L) — Three tools: search_knowledge_base, validate_and_fix_code, review_and_fix_code
- `knowledge_base.py` (122L) — ChromaDB integration
- `prompts.py` (106L) — Prompt template management
- `config.py` (48L) — Centralized configuration

**`notebooks/`** — Jupyter notebooks
- `deepchain_terraform_assistant.ipynb` — Main execution notebook ⭐
- `token_analysis.ipynb` — Claude API token consumption analysis
- `chromadb_explorer.ipynb` — Knowledge base exploration

**`prompts/`** — LLM prompt templates
- `terraform-system.md` — System prompt defining agent behavior
- `terraform-user.md`, `terraform-review.md`, `terraform-validate.md`, `terraform-evaluation.md`

**`docs/`** — Best practices documentation
- `structure.md` — Terraform module structure
- `cloud-storage.md` — GCS-specific best practices

**`work/`** — Generated output (Terraform + documentation)
- `modules/gcs_bucket/` — Reusable Terraform module
- `envs/{dev,prod}/` — Environment-specific configurations
- `README.md`, `DEPLOYMENT.md`, `VALIDATION_REPORT.md`, `PROJECT_SUMMARY.md`

---

## 🚀 Getting Started

### Prerequisites

**System Requirements:**
```bash
# Python 3.14+
python --version

# uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ollama with qwen2.5-coder:7b model
ollama pull qwen2.5-coder:7b
# Verify: curl http://localhost:11434/api/tags

# For GCP deployment (optional):
gcloud auth application-default login
```

### Setup

```bash
# 1. Install dependencies
uv sync

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys:
# - ANTHROPIC_API_KEY from https://console.anthropic.com/account/keys

# 3. Verify setup
python -c "import chromadb; from langchain_anthropic import ChatAnthropic; print('✓ Setup OK')"
```

### Running the Agent

```bash
# Open notebook in VS Code
code notebooks/deepchain_terraform_assistant.ipynb

# Select Python kernel (uv environment)
# Execute cells in order
# Check results in ./work/ directory
```

---

## 🛠️ Key Components & How They Work

### Agent Flow (4 Phases)

```
1️⃣ INITIALIZATION
   ├─ Load prompts (system, user, templates)
   ├─ Create ChromaDB vector store
   └─ Index docs/

2️⃣ SETUP
   ├─ Initialize Claude API client
   └─ Register three tools

3️⃣ EXECUTION
   ├─ Run autonomous DeepAgent
   ├─ Agent calls tools as needed:
   │  ├─ search_knowledge_base(query) → retrieves best practices
   │  ├─ validate_and_fix_code(path) → terraform validate + fixes
   │  └─ review_and_fix_code(path) → LLM code review with Ollama
   └─ Generate final Terraform code

4️⃣ OUTPUT
   └─ Save to ./work/ with documentation
```

### The Three Tools

**`search_knowledge_base(query: str)`**
- Searches ChromaDB for relevant best practices
- Returns semantic matches from docs/
- Used by agent before writing code

**`validate_and_fix_code(path: str)`**
- Runs `terraform init`, `validate`, `plan`
- Returns validation errors
- Agent applies fixes and re-validates

**`review_and_fix_code(path: str)`**
- Uses local Ollama model (qwen2.5-coder:7b)
- Reviews code against best practices
- Returns CRITICAL/MAJOR/MINOR issues
- Agent fixes CRITICAL and MAJOR issues

---

## 📊 What Gets Generated

### Infrastructure (in `./work/`)

**Module:** `modules/gcs_bucket/`
- Reusable Google Cloud Storage bucket module
- 11 configurable variables
- 6 outputs for downstream consumption
- Security best practices enforced (UBLA, public access prevention)
- Supports versioning, lifecycle rules, logging, IAM

**Environments:** `envs/{dev,prod}/`
- Dev environment: Basic GCS bucket for testing
- Prod environment: GCS bucket with lifecycle rules (cost optimization)
- Each with isolated Terraform state
- Ready to deploy: `terraform plan && terraform apply`

### Documentation

- **README.md** (400+ lines) — Comprehensive usage guide
- **DEPLOYMENT.md** (400+ lines) — Step-by-step deployment instructions
- **VALIDATION_REPORT.md** (300+ lines) — QA and security audit results
- **PROJECT_SUMMARY.md** — Executive summary of deliverables

### Quality Artifacts

- ✅ `terraform validate` passes (both envs)
- ✅ `.terraform.lock.hcl` generated (provider locking)
- ✅ `.gitignore` configured properly
- ✅ All best practices documented and implemented

---

## 🔧 Configuration & Customization

### System Prompt

Located in `prompts/terraform-system.md`. Key sections:

**Core Principles:**
- KISS First (match complexity to task)
- Zero Drift (no timestamp() in names)
- Declarative over Imperative
- Explicit over Implicit

**Operational Protocol:**
1. Knowledge Phase — Search knowledge base first
2. Planning Phase — Create minimal implementation plan
3. Code Generation — Generate valid HCL with no errors
4. Validation Phase — Run terraform validate, stop on errors
5. Review Phase — Fix CRITICAL/MAJOR issues

**File Generation Constraint:**
> Only create files that directly address a user requirement. Do not generate unnecessary files, documentation, or boilerplate.

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...  # From https://console.anthropic.com
```

### Adding Custom Knowledge

1. Create markdown file in `docs/` (e.g., `docs/custom-practice.md`)
2. Next notebook run will automatically index it in ChromaDB
3. Agent can now search and reference it

### Modifying Agent Behavior

Edit `prompts/terraform-system.md` to change:
- Preferred architectures
- Validation rules
- Code style preferences
- Security constraints

---

## 📝 Development Guidelines

### Code Style

- **Type hints required:** All functions must have type annotations
- **Docstrings:** Brief one-liners for simple functions, longer for complex ones
- **Imports:** Group standard library, third-party, local
- **Format:** Black (automatic via uv)

### Testing Locally

```bash
# Run the notebook and check:
1. ChromaDB initialization (should complete in seconds)
2. Agent tool registration (should show 3 tools)
3. Terraform generation (should complete in 2-5 min)
4. Validation output (should show ✓ validate passed)
5. Output files (should be in ./work/)
```

### Debugging

```bash
# View agent thinking
# Set in terraform-system.md: Add logging statements

# Check ChromaDB content
# Run: notebooks/chromadb_explorer.ipynb

# Analyze token consumption
# Run: notebooks/token_analysis.ipynb
```

---

## 🐛 Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: chromadb` | Virtual env not initialized | `rm -rf .venv && uv sync` |
| `Ollama connection error` | Service not running | `ollama serve` in another terminal |
| `ANTHROPIC_API_KEY invalid` | Wrong key or format | Verify key from console.anthropic.com |
| `ChromaDB initialization hangs` | Corrupted vectorstore | `rm -rf .vectorstore .vectorstore2` |
| `Permission denied: ./work/` | File permissions | `chmod 755 work/ && rm -rf work/*` |

See `README.md` Troubleshooting section for more details.

---

## 📚 Key Files to Know

| File | Purpose | When to Edit |
|------|---------|--------------|
| `README.md` | User-facing documentation | When adding features, changing setup |
| `.env.example` | Environment variables template | When adding new configs or credentials |
| `prompts/terraform-system.md` | Agent behavior definition | When changing generation strategy |
| `terraform_agent/config.py` | Model/path configuration | When changing LLM or model settings |
| `terraform_agent/agent.py` | Agent orchestration | When modifying agent flow |
| `terraform_agent/tools.py` | Tool implementations | When adding/modifying tools |
| `docs/*.md` | Best practices knowledge base | When adding new architectural patterns |

---

## 🎯 Next Steps / Future Work

### Short Term (1-2 weeks)
- [ ] Add AWS/Azure support (beyond GCS)
- [ ] Implement state management for Terraform (GCS backend)
- [ ] Add CI/CD integration example

### Medium Term (1-2 months)
- [ ] Support custom Terraform modules
- [ ] Add cost estimation
- [ ] Integrate with Terraform Cloud

### Long Term
- [ ] Multi-cloud orchestration
- [ ] Real-time drift detection
- [ ] Automated remediation

---

## 📞 Support & Resources

### Project Links
- **Repository:** `/Users/melkouhen/audit-tools/test-langchain`
- **Main Notebook:** `notebooks/deepchain_terraform_assistant.ipynb`
- **Best Practices:** `docs/` directory

### External Resources
- [Terraform Language](https://www.terraform.io/language)
- [Google Cloud Terraform Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [LangChain Documentation](https://python.langchain.com)
- [Anthropic Claude API](https://docs.anthropic.com)
- [Ollama GitHub](https://github.com/ollama/ollama)

### Getting Help
1. Check `README.md` Troubleshooting section
2. Review `notebooks/chromadb_explorer.ipynb` to understand knowledge base
3. Check recent commits: `git log --oneline -15`
4. Review prompts in `prompts/` to understand agent behavior

---

## 🤝 Contributing

**Before making changes:**
1. Read this CLAUDE.md
2. Check recent commits to understand current direction
3. Run the notebook locally to verify baseline works
4. Keep changes focused (one feature/fix per commit)

**Commit message format:**
```
<type>: <description>

<optional details>

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
```

Types: `feat`, `fix`, `refactor`, `docs`, `chore`

---

## 📋 Checklist for Running the Agent

- [ ] Python 3.14+ installed
- [ ] `uv` installed and working
- [ ] Ollama running with qwen2.5-coder:7b model
- [ ] `.env` file created with ANTHROPIC_API_KEY
- [ ] `uv sync` completed without errors
- [ ] All system checks pass (python --version, curl ollama, etc.)
- [ ] Notebook opens in VS Code without kernel errors
- [ ] First cell initializes without errors (imports, config loading)
- [ ] Agent runs through all 4 phases
- [ ] Output generated in `./work/` directory
- [ ] `work/PROJECT_SUMMARY.md` readable and complete

---

**Last Updated:** May 11, 2026  
**Status:** ✅ Production-ready  
**Maintainer:** Mehdi El Kouhen  
