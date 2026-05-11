# Langfuse Integration Guide

## Overview

This Terraform agent includes production-grade LLM observability through **Langfuse**, a comprehensive platform for tracing, debugging, and monitoring AI applications.

**Langfuse traces include:**
- ✅ Agent execution flow (planning, tool selection, response generation)
- ✅ Individual tool calls with inputs/outputs and latency
- ✅ Token usage and cost tracking
- ✅ Error tracking with full context
- ✅ Latency and performance metrics
- ✅ LangChain integration (automatic tracing of all LangChain calls)

---

## Quick Start

### Option 1: Cloud Langfuse (Recommended)

**1. Sign up for Langfuse:**
```bash
# Visit https://langfuse.com
# Click "Get Started" and create an account
```

**2. Create a project:**
- Log in to Langfuse dashboard
- Click "Projects" → "Create New Project"
- Name it "terraform-agent"

**3. Get your API credentials:**
- Click Project Settings → API Keys
- Copy `Public Key` (starts with `pk-lf-`)
- Copy `Secret Key` (starts with `sk-lf-`)

**4. Configure your application:**
```bash
# In .env file
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

**5. Run your agent:**
```bash
# Open the notebook and execute cells
code notebooks/deepchain_terraform_assistant.ipynb

# Traces will automatically appear in your Langfuse dashboard
```

### Option 2: Self-Hosted Langfuse

**1. Deploy Langfuse locally:**
```bash
# Using Docker (recommended)
docker run -d \
  -e DATABASE_URL=postgresql://user:password@postgres:5432/langfuse \
  -e NEXTAUTH_SECRET=your-secret-key \
  -p 3000:3000 \
  langfuse/langfuse:latest

# Or use Docker Compose (see https://docs.langfuse.com/deployment/self-host)
```

**2. Configure your application:**
```bash
# In .env file
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=http://localhost:3000
```

**3. Access the dashboard:**
- Open http://localhost:3000 in your browser

---

## Architecture & Implementation

### How Tracing Works

```
┌─────────────────────────────────────────────────────────────┐
│                   Terraform Agent (Python)                  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  TerraformAgent.run()                                │  │
│  │  ├─ Initialize LangfuseCallbackHandler               │  │
│  │  │  (if LANGFUSE_PUBLIC_KEY + SECRET_KEY configured) │  │
│  │  └─ Pass to agent.invoke(config={"callbacks": [...]})│  │
│  └──────────────────────────────────────────────────────┘  │
│           │                                                   │
│           ├─> Tool: search_knowledge_base()                 │
│           │   └─> trace_tool_execution() → Langfuse         │
│           │                                                   │
│           ├─> Tool: terraform_init()                        │
│           │   └─> (subprocess tracking)                     │
│           │                                                   │
│           ├─> Tool: terraform_validate()                    │
│           │   └─> trace_tool_execution() → Langfuse         │
│           │                                                   │
│           └─> Tool: review_and_fix_code()                   │
│               └─> (Ollama model calls)                      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
         │
         └──> Langfuse Backend
             ├─ Cloud: https://cloud.langfuse.com
             └─ Self-hosted: http://localhost:3000
```

### Components

**1. `terraform_agent/agent.py`**
- Creates `LangfuseCallbackHandler` with credentials from config
- Passes handler to `agent.invoke()` for automatic LangChain tracing
- Logs initialization status (enabled/disabled)

**2. `terraform_agent/config.py`**
- Loads Langfuse credentials from environment variables
- Sets `LANGFUSE_ENABLED` flag based on credential availability
- Provides fallback to cloud Langfuse if `BASE_URL` not specified

**3. `terraform_agent/tools.py`**
- `init_tools()` creates Langfuse client for tool-level tracing
- `trace_tool_execution()` helper logs individual tool calls
- Each tool calls this helper after execution (when implemented)

---

## Configuration Options

### Environment Variables

```bash
# Required for tracing (both must be set)
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...

# Optional (defaults to cloud Langfuse)
LANGFUSE_BASE_URL=https://cloud.langfuse.com
# Or for self-hosted:
# LANGFUSE_BASE_URL=http://localhost:3000
```

### Programmatic Configuration

In Python code:
```python
from terraform_agent import Config

config = Config(base_dir=Path.cwd())

# Check if tracing is enabled
if config.LANGFUSE_ENABLED:
    print("✓ Langfuse tracing is enabled")
    print(f"  URL: {config.LANGFUSE_BASE_URL}")
else:
    print("✗ Langfuse tracing is disabled (missing credentials)")
```

---

## Understanding Your Traces

### Trace Hierarchy

When you run the agent, you'll see traces like this in Langfuse:

```
🔶 terraform-agent-run (≈2-5 min total)
├─ 🔵 search_knowledge_base (query: "GCS bucket variables")
│  └─ Latency: 245ms
│  └─ Input: {"query": "..."}
│  └─ Output: "# GCS Bucket Best Practices\n..."
│
├─ 🔵 terraform_init (path: "./work/modules/gcs_bucket")
│  └─ Latency: 1.2s
│  └─ Status: ✓ SUCCESS
│
├─ 🔵 terraform_validate (path: "./work/modules/gcs_bucket")
│  └─ Latency: 890ms
│  └─ Status: ✓ SUCCESS
│
└─ 🔵 review_and_fix_code (path: "./work/modules/gcs_bucket")
   └─ Latency: 3.4s
   └─ Input: 12 files, 456 lines of Terraform
   └─ Output: "Code review complete: 0 issues"
