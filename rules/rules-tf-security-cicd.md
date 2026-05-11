# Terraform Security & CI/CD Rules

<rule id="TF-NO-HARDCODED-SECRETS-009" severity="CRITICAL" category="Security">
<title>No Hardcoded Secrets</title>

<description>
Never hardcode secrets (passwords, API keys, credentials) in Terraform code.
Use variables, secret managers, or environment variables instead.
</description>

<problem>
Hardcoded secrets in code cause:
- Secrets exposed in version control history (even after deletion!)
- Secrets visible in `terraform plan` output
- Secrets stored in state files in plaintext
- Secrets accessible to anyone with repo access
- Compliance/audit violations
</problem>

<pattern id="correct">
<title>✅ Secrets Managed Safely</title>

**Option 1: Input Variables**
```hcl
variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true  # ← Masks in output
}

# Usage: terraform apply -var="db_password=xxx"
# or via terraform.tfvars (added to .gitignore)
```

**Option 2: Secret Manager**
```hcl
# Use Google Secret Manager
data "google_secret_manager_secret_version" "db_password" {
  secret = "db-password"
  version = "latest"
}

resource "google_sql_database_instance" "db" {
  # Use: data.google_secret_manager_secret_version.db_password.secret_data
}
```

**Option 3: Environment Variables**
```bash
export TF_VAR_db_password="xxx"
terraform apply  # Reads from env var
```

**Best Practices:**
✓ Mark sensitive variables with `sensitive = true`  
✓ Use secret manager (not local files)  
✓ Rotate credentials regularly  
✓ Use service accounts instead of user credentials  
✓ Grant minimal permissions (least privilege)  
</pattern>

<antipattern id="incorrect">
<title>❌ Hardcoded Secrets</title>

```hcl
# ❌ WRONG: Password in code
resource "google_sql_database_instance" "db" {
  name = "production-db"
  
  root_user {
    password = "MySecurePassword123!"  # ❌ EXPOSED
  }
}

# ❌ WRONG: API key in code
variable "sendgrid_api_key" {
  default = "SG.xxxxxxxxxxxx"  # ❌ In version control forever
}

# ❌ WRONG: Service account key file committed
locals {
  gcp_credentials = file("credentials.json")  # ❌ Keys in repo
}
```

**Consequences:**
❌ Secrets in Git history (unforgettable)  
❌ Visible in `terraform plan` output  
❌ Anyone with repo access has credentials  
❌ Audit trail shows who saw the secrets  
❌ Compliance violations (HIPAA, PCI-DSS, SOC2)  
</antipattern>

<why>
**Threat Model:**
1. Repository accessed by: developers, CI/CD, contractors, consultants
2. Git history is permanent (even deleted secrets remain in history)
3. Credentials can be rotated, but compromised credentials = attacker access
4. Least privilege: developers should not know production credentials

**Secret Manager Benefits:**
- Centralized secret rotation
- Audit logs (who accessed what)
- Access control (different permissions per secret)
- Encryption at rest and in transit
</why>

<when-to-apply>
**Apply this rule:**
- ANY sensitive data: passwords, keys, tokens
- API credentials
- Service account files
- Private configuration

**Include:**
- Mark variables `sensitive = true` (masks in output)
- Use secret managers for production
</when-to-apply>

<implementation-checklist>
- [ ] Audit existing code for hardcoded secrets
- [ ] Move secrets to variables (add `sensitive = true`)
- [ ] Use secret manager for production credentials
- [ ] Update .gitignore to exclude .tfvars files
- [ ] Create terraform.tfvars.example with placeholder values
- [ ] Rotate any exposed credentials immediately
- [ ] Document secret injection in README/runbook
- [ ] Set up secret scanning in CI/CD (e.g., GitGuardian)
</implementation-checklist>

<related-rules>
- TF-AVOID-HARDCODING-011: Avoid hardcoding regions/AMIs
</related-rules>

</rule>


<rule id="TF-AVOID-HARDCODING-011" severity="MAJOR" category="Code Quality">
<title>Avoid Hardcoding: Use Variables & Locals</title>

<description>
Never hardcode region, project IDs, AMI IDs, or other environment-specific parameters.
Use variables and locals instead for flexibility and maintainability.
</description>

<problem>
Hardcoded values cause:
- Code duplication across environments
- Difficult to run same code in different regions
- Easy to accidentally deploy to wrong region/project
- Hard to find all occurrences when values need to change
</problem>

<pattern id="correct">
<title>✅ Parameterized Configuration</title>

```hcl
# variables.tf
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "us-central1"
}

# main.tf - Uses variables, never hardcoded
provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_storage_bucket" "data" {
  name          = "${var.project_id}-data"
  location      = var.region
  force_destroy = false
}

# terraform.tfvars (per environment)
project_id = "my-company-prod"
region     = "europe-west1"
```

