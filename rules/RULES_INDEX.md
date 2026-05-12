# Terraform Rules Index

**Version:** 2.4  
**Last Updated:** 2026-05-12  
**Total Rules:** 25  
**Total Categories:** 5  
**Scopes:** 3 (cloudrun, gcs, global)

---

## Rules by Severity

### CRITICAL (16 règles)

| ID | Title | Scope | Category | File |
|----|-------|-------|----------|------|
| CLOUDRUN-INGRESS-SECURITY | Restrict Ingress to Minimum Required Access | cloudrun | Security | rule-cloudrun-ingress-security.md |
| CLOUDRUN-MODULE-USAGE | Use Official GoogleCloudPlatform/cloud-run/google Module | cloudrun | Architecture | rule-cloudrun-module-usage.md |
| CLOUDRUN-SECRETS-MANAGEMENT | Use Secret Manager for Sensitive Environment Variables | cloudrun | Security | rule-cloudrun-secrets-management.md |
| GCS-MODULE-USAGE | Use Official terraform-google-modules/cloud-storage/google Module | gcs | Architecture | rule-gcs-module-usage.md |
| GCS-NAMING-UBLA | GCS Bucket Naming Convention and Uniform Bucket-Level Access | gcs | Security | rule-gcs-naming-ubla.md |
| GCS-PROVIDER-VERSION | GCS Module Provider Version Constraint | gcs | Code Quality | rule-gcs-provider-version.md |
| TF-ALWAYS-PLAN | Always Review Plan Before Apply | global | Operations | rule-tf-always-plan.md |
| TF-BACKEND-STATE | Remote State Management via GCS Backend | global | State Management | rule-tf-backend-state.md |
| TF-ENV-COMPOSITION | Environment Configurations Must Not Declare Cloud Resources Directly | global | Architecture | rule-tf-env-composition.md |
| TF-ENV-ISOLATION | Environment Isolation: Separate Directories and State Files | global | Architecture | rule-tf-env-isolation.md |
| TF-ENV-ISOLATION-BACKEND | Environment Isolation: Separate Backends & State | global | Security | rule-tf-env-isolation-backend.md |
| TF-ENV-SEPARATION | Environment Separation: Folders vs Workspaces | global | Architecture | rule-tf-env-separation.md |
| TF-NO-SECRETS | No Hardcoded Secrets | global | Security | rule-tf-no-hardcoded-secrets.md |
| TF-STATE-DELETION | Never Delete State Files Directly | global | Security | rule-tf-state-deletion.md |
| TF-STRUCTURE | Project Layout Organization | global | Architecture | rule-tf-structure.md |
| TF-VERSION-PINNING | Version Pinning: Providers & Terraform | global | State Management | rule-tf-version-pinning.md |

### MAJOR (8 règles)

| ID | Title | Scope | Category | File |
|----|-------|-------|----------|------|
| GCS-BUCKET-SYNTAX | Distinguish GCS Bucket Block vs Argument Syntax | gcs | Code Quality | rule-gcs-bucket-syntax.md |
| GCS-INPUT-TYPES | Module Input Types: Map vs Scalar | gcs | Code Quality | rule-gcs-input-types.md |
| TF-AVOID-HARDCODING | Avoid Hardcoding: Use Variables & Locals | global | Code Quality | rule-tf-avoid-hardcoding.md |
| TF-CICD | CI/CD Integration: Format, Validate, Plan | global | Operations | rule-tf-cicd-integration.md |
| TF-MODULES-DRY | Module Creation Criteria (DRY Principle) | global | Code Quality | rule-tf-modules-dry.md |
| TF-MODULES-SCOPE | Module Scope: Shallow & Focused | global | Code Quality | rule-tf-modules-scope.md |
| TF-PROVIDER-LOCKING | Provider Lock Files: Commit .terraform.lock.hcl | global | State Management | rule-tf-provider-locking.md |
| TF-RESOURCE-NAMING | Resource Naming Convention | global | Code Quality | rule-tf-resource-naming.md |

### MINOR (1 règle)

| ID | Title | Scope | Category | File |
|----|-------|-------|----------|------|
| TF-STATE-DRIFT | State Drift Detection: Regular Plan Runs | global | Operations | rule-tf-state-drift.md |

---

## Rules by Category

### Architecture (6 règles)

