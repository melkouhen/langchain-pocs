<?xml version="1.0" encoding="UTF"?>
<rule id="TF-BACKEND-STATE" severity="CRITICAL" scope="global" category="State Management">
  <title>Remote State Management via GCS Backend</title>

  <description>
  Terraform state files MUST be stored in remote backends (Google Cloud Storage)
  instead of local files. Remote backends provide state locking, versioning,
  encryption, audit logs, and team collaboration. Local state files expose
  sensitive credentials on developer laptops and prevent concurrent operations.
  </description>

  <context>
    Provider: Google Cloud Storage (GCS)
    Backend type: google/gcs
    State files: Encrypted, versioned, locked
    Per-environment: Each env has different backend bucket
  </context>

  <problem>
  Local state files cause critical security & operational risks:
  - Credentials stored in plaintext on laptop (data breach risk)
  - Multiple developers modify state simultaneously (data corruption)
  - No backup/versioning (state loss = infrastructure loss)
  - No lock mechanism (concurrent applies conflict)
  - Impossible to share state between team members
  - Unsynced state between dev/CI machines (divergence)
  - Easy to accidentally commit state file to git
  - No audit trail of who changed state and when
  </problem>

  <pattern id="correct">
  ```hcl
  # ✅ Correct: Remote GCS Backend

  # envs/dev/backend.tf
  terraform {
    backend "gcs" {
      bucket  = "terraform-state-dev-beaming-botany"
      prefix  = "dev/"
      project = "beaming-botany-495511-n6"
    }
  }

  # envs/prod/backend.tf
  terraform {
    backend "gcs" {
      bucket  = "terraform-state-prod-beaming-botany"
      prefix  = "prod/"
      project = "beaming-botany-495511-n6"
    }
  }

  # Usage:
  cd envs/dev
  terraform init          # Downloads providers, configures GCS backend
  terraform plan          # Reads state from GCS, locks bucket
  terraform apply         # Writes new state to GCS with version

  # Advantages:
  # ✓ State stored in managed GCS service
  # ✓ Automatic versioning (track all changes)
  # ✓ State locking (prevents concurrent modifies)
  # ✓ Encryption at rest (Google-managed or KMS)
  # ✓ Audit logs (who accessed state, when)
  # ✓ No sensitive data on laptop
  # ✓ Team members all read same state
  ```
  </pattern>

  <antipattern id="incorrect">
  ```hcl
  # ❌ Incorrect: Local State File
  
  # envs/dev/providers.tf (NO BACKEND DEFINED)
  terraform {
    required_version = ">= 1.0"
    required_providers {
      google = { version = "~> 5.0" }
    }
  }
  # → Default backend is "local"
  # → State stored in ./terraform.tfstate (INSECURE)

  # Problems:
  # ❌ terraform.tfstate contains plaintext credentials
  # ❌ File on laptop = data breach if stolen
  # ❌ Multiple developers = state file conflicts
  # ❌ No versioning = can't rollback changes
  # ❌ No lock = concurrent applies corrupt state
  # ❌ Easy to commit to git accidentally
  # ❌ CI/CD server has its own copy (diverged)

  # Worse: Committing state to git
  git add terraform.tfstate
  git push  # ⚠️ CRITICAL: Credentials exposed in git history
  ```
  </antipattern>

  <why>
  **Root cause:**
  1. Terraform defaults to local state if no backend is configured
  2. Local state files contain ALL sensitive data (passwords, tokens, keys)
  3. Developers work on laptops = state file stays in sync only on that machine
  4. Multiple devs modify state = file overwrite conflicts, data loss
  5. No mechanism for state locking (prevents concurrent operations)

  **Why this matters:**
  - Production credentials in plaintext on laptop (security incident)
  - State loss = infrastructure must be recreated from scratch
  - Concurrent applies cause state corruption (invalid infrastructure)
  - No history = can't trace when/why changes happened
  - Team can't collaborate (state not shared)
  </why>

  <validation>
  ```bash
  # 1. Verify backend.tf exists in each environment
  cat envs/dev/backend.tf | grep -A3 'backend "gcs"'
  # Should show GCS bucket config

  # 2. Verify no local state files
  find envs/ -name "terraform.tfstate*" -o -name "*.tfstate.backup"
  # Should return NOTHING (empty)

  # 3. Verify state is in GCS after init
  cd envs/dev && terraform init
  gsutil ls gs://terraform-state-dev-beaming-botany/dev/
  # Should show: terraform.tfstate

  # 4. Verify state is locked
  terraform plan
  # GCS bucket has lease lock during operation
  gsutil ls -L gs://terraform-state-dev-beaming-botany/
  # Should show: (leased while command runs)

  # 5. Verify state locking works
  terraform apply -auto-approve &  # Start long operation
  sleep 1 && terraform plan        # Try plan in parallel
  # Second command should BLOCK (waiting for lock)

  # 6. Check git is ignoring state files
  cat .gitignore | grep tfstate
  # Should include: *.tfstate*, *.tfstate.backup
  ```
  </validation>

  <when-to-apply>
  **Apply this rule WHENEVER:**
  - Creating new Terraform project
  - Migrating from local to remote state
  - Setting up team collaboration
  - Configuring CI/CD pipeline
  - Creating per-environment backends
  
  **DO NOT apply if:**
  - Learning Terraform (local state is fine for local-only labs)
  - Personal throwaway experiments
  - Terraform Cloud/Enterprise (different backend model)
  </when-to-apply>

  <implementation-checklist>
  - [ ] Create GCS buckets for each environment (dev, staging, prod)
  - [ ] Enable versioning on state buckets
  - [ ] Create backend.tf file in each env folder
  - [ ] Configure bucket name, prefix, project in backend.tf
  - [ ] Add *.tfstate* to .gitignore
  - [ ] Run `terraform init` to migrate state to GCS
  - [ ] Verify state is in GCS (gsutil ls gs://bucket/prefix/)
  - [ ] Test state locking: parallel terraform operations should block
  - [ ] Enable bucket encryption (Google-managed or KMS)
  - [ ] Enable MFA delete (optional, for production)
  - [ ] Set retention policy on state bucket (prevent deletion)
  - [ ] Configure bucket IAM (only team members can read)
  - [ ] Document backend setup in README
  - [ ] Add backend bucket name to CI/CD variables
  - [ ] Backup process for state bucket (if using local snapshots)
  </implementation-checklist>

  <related-rules>
  - TF-ENV-ISOLATION-002: Per-environment state files
  - TF-SECURITY-001: Credential protection
  - GCS-BUCKET-CONFIG-001: GCS bucket hardening
  </related-rules>

  <references>
  - https://www.terraform.io/language/settings/backends/gcs
  - https://cloud.google.com/docs/terraform/best-practices
  - https://cloud.google.com/storage/docs/state-locking
  - https://registry.terraform.io/providers/hashicorp/google/latest/docs
  </references>
</rule>
