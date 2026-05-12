# Terraform: Avoid Hardcoding Values

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
