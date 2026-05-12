# Terraform Versioning & State Management Rules

<rule id="TF-VERSION-PINNING" severity="CRITICAL" category="State Management">
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
