# Terraform Environment Management Rules

<rule id="TF-ENV-SEPARATION-004" severity="CRITICAL" category="Architecture">
<title>Environment Separation: Folders vs Workspaces</title>

<description>
Multi-environment projects MUST use folder-based separation (envs/dev/, envs/prod/) 
instead of Terraform workspaces. Workspaces are only for local testing and prototyping,
never for team production environments.
</description>

<context>
Team Size: 2+ developers
Environments: dev, staging, prod
Risk Level: HIGH (production safety)
</context>

<problem>
Using workspaces for team environments causes:
- **Shared provider config**: All envs use same credentials, same cloud account
- **Blind apply risk**: Easy to accidentally deploy to wrong workspace
- **Backend confusion**: Single backend for all workspaces
- **Poor CI/CD visibility**: Pipeline logs don't clearly show which env is being modified
- **No infrastructure-as-code**: State separation isn't captured in Git

**Real-world incident:**
```bash
# Developer thinks they're in "dev" workspace, but actually in "prod"
terraform workspace show  # Returns "prod"
terraform apply          # ⚠️ APPLIES TO PRODUCTION ACCIDENTALLY

# With folders:
cd envs/prod && terraform apply  # Hard to get location wrong
```
</problem>

<pattern id="correct">
<title>✅ Correct: Folder-Based Separation</title>
<explanation>Each environment in its own folder with separate backend configuration</explanation>

```
envs/
├── dev/
│   ├── main.tf
│   ├── variables.tf
│   ├── terraform.tfvars
│   └── backend.tf          # ← Separate backend for dev
│       # backend "gcs" { bucket = "terraform-state-dev" }
│
├── staging/
│   ├── main.tf
│   ├── variables.tf
│   ├── terraform.tfvars
│   └── backend.tf          # ← Separate backend for staging
│       # backend "gcs" { bucket = "terraform-state-staging" }
│
└── prod/
    ├── main.tf
    ├── variables.tf
    ├── terraform.tfvars
    └── backend.tf          # ← Separate backend for prod
        # backend "gcs" { bucket = "terraform-state-prod" }
```

**Usage:**
```bash
# Apply to dev (clear intent)
cd envs/dev && terraform apply

# Apply to prod (clear intent, stored in Git)
cd envs/prod && terraform apply

# CI/CD pipeline: runs from specific directory
# No ambiguity about which environment is being modified
```

**Advantages:**
✓ State files completely isolated  
✓ Clear directory location = clear environment  
✓ Backend configuration per environment  
✓ CI/CD logs show exact path (envs/prod/)  
✓ Git tracks which env configurations exist  
✓ New team members can't accidentally deploy to wrong env  
</pattern>

<antipattern id="incorrect">
<title>❌ Workspace-Based Separation (Team Use)</title>

```bash
# All environments in one directory
terraform/
├── main.tf
├── variables.tf
└── terraform.tfvars

# Using workspaces
terraform workspace new dev
terraform workspace new prod

# Apply to prod
terraform workspace select prod
terraform apply  # ⚠️ Hard to see which env you're in
```

**Problems:**
❌ Single backend for all workspaces  
❌ Shared provider credentials  
❌ Easy to forget workspace context  
❌ CI/CD logs don't show workspace being used  
❌ No clear separation in version control  
❌ `terraform workspace show` is easy to miss  
</antipattern>

<why>
**Root Cause:** Workspaces were designed for lightweight local testing, not team multi-env management.

**Consequences:**
1. **Safety**: Shared provider = risk of cross-env accidents
2. **Auditability**: No clear Git history of which env was deployed to
3. **Team confusion**: Developers unsure which workspace they're in
4. **Scalability**: Difficult to give devs different permissions per environment

**Why folders win:**
- Directory path is unambiguous: `cd envs/prod` = production
- Backend separation is explicit and version-controlled
- CI/CD can easily constrain who can deploy to which folder
- Onboarding new devs: clear folder structure, no "workspace" concept
</why>

<when-to-apply>
**Use FOLDERS (this rule) for:**
- Team projects (2+ developers)
- Production environments
- Any environment with shared state

**Use WORKSPACES only for:**
- Personal local testing (`test`, `playground`)
- Temporary feature branches
- Single developer experiments
</when-to-apply>

<implementation-checklist>
- [ ] Create `envs/dev/`, `envs/staging/`, `envs/prod/` folders
- [ ] Create separate backend.tf in each env folder with unique bucket
- [ ] Move environment-specific tfvars into each env folder
- [ ] Update main.tf in each env to reference `../../modules/`
- [ ] Delete workspaces: `terraform workspace delete <name>`
- [ ] Test each environment: `cd envs/dev && terraform init && terraform plan`
- [ ] Verify separate state files created in separate buckets
- [ ] Document in README: "Always work from envs/ folders, never use workspaces"
- [ ] Update CI/CD to run from specific env folders only
</implementation-checklist>

