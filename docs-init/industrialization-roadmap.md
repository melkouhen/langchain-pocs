# Axes d'Industrialisation - Terraform Code Generation Agent

**Date:** 2026-05-12  
**Statut:** Production-ready → Enterprise-grade  
**Objectif:** Transformer le PoC en solution industrielle scalable, testable et maintenable

---

## 🎯 Vue d'ensemble

Le projet est actuellement **production-ready** avec ~2400 lignes de code Python, une suite d'évaluation LLM-as-judge, et un système de callbacks pour le tracking. Les axes d'industrialisation visent à :

1. **Scalabilité** : Supporter plusieurs équipes et projets simultanés
2. **Fiabilité** : Tests automatisés, CI/CD, monitoring
3. **Maintenabilité** : Documentation, architecture modulaire, standards
4. **Sécurité** : Gestion secrets, audit trail, validation renforcée
5. **Performance** : Optimisation coûts, caching, parallélisation

---

## 📊 Axe 1 : Testing & Quality Assurance

### 1.1 Tests Unitaires et d'Intégration

**État actuel:**
- ✅ Harness d'évaluation LLM-as-judge (`eval/harness.py`)
- ✅ 1 test case fonctionnel (GCS bucket)
- ❌ Pas de tests unitaires
- ❌ Pas de tests d'intégration automatisés
- ❌ Pas de coverage tracking

**Actions prioritaires:**

```python
# 1. Structure de tests pytest
tests/
├── unit/
│   ├── test_knowledge_base.py        # ChromaDB search, summarization
│   ├── test_model_router.py          # Ollama/Claude routing
│   ├── test_tools.py                 # Terraform CLI wrapper
│   └── test_prompts.py               # Template rendering
├── integration/
│   ├── test_generator_e2e.py         # Full workflow
│   ├── test_terraform_validation.py  # Real terraform commands
│   └── test_callbacks.py             # Phase tracking
├── fixtures/
│   ├── mock_terraform_output.py
│   ├── sample_prompts.py
│   └── test_knowledge_base/          # Docs subset
└── conftest.py                       # Pytest fixtures

# 2. Tests critiques à implémenter
- test_knowledge_base_search_returns_relevant_docs()
- test_model_router_fallback_to_claude()
- test_terraform_init_validates_path_security()
- test_generator_handles_terraform_errors()
- test_callbacks_detect_all_phases()

# 3. Couverture cible : 80%+
pytest --cov=terraform_agent --cov-report=html
```

**Livrables:**
- [ ] 50+ tests unitaires couvrant les modules critiques
- [ ] 10+ tests d'intégration end-to-end
- [ ] Coverage report automatique dans CI
- [ ] Tests de régression pour bugs connus

**Effort estimé:** 2-3 semaines, 1 développeur

---

### 1.2 Expansion de la Suite d'Évaluation

**État actuel:**
- 1 test case (Simple GCS Bucket)
- Évaluation LLM avec 6 critères pondérés
- Validation Terraform (init/validate/plan)

**Actions:**

```yaml
# eval/test_cases.yaml
test_suites:
  - suite: storage
    cases:
      - tc01: Simple GCS Bucket (✅ existing)
      - tc02: GCS with Lifecycle & IAM
      - tc03: Multi-region bucket with CMEK
      - tc04: GCS + Cloud Storage Transfer
  
  - suite: networking
    cases:
      - tc05: VPC with subnets
      - tc06: Cloud Load Balancer
      - tc07: VPN Gateway
  
  - suite: compute
    cases:
      - tc08: GCE instance group
      - tc09: GKE cluster
      - tc10: Cloud Run service
  
  - suite: security
    cases:
      - tc11: Service account with minimal IAM
      - tc12: Secret Manager integration
      - tc13: Security Command Center

  - suite: edge_cases
    cases:
      - tc14: Invalid prompt (should fail gracefully)
      - tc15: Conflicting requirements
      - tc16: Malicious prompt injection attempt
```

**Métriques d'évaluation enrichies:**
```python
# eval/evaluator.py - Nouvelles métriques
- security_score: Détection CVE, OWASP top 10
- cost_optimization_score: Infracost estimation
- compliance_score: CIS benchmarks, PCI-DSS
- drift_detection: Comparaison avec état actuel
- documentation_score: Qualité README/comments
```

