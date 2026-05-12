# Terraform Rules Index

**Version:** 2.2  
**Last Updated:** 2026-05-12  
**Total Rules:** 25  
**Total Categories:** 5

---

## Rules by Severity

### CRITICAL (18 règles)

| ID | Title | Category | File |
|----|-------|----------|------|
| CLOUDRUN-INGRESS-SECURITY | Restrict Ingress to Minimum Required Access | Security | rule-cloudrun-ingress-security.md |
| CLOUDRUN-MODULE-USAGE | Use Official GoogleCloudPlatform/cloud-run/google Module | Code Quality | rule-cloudrun-module-usage.md |
| CLOUDRUN-SECRETS-MANAGEMENT | Use Secret Manager for Sensitive Environment Variables | Security | rule-cloudrun-secrets-management.md |
| GCS-BUCKET-SYNTAX | Distinguish GCS Bucket Block vs Argument Syntax | Code Quality | rule-gcs-bucket-syntax.md |
| GCS-INPUT-TYPES | Module Input Types: Map vs Scalar | Code Quality | rule-gcs-input-types.md |
| GCS-MODULE-USAGE | Use Official terraform-google-modules/cloud-storage/google Module | Code Quality | rule-gcs-module-usage.md |
| GCS-NAMING-UBLA | GCS Bucket Naming Convention and Uniform Bucket-Level Access | Security | rule-gcs-naming-ubla.md |
| GCS-PROVIDER-VERSION | GCS Module Provider Version Constraint | Code Quality | rule-gcs-provider-version.md |
| TF-ALWAYS-PLAN | Always Review Plan Before Apply | Operations | rule-tf-always-plan.md |
| TF-BACKEND-STATE | Remote State Management via GCS Backend | State Management | rule-tf-backend-state.md |
| TF-ENV-COMPOSITION | Environment Configurations Must Not Declare Cloud Resources Directly | Architecture | rule-tf-env-composition.md |
| TF-ENV-ISOLATION | Environment Isolation: Separate Directories and State Files | Architecture | rule-tf-env-isolation.md |
| TF-ENV-ISOLATION-BACKEND | Environment Isolation: Separate Backends & State | Security | rule-tf-env-isolation-backend.md |
| TF-ENV-SEPARATION | Environment Separation: Folders vs Workspaces | Architecture | rule-tf-env-separation.md |
| TF-NO-SECRETS | No Hardcoded Secrets | Security | rule-tf-no-hardcoded-secrets.md |
| TF-STATE-DELETION | Never Delete State Files Directly | Security | rule-tf-state-deletion.md |
| TF-STRUCTURE | Project Layout Organization | Architecture | rule-tf-structure.md |
| TF-VERSION-PINNING | Version Pinning: Providers & Terraform | State Management | rule-tf-version-pinning.md |

### MAJOR (7 règles)

| ID | Title | Category | File |
|----|-------|----------|------|
| TF-AVOID-HARDCODING | Avoid Hardcoding: Use Variables & Locals | Code Quality | rule-tf-avoid-hardcoding.md |
| TF-CICD | CI/CD Integration: Format, Validate, Plan | Operations | rule-tf-cicd-integration.md |
| TF-MODULES-DRY | Module Creation Criteria (DRY Principle) | Code Quality | rule-tf-modules-dry.md |
| TF-MODULES-SCOPE | Module Scope: Shallow & Focused | Code Quality | rule-tf-modules-scope.md |
| TF-PROVIDER-LOCKING | Provider Lock Files: Commit .terraform.lock.hcl | State Management | rule-tf-provider-locking.md |
| TF-RESOURCE-NAMING | Resource Naming Convention | Code Quality | rule-tf-resource-naming.md |
| TF-STATE-DRIFT | State Drift Detection: Regular Plan Runs | Operations | rule-tf-state-drift.md |

---

## Rules by Category

### Architecture (4 règles)

| ID | Severity | Title |
|----|----------|-------|
| TF-ENV-COMPOSITION | CRITICAL | Environment Configurations Must Not Declare Cloud Resources Directly |
| TF-ENV-ISOLATION | CRITICAL | Environment Isolation: Separate Directories and State Files |
| TF-ENV-SEPARATION | CRITICAL | Environment Separation: Folders vs Workspaces |
| TF-STRUCTURE | CRITICAL | Project Layout Organization |

**Principes:** Structure 3-tiers (modules/ + envs/ + global/), séparation environnements, composition via modules

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

### Code Quality (9 règles)

| ID | Severity | Title |
|----|----------|-------|
| CLOUDRUN-MODULE-USAGE | CRITICAL | Use Official GoogleCloudPlatform/cloud-run/google Module |
| GCS-BUCKET-SYNTAX | CRITICAL | Distinguish GCS Bucket Block vs Argument Syntax |
| GCS-INPUT-TYPES | CRITICAL | Module Input Types: Map vs Scalar |
| GCS-MODULE-USAGE | CRITICAL | Use Official terraform-google-modules/cloud-storage/google Module |
| GCS-PROVIDER-VERSION | CRITICAL | GCS Module Provider Version Constraint |
| TF-AVOID-HARDCODING | MAJOR | Avoid Hardcoding: Use Variables & Locals |
| TF-MODULES-DRY | MAJOR | Module Creation Criteria (DRY Principle) |
| TF-MODULES-SCOPE | MAJOR | Module Scope: Shallow & Focused |
| TF-RESOURCE-NAMING | MAJOR | Resource Naming Convention |

**Principes:** Utilisation des modules officiels (Cloud Run, GCS), syntaxe correcte, types appropriés, modules DRY et shallow, paramétrage via variables

---

### Operations (3 règles)

| ID | Severity | Title |
|----|----------|-------|
| TF-ALWAYS-PLAN | CRITICAL | Always Review Plan Before Apply |
| TF-CICD | MAJOR | CI/CD Integration: Format, Validate, Plan |
| TF-STATE-DRIFT | MAJOR | State Drift Detection: Regular Plan Runs |

**Principes:** Plan avant apply, CI/CD pipelines, drift detection régulière

---

## Rules by Prefix

### GCS (Google Cloud Storage) — 4 rules
| ID | Severity | Category |
|----|----------|----------|
| GCS-BUCKET-SYNTAX | CRITICAL | Code Quality |
| GCS-INPUT-TYPES | CRITICAL | Code Quality |
| GCS-NAMING-UBLA | CRITICAL | Security |
| GCS-PROVIDER-VERSION | CRITICAL | Code Quality |

### TF (Terraform General) — 17 rules
All other rules covering architecture, state management, operations, and code quality

---

## Statistics

### Global

| Metric | Value |
|--------|-------|
| Total Rules | 25 |
| CRITICAL | 18 (72%) |
| MAJOR | 7 (28%) |
| MINOR | 0 (0%) |
| Categories | 5 |

### By Category + Severity

| Catégorie | CRITICAL | MAJOR | Total |
|-----------|----------|-------|-------|
| Architecture | 4 | 0 | 4 |
| Security | 6 | 0 | 6 |
| State Management | 2 | 1 | 3 |
| Code Quality | 5 | 4 | 9 |
| Operations | 1 | 2 | 3 |
| **Total** | **18** | **7** | **25** |

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
