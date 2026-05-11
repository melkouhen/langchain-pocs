# Terraform Versioning & State Management Rules

<rule id="TF-VERSION-PINNING-006" severity="CRITICAL" category="Reliability">
<title>Version Pinning: Providers & Terraform</title>

<description>
Pin versions of Terraform and all providers in `required_version` and `required_providers` blocks.
Unpinned versions cause drift and unexpected behavior changes between `terraform init` runs.
</description>

<problem>
Without version pinning:
- Developer A runs `terraform init` → provider 6.0 installed
- Developer B runs `terraform init` → provider 7.0 installed
- Different behavior between local and CI/CD environments
- Terraform core upgrades break code silently
- Difficult to audit what version was used in production
</problem>

<pattern id="correct">
<title>✅ Pinned Versions</title>

```hcl
# versions.tf or main.tf
terraform {
  required_version = "~> 1.9"  # Terraform core version constraint
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"      # Google provider 6.x (>= 6.0, < 7.0)
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 6.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}
```

**Version Constraint Syntax:**
- `~> 6.0` = allows >= 6.0, < 7.0 (minor/patch updates only)
- `= 6.5.0` = exact version only (very restrictive)
- `>= 6.0, < 7.0` = explicit range
- Avoid `>= 6.0` (unbounded) or `*` (any version)

**Best Practice:**
Use `~>` (tilde) for flexibility + safety:
- Allows patch updates (6.0 → 6.5)
- Prevents major upgrades (6.0 → 7.0)
- Reduces drift, enables security patches
</pattern>

<antipattern id="incorrect">
<title>❌ Unpinned Versions</title>

```hcl
# ❌ WRONG: No version constraints
terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      # No version specified = any version!
    }
  }
}

# ❌ WRONG: Too broad
required_providers {
  google = {
    source  = "hashicorp/google"
    version = ">= 5.0"  # Could be 5.0, 6.0, or 10.0!
  }
}

# ❌ WRONG: Fixed version (no patches)
required_providers {
  google = {
    source  = "hashicorp/google"
    version = "= 6.0.0"  # No security patches allowed
  }
}
```

**Consequences:**
❌ .terraform.lock.hcl differs between team members  
❌ CI/CD uses different provider than local dev  
❌ Major version upgrades break code unexpectedly  
❌ Impossible to know which version was used in prod  
</antipattern>

<why>
**Reproducibility:** Same code + same versions = same results

**Provider versions contain:**
- New resource types (features)
- Removed resource types (breaking changes)
- Bug fixes and security patches
- API behavior changes

**Without pinning:**
- Code works in dev (provider 6.0)
- CI/CD runs with provider 7.0 (new API behavior)
- Prod deploys provider 8.0 (different behavior again)
- Result: Works local, fails in CI, fails in prod
</why>

<when-to-apply>
**Always pin versions for:**
- Production code
- Team projects
- Any code in version control

**Can skip for:**
- Local throwaway tests
- Temporary Terraform experiments
</when-to-apply>

<implementation-checklist>
- [ ] Create `versions.tf` with required_version block
- [ ] Pin Terraform version: `~> 1.9` or current minor version
- [ ] Pin each provider: `~> X.Y` (latest major.minor)
- [ ] Check `.terraform.lock.hcl` is generated
- [ ] Commit `.terraform.lock.hcl` to Git
- [ ] Document provider choice in comments if non-obvious
- [ ] Test: `terraform init` produces same lock file every time
</implementation-checklist>

<related-rules>
- TF-PROVIDER-LOCKING-007: Lock files
- TF-CI-CD-INTEGRATION-012: Reproducible builds
</related-rules>

</rule>


<rule id="TF-PROVIDER-LOCKING-007" severity="MAJOR" category="Reliability">
<title>Provider Lock Files: Commit .terraform.lock.hcl</title>

<description>
Always commit `.terraform.lock.hcl` to version control. This file locks all provider
versions and ensures team members use identical providers.
</description>

<problem>
Without committed lock files:
- Each `terraform init` might resolve to different versions
- Team members have different provider versions locally
- CI/CD uses different versions than developers
- Difficult to debug "works on my machine" issues
</problem>

<pattern id="correct">
<title>✅ Committed Lock Files</title>

```
terraform-project/
├── .gitignore
├── .terraform.lock.hcl      # ← COMMIT THIS FILE
├── versions.tf
├── main.tf
└── variables.tf

# .terraform.lock.hcl content (example):
# provider "registry.terraform.io/hashicorp/google" {
#   version     = "6.10.0"
#   constraints = "~> 6.0"
#   hashes = [
#     "h1:...",
#     "h1:...",
#   ]
# }
```