| ID | Severity | Title |
|----|----------|-------|
| CLOUDRUN-MODULE-USAGE | CRITICAL | Use Official GoogleCloudPlatform/cloud-run/google Module |
| GCS-MODULE-USAGE | CRITICAL | Use Official terraform-google-modules/cloud-storage/google Module |
| TF-ENV-COMPOSITION | CRITICAL | Environment Configurations Must Not Declare Cloud Resources Directly |
| TF-ENV-ISOLATION | CRITICAL | Environment Isolation: Separate Directories and State Files |
| TF-ENV-SEPARATION | CRITICAL | Environment Separation: Folders vs Workspaces |
| TF-STRUCTURE | CRITICAL | Project Layout Organization |

**Principes:** Structure 3-tiers (modules/ + envs/ + global/), séparation environnements, composition via modules, utilisation modules officiels

---

### Security (6 règles)

| ID | Severity | Title |
|----|----------|-------|
| CLOUDRUN-INGRESS-SECURITY | CRITICAL | Restrict Ingress to Minimum Required Access |
| CLOUDRUN-SECRETS-MANAGEMENT | CRITICAL | Use Secret Manager for Sensitive Environment Variables |
| GCS-NAMING-UBLA | CRITICAL | GCS Bucket Naming Convention and Uniform Bucket-Level Access |
| TF-ENV-ISOLATION-BACKEND | CRITICAL | Environment Isolation: Separate Backends & State |
| TF-NO-SECRETS | CRITICAL | No Hardcoded Secrets |
| TF-STATE-DELETION | CRITICAL | Never Delete State Files Directly |

**Principes:** Pas de secrets hardcodés, backends séparés, nommage DNS-compliant, protection state files, ingress restrictif, Secret Manager pour Cloud Run

---

### State Management (3 règles)

| ID | Severity | Title |
|----|----------|-------|
| TF-BACKEND-STATE | CRITICAL | Remote State Management via GCS Backend |
| TF-PROVIDER-LOCKING | MAJOR | Provider Lock Files: Commit .terraform.lock.hcl |
| TF-VERSION-PINNING | CRITICAL | Version Pinning: Providers & Terraform |

**Principes:** State remote (GCS), versions pinnées, lock files committés

---

### Code Quality (7 règles)

| ID | Severity | Title |
|----|----------|-------|
| GCS-BUCKET-SYNTAX | MAJOR | Distinguish GCS Bucket Block vs Argument Syntax |
| GCS-INPUT-TYPES | MAJOR | Module Input Types: Map vs Scalar |
| GCS-PROVIDER-VERSION | CRITICAL | GCS Module Provider Version Constraint |
| TF-AVOID-HARDCODING | MAJOR | Avoid Hardcoding: Use Variables & Locals |
| TF-MODULES-DRY | MAJOR | Module Creation Criteria (DRY Principle) |
| TF-MODULES-SCOPE | MAJOR | Module Scope: Shallow & Focused |
| TF-RESOURCE-NAMING | MAJOR | Resource Naming Convention |

**Principes:** Syntaxe correcte, types appropriés, version pinning, modules DRY et shallow, paramétrage via variables

---

### Operations (3 règles)

| ID | Severity | Title |
|----|----------|-------|
| TF-ALWAYS-PLAN | CRITICAL | Always Review Plan Before Apply |
| TF-CICD | MAJOR | CI/CD Integration: Format, Validate, Plan |
| TF-STATE-DRIFT | MINOR | State Drift Detection: Regular Plan Runs |

**Principes:** Plan avant apply (CRITICAL), CI/CD pipelines (MAJOR), drift detection (MINOR - monitoring)

---

## Rules by Scope

### Cloud Run (cloudrun) — 3 rules
| ID | Severity | Category |
|----|----------|----------|
| CLOUDRUN-INGRESS-SECURITY | CRITICAL | Security |
| CLOUDRUN-MODULE-USAGE | CRITICAL | Architecture |
| CLOUDRUN-SECRETS-MANAGEMENT | CRITICAL | Security |

**Scope:** Google Cloud Run services (containerized applications)

---

### Cloud Storage (gcs) — 5 rules
| ID | Severity | Category |
|----|----------|----------|
| GCS-BUCKET-SYNTAX | MAJOR | Code Quality |
| GCS-INPUT-TYPES | MAJOR | Code Quality |
| GCS-MODULE-USAGE | CRITICAL | Architecture |
| GCS-NAMING-UBLA | CRITICAL | Security |
| GCS-PROVIDER-VERSION | CRITICAL | Code Quality |