**Livrables:**
- [ ] 20+ test cases couvrant GCP services majeurs
- [ ] Évaluation multi-critères enrichie (10+ dimensions)
- [ ] Benchmark de performance (latence, tokens, coûts)
- [ ] Dashboard de résultats (Streamlit/Grafana)

**Effort estimé:** 3-4 semaines, 1 développeur

---

## 🏗️ Axe 2 : CI/CD & Automation

### 2.1 Pipeline CI/CD GitHub Actions

**État actuel:**
- ❌ Pas de pipeline CI/CD
- ✅ Commits structurés avec Co-Authored-By Claude
- ✅ Git hooks via `rtk`

**Actions:**

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [master, develop]
  pull_request:
    branches: [master]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'  # Stable version for CI
      
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      
      - name: Install dependencies
        run: uv sync
      
      - name: Lint & Type check
        run: |
          uv run ruff check .
          uv run mypy terraform_agent/
      
      - name: Unit tests
        run: uv run pytest tests/unit -v --cov
      
      - name: Integration tests
        run: uv run pytest tests/integration -v
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          USE_OLLAMA_FOR: ""  # Use Claude in CI
  
  eval:
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/master'
    steps:
      - name: Run evaluation harness
        run: uv run python -m eval.harness
      
      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: eval-results
          path: eval/results/
      
      - name: Comment PR with scores
        uses: actions/github-script@v7
        with:
          script: |
            const report = require('./eval/results/latest/report.json');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              body: `## Evaluation Results\nAverage score: ${report.average_score}/5`
            });

  security:
    runs-on: ubuntu-latest
    steps:
      - name: Security scan
        run: |
          uv run bandit -r terraform_agent/
          uv run safety check
      
      - name: SAST with Semgrep
        uses: returntocorp/semgrep-action@v1

  release:
    needs: [test, eval, security]
    if: github.ref == 'refs/heads/master'
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker image
        run: docker build -t terraform-agent:${{ github.sha }} .
      
      - name: Push to registry
        run: docker push terraform-agent:${{ github.sha }}
```

**Livrables:**
- [ ] CI complet (lint, test, security scan)
- [ ] Déploiement automatique sur merge
- [ ] Notifications Slack/Teams sur failures
- [ ] Badge de build status dans README

**Effort estimé:** 1-2 semaines, 1 DevOps

---

### 2.2 Containerisation & Déploiement

**État actuel:**
- ❌ Pas de Dockerfile
- ✅ Installation via `uv sync`
- ⚠️  Dépendance Python 3.14 (alpha)

**Actions:**

```dockerfile
# Dockerfile
FROM python:3.12-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    terraform \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY . .

# Runtime stage
FROM base as runtime
EXPOSE 8000
CMD ["uv", "run", "python", "-m", "terraform_agent.api"]