```

### Key Metrics to Monitor

**Latency**
- `search_knowledge_base`: Should be <500ms (depends on ChromaDB)
- `terraform_validate`: Typically 500ms-2s
- `review_and_fix_code`: Typically 2-5s (uses Ollama)
- Agent total: Typically 2-10 minutes

**Token Usage**
- Visible in agent trace details
- Track cost and optimization opportunities
- Langfuse shows cost breakdown by model

**Errors & Debugging**
- Failed tools show in red
- View full error output in trace details
- Search for errors across all traces

### Example Dashboard Queries

**Find all failed terraform validations:**
```
name = "tool_terraform_validate" AND (output LIKE "%ERROR%" OR status = "ERROR")
```

**Show average tool latency by tool name:**
```
GROUP BY name = "tool_*"
SELECT name, AVG(latency)
```

**Find expensive traces (high token usage):**
```
ORDER BY usage_tokens DESC
LIMIT 10
```

---

## Best Practices

### 1. Keep Traces Focused

**✅ Good:** Trace individual tool execution
```python
trace_tool_execution("search_knowledge_base", {"query": query}, result, elapsed)
```

**❌ Avoid:** Logging entire LangChain conversation
```python
# Don't trace huge outputs - truncate if needed
output = result[:500] + ("..." if len(result) > 500 else "")
```

### 2. Add Context to Traces

Use metadata to add context:
```python
langfuse_client.span(
    name="tool_review_and_fix",
    input={"path": path, "files_count": len(tf_files)},
    metadata={"environment": "prod", "project": "gcs-infrastructure"},
)
```

### 3. Monitor in Production

Set up alerts for:
- Failed tool executions
- Unusually high latency
- Token usage increases
- Error rates

### 4. Use Annotations for Analysis

Add tags to traces for filtering:
```python
span.update(tags=["production", "gcs", "terraform"])
```

---

## Troubleshooting

### Issue: Traces Not Appearing

**Check 1: Credentials are set**
```bash
echo $LANGFUSE_PUBLIC_KEY
echo $LANGFUSE_SECRET_KEY
```

**Check 2: Base URL is correct**
```python
from terraform_agent import Config
config = Config()
print(f"Enabled: {config.LANGFUSE_ENABLED}")
print(f"URL: {config.LANGFUSE_BASE_URL}")
```

**Check 3: Network connectivity**
```bash
# For cloud Langfuse
curl -I https://cloud.langfuse.com/api/health

# For self-hosted
curl -I http://localhost:3000/api/health
```

### Issue: Slow Trace Upload

**Cause:** Network latency or large payloads
**Solution:**
- Reduce output truncation (500-1000 char max)
- Use spans for long-running operations
- Consider batch uploads

### Issue: Self-hosted Langfuse Not Running

**Solution:**
```bash
# Check container status
docker ps | grep langfuse

# View logs
docker logs <container-id>

# Restart if needed
docker restart <container-id>
```

---

## Advanced Usage

### Custom Span Attributes

```python
from langfuse import Langfuse

langfuse = Langfuse(public_key="pk-lf-...", secret_key="sk-lf-...")

with langfuse.span(name="custom_operation") as span:
    # Do work
    span.update(output="result", metadata={"custom": "value"})
```

### Scoring & Annotations

```python
# Score a trace for quality/cost analysis
trace.update(score={"name": "quality", "value": 0.95})

# Add annotations for manual review
trace.update(tags=["needs_review", "high_cost"])
```

### Batch Processing

```python
# Log multiple spans efficiently
for i, operation in enumerate(operations):
    langfuse.span(name=f"batch_operation_{i}", input=operation)

# Flush when done
langfuse.flush()
```

---

## Langfuse Dashboard Features

### Traces View
- See full execution flow with timing
- Drill into individual tool calls
- View inputs/outputs for each step

### Analytics
- Token usage by model
- Latency percentiles
- Error rates and failure analysis
- Cost breakdown

### Sessions
- Group traces by execution session
- Compare agent runs
- Track improvements over time

### Alerts & Monitoring
- Set up Slack notifications for failures
- Monitor latency SLOs
- Track cost budgets

---

## References

- **Langfuse Docs:** https://docs.langfuse.com
- **LangChain Integration:** https://docs.langfuse.com/integrations/langchain
- **API Reference:** https://docs.langfuse.com/api/reference
- **Self-Hosting:** https://docs.langfuse.com/deployment/self-host
- **Community:** https://github.com/langfuse/langfuse/discussions

---

**Last Updated:** May 2026  
**Status:** Production-ready ✅
