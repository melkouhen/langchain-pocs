# Terraform Rules Index

**Version:** 1.1  
**Last Updated:** 2026-05-12  
**Total Rules:** 24 (1 doublon supprimé)

---

## Rules by Severity

### CRITICAL (14 règles)

> **Note:** TF-REMOTE-STATE-008 a été supprimé car il était un doublon de TF-BACKEND-STATE-003
| ID | Title | Category | File |
|----|-------|----------|------|
| GCS-BUCKET-SYNTAX-001 | GCS Bucket Block vs Argument Syntax | Code Quality | rule-gcs-bucket-syntax.md |
| GCS-INPUT-002 | Module Input Types: Map vs Scalar | Code Quality | rule-gcs-input-types.md |
| GCS-NAMING-UBLA-001 | GCS Bucket Naming Convention and UBLA | Naming & Security | rule-gcs-naming-ubla.md |
| GCS-PROVIDER-001 | GCS Module Provider Version Constraint | Compatibility | rule-gcs-provider-version.md |
| TF-ALWAYS-PLAN-013 | Always Review Plan Before Apply | Best Practice | rule-tf-always-plan.md |
| TF-BACKEND-STATE-003 | Remote State Backend via GCS | State Management | rule-tf-backend-state.md |
| TF-ENV-001 | Environment Configurations Must Not Declare Resources | Structure | rule-tf-env-composition.md |
| TF-ENV-ISOLATION-002 | Environment Isolation: Separate Directories and State | Infrastructure | rule-tf-env-isolation.md |
| TF-ENV-ISOLATION-005 | Environment Isolation: Separate Backends & State | Security | rule-tf-env-isolation-backend.md |
| TF-ENV-SEPARATION-004 | Environment Separation: Folders vs Workspaces | Architecture | rule-tf-env-separation.md |
| TF-NO-HARDCODED-SECRETS-009 | No Hardcoded Secrets | Security | rule-tf-no-hardcoded-secrets.md |
| TF-STATE-DELETION-009 | Never Delete State Files Directly | Safety | rule-tf-state-deletion.md |
| TF-STRUCTURE-001 | Project Layout Organization | Architecture | rule-tf-structure.md |
| TF-VERSION-PINNING-006 | Version Pinning: Providers & Terraform | Reliability | rule-tf-version-pinning.md |

### MAJOR (10 règles)
| ID | Title | Category | File |
|----|-------|----------|------|
| TF-AVOID-HARDCODING-011 | Avoid Hardcoding: Use Variables & Locals | Code Quality | rule-tf-avoid-hardcoding.md |
| TF-CI-CD-INTEGRATION-012 | CI/CD Integration: Format, Validate, Plan | Automation | rule-tf-cicd-integration.md |
| TF-MODULES-002 | Module Creation Criteria (DRY Principle) | Code Quality | rule-tf-modules-dry.md |
| TF-MODULES-003 | Module Scope: Shallow & Focused | Code Quality | rule-tf-modules-scope.md |
| TF-PROVIDER-LOCKING-007 | Provider Lock Files: Commit .terraform.lock.hcl | Reliability | rule-tf-provider-locking.md |
| TF-RESOURCE-NAMING-010 | Resource Naming Convention | Code Quality | rule-tf-resource-naming.md |
| TF-STATE-DRIFT-010 | State Drift Detection: Regular Plan Runs | Monitoring | rule-tf-state-drift.md |

---

## Rules by Category

### Architecture (4)
- TF-ENV-SEPARATION-004 (CRITICAL) — Environment Separation: Folders vs Workspaces
- TF-REMOTE-STATE-008 (CRITICAL) — Remote State Backend: Never Local State
- TF-STRUCTURE-001 (CRITICAL) — Project Layout Organization

### Automation (1)
- TF-CI-CD-INTEGRATION-012 (MAJOR) — CI/CD Integration: Format, Validate, Plan

