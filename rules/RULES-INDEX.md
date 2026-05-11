# Terraform Best Practices Rules Index

## 📚 Overview

This index provides quick access to all 16 Terraform best practices rules, organized by category and severity.

**Format**: All rules use XML-Markdown structure (see `terraform-system.md` for details)

---

## 🏗️ Project Structure & Modules (3 rules)

### [TF-STRUCTURE-001: Project Layout Organization](rules-tf-project-structure.md#tf-structure-001)
**Severity**: 🔴 MAJOR | **Category**: Architecture

Three-tier structure: `modules/` (reusable), `envs/` (environment-specific), `global/` (shared).

**Why**: Scalability, clear separation of concerns, team collaboration.

---

### [TF-MODULES-002: Module Creation Criteria](rules-tf-project-structure.md#tf-modules-002)
**Severity**: 🟠 MAJOR | **Category**: Code Quality

Create a module only when code is used in 2+ places. Avoid premature abstraction.

**Why**: Keep It Simple (KISS), reduce maintenance burden.

---

### [TF-MODULES-003: Module Scope (Shallow & Focused)](rules-tf-project-structure.md#tf-modules-003)
**Severity**: 🟠 MAJOR | **Category**: Code Quality

Keep modules shallow (max 1-2 levels), one resource group per module.

**Why**: Easier to understand, debug, test, and navigate.

---

## 🌍 Environment Management (2 rules)

### [TF-ENV-SEPARATION-004: Folders vs Workspaces](rules-tf-environments.md#tf-env-separation-004)
**Severity**: 🔴 CRITICAL | **Category**: Architecture

Use folder-based separation (`envs/dev/`, `envs/prod/`), never workspaces for team projects.

**Why**: Safety, auditability, prevents accidental cross-env deployments.

---

### [TF-ENV-ISOLATION-005: Separate Backends & State](rules-tf-environments.md#tf-env-isolation-005)
**Severity**: 🔴 CRITICAL | **Category**: Security

Each environment has completely separate backend, state file, and ideally separate cloud projects.

**Why**: Production safety, prevent single-point failures, enable per-env permissions.

---

## 📌 Versioning & State Management (4 rules)

### [TF-VERSION-PINNING-006: Version Pinning](rules-tf-state-versioning.md#tf-version-pinning-006)
**Severity**: 🔴 CRITICAL | **Category**: Reliability

Pin Terraform and all providers: `required_version = "~> 1.9"`, `google = "~> 6.0"`.

**Why**: Reproducibility, prevent drift between environments, enable security patches.

---

### [TF-PROVIDER-LOCKING-007: Provider Lock Files](rules-tf-state-versioning.md#tf-provider-locking-007)
**Severity**: 🟠 MAJOR | **Category**: Reliability

Always commit `.terraform.lock.hcl` to version control.

**Why**: Team members use identical provider versions, prevents "works on my machine".

---

### [TF-REMOTE-STATE-008: Remote Backend](rules-tf-state-versioning.md#tf-remote-state-008)
**Severity**: 🔴 CRITICAL | **Category**: Architecture

Use remote backends (GCS, S3), never local state files for team projects.

**Why**: Security (no credentials on laptop), collaboration (locking), backup/versioning.

---

### [TF-STATE-DELETION-009: State File Safety](rules-tf-naming-state.md#tf-state-deletion-009)
**Severity**: 🔴 CRITICAL | **Category**: Safety

Never manually delete/modify `.tfstate` files. Use `terraform destroy` or `terraform state rm`.

**Why**: Prevent orphaned resources, state corruption, infrastructure inconsistency.

---

## 🔒 Security & CI/CD (4 rules)

### [TF-NO-HARDCODED-SECRETS-009: No Hardcoded Secrets](rules-tf-security-cicd.md#tf-no-hardcoded-secrets-009)
**Severity**: 🔴 CRITICAL | **Category**: Security

Never hardcode passwords, API keys, or credentials. Use variables, secret managers, environment variables.

**Why**: Secrets in Git = permanent exposure, compliance violations (HIPAA, PCI-DSS).

---

### [TF-AVOID-HARDCODING-011: Parameterize Configuration](rules-tf-security-cicd.md#tf-avoid-hardcoding-011)
**Severity**: 🟠 MAJOR | **Category**: Code Quality

Never hardcode region, project IDs, AMI IDs. Use variables and locals.

**Why**: Reusability, maintainability, prevent cross-env mistakes.

---

### [TF-CI-CD-INTEGRATION-012: Automated Validation](rules-tf-security-cicd.md#tf-ci-cd-integration-012)
**Severity**: 🟠 MAJOR | **Category**: Automation

Automate in CI/CD: `terraform fmt`, `terraform validate`, `terraform plan`, approval gate.

**Why**: Prevent syntax errors, invalid code reaching production, enable auditing.

---

### [TF-ALWAYS-PLAN-013: Review Plan Before Apply](rules-tf-security-cicd.md#tf-always-plan-013)
**Severity**: 🔴 CRITICAL | **Category**: Best Practice

Never run `terraform apply` without reviewing `terraform plan` first.

**Why**: Safety net to catch mistakes (wrong region, unintended deletions) before deployment.

---

## 🏷️ Naming & Monitoring (2 rules)