**Locals for Derived Values:**
```hcl
locals {
  common_labels = {
    environment = var.environment
    team        = "platform"
    managed_by  = "terraform"
  }
}

# Usage in resources:
labels = local.common_labels
```
</pattern>

<antipattern id="incorrect">
<title>❌ Hardcoded Values</title>

```hcl
# ❌ WRONG: Region hardcoded
provider "google" {
  project = "my-project"
  region  = "us-central1"  # Can't change for other regions
}

# ❌ WRONG: Project ID hardcoded
resource "google_storage_bucket" "data" {
  name     = "my-company-prod-data"  # Hardcoded project ID in name
  location = "europe-west1"          # Hardcoded region
}

# ❌ WRONG: Duplicated across environments
# In envs/prod/main.tf
resource "google_sql_database_instance" "db" {
  name   = "prod-database"
  region = "us-central1"
}

# In envs/dev/main.tf
resource "google_sql_database_instance" "db" {
  name   = "dev-database"
  region = "us-central1"  # ← Duplicated, impossible to change both at once
}
```
</antipattern>

<why>
**Parameterization enables:**
1. **Reusability**: Same module code in dev and prod
2. **Maintainability**: Change region once, applies everywhere
3. **Team clarity**: Values are explicit in tfvars, not hidden in code
4. **Environment parity**: Identical code, different config
</why>

<when-to-apply>
**Parameterize:**
- Region/location
- Project/account IDs
- Environment name
- Image/AMI IDs
- Resource names (use variables + defaults)

**Can hardcode (if stable):**
- Internal naming patterns (use locals for reuse)
- API versions (if stable across envs)
</when-to-apply>

<implementation-checklist>
- [ ] Identify all hardcoded values in code
- [ ] Create variables.tf with parameters
- [ ] Replace hardcoded values with var.* or local.*
- [ ] Create terraform.tfvars for each environment
- [ ] Test: `terraform plan` with different tfvars
- [ ] Document variable purpose and defaults in descriptions
- [ ] Create terraform.tfvars.example for new users
</implementation-checklist>

<related-rules>
- TF-NO-HARDCODED-SECRETS-009: Secrets specifically
</related-rules>

</rule>


<rule id="TF-CI-CD-INTEGRATION-012" severity="MAJOR" category="Automation">
<title>CI/CD Integration: Format, Validate, Plan</title>

<description>
Integrate Terraform into CI/CD pipelines with automated:
1. `terraform fmt` (code formatting)
2. `terraform validate` (syntax checking)
3. `terraform plan` (preview changes)
4. Approval gate before apply

This prevents syntax errors and accidental infrastructure changes.
</description>

<problem>
Without CI/CD integration:
- Developers apply invalid code to production
- Code style inconsistencies
- No preview of changes before apply
- No audit trail of who changed what
- Manual apply = human error
</problem>

<pattern id="correct">
<title>✅ CI/CD Pipeline</title>

**GitHub Actions Example:**
```yaml
name: Terraform

on:
  pull_request:
    paths:
      - 'envs/**'
      - 'modules/**'

jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.9.0

      - name: Terraform Format Check
        run: terraform fmt -check -recursive .

      - name: Terraform Validate
        run: |
          cd envs/dev && terraform init && terraform validate
          cd ../staging && terraform init && terraform validate
          cd ../prod && terraform init && terraform validate

      - name: Terraform Plan (dev)
        env:
          GOOGLE_CREDENTIALS: ${{ secrets.GOOGLE_CREDENTIALS_DEV }}
        run: |
          cd envs/dev
          terraform init
          terraform plan -out=tfplan

      - name: Upload Plan
        uses: actions/upload-artifact@v3
        with:
          name: tfplan
          path: envs/dev/tfplan

  approval:
    needs: terraform
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - name: Terraform Apply (Requires Approval)
        run: echo "Waiting for approval..."
```

**Steps in Pipeline:**
1. `terraform fmt -check` → Ensure code is formatted
2. `terraform validate` → Ensure syntax is valid
3. `terraform plan` → Show what will change
4. Approval gate → Human review before apply
5. `terraform apply` → Deploy (requires approval)

**Key Security:**
✓ All credentials in GitHub Secrets  
✓ Apply requires approval  
✓ Plan output visible to reviewers  
✓ Audit trail in GitHub Actions logs  
</pattern>

<antipattern id="incorrect">
<title>❌ Manual Terraform Apply</title>