<related-rules>
- TF-ENV-ISOLATION-005: State isolation details
- TF-STRUCTURE-001: Project layout
</related-rules>

</rule>


<rule id="TF-ENV-ISOLATION-005" severity="CRITICAL" category="Security">
<title>Environment Isolation: Separate Backends & State</title>

<description>
Each environment MUST have completely separate infrastructure:
- Different backend buckets (dev ≠ staging ≠ prod)
- Different state files per environment
- Different cloud projects/credentials (if possible)
- Never share "default" workspace across environments
</description>

<problem>
Shared state files between environments cause:
- Accidental cross-environment modifications
- One bad `terraform apply` could destroy multiple environments
- Difficult to audit who changed what in which environment
- Impossible to have different permissions per environment
</problem>

<pattern id="correct">
<title>✅ Complete Environment Isolation</title>

**GCP Example: Separate Buckets**
```hcl
# envs/dev/backend.tf
terraform {
  backend "gcs" {
    bucket  = "terraform-state-dev"     # ← Dev bucket
    prefix  = "dev/"
    project = "my-project-dev"
  }
}

# envs/prod/backend.tf
terraform {
  backend "gcs" {
    bucket  = "terraform-state-prod"    # ← Prod bucket
    prefix  = "prod/"
    project = "my-project-prod"
  }
}
```

**AWS Example: Separate Buckets**
```hcl
# envs/dev/backend.tf
terraform {
  backend "s3" {
    bucket         = "terraform-state-dev"
    key            = "dev.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks-dev"
  }
}

# envs/prod/backend.tf
terraform {
  backend "s3" {
    bucket         = "terraform-state-prod"
    key            = "prod.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks-prod"
  }
}
```

**Isolation Checklist:**
✓ Different backend bucket/storage per env  
✓ Different prefix paths within bucket  
✓ Different cloud projects (dev ≠ prod)  
✓ Different credentials/service accounts  
✓ Backend locking (DynamoDB/Cloud Storage) per env  
✓ Different team permissions per backend  
</pattern>

<antipattern id="incorrect">
<title>❌ Shared Backend (High Risk)</title>

```hcl
# ❌ WRONG: Single backend for all environments
terraform {
  backend "gcs" {
    bucket = "terraform-state"  # Used by dev, staging, AND prod
    prefix = var.environment    # Only prefix is different!
  }
}
# Result: Same bucket, same permissions, shared state file
# Risk: One bad command destroys all environments
```

**Risk scenario:**
```bash
cd envs/prod && terraform destroy -auto-approve
# Oops! Accidentally destroys production because state file is shared

# Better case: terraform state rm <resource>
# Removes from shared state, affects all envs reading from same bucket
```
</antipattern>

<why>
**Safety Principle:** Assume mistakes will happen. Infrastructure should make mistakes hard.

**Shared backend violates this because:**
1. Single point of failure (one bucket = all envs)
2. Impossible to have environment-specific permissions
3. Easy to accidentally delete production state
4. No audit trail of who changed what in which env

**Separate backends ensure:**
1. Production bucket is locked down (restrict who can access)
2. Dev/staging mistakes don't affect prod
3. Each env has own locking mechanism (prevents conflicts)
4. Clear audit logs per environment
</why>

<when-to-apply>
**Always apply this rule:**
- Any production environment
- Any team with 2+ developers
- Any environment with external dependencies

**Exception:** Single developer, local testing (but still bad habit)
</when-to-apply>

<implementation-checklist>
- [ ] Create separate backend bucket for each env (dev, staging, prod)
- [ ] Verify backend.tf exists in each envs/ folder
- [ ] Initialize each env separately: `cd envs/dev && terraform init`
- [ ] Verify state files created in separate buckets
- [ ] Check backend bucket permissions: restrict prod access
- [ ] Enable state file versioning in backend bucket
- [ ] Set up backend locking (DynamoDB/state lock file)
- [ ] Document in runbook: never share backend buckets
- [ ] Audit logs: who accessed which backend, when
</implementation-checklist>

<related-rules>
- TF-ENV-SEPARATION-004: Folder-based separation
- TF-STATE-BACKEND-008: Remote state configuration
- TF-STATE-DRIFT-010: Drift detection
</related-rules>

<examples>
<example number="1">
<title>Separate Google Cloud Projects per Env</title>
<code>
# envs/dev/backend.tf
terraform {
  backend "gcs" {
    bucket  = "tf-state-dev"
    project = "my-org-dev"      # dev project
  }
}

# envs/prod/backend.tf
terraform {
  backend "gcs" {
    bucket  = "tf-state-prod"
    project = "my-org-prod"     # prod project
  }
}
# ✓ Separate projects = separate quotas, permissions, audits
</code>
</example>
</examples>

</rule>