### [TF-RESOURCE-NAMING-010: Naming Convention](rules-tf-naming-state.md#tf-resource-naming-010)
**Severity**: 🟠 MAJOR | **Category**: Code Quality

Use consistent pattern: `${environment}-${type}-${purpose}` (e.g., `prod-gcs-data`).

**Why**: Searchability, automation, team clarity, quick correlation to code.

---

### [TF-STATE-DRIFT-010: Drift Detection](rules-tf-naming-state.md#tf-state-drift-010)
**Severity**: 🟠 MAJOR | **Category**: Monitoring

Run `terraform plan` regularly to detect drift (manual changes via cloud console).

**Why**: Prevent surprises, detect security issues, keep code in sync with reality.

---

## 📊 Severity Legend

| Severity | Color | Meaning |
|----------|-------|---------|
| 🔴 CRITICAL | Red | Must fix immediately (security, correctness, production safety) |
| 🟠 MAJOR | Orange | Should fix (best practices, maintainability, team safety) |
| 🟡 MINOR | Yellow | Nice to have (style, optimization, convenience) |

---

## 🔍 Quick Reference by Severity

### CRITICAL (Must Fix)
1. TF-ENV-SEPARATION-004 - Folder-based environment separation
2. TF-ENV-ISOLATION-005 - Separate backends per environment
3. TF-VERSION-PINNING-006 - Pin Terraform & provider versions
4. TF-REMOTE-STATE-008 - Use remote backends (not local)
5. TF-STATE-DELETION-009 - Never delete state files directly
6. TF-NO-HARDCODED-SECRETS-009 - No secrets in code
7. TF-ALWAYS-PLAN-013 - Review plan before apply

### MAJOR (Should Fix)
1. TF-STRUCTURE-001 - Project layout
2. TF-MODULES-002 - Module creation criteria
3. TF-MODULES-003 - Module scope
4. TF-PROVIDER-LOCKING-007 - Lock file management
5. TF-AVOID-HARDCODING-011 - Parameterize config
6. TF-CI-CD-INTEGRATION-012 - Automated validation
7. TF-RESOURCE-NAMING-010 - Naming convention
8. TF-STATE-DRIFT-010 - Drift detection

---

## 🗂️ Quick Reference by Category

### Architecture (5 rules)
- TF-STRUCTURE-001, TF-ENV-SEPARATION-004, TF-ENV-ISOLATION-005, TF-REMOTE-STATE-008, TF-VERSION-PINNING-006

### Security (2 rules)
- TF-NO-HARDCODED-SECRETS-009, TF-ENV-ISOLATION-005

### Code Quality (5 rules)
- TF-MODULES-002, TF-MODULES-003, TF-AVOID-HARDCODING-011, TF-RESOURCE-NAMING-010, TF-PROVIDER-LOCKING-007

### Reliability (3 rules)
- TF-VERSION-PINNING-006, TF-PROVIDER-LOCKING-007, TF-REMOTE-STATE-008

### Safety (2 rules)
- TF-STATE-DELETION-009, TF-ALWAYS-PLAN-013

### Automation (1 rule)
- TF-CI-CD-INTEGRATION-012

### Monitoring (1 rule)
- TF-STATE-DRIFT-010

---

## 📖 How to Use This Index

**For Code Generation:**
1. Identify your use case (e.g., "creating GCS bucket in prod")
2. Check relevant rules (TF-ENV-ISOLATION-005, TF-AVOID-HARDCODING-011, TF-NO-HARDCODED-SECRETS-009)
3. Apply patterns from those rules

**For Code Review:**
1. Tool returns rule ID in review output
2. Find rule in this index
3. Click to full rule documentation
4. Review correct pattern and implementation checklist
5. Apply fixes

**For Team Onboarding:**
1. Read all CRITICAL rules first (7 rules)
2. Then read MAJOR rules relevant to your project
3. Bookmark this index for quick reference

---

## 📁 Rule Files

All rules are stored in separate markdown files for easy navigation:

- [rules-tf-project-structure.md](rules-tf-project-structure.md) - Modules & layout
- [rules-tf-environments.md](rules-tf-environments.md) - Environment management
- [rules-tf-state-versioning.md](rules-tf-state-versioning.md) - Versioning & state
- [rules-tf-security-cicd.md](rules-tf-security-cicd.md) - Security & CI/CD
- [rules-tf-naming-state.md](rules-tf-naming-state.md) - Naming & monitoring

---

## 🔗 GCS Module Specific Rules

When working with `terraform-google-modules/cloud-storage/google` module:

**Critical rules:**
- [GCS-PROVIDER-001](../work/knowledge/rules-gcs-providers.md): Provider version constraints
- [GCS-INPUT-002](../work/knowledge/rules-gcs-input-types.md): Input types (map vs scalar)

**General rules that apply:**
- TF-ENV-ISOLATION-005 - Separate backends per env
- TF-AVOID-HARDCODING-011 - Parameterize project_id, region, bucket names
- TF-NO-HARDCODED-SECRETS-009 - No IAM credentials hardcoded
- TF-ALWAYS-PLAN-013 - Review plan before applying

---

**Last Updated**: 2026-05-11  
**Total Rules**: 16 + 2 GCS-specific  
**Format**: XML-Markdown (optimized for LLM processing)
