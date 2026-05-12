# Terraform Provider Lock Files

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
