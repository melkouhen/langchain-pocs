<?xml version="1.0" encoding="UTF"?>
<rule id="TF-ENV-ISOLATION" severity="CRITICAL" scope="global" category="Architecture">
  <title>Environment Isolation: Separate Directories and State Files</title>

  <description>
  Development, staging, and production environments MUST be completely isolated
  through separate directories, independent Terraform state files, and distinct
  backend configurations. This prevents accidental cross-environment modifications
  and enables different access controls, approval workflows, and retention policies
  per environment.
  </description>

  <context>
    Directory structure: envs/dev/, envs/staging/, envs/prod/
    Backend configuration: Per-environment backend.tf files
    Module layer: Shared modules in modules/ (reusable, not environment-specific)
  </context>

  <problem>
  Shared environments or workspaces cause:
  - Accidental production modifications during dev testing
  - Single bad `terraform apply` destroys multiple environments
  - Impossible to have different permissions/approval policies per environment
  - State files shared across teams with different security requirements
  - No clear audit trail for which environment was modified
  - Developers accidentally switch environments and deploy to wrong place
  </problem>

  <pattern id="correct">
  ```
  ✅ Correct: Separate directories with isolated state
  
  work_dir/
  ├── modules/
  │   └── gcs_bucket/
  │       ├── main.tf       (reusable, no hardcoded values)
  │       ├── variables.tf
  │       └── outputs.tf
  │
  ├── envs/
  │   ├── dev/
  │   │   ├── main.tf            (calls module)
  │   │   ├── variables.tf        (dev-specific vars)
  │   │   ├── outputs.tf
  │   │   ├── terraform.tfvars    (dev values)
  │   │   └── backend.tf          (GCS: terraform-state-dev-*)
  │   │
  │   ├── staging/
  │   │   ├── main.tf
  │   │   ├── variables.tf
  │   │   ├── terraform.tfvars
  │   │   └── backend.tf          (GCS: terraform-state-staging-*)
  │   │
  │   └── prod/
  │       ├── main.tf
  │       ├── variables.tf
  │       ├── terraform.tfvars
  │       └── backend.tf          (GCS: terraform-state-prod-*)
  │
  └── providers.tf         (global provider config)

  # Each environment has SEPARATE STATE
  cd envs/dev && terraform init
  # → State stored in GCS bucket: terraform-state-dev-*

  cd envs/prod && terraform init
  # → State stored in DIFFERENT GCS bucket: terraform-state-prod-*

  # ✅ Clear, isolated, auditable
  ```
  </pattern>

  <antipattern id="incorrect">
  ```
  ❌ Incorrect: Workspace-based separation (HIGH RISK)

  terraform/
  ├── main.tf              (single file for all envs)
  ├── variables.tf
  └── terraform.tfvars

  # Using workspaces
  terraform workspace new dev
  terraform workspace new prod
  
  # Deploy to prod
  terraform workspace select prod
  terraform apply  # ⚠️ Hard to see which environment

  # Problems:
  # - Single backend for all workspaces (state not isolated)
  # - Shared provider credentials across environments
  # - Easy to forget which workspace is active
  # - CI/CD logs don't show workspace name
  # - No version control separation
  ```
  </antipattern>

  <why>
  **Root cause:**
  1. Workspaces share the same backend bucket but with different prefixes
  2. `terraform workspace show` is easy to miss before apply
  3. Team members working on different environments compete for lock files
  4. State files contain sensitive data (credentials, API keys)
  5. Access controls can't be different per environment

  **Why this matters:**
  - Production must never be touched during dev operations
  - Audit trails must clearly show which environment was modified
  - Different SLAs/approval workflows per environment
  - Team members should NEVER have prod credentials on laptop
  - State deletion/recovery must be per-environment
  </why>

  <validation>
  ```bash
  # 1. Verify directory structure
  ls -la work_dir/envs/
  # Should show: dev/ staging/ prod/

  # 2. Verify each env has independent backend
  cat work_dir/envs/dev/backend.tf | grep bucket
  # Should show: terraform-state-dev-*
  
  cat work_dir/envs/prod/backend.tf | grep bucket
  # Should show: terraform-state-prod-* (DIFFERENT)

  # 3. Verify state files are separate
  cd envs/dev && terraform state list
  cd envs/prod && terraform state list
  # Different resources shown = ✓ separate state

  # 4. Verify CI/CD runs from env directories
  grep "cd envs/" .github/workflows/deploy.yml
  # Should show specific env paths, not workspace switching
  ```
  </validation>

  <when-to-apply>
  **Apply this rule WHENEVER:**
  - Designing new Terraform project structure
  - Migrating from workspace-based setup
  - Adding new environment (staging, prod)
  - Configuring CI/CD pipeline
  - Reviewing terraform state organization
  
  **DO NOT apply if:**
  - Using Terraform Cloud/Enterprise (has different model)
  - Single-environment project (still follow pattern for future growth)
  </when-to-apply>

  <implementation-checklist>
  - [ ] Create `envs/dev/`, `envs/staging/`, `envs/prod/` directories
  - [ ] Create separate backend.tf in each env with unique GCS bucket
  - [ ] Move environment-specific tfvars into each env directory
  - [ ] Create main.tf in each env that calls shared modules (../../modules/)
  - [ ] Delete all workspaces: `terraform workspace delete <name>`
  - [ ] Remove workspace references from Makefile/CI scripts
  - [ ] Test: `cd envs/dev && terraform init && terraform plan`
  - [ ] Test: `cd envs/prod && terraform init && terraform plan`
  - [ ] Verify state files are in separate buckets
  - [ ] Update CI/CD to run commands from specific env directories
  - [ ] Document in README: "Always work from envs/ folders, never use workspaces"
  - [ ] Add `terraform workspace` to .gitignore (prevent accidental commits)
  </implementation-checklist>

  <related-rules>
  - TF-BACKEND-001: Remote state management (GCS)
  - TF-MODULE-001: Module-based project structure
  - TF-SECURITY-001: Credential isolation per environment
  </related-rules>

  <references>
  - https://www.terraform.io/language/state/layouts
  - https://www.terraform.io/language/state/workspaces
  - https://cloud.google.com/docs/terraform/best-practices#separate_environments
  </references>
</rule>