# Evaluation stage (for CI)
FROM base as eval
CMD ["uv", "run", "python", "-m", "eval.harness"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  terraform-agent:
    build: .
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - USE_OLLAMA_FOR=summarization,parsing,review
    volumes:
      - ./work:/app/work
      - ./rules:/app/rules:ro
    ports:
      - "8000:8000"
  
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
  
  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - chroma-data:/chroma/chroma
  
  phoenix:
    image: arizephoenix/phoenix:latest
    ports:
      - "6006:6006"
    environment:
      - PHOENIX_WORKING_DIR=/data

volumes:
  ollama-data:
  chroma-data:
```

**Livrables:**
- [ ] Dockerfile multi-stage optimisé
- [ ] Docker Compose pour stack complète
- [ ] Kubernetes manifests (optionnel)
- [ ] Documentation déploiement cloud (Cloud Run, ECS)

**Effort estimé:** 1 semaine, 1 DevOps

---

## 🔐 Axe 3 : Sécurité & Compliance

### 3.1 Gestion des Secrets & Credentials

**État actuel:**
- ⚠️  `.env` file avec ANTHROPIC_API_KEY
- ⚠️  Pas de rotation automatique
- ⚠️  Pas d'audit trail sur les accès

**Actions:**

```python
# terraform_agent/secrets.py
from google.cloud import secretmanager
from azure.keyvault.secrets import SecretClient
import boto3

class SecretManager:
    """Unified secret management across cloud providers."""
    
    def __init__(self, provider: str = "gcp"):
        self.provider = provider
        self._client = self._init_client()
    
    def get_secret(self, name: str) -> str:
        """Retrieve secret with automatic rotation check."""
        if self.provider == "gcp":
            return self._get_gcp_secret(name)
        elif self.provider == "aws":
            return self._get_aws_secret(name)
        # ...
    
    def rotate_secret(self, name: str, new_value: str):
        """Rotate secret with zero-downtime."""
        # Implementation...

# terraform_agent/config.py
class Config:
    def __init__(self):
        if os.getenv("ENVIRONMENT") == "production":
            secret_mgr = SecretManager(provider="gcp")
            self.ANTHROPIC_API_KEY = secret_mgr.get_secret("anthropic-api-key")
        else:
            self.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
```

**Configuration recommandée:**

```yaml
# GCP Secret Manager
gcloud secrets create anthropic-api-key \
  --data-file=- \
  --replication-policy="automatic"

# Rotation automatique (30j)
gcloud secrets versions add anthropic-api-key \
  --data-file=new-key.txt

# IAM minimal
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:terraform-agent@PROJECT.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

**Livrables:**
- [ ] Intégration GCP Secret Manager / AWS Secrets Manager
- [ ] Rotation automatique des clés (30j)
- [ ] Audit log de tous les accès secrets
- [ ] Zero-downtime sur rotation

**Effort estimé:** 1 semaine, 1 développeur

---

### 3.2 Sécurisation des Outils Terraform

**État actuel:**
- ✅ Validation de path (`_validate_terraform_path`)
- ⚠️  Pas de sandboxing
- ⚠️  Terraform en mode local (state sur disque)

**Actions:**

```python
# terraform_agent/security.py
import subprocess
from pathlib import Path

class SecureTerraformRunner:
    """Execute Terraform in isolated environment."""
    
    def __init__(self, work_dir: Path):
        self.work_dir = work_dir
        self.allowed_commands = ["init", "validate", "plan"]
    
    def run_isolated(self, cmd: list[str], timeout: int = 300) -> str:
        """Run Terraform with resource limits & sandboxing."""
        
        # 1. Validate command whitelist
        if cmd[1] not in self.allowed_commands:
            raise SecurityError(f"Command {cmd[1]} not allowed")
        
        # 2. Use Docker sandbox (alternative: gVisor, Firecracker)
        docker_cmd = [
            "docker", "run", "--rm",
            "--network=none",  # No network access
            "--read-only",     # Read-only filesystem
            "--tmpfs", "/tmp:rw,noexec,nosuid",
            "-v", f"{self.work_dir}:/workspace:rw",
            "-w", "/workspace",
            "--memory=512m",   # Memory limit
            "--cpus=1",        # CPU limit
            "hashicorp/terraform:latest",
            *cmd
        ]
        
        result = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
        
        # 3. Log all executions to audit trail
        self._audit_log(cmd, result.returncode, result.stdout)
        
        return result.stdout

# terraform_agent/tools.py
@tool
def terraform_init(path: str) -> str:
    runner = SecureTerraformRunner(Path(path))
    return runner.run_isolated(["terraform", "init"])
```

**Backend remote state:**

```hcl
# work/backend.tf (auto-generated)
terraform {
  backend "gcs" {
    bucket = "terraform-state-${project_id}"
    prefix = "agents/${run_id}"
    
    # Encryption
    encryption_key = "projects/${project}/locations/global/keyRings/terraform/cryptoKeys/state"
  }
}
```

**Livrables:**
- [ ] Sandboxing Terraform (Docker/gVisor)
- [ ] Remote state backend (GCS/S3)
- [ ] State locking avec DynamoDB/Cloud Storage
- [ ] Audit trail de toutes les opérations Terraform

**Effort estimé:** 2 semaines, 1 développeur

---

## 📈 Axe 4 : Observabilité & Monitoring

### 4.1 Métriques & Dashboards

**État actuel:**
- ✅ Phoenix tracing (observability basique)
- ✅ Logs structurés avec preview
- ❌ Pas de métriques business
- ❌ Pas de dashboards

**Actions:**

```python
# terraform_agent/metrics.py
from prometheus_client import Counter, Histogram, Gauge
from datadog import statsd

# Métriques Prometheus
generation_requests = Counter(
    'terraform_generation_requests_total',
    'Total Terraform generation requests',
    ['status', 'provider', 'resource_type']
)

generation_duration = Histogram(
    'terraform_generation_duration_seconds',
    'Time spent generating Terraform code',
    buckets=[10, 30, 60, 120, 300, 600]
)

tokens_consumed = Counter(
    'terraform_tokens_consumed_total',
    'Total tokens consumed',
    ['model', 'operation']
)

cost_estimate = Gauge(
    'terraform_cost_estimate_usd',
    'Estimated infrastructure cost'
)

# terraform_agent/callbacks.py
class MetricsCallback(BaseCallbackHandler):
    def on_llm_start(self, serialized, prompts, **kwargs):
        self.start_time = time.time()
    
    def on_llm_end(self, response, **kwargs):
        duration = time.time() - self.start_time
        generation_duration.observe(duration)
        
        tokens = response.llm_output.get('token_usage', {})
        tokens_consumed.labels(
            model=kwargs.get('model_name'),
            operation='generation'
        ).inc(tokens.get('total_tokens', 0))
```

**Dashboard Grafana:**

```yaml
# monitoring/grafana-dashboard.json
panels:
  - title: "Generation Throughput"
    type: graph
    targets:
      - expr: rate(terraform_generation_requests_total[5m])
  
  - title: "P95 Latency"
    type: graph
    targets:
      - expr: histogram_quantile(0.95, terraform_generation_duration_seconds)
  
  - title: "Cost per Generation"
    type: stat
    targets:
      - expr: sum(terraform_tokens_consumed_total) * 0.000003  # Claude pricing
  
  - title: "Error Rate"
    type: graph
    targets:
      - expr: rate(terraform_generation_requests_total{status="error"}[5m])
  
  - title: "Knowledge Base Hit Rate"
    type: gauge
    targets:
      - expr: kb_cache_hits / kb_total_searches
```

**Livrables:**
- [ ] Métriques Prometheus exportées
- [ ] Dashboard Grafana avec 15+ panels
- [ ] Alerting sur SLIs (latency, error rate, cost)
- [ ] Weekly cost report automatique

**Effort estimé:** 1-2 semaines, 1 développeur

---

### 4.2 Distributed Tracing

**État actuel:**
- ✅ Phoenix tracing local
- ❌ Pas de distributed tracing multi-service

**Actions:**

```python
# terraform_agent/tracing.py
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

def init_tracing(service_name: str):
    """Initialize OpenTelemetry distributed tracing."""
    
    # Configure OTLP exporter (Jaeger, Tempo, etc.)
    otlp_exporter = OTLPSpanExporter(
        endpoint="jaeger:4317",
        insecure=True
    )
    
    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    trace.set_tracer_provider(provider)
    
    return trace.get_tracer(service_name)

# terraform_agent/generator.py
class TerraformGenerator:
    def __init__(self, config, prompts, kb):
        self.tracer = init_tracing("terraform-agent")
        # ...
    
    def run(self, user_prompt: str):
        with self.tracer.start_as_current_span("terraform.generation") as span:
            span.set_attribute("prompt.length", len(user_prompt))
            span.set_attribute("user.id", self.get_user_id())
            
            with self.tracer.start_as_current_span("kb.search"):
                best_practices = self.kb.search(user_prompt)
            
            with self.tracer.start_as_current_span("llm.generate"):
                result = self.agent.invoke(messages)
            
            with self.tracer.start_as_current_span("terraform.validate"):
                validation = self.tools.terraform_validate()
            
            span.set_attribute("generation.success", True)
            span.set_attribute("tokens.total", result.usage.total_tokens)
            
            return result
```

**Stack de monitoring complète:**

```yaml
# monitoring/docker-compose.yml
services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # UI
      - "4317:4317"    # OTLP gRPC
  
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana:latest
    volumes:
      - ./grafana-dashboards:/etc/grafana/provisioning/dashboards
    ports:
      - "3000:3000"
  
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
```

**Livrables:**
- [ ] OpenTelemetry tracing complet
- [ ] Jaeger UI pour debugging
- [ ] Corrélation logs/traces/métriques
- [ ] Flame graphs de performance

**Effort estimé:** 1 semaine, 1 développeur

---

## 🚀 Axe 5 : Performance & Scalabilité

### 5.1 Optimisation des Coûts LLM

**État actuel:**
- ✅ Model routing (Ollama pour tasks simples)
- ✅ Prompt caching activé
- ❌ Pas de caching des résultats
- ❌ Pas de batching

**Actions:**

```python
# terraform_agent/cache.py
import redis
import hashlib
from functools import lru_cache

class GenerationCache:
    """Cache Terraform generations with TTL."""
    
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.ttl = 3600 * 24 * 7  # 7 days
    
    def get(self, prompt: str) -> str | None:
        """Get cached generation by prompt hash."""
        key = self._hash_prompt(prompt)
        cached = self.redis.get(f"gen:{key}")
        
        if cached:
            self.redis.incr(f"cache:hits")
            return cached.decode()
        
        self.redis.incr(f"cache:misses")
        return None
    
    def set(self, prompt: str, result: str):
        """Cache generation result."""
        key = self._hash_prompt(prompt)
        self.redis.setex(f"gen:{key}", self.ttl, result)
    
    def _hash_prompt(self, prompt: str) -> str:
        """Hash prompt for cache key (include version for cache invalidation)."""
        content = f"v2:{prompt}"  # Version prefix
        return hashlib.sha256(content.encode()).hexdigest()

# terraform_agent/generator.py
class TerraformGenerator:
    def __init__(self, config, prompts, kb):
        self.cache = GenerationCache(config.REDIS_URL)
        # ...
    
    def run(self, user_prompt: str):
        # Check cache first
        if cached := self.cache.get(user_prompt):
            logger.info("Using cached generation")
            return cached
        
        # Generate
        result = self._generate(user_prompt)
        
        # Cache successful generations
        if result.success:
            self.cache.set(user_prompt, result)
        
        return result
```

**Batching pour évaluations:**

```python
# eval/batch_harness.py
import asyncio
from anthropic import AsyncAnthropic

async def evaluate_batch(test_cases: list[TestCase]):
    """Evaluate multiple test cases in parallel."""
    
    client = AsyncAnthropic()
    
    # Run 5 evaluations in parallel
    tasks = [
        evaluate_async(client, tc)
        for tc in test_cases
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return results

# Cost reduction: ~40% via caching + batching
```

**Livrables:**
- [ ] Redis cache pour générations
- [ ] Cache hit rate > 30% après warmup
- [ ] Batching async pour évaluations
- [ ] Cost dashboard ($/génération)

**Effort estimé:** 1 semaine, 1 développeur

---

### 5.2 Parallélisation & Scalabilité Horizontale

**État actuel:**
- ⚠️  1 génération à la fois (synchrone)
- ⚠️  ChromaDB local (single node)

**Actions:**

```python
# terraform_agent/api.py
from fastapi import FastAPI, BackgroundTasks
from celery import Celery

app = FastAPI()
celery = Celery('terraform-agent', broker='redis://localhost:6379/0')

@celery.task
def generate_terraform_async(prompt: str, user_id: str):
    """Async Terraform generation with Celery."""
    generator = TerraformGenerator(config, prompts, kb)
    result = generator.run(prompt)
    
    # Store result in database
    db.save_generation(user_id, prompt, result)
    
    # Send notification
    notify_user(user_id, result)
    
    return result

@app.post("/generate")
async def generate(request: GenerationRequest, background_tasks: BackgroundTasks):
    """
    Async API endpoint for Terraform generation.
    
    Returns immediately with job_id, client polls for completion.
    """
    job_id = str(uuid.uuid4())
    
    # Enqueue task
    task = generate_terraform_async.delay(
        request.prompt,
        request.user_id
    )
    
    return {
        "job_id": job_id,
        "task_id": task.id,
        "status": "pending"
    }

@app.get("/generate/{job_id}")
async def get_generation(job_id: str):
    """Poll generation status."""
    task = celery.AsyncResult(job_id)
    
    if task.ready():
        return {
            "status": "completed",
            "result": task.result
        }
    
    return {"status": "pending"}
```

**ChromaDB en mode cluster:**

```yaml
# docker-compose.yml
services:
  chroma-frontend:
    image: chromadb/chroma:latest
    environment:
      - CHROMA_SERVER_AUTH_PROVIDER=token
      - CHROMA_SERVER_AUTH_TOKEN_TRANSPORT_HEADER=X-Chroma-Token
    ports:
      - "8000:8000"
  
  chroma-worker-1:
    image: chromadb/chroma:latest
    environment:
      - CHROMA_WORKER_ID=worker-1
  
  chroma-worker-2:
    image: chromadb/chroma:latest
    environment:
      - CHROMA_WORKER_ID=worker-2
```

**Load balancing:**

```nginx
# nginx.conf
upstream terraform_agents {
    least_conn;
    server agent-1:8000;
    server agent-2:8000;
    server agent-3:8000;
}

server {
    listen 80;
    
    location /generate {
        proxy_pass http://terraform_agents;
        proxy_timeout 600s;
    }
}
```

**Livrables:**
- [ ] API REST async avec FastAPI
- [ ] Queue Celery + Redis
- [ ] ChromaDB en mode cluster (3+ nodes)
- [ ] Load balancer nginx/Envoy
- [ ] Auto-scaling (Kubernetes HPA)

**Effort estimé:** 2-3 semaines, 1 développeur + 1 DevOps

---

## 📚 Axe 6 : Documentation & Developer Experience

### 6.1 Documentation Technique Complète

**État actuel:**
- ✅ README.md complet
- ✅ CLAUDE.md pour contexte
- ❌ Pas de documentation API
- ❌ Pas de guides développeur

**Actions:**

```markdown
# docs/
├── architecture/
│   ├── adr/                           # Architecture Decision Records
│   │   ├── 001-model-routing.md
│   │   ├── 002-callbacks-vs-pipeline.md
│   │   └── 003-chromadb-backend.md
│   ├── diagrams/
│   │   ├── system-overview.mmd       # Mermaid diagrams
│   │   ├── data-flow.mmd
│   │   └── deployment.mmd
│   └── component-guide.md
│
├── api/
│   ├── openapi.yaml                  # OpenAPI 3.0 spec
│   ├── endpoints.md
│   └── authentication.md
│
├── developer-guide/
│   ├── getting-started.md
│   ├── contributing.md
│   ├── testing-guide.md
│   ├── debugging.md
│   └── release-process.md
│
├── operations/
│   ├── deployment.md
│   ├── monitoring.md
│   ├── disaster-recovery.md
│   └── cost-optimization.md
│
└── tutorials/
    ├── 01-first-generation.md
    ├── 02-custom-rules.md
    ├── 03-multi-cloud.md
    └── 04-ci-cd-integration.md
```

**OpenAPI Spec auto-générée:**

```python
# terraform_agent/api.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="Terraform Code Generation API",
    description="AI-powered Terraform code generation with best practices",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Terraform Agent API",
        version="1.0.0",
        routes=app.routes,
    )
    
    # Add authentication
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

**Livrables:**
- [ ] 50+ pages de documentation
- [ ] OpenAPI spec complète
- [ ] 10+ ADRs documentant décisions clés
- [ ] Interactive tutorials (Jupyter notebooks)
- [ ] Video walkthroughs (5 min each)

**Effort estimé:** 2 semaines, 1 tech writer + 1 développeur

---

### 6.2 Developer Tooling

**Actions:**

```toml
# pyproject.toml - Dev tools configuration
[tool.ruff]
line-length = 100
target-version = "py312"
select = ["E", "F", "I", "N", "W", "UP"]

[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --cov=terraform_agent --cov-report=term --cov-report=html"

[tool.coverage.run]
omit = ["tests/*", ".venv/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError"
]
```

```makefile
# Makefile - Developer commands
.PHONY: install test lint format clean

install:
	uv sync

test:
	uv run pytest tests/ -v

test-watch:
	uv run pytest-watch tests/

lint:
	uv run ruff check .
	uv run mypy terraform_agent/

format:
	uv run ruff format .
	uv run isort .

security:
	uv run bandit -r terraform_agent/
	uv run safety check

eval:
	uv run python -m eval.harness

clean:
	rm -rf .venv/ .pytest_cache/ .mypy_cache/ .ruff_cache/
	rm -rf work/* .vectorstore/
	find . -type d -name "__pycache__" -exec rm -rf {} +

docker-build:
	docker build -t terraform-agent:latest .

docker-run:
	docker-compose up -d

logs:
	docker-compose logs -f terraform-agent

benchmark:
	uv run python -m eval.benchmark --iterations=10
```

**Pre-commit hooks:**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        additional_dependencies: [types-redis]
  
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-ll]
```

**Livrables:**
- [ ] Makefile avec 15+ commandes
- [ ] Pre-commit hooks automatiques
- [ ] VS Code settings.json configuré
- [ ] Jupyter notebook templates
- [ ] CLI tool (`terraform-agent` command)

**Effort estimé:** 1 semaine, 1 développeur

---

## 🌐 Axe 7 : Multi-Cloud & Extensibilité

### 7.1 Support AWS & Azure

**État actuel:**
- ✅ GCP (Google Cloud Storage)
- ❌ AWS (S3, EC2, VPC, etc.)
- ❌ Azure (Blob Storage, VMs, etc.)

**Actions:**

```python
# terraform_agent/providers/
├── __init__.py
├── base.py                    # Abstract provider interface
├── gcp.py                     # Google Cloud Platform
├── aws.py                     # Amazon Web Services
└── azure.py                   # Microsoft Azure

# terraform_agent/providers/base.py
from abc import ABC, abstractmethod

class CloudProvider(ABC):
    """Abstract interface for cloud provider-specific logic."""
    
    @abstractmethod
    def get_storage_module_template(self) -> str:
        """Return Terraform template for object storage."""
        pass
    
    @abstractmethod
    def validate_naming(self, name: str) -> bool:
        """Validate resource name against provider rules."""
        pass
    
    @abstractmethod
    def get_best_practices(self) -> list[str]:
        """Return provider-specific best practices."""
        pass

# terraform_agent/providers/aws.py
class AWSProvider(CloudProvider):
    def get_storage_module_template(self) -> str:
        return """
resource "aws_s3_bucket" "this" {
  bucket = var.bucket_name
  
  tags = var.tags
}

resource "aws_s3_bucket_versioning" "this" {
  bucket = aws_s3_bucket.this.id
  
  versioning_configuration {
    status = var.versioning_enabled ? "Enabled" : "Disabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "this" {
  bucket = aws_s3_bucket.this.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
"""
    
    def validate_naming(self, name: str) -> bool:
        # AWS S3 bucket naming rules
        if len(name) < 3 or len(name) > 63:
            return False
        if not name.replace('-', '').replace('.', '').isalnum():
            return False
        return True
```

**Knowledge base multi-cloud:**

```markdown
# rules/aws/
├── s3-best-practices.md
├── ec2-security.md
├── vpc-networking.md
└── iam-policies.md

# rules/azure/
├── blob-storage.md
├── vm-best-practices.md
├── vnet-design.md
└── rbac-guidelines.md

# rules/multi-cloud/
├── cost-optimization.md
├── disaster-recovery.md
└── security-baseline.md
```

**Livrables:**
- [ ] AWS provider complet (S3, EC2, VPC, RDS)
- [ ] Azure provider complet (Storage, VMs, VNet)
- [ ] 50+ best practices par provider
- [ ] Tests d'intégration multi-cloud
- [ ] Documentation migration GCP→AWS

**Effort estimé:** 4-6 semaines, 2 développeurs

---

### 7.2 Plugin System pour Extensions

**Actions:**

```python
# terraform_agent/plugins/
├── __init__.py
├── base.py                    # Plugin interface
├── registry.py                # Plugin discovery
└── examples/
    ├── cost_estimator.py      # Infracost integration
    ├── security_scanner.py    # Checkov/tfsec
    └── drift_detector.py      # Terraform state diff

# terraform_agent/plugins/base.py
from abc import ABC, abstractmethod

class TerraformAgentPlugin(ABC):
    """Base class for agent plugins."""
    
    name: str
    version: str
    
    @abstractmethod
    def on_generation_start(self, prompt: str):
        """Hook called before code generation."""
        pass
    
    @abstractmethod
    def on_generation_end(self, code: str) -> dict:
        """
        Hook called after code generation.
        
        Returns:
            dict with plugin-specific results (e.g., cost estimate, security issues)
        """
        pass
    
    @abstractmethod
    def on_validation(self, validation_result: dict):
        """Hook called after Terraform validation."""
        pass

# terraform_agent/plugins/cost_estimator.py
from infracost import Infracost

class CostEstimatorPlugin(TerraformAgentPlugin):
    name = "cost-estimator"
    version = "1.0.0"
    
    def __init__(self):
        self.infracost = Infracost()
    
    def on_generation_end(self, code: str) -> dict:
        """Estimate monthly cost of generated infrastructure."""
        
        # Write Terraform to temp dir
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "main.tf").write_text(code)
            
            # Run infracost
            cost = self.infracost.breakdown(tmpdir)
        
        return {
            "monthly_cost_usd": cost.monthly_cost,
            "cost_breakdown": cost.resources,
            "recommendations": self._get_cost_optimizations(cost)
        }

# terraform_agent/generator.py
class TerraformGenerator:
    def __init__(self, config, prompts, kb, plugins: list[TerraformAgentPlugin] = None):
        self.plugins = plugins or []
        # ...
    
    def run(self, user_prompt: str):
        # Trigger plugin hooks
        for plugin in self.plugins:
            plugin.on_generation_start(user_prompt)
        
        result = self._generate(user_prompt)
        
        plugin_results = {}
        for plugin in self.plugins:
            plugin_results[plugin.name] = plugin.on_generation_end(result.code)
        
        return {
            "code": result.code,
            "plugins": plugin_results
        }
```

**Plugin configuration:**

```yaml
# config/plugins.yaml
plugins:
  - name: cost-estimator
    enabled: true
    config:
      currency: USD
      threshold_warning: 100  # Warn if > $100/month
  
  - name: security-scanner
    enabled: true
    config:
      scanners: [checkov, tfsec]
      severity_threshold: HIGH
  
  - name: compliance-checker
    enabled: false
    config:
      frameworks: [CIS, PCI-DSS]
```

**Livrables:**
- [ ] Plugin system avec 5+ hooks
- [ ] 3 plugins de référence (cost, security, drift)
- [ ] Plugin registry + marketplace
- [ ] Documentation plugin development
- [ ] Example plugins dans examples/

**Effort estimé:** 2-3 semaines, 1 développeur

---

## 📊 Priorisation & Roadmap

### Phase 1 : Fondations (0-3 mois)

**Priorité CRITIQUE:**
1. ✅ Tests unitaires (80%+ coverage)
2. ✅ CI/CD GitHub Actions
3. ✅ Containerisation Docker
4. ✅ Gestion secrets (Secret Manager)

**ROI:** Stabilité, confiance, déploiements automatisés

**Effort:** 8-10 semaines développeur

---

### Phase 2 : Production (3-6 mois)

**Priorité HAUTE:**
1. ✅ Monitoring & alerting (Prometheus, Grafana)
2. ✅ Distributed tracing (Jaeger)
3. ✅ API REST async + queue Celery
4. ✅ Cache Redis (30%+ hit rate)
5. ✅ Expansion suite d'évaluation (20+ test cases)

**ROI:** Fiabilité 99.9%, visibilité opérationnelle, scalabilité

**Effort:** 10-12 semaines développeur

---

### Phase 3 : Scale (6-12 mois)

**Priorité MOYENNE:**
1. ✅ Multi-cloud (AWS, Azure)
2. ✅ Plugin system
3. ✅ Documentation complète
4. ✅ Terraform sandboxing + remote state
5. ✅ Auto-scaling Kubernetes

**ROI:** Nouveaux marchés, extensibilité, sécurité renforcée

**Effort:** 16-20 semaines développeur

---

## 💰 Estimation Globale

| Phase | Durée | Effort (dev-weeks) | Coût (estimé) |
|-------|-------|-------------------|---------------|
| Phase 1 : Fondations | 3 mois | 8-10 | 40-50k€ |
| Phase 2 : Production | 3 mois | 10-12 | 50-60k€ |
| Phase 3 : Scale | 6 mois | 16-20 | 80-100k€ |
| **TOTAL** | **12 mois** | **34-42** | **170-210k€** |

*Hypothèses: 1 développeur full-time = 5k€/semaine, équipe de 2-3 personnes*

---

## 🎯 KPIs de Succès

### Qualité
- [ ] Test coverage > 80%
- [ ] Zero critical security vulnerabilities
- [ ] Mean time to recovery (MTTR) < 1h

### Performance
- [ ] P95 latency < 120s pour génération
- [ ] Cache hit rate > 30%
- [ ] Cost per generation < $0.50

### Fiabilité
- [ ] Uptime > 99.9%
- [ ] Error rate < 1%
- [ ] Successful generations > 95%

### Scalabilité
- [ ] Support 100+ concurrent users
- [ ] Handle 10k+ generations/day
- [ ] Auto-scale 0→10 instances in < 2min

---

## 🚀 Prochaines Étapes Immédiates

**Semaine 1-2:**
1. Setup structure tests pytest
2. Implémenter 20+ tests unitaires critiques
3. Configurer GitHub Actions CI basique

**Semaine 3-4:**
1. Dockerfile + docker-compose
2. Intégration Secret Manager
3. Premiers dashboards Grafana

**Review:**
- [ ] Code review avec équipe
- [ ] Validation architecture avec CTO
- [ ] Budget approval pour Phase 1

---

**Document créé le:** 2026-05-12  
**Auteur:** Claude Sonnet 4.5 (via mehdi el kouhen)  
**Version:** 1.0  
**Statut:** Draft → À valider avec équipe produit
