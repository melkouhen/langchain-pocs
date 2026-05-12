# Terraform Environment Separation

<rule id="TF-ENV-SEPARATION" severity="CRITICAL" scope="global" category="Architecture">
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
- [ ] Remove workspace references from Makefile/CI scripts
- [ ] Test: `cd envs/dev && terraform init && terraform plan`
- [ ] Test: `cd envs/prod && terraform init && terraform plan`
- [ ] Verify state files are in separate buckets
- [ ] Update CI/CD to run commands from specific env directories
- [ ] Document in README: "Always work from envs/ folders, never use workspaces"
- [ ] Add `terraform workspace` to .gitignore (prevent accidental commits)
</implementation-checklist>

<related-rules>
- TF-ENV-ISOLATION-005: State isolation details
- TF-STRUCTURE-001: Project layout
</related-rules>

</rule>
