# Terraform Project Structure & Organization

<rule id="TF-STRUCTURE-001" severity="CRITICAL" category="Architecture">
<title>Project Layout Organization</title>

<description>
Terraform projects must follow a three-tier organizational structure to ensure scalability,
maintainability, and clear separation of concerns. This prevents code duplication and makes
it easy for teams to navigate and contribute to projects.
</description>

<problem>
Without clear structure, Terraform projects become chaotic:
- Reusable code is duplicated across configurations
- Environment-specific and shared code is mixed
- Difficult to understand resource ownership
- Team members struggle to find what they need
</problem>

<pattern id="correct">
<title>✅ Correct Project Structure</title>
<explanation>Three-tier layout: modules (reusable), envs (environment-specific), global (shared)</explanation>

```
terraform-project/
├── modules/
│   ├── gcs_bucket/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── README.md
│   ├── vpc/
│   ├── compute_instance/
│   └── ...
│
├── envs/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   ├── staging/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   └── prod/
│       ├── main.tf
│       ├── variables.tf
│       ├── terraform.tfvars
│       └── backend.tf
│
├── global/
│   ├── iam.tf
│   ├── shared-buckets.tf
│   ├── variables.tf
│   └── backend.tf
│
├── README.md
├── terraform.tfvars.example
└── versions.tf
```

<section name="tier-definitions">

**TIER 1: `modules/` - Reusable Code**
- Parameterized infrastructure components
- No hardcoded values or environment-specific logic
- Each module = one cohesive resource group
- Must be usable by multiple configurations

Example: `modules/gcs_bucket/` implements generic GCS bucket logic

**TIER 2: `envs/` - Environment Configurations**
- dev/, staging/, prod/ subdirectories
- Each environment has SEPARATE backend configuration
- SEPARATE state files per environment
- References modules from `modules/`
- Contains environment-specific values (tfvars)

Example: `envs/prod/main.tf` uses `module "gcs" { source = "../../modules/gcs_bucket" }`

**TIER 3: `global/` - Shared Resources**
- Resources that exist outside environment lifecycles
- Cross-cutting infrastructure (IAM roles, shared buckets)
- Single state file for all environments
- Rarely destroyed

Example: `global/iam.tf` defines roles used by all envs

</section>
</pattern>

<antipattern id="incorrect">
<title>❌ Common Mistakes</title>

**❌ Flat structure (no modules)**
```
terraform/
├── main.tf (2000 lines, all environments mixed)
├── variables.tf
└── terraform.tfvars
```
Result: Code duplication, hard to scale

**❌ Workspaces instead of folders**
```
terraform/
├── main.tf
└── # Using `terraform workspace dev/staging/prod`
```
Result: Shared code, shared backend, team confusion

**❌ Module nesting too deep**
```
modules/
└── platform/
    └── cloud/
        └── gcp/
            └── storage/
                └── bucket/
```
Result: Hard to find code, complex imports
</antipattern>

<why>
**Benefits of Three-Tier Structure:**
1. **Modularity**: Code reuse across environments and projects
2. **Separation of Concerns**: Modules ≠ Env ≠ Global
3. **State Safety**: Separate backends prevent accidental cross-env modifications
4. **Scalability**: Teams can work on different envs independently
5. **Clarity**: New team members understand code organization immediately

**Why NOT use Workspaces for multi-env:**
- Shared provider configuration = risk of deploying to wrong env
- Single backend = harder to secure environments separately
- CI/CD pipelines show less clarity on which env is being modified
- Can accidentally destroy production while thinking you're in dev
</why>

<when-to-apply>
**Apply this rule:**
- Creating any new Terraform project (team or individual)
- Refactoring existing flat structure
- When project has 2+ environments

**Adapt structure if:**
- Project is genuinely single-environment (can skip envs/ folder)
- Global resources are minimal (can merge into envs/)
</when-to-apply>

<implementation-checklist>
- [ ] Create `modules/` folder with reusable components
- [ ] Create `envs/dev/`, `envs/staging/`, `envs/prod/` folders
- [ ] Create `global/` folder for cross-env resources
- [ ] Move reusable code into modules (no hardcoded values)
- [ ] Create separate backend.tf in each envs/ subfolder
- [ ] Update each env's main.tf to reference modules/ via relative paths
- [ ] Create environment-specific terraform.tfvars files
- [ ] Test each environment initialization: `cd envs/dev && terraform init`
- [ ] Verify separate state files created per environment
</implementation-checklist>

<related-rules>
- TF-MODULES-002: Module creation criteria
- TF-MODULES-003: Module scope (avoid deep nesting)
- TF-ENV-SEPARATION-004: Environment isolation
- TF-STATE-BACKEND-008: Remote state backends
</related-rules>

<examples>
<example number="1">
<title>Module Reference from Environment</title>
<code>
# In envs/prod/main.tf
module "gcs_bucket" {
  source = "../../modules/gcs_bucket"
  
  project_id  = var.project_id
  bucket_name = var.bucket_name
  environment = "prod"
  
  lifecycle_rule_age = 365  # Prod: keep 1 year
}
</code>
</example>

<example number="2">
<title>Backend Isolation Per Environment</title>
<code>
# In envs/dev/backend.tf
terraform {
  backend "gcs" {
    bucket = "terraform-state-dev"
    prefix = "dev/"
  }
}

# In envs/prod/backend.tf
terraform {
  backend "gcs" {
    bucket = "terraform-state-prod"
    prefix = "prod/"
  }
}
# ✓ Completely separate state files
</code>
</example>
</examples>

<references>
- Terraform Documentation: Standard Module Structure
- Date Discovered: General best practice
- Status: Industry standard
- Team Impact: Medium (refactoring existing projects takes effort)
</references>

</rule>