**Scope:** Google Cloud Storage buckets and objects

---

### Global (global) — 17 rules
All Terraform general rules covering architecture, state management, operations, and code quality.
Applicable to all resources and project structure regardless of GCP service.

| ID | Severity | Category |
|----|----------|----------|
| TF-ALWAYS-PLAN | CRITICAL | Operations |
| TF-AVOID-HARDCODING | MAJOR | Code Quality |
| TF-BACKEND-STATE | CRITICAL | State Management |
| TF-CICD | MAJOR | Operations |
| TF-ENV-COMPOSITION | CRITICAL | Architecture |
| TF-ENV-ISOLATION | CRITICAL | Architecture |
| TF-ENV-ISOLATION-BACKEND | CRITICAL | Security |
| TF-ENV-SEPARATION | CRITICAL | Architecture |
| TF-MODULES-DRY | MAJOR | Code Quality |
| TF-MODULES-SCOPE | MAJOR | Code Quality |
| TF-NO-SECRETS | CRITICAL | Security |
| TF-PROVIDER-LOCKING | MAJOR | State Management |
| TF-RESOURCE-NAMING | MAJOR | Code Quality |
| TF-STATE-DELETION | CRITICAL | Security |
| TF-STATE-DRIFT | MINOR | Operations |
| TF-STRUCTURE | CRITICAL | Architecture |
| TF-VERSION-PINNING | CRITICAL | State Management |

---

## Statistics

### Global

| Metric | Value |
|--------|-------|
| Total Rules | 25 |
| CRITICAL | 16 (64%) |
| MAJOR | 8 (32%) |
| MINOR | 1 (4%) |
| Categories | 5 |

### By Category + Severity

| Catégorie | CRITICAL | MAJOR | MINOR | Total |
|-----------|----------|-------|-------|-------|
| Architecture | 6 | 0 | 0 | 6 |
| Security | 6 | 0 | 0 | 6 |
| State Management | 2 | 1 | 0 | 3 |
| Code Quality | 1 | 6 | 0 | 7 |
| Operations | 1 | 1 | 1 | 3 |
| **Total** | **16** | **8** | **1** | **25** |

---

## Usage

### For Developers

**Priorité 1 — CRITICAL (14 règles):**
1. Architecture (4) — structure du projet
2. Security (4) — credentials et isolation  
3. State Management (2) — backend et versioning
4. Code Quality (3) + Operations (1)

**Priorité 2 — MAJOR (7 règles):**
- Appliquer progressivement pour qualité et ops

### For Agent/Knowledge Base

Stratégie de recherche:
1. Identifier catégorie du problème
2. Rechercher règles de cette catégorie avec `search_knowledge_base()`
3. Appliquer patterns corrects
4. Valider avec checklist de la règle

**Exemples de requêtes:**
- `"security google_storage_bucket"` → trouve GCS-NAMING-UBLA
- `"state management backend"` → trouve TF-BACKEND-STATE
- `"architecture environment separation"` → trouve TF-ENV-SEPARATION

### Rule Format

Chaque fichier de règle contient:
- **Balise XML** `<rule id="..." severity="..." category="...">`
- **Sections obligatoires**: `<title>`, `<description>`, `<context>`, `<problem>`, `<pattern>`, `<antipattern>`, `<why>`, `<validation>`, `<when-to-apply>`, `<implementation-checklist>`, `<related-rules>`, `<references>`

---

## Maintenance

### Adding a new rule
1. Create `rule-{prefix}-{name}.md` in `rules/`
2. Follow XML format from `RULES_FORMAT.md`
3. Use one of 5 categories: Architecture, Security, State Management, Code Quality, Operations
4. Add entry to this index (sorted by ID)
5. Update statistics

### Modifying a rule
1. Update rule file
2. If severity or category changes, update this index
3. Re-index knowledge base if needed

### Deleting a rule
1. Remove rule file from `rules/`
2. Remove entries from this index
3. Update statistics
4. Re-index knowledge base

---

## Version History

**v2.0 (2026-05-12):**
- Consolidated 13 categories into 5 main categories
- Updated all 21 rules with new category structure
- Improved semantic clarity and navigation

**v1.1 (Previous):**
- 13 categories (too granular)
- Removed duplicate TF-REMOTE-STATE-008

**v1.0 (Initial):**
- First version with 24 rules

---

**Generated:** 2026-05-12  
**By:** Claude Sonnet 4.5  
**Version:** 2.0
