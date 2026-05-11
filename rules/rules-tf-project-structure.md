# Terraform Project Structure & Organization Rules

<rule id="TF-STRUCTURE-001" severity="MAJOR" category="Architecture">
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


<rule id="TF-MODULES-002" severity="MAJOR" category="Code Quality">
<title>Module Creation Criteria (DRY Principle)</title>

<description>
Create a module only when code is used in 2 or more places. Single-use infrastructure
should remain inline. Unnecessary modularization adds complexity without benefit.
</description>

<problem>
Over-modularization leads to:
- Too many small modules to maintain
- Module overhead (extra variables, outputs) for single-use code
- Harder to understand overall architecture
- Maintenance burden without reuse benefit
</problem>

<pattern id="correct">
<title>✅ When to Modularize</title>

**Create a module IF:**
- Code is used in 2+ environments (e.g., GCS bucket in dev AND prod)
- Code is used in 2+ projects
- Infrastructure component is cohesive and reusable

**EXAMPLE - Module Created for Reuse:**
```hcl
# modules/gcs_bucket/ created because used in:
# - envs/dev/main.tf
# - envs/prod/main.tf
# - envs/staging/main.tf
# ✓ Justified: 3 uses

module "gcs" {
  source = "../../modules/gcs_bucket"
  bucket_name = var.bucket_name
  environment = var.environment
}
```

**EXAMPLE - Keep Inline (No Module):**
```hcl
# Single-use resource: no module needed
# Used only in envs/prod/main.tf, never elsewhere

resource "google_storage_bucket" "backup" {
  name          = "prod-backups"
  location      = "EU"
  force_destroy = false
  
  versioning {
    enabled = true
  }
}
# ✓ Justified: only one use
```
</pattern>

<antipattern id="incorrect">
<title>❌ Over-Modularization</title>

```hcl
# ❌ WRONG: Module created for single use
modules/
├── simple_bucket/
│   ├── main.tf (10 lines)
│   ├── variables.tf
│   └── outputs.tf

# Used only once in envs/prod/main.tf
# Result: 3 extra files for 10 lines of code
```

**Cost of premature modularization:**
- Extra boilerplate (variables.tf, outputs.tf)
- Harder to understand flow (need to jump between files)
- Maintenance burden for no reuse benefit
- Module becomes cargo-cult code
</antipattern>

<why>
**KISS Principle (Keep It Simple, Stupid):**
- Modules have real cost: extra files, imports, documentation
- Benefits only accrue with actual reuse (2+ uses)
- Premature abstraction makes code harder to follow

**Reuse is the Only Justification:**
- If resource is used in multiple places, module reduces duplication
- Single-use resources stay simpler as inline code
- "Rule of Three": Don't abstract until third use (but 2+ is practical threshold)
</why>

<when-to-apply>
**Before creating a module, ask:**
1. Is this code used in 2+ different places?
2. Will this module be maintained separately?
3. Are benefits of parameterization worth the extra files?

If not all "yes", keep code inline.
</when-to-apply>

<implementation-checklist>
- [ ] Audit existing modules: are all used in 2+ places?
- [ ] Remove single-use modules (inline their code into envs/)
- [ ] Document which environments/projects use each module
- [ ] Update module README with use cases
- [ ] Test refactored code: `terraform plan` still works
</implementation-checklist>

<related-rules>
- TF-STRUCTURE-001: Project layout
- TF-MODULES-003: Module scope
</related-rules>

<references>
- Principle: DRY (Don't Repeat Yourself) - applied judiciously
- Status: Validated practice
</references>

</rule>


<rule id="TF-MODULES-003" severity="MAJOR" category="Code Quality">
<title>Module Scope: Shallow & Focused</title>

<description>
Keep modules shallow (avoid deep nesting) and focused (one resource group per module).
Each module should be independently understandable and testable.
</description>

<problem>
Deep module nesting and scattered responsibility cause:
- Difficult to understand module dependencies
- Hard to locate where resources are defined
- Complex variable propagation through layers
- Increased debugging difficulty
</problem>

<pattern id="correct">
<title>✅ Shallow, Focused Modules</title>

**Structure: One resource group per module**
```
modules/
├── gcs_bucket/          # ✓ One focus: GCS bucket + IAM
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
│
├── vpc/                 # ✓ One focus: VPC + subnets
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
│
└── compute_instance/    # ✓ One focus: Compute instance
    ├── main.tf
    ├── variables.tf
    └── outputs.tf
```

**Module Responsibility:**
- gcs_bucket: creates bucket, configures versioning, manages IAM bindings
- vpc: creates VPC network, creates subnets, configures routes
- compute_instance: creates VM, attaches disks, configures networking

**Each module is:**
✓ Self-contained  
✓ Can be used independently  
✓ Requires minimal external knowledge  
</pattern>

<antipattern id="incorrect">
<title>❌ Deep Nesting (Avoid)</title>

```
modules/
└── platform/           # Too abstract
    └── cloud/          # Still abstract
        └── gcp/        # Still abstract
            └── storage/
                └── bucket/  # Finally concrete (5 levels!)
                    ├── main.tf
                    └── variables.tf

# Using: module "bucket" { source = "../../../../modules/platform/cloud/gcp/storage/bucket" }
# Problems: Hard to navigate, complex path, unclear dependency
```

**Nested Modules Anti-Pattern:**
```
modules/
├── platform/
│   ├── storage/
│   │   ├── main.tf (calls module.bucket_config)
│   │   └── bucket_config/
│   │       └── main.tf
# Variable propagation: var → module → submodule → resource
# Chain too long, hard to trace
```
</antipattern>

<why>
**Shallow modules are easier to:**
1. Understand at a glance
2. Debug when things fail
3. Test independently
4. Navigate with clear file paths
5. Document (each module has clear scope)

**Deep nesting causes:**
- Cognitive overload (too many levels to track)
- Difficult relative paths (../../../../..)
- Unclear which module is responsible for what
- Testing becomes integration-heavy, not unit-focused
</why>

<when-to-apply>
**Keep modules to 1-2 levels maximum:**
- `modules/gcs_bucket/` ✓ Good
- `modules/platform/cloud/bucket/` ✗ Too deep

**One resource group = one module:**
- Bucket configuration → ONE module
- VPC + subnets → ONE module (they're tightly coupled)
- Compute + networking → Split into separate modules (loose coupling)
</when-to-apply>

<implementation-checklist>
- [ ] Audit existing module nesting depth
- [ ] Flatten modules deeper than 2 levels
- [ ] Verify each module has single clear responsibility
- [ ] Update relative import paths (if refactored)
- [ ] Test all modules: `terraform plan` from each env
- [ ] Document module scope in README
</implementation-checklist>

<related-rules>
- TF-STRUCTURE-001: Project layout
- TF-MODULES-002: Module creation criteria
</related-rules>

</rule>