```bash
# ❌ WRONG: Developer runs apply locally
terraform apply -auto-approve

# No review, no preview, no audit trail
# If wrong resource is destroyed, hard to undo

# ❌ WRONG: No validation in CI
# Push code → CI runs tests → No terraform validate

# ❌ WRONG: Shared credentials
# Put credentials directly in code/config
# Anyone with repo access gets credentials
```

**Consequences:**
❌ Invalid code applied to prod  
❌ No audit trail  
❌ Credentials exposed  
❌ Manual errors (typos, wrong environment)  
</antipattern>

<why>
**CI/CD Benefits:**
1. **Safety**: Validation before any cloud changes
2. **Auditability**: Every change tracked
3. **Security**: Credentials in CI/CD secrets, not code
4. **Consistency**: Same pipeline for all developers
5. **Approval**: Human review before production

**Prevents:**
- Syntax errors reaching production
- Inconsistent formatting
- Unreviewed infrastructure changes
- Credential leaks
</why>

<when-to-apply>
**Implement for:**
- Any production Terraform
- Team projects
- Any code in shared repo

**Can skip for:**
- Local throwaway tests
</when-to-apply>

<implementation-checklist>
- [ ] Create .github/workflows/terraform.yml (or equivalent for GitLab/etc.)
- [ ] Add `terraform fmt -check` step
- [ ] Add `terraform validate` step (per environment)
- [ ] Add `terraform plan` step with artifact upload
- [ ] Set up approval gate for main branch
- [ ] Store credentials in CI/CD secrets
- [ ] Test pipeline with PR (should show plan)
- [ ] Document pipeline in README
- [ ] Never run `apply -auto-approve` in CI
</implementation-checklist>

<related-rules>
- TF-ALWAYS-PLAN-013: Plan before apply
- TF-VERSION-PINNING-006: Consistent versions in CI
</related-rules>

</rule>


<rule id="TF-ALWAYS-PLAN-013" severity="CRITICAL" category="Best Practice">
<title>Always Review Plan Before Apply</title>

<description>
Never run `terraform apply` without reviewing `terraform plan` first.
The plan is your "dry run" — it shows exactly what will change before making changes.
</description>

<problem>
Applying without plan review:
- Unexpected resources destroyed/modified
- Wrong variables interpreted
- Typos go unnoticed until applied
- No opportunity to stop bad changes
</problem>

<pattern id="correct">
<title>✅ Plan-Review-Apply Workflow</title>

```bash
# Step 1: Create plan
terraform plan -out=tfplan

# Step 2: REVIEW the plan carefully
# Look for:
# - Resources being destroyed (intentional?)
# - Unexpected modifications
# - Correct variables being used

# Step 3: Apply ONLY if plan looks correct
terraform apply tfplan
```

**What to Check in Plan:**
✓ Resources being created (should match intent)  
✓ Resources being modified (why? is this expected?)  
✓ Resources being destroyed (really want to delete this?)  
✓ Variable values are correct  
✓ Counts/for_each are correct  

**Rule of Thumb:** If you can't explain what each line of the plan does, don't apply it.
</pattern>

<antipattern id="incorrect">
<title>❌ Auto-Approve Apply</title>

```bash
# ❌ WRONG: Skip plan review
terraform apply -auto-approve

# ❌ WRONG: Apply without even running plan
terraform apply

# ❌ WRONG: In CI, apply without approval
# GitHub Actions: apply immediately after successful tests
# No human review of plan output
```

**Real-world incident:**
```bash
# Developer runs: terraform apply -auto-approve
# Refactored code accidentally destroys database
# Database backup 2 hours old
# 2 hours of data lost

# With plan review:
# terraform plan would show: database resource will be destroyed
# Developer sees this, stops, fixes code first
```
</antipattern>

<why>
**Terraform is powerful:**
- One command can destroy infrastructure
- No built-in "undo" (though TF can import destroyed resources)
- State drift means reality is different from code

**Plan review is your safety net:**
- Shows exactly what will happen
- Catches typos before infrastructure changes
- Opportunity to stop before damage
- Especially critical in production
</why>

<when-to-apply>
**Always apply this rule:**
- Any `terraform apply` in production
- CI/CD apply gates (approval required)
- Any destructive operations
- Any code you didn't write

**Acceptable exceptions:**
- Local development experiments (still good practice though)
</when-to-apply>

<implementation-checklist>
- [ ] Make it team policy: plan before apply always
- [ ] CI/CD: store plan artifact, require approval
- [ ] Document in runbook: show plan before apply
- [ ] Train team: what to look for in plan output
- [ ] Never use `-auto-approve` in production
- [ ] For emergency fixes: still run plan, just approval might be verbal
</implementation-checklist>

<related-rules>
- TF-CI-CD-INTEGRATION-012: Automated plan in CI/CD
</related-rules>

</rule>