**Workflow:**
```bash
# Dev 1: Updates provider version
terraform init  # Downloads new version
# Automatically updates .terraform.lock.hcl

git add .terraform.lock.hcl
git commit -m "chore: update google provider to 6.10.0"

# Dev 2: Gets same lock file
git pull
terraform init  # Uses exact version from lock file
# ✓ Same version as Dev 1
```
</pattern>

<antipattern id="incorrect">
<title>❌ Lock File in .gitignore</title>

```
.gitignore
.terraform/
.terraform.lock.hcl  # ❌ WRONG: Should be committed!
*.tfstate

# Result:
# Dev 1: terraform init → provider 6.10.0
# Dev 2: terraform init → provider 6.9.0 (different!)
# CI/CD: terraform init → provider 6.11.0 (different again!)
```
</antipattern>

<why>
**Lock files are:**
- Human-readable (can review in PRs)
- Hashable (prevent tampering)
- Reproducible (same lock = same providers)

**For team projects:**
- Lock file = contract: "we all use these exact versions"
- PR can review what providers are being updated
- Rollback: revert lock file to previous version
</why>

<when-to-apply>
**Commit lock files for:**
- Team projects
- Production code
- Anything in shared version control

**Can skip for:**
- Throwaway local experiments
</when-to-apply>

<implementation-checklist>
- [ ] Remove `.terraform.lock.hcl` from .gitignore (if present)
- [ ] Run `terraform init` to generate lock file
- [ ] Review lock file: verify provider versions look correct
- [ ] Commit lock file: `git add .terraform.lock.hcl`
- [ ] Document in README: "Always commit lock files"
- [ ] Update CI/CD: ensure lock file is used during init
</implementation-checklist>

<related-rules>
- TF-VERSION-PINNING-006: Version constraints
</related-rules>

</rule>


<rule id="TF-REMOTE-STATE-008" severity="CRITICAL" category="Architecture">
<title>Remote State Backend: Never Local State</title>

<description>
Use a remote backend (GCS, S3, etc.) for all team projects. Local state files
expose infrastructure data and prevent collaboration.
</description>

<problem>
Local state files cause:
- Sensitive data stored on developer's laptop (credentials in plaintext!)
- No locking → multiple devs apply simultaneously → state corruption
- No history/versioning → can't rollback to previous state
- Unsynced state between team members
- Easy to accidentally delete/modify state file
</problem>

<pattern id="correct">
<title>✅ Remote Backend (GCS Example)</title>

```hcl
# backend.tf
terraform {
  backend "gcs" {
    bucket  = "terraform-state-prod"
    prefix  = "prod/"
    project = "my-project"
  }
}
```

**Advantages:**
✓ State stored in managed cloud service  
✓ Automatic versioning and backups  
✓ State locking (prevents concurrent applies)  
✓ Team access control (who can read/modify)  
✓ Audit logs (who changed state, when)  
✓ No local files = no laptop exposure  

**Backend Types:**
- GCS (Google Cloud Storage) - Recommended for GCP
- S3 (AWS) - Recommended for AWS
- Azure Blob Storage - Recommended for Azure
- Terraform Cloud - Multi-cloud, advanced features
</pattern>

<antipattern id="incorrect">
<title>❌ Local State File</title>

```hcl
# ❌ WRONG: No backend specified (defaults to local)
terraform {
  # No backend block = terraform.tfstate in current directory
}

# Result:
# - terraform.tfstate contains secrets in plaintext
# - Stored on developer's laptop
# - Multiple devs → state file conflicts
# - No locking, corruption risk
```
</antipattern>

<why>
**State files contain:**
- Resource IDs and metadata
- Database passwords
- API keys and credentials
- Private IP addresses
- All sensitive infrastructure data

**Local state risks:**
1. **Security**: Secrets on unencrypted laptop
2. **Collaboration**: No locking → conflicts
3. **Disaster**: No backups → state loss = infrastructure loss
4. **Compliance**: Sensitive data not in managed service
</why>

<when-to-apply>
**Use remote backend for:**
- Any production environment
- Team projects (2+ developers)
- Any project with sensitive data

**Local state is OK for:**
- Personal throwaway experiments
- Learning/tutorials
</when-to-apply>

<implementation-checklist>
- [ ] Choose backend service (GCS, S3, etc.)
- [ ] Create backend storage (bucket, enable versioning)
- [ ] Create backend.tf with credentials
- [ ] Run `terraform init` to migrate state (if migrating)
- [ ] Verify: `terraform state list` works
- [ ] Ensure backend has proper access controls
- [ ] Enable state file encryption at rest
- [ ] Document backend setup in README
- [ ] Remove local terraform.tfstate files from laptops
</implementation-checklist>

<related-rules>
- TF-ENV-ISOLATION-005: Per-environment backends
- TF-STATE-DELETION-009: State file safety
- TF-STATE-DRIFT-010: Drift detection
</related-rules>

</rule>