### Best Practice (1)
- TF-ALWAYS-PLAN-013 (CRITICAL) — Always Review Plan Before Apply

### Code Quality (6)
- GCS-BUCKET-SYNTAX-001 (CRITICAL) — GCS Bucket Block vs Argument Syntax
- GCS-INPUT-002 (CRITICAL) — Module Input Types: Map vs Scalar
- TF-AVOID-HARDCODING-011 (MAJOR) — Avoid Hardcoding: Use Variables & Locals
- TF-MODULES-002 (MAJOR) — Module Creation Criteria (DRY Principle)
- TF-MODULES-003 (MAJOR) — Module Scope: Shallow & Focused
- TF-RESOURCE-NAMING-010 (MAJOR) — Resource Naming Convention

### Compatibility (1)
- GCS-PROVIDER-001 (CRITICAL) — GCS Module Provider Version Constraint

### Infrastructure (1)
- TF-ENV-ISOLATION-002 (CRITICAL) — Environment Isolation: Separate Directories and State

### Monitoring (1)
- TF-STATE-DRIFT-010 (MAJOR) — State Drift Detection: Regular Plan Runs

### Naming & Security (1)
- GCS-NAMING-UBLA-001 (CRITICAL) — GCS Bucket Naming Convention and UBLA

### Reliability (2)
- TF-PROVIDER-LOCKING-007 (MAJOR) — Provider Lock Files: Commit .terraform.lock.hcl
- TF-VERSION-PINNING-006 (CRITICAL) — Version Pinning: Providers & Terraform

### Safety (1)
- TF-STATE-DELETION-009 (CRITICAL) — Never Delete State Files Directly

### Security (2)
- TF-ENV-ISOLATION-005 (CRITICAL) — Environment Isolation: Separate Backends & State
- TF-NO-HARDCODED-SECRETS-009 (CRITICAL) — No Hardcoded Secrets

### State Management (1)
- TF-BACKEND-STATE-003 (CRITICAL) — Remote State Backend via GCS

### Structure (1)
- TF-ENV-001 (CRITICAL) — Environment Configurations Must Not Declare Resources

---

## Rules by Prefix

### GCS (Google Cloud Storage) — 4 rules
- GCS-BUCKET-SYNTAX-001, GCS-INPUT-002, GCS-NAMING-UBLA-001, GCS-PROVIDER-001

### TF (Terraform General) — 21 rules
- All other rules

---

## Usage

### For Developers
Browse rules by:
- **Severity**: Start with CRITICAL rules (14 total)
- **Category**: Find rules relevant to your work (e.g., Security, Architecture)
- **Prefix**: Filter by technology (GCS, TF)

### For Agent/Knowledge Base
All rules are indexed in ChromaDB. Search by:
- Rule ID (e.g., "TF-STRUCTURE-001")
- Keywords (e.g., "state management", "environment isolation")
- Category or severity

### Rule Format
Each rule file contains:
- **XML structure** with `<rule>` tag
- **Severity** attribute (CRITICAL, MAJOR, MINOR)
- **Category** attribute
- **Sections**: description, problem, pattern (correct), antipattern (incorrect), why, validation, when-to-apply, implementation-checklist, related-rules, references

---

## Statistics

| Metric | Value |
|--------|-------|
| Total Rules | 24 |
| CRITICAL | 14 (58%) |
| MAJOR | 10 (42%) |
| MINOR | 0 (0%) |
| Categories | 13 |
| Average Checklist Items | 8-12 per rule |

---

## Maintenance

**Adding a new rule:**
1. Create `rule-{prefix}-{name}.md` in `rules/`
2. Follow XML format from `RULES_FORMAT.md`
3. Add entry to this index (sorted by ID)
4. Update statistics

**Modifying severity:**
1. Update `severity` attribute in rule file
2. Update this index
3. Re-run knowledge base indexing

**Generated:** 2026-05-12 by Claude Sonnet 4.5
