# No GCS Backend for Terraform State

<rule id="TF-NO-GCS-BACKEND" severity="CRITICAL" scope="terraform.backend" category="State Management">
<title>Do Not Use a GCS Backend — Store Terraform State Locally</title>

<description>
Terraform state MUST NOT be stored in a Google Cloud Storage (GCS) bucket. Use the default local
backend (state file kept on disk next to the configuration) instead. A `backend "gcs"` block — or
any other remote backend pointing to GCS — is forbidden in every environment.
</description>

<problem>
Storing the Terraform state in a GCS bucket introduces an unwanted dependency: the very cloud
project that Terraform is supposed to manage also hosts the state used to manage it. This creates:
- A circular bootstrap problem (the state bucket must exist before Terraform can run)
- A blast radius where a single misconfiguration in GCP can lock out state access
- An additional surface for permissions, encryption keys, and bucket lifecycle to drift
- A hidden coupling between Terraform tooling and GCP availability/IAM
</problem>

<pattern id="correct">
<title>✅ Local State (no backend block, or explicit local backend)</title>

```hcl
# terraform.tf — implicit local backend (default)
terraform {
  required_version = ">= 1.5"

  required_providers {
    google = {
      source = "hashicorp/google"
    }
  }
  # ✅ No `backend` block at all → Terraform writes terraform.tfstate locally
}
```

```hcl
# terraform.tf — explicit local backend (equivalent, more readable)
terraform {
  required_version = ">= 1.5"

  backend "local" {
    path = "terraform.tfstate"   # ✅ State stays on the operator's machine
  }

  required_providers {
    google = {
      source = "hashicorp/google"
    }
  }
}
```

**Operational notes:**
- The state file `terraform.tfstate` (and `terraform.tfstate.backup`) MUST be `.gitignore`d
- The state file MUST NOT be committed to version control (contains secrets, IDs, IPs)
- Back up the state file out-of-band (encrypted archive, password manager attachment, etc.)
- Only one operator at a time should run `terraform apply` — there is no remote lock
</pattern>

<antipattern id="incorrect-gcs">
<title>❌ GCS Backend (forbidden)</title>

```hcl
# ❌ WRONG: Terraform state stored in a GCS bucket
terraform {
  backend "gcs" {
    bucket = "tf-state-prod"
    prefix = "infra/"
  }
}
```

**Why this is rejected:**
❌ Couples state availability to GCP project/IAM/quotas
❌ Requires a separate bootstrap step to create the bucket
❌ Adds bucket-level configuration (versioning, CMEK, retention) to maintain
❌ Any operator with bucket read access can read every secret in the state
</antipattern>

<antipattern id="incorrect-other-remote">
<title>❌ Other Remote Backends Pointed at GCS</title>

```hcl
# ❌ Also wrong: HTTP backend wrapping a GCS object
terraform {
  backend "http" {
    address = "https://storage.googleapis.com/tf-state-prod/infra.tfstate"
    # ...
  }
}
```

Any remote backend that ultimately stores the state in GCS is equally forbidden, regardless of the
protocol used to reach it.
</antipattern>

<why>
**Root Cause:**
A GCS backend places the Terraform state inside the same cloud it provisions. The state is then
subject to the same outages, IAM mistakes, and bootstrap ordering issues as the resources it
describes.

**Consequences of using a GCS backend:**
- Bootstrap chicken-and-egg: the bucket must be created before any Terraform run
- An IAM mistake on the bucket locks every operator out of the state
- Bucket lifecycle / retention misconfiguration can silently delete state versions
- State secrets are exposed to anyone with `storage.objects.get` on the bucket
- Disaster recovery requires GCP itself to be healthy

**Prevention:**
Keep the state local. The operator owns the file, backs it up themselves, and the tooling has no
runtime dependency on the cloud being managed.
</why>

<when-to-apply>
**Apply this rule WHENEVER:**
- Initializing a new Terraform root module
- Reviewing an existing `terraform { backend ... }` block
- Migrating an environment between backends

**DO NOT apply if:**
- The team has explicitly opted into a managed remote backend (HCP Terraform, Terragrunt-managed
  remote state, etc.) AND that decision has been documented and approved — in which case a separate
  rule supersedes this one

**Context-Dependent:**
Single-operator and small-team projects benefit most from local state. If concurrent `apply`
becomes a real need, revisit this rule rather than silently switching to GCS.
</when-to-apply>

<implementation-checklist>
- [ ] Grep the repository for `backend "gcs"` — there must be zero matches
- [ ] Remove any `backend "gcs"` block from `terraform.tf` / `backend.tf`
- [ ] If migrating: `terraform state pull > terraform.tfstate` from the GCS backend first
- [ ] Run `terraform init -migrate-state` to move state to the local backend
- [ ] Add `terraform.tfstate` and `terraform.tfstate.backup` to `.gitignore`
- [ ] Verify `git status` does not show the state file as tracked
- [ ] Document the local-state backup procedure in the project README
- [ ] Decommission the previous GCS state bucket (after verifying the local copy is healthy)
</implementation-checklist>

<related-rules>
- TF-NO-HARDCODED-SECRETS: State contains secrets, so it must never be committed
- TF-STATE-DELETION: Protecting the state file from accidental deletion
- TF-STATE-DRIFT: Detecting drift between state and reality
</related-rules>

<references>
- https://developer.hashicorp.com/terraform/language/settings/backends/local
- https://developer.hashicorp.com/terraform/language/settings/backends/configuration
</references>

</rule>
