# Terraform Environment Isolation: Backend & State

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
