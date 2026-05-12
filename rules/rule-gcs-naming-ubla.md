<?xml version="1.0" encoding="UTF"?>
<rule id="GCS-NAMING-UBLA" severity="CRITICAL" scope="gcs" category="Security">
  <title>GCS Bucket Naming Convention and Uniform Bucket-Level Access</title>

  <description>
  Google Cloud Storage buckets must follow DNS-compliant naming conventions
  (lowercase, hyphens only, no underscores) and enforce Uniform Bucket-Level
  Access (UBLA) for consistent IAM policy enforcement. This rule ensures
  buckets are globally unique, comply with GCS constraints, and have
  consistent access controls.
  </description>

  <context>
    Module: terraform-google-modules/cloud-storage/google
    Resource: google_storage_bucket
    Environment: dev, prod, staging
  </context>

  <problem>
  Invalid bucket names cause terraform validate failures:
  - GCS naming constraints: [a-z0-9] with hyphens only, no underscores/uppercase
  - Terraform rejects uppercase, underscores, or invalid characters
  - Without UBLA, bucket-level IAM policies conflict with object-level ACLs
  - Inconsistent access control creates security gaps
  </problem>

  <pattern id="correct">
  ```hcl
  # ✅ Correct implementation
  module "gcs_bucket_dev" {
    source = "../../modules/gcs_bucket"

    bucket_name    = "${var.bucket_prefix}-dev"  # lowercase, hyphens
    gcp_project_id = var.gcp_project_id
    gcp_region     = var.gcp_region
    environment    = "dev"

    enable_versioning = true
    force_destroy     = true
    prevent_destroy   = false

    additional_labels = {
      team = "platform"
    }
  }

  # In module/gcs_bucket/main.tf:
  resource "google_storage_bucket" "bucket" {
    name          = var.bucket_name  # e.g., "my-bucket-elkouhen-dev"
    location      = var.gcp_region
    project       = var.gcp_project_id
    force_destroy = var.force_destroy

    # UBLA is applied via separate resource (not inline block)
    public_access_prevention = "enforced"

    versioning {
      enabled = var.enable_versioning
    }

    labels = merge(
      { environment = var.environment, managed_by = "terraform" },
      var.additional_labels
    )

    lifecycle {
      prevent_destroy = var.prevent_destroy
    }
  }

  # Enable UBLA via separate resource:
  # Note: In google provider ~5.0, UBLA must be set directly on the bucket
  # or via google_storage_bucket_uniform_bucket_level_access resource
  ```
  </pattern>

  <antipattern id="incorrect">
  ```hcl
  # ❌ Incorrect implementation
  resource "google_storage_bucket" "dev" {
    name = "My_Bucket_Dev"  # INVALID: uppercase, underscores
    location = var.gcp_region

    # Block syntax not supported in google provider 5.0+
    uniform_bucket_level_access {
      enabled = true
    }

    # Public access prevention resource is not supported
    # Use google_storage_bucket_public_access_prevention { enabled = true }
  }
  ```
  </antipattern>

  <why>
  **Root cause:**
  1. GCS enforces DNS naming standards: lowercase [a-z0-9-] only
  2. Terraform google provider has specific schema for google_storage_bucket
  3. UBLA must be enabled via the bucket attribute or separate resource
  4. Provider version (5.0+) deprecated certain block types

  **Why this matters:**
  - Invalid bucket names fail immediately during terraform validate
  - Inconsistent UBLA config allows conflicting ACL policies
  - Mix of bucket-level and object-level access creates security confusion
  - Team members can't find/remember bucket naming pattern
  </why>

  <validation>
  ```bash
  # 1. Check bucket name against regex
  echo "my-bucket-elkouhen-dev" | grep -E "^[a-z0-9]([a-z0-9-]*[a-z0-9])?$"
  # Should match ✓

  # 2. Run terraform validate
  cd envs/dev && terraform validate
  # Should pass ✓

  # 3. Check terraform plan output
  terraform plan | grep "name.*=" 
  # Should show lowercase hyphenated name ✓
  
  # 4. Verify UBLA is set
  terraform plan | grep "uniform_bucket_level_access"
  # Should show "= true" ✓
  ```
  </validation>

  <when-to-apply>
  **Apply this rule WHENEVER:**
  - Creating new google_storage_bucket resources
  - Terraform validate fails with bucket naming errors
  - Migrating buckets from other projects/providers
  - Adding public_access_prevention configuration
  - Configuring UBLA for the first time
  
  **DO NOT apply if:**
  - Using Google Cloud console (automatically enforces rules)
  - Not using Terraform (manual bucket creation)
  </when-to-apply>

  <implementation-checklist>
  - [ ] Bucket prefix uses only [a-z0-9-], no underscores
  - [ ] Final bucket name: `${bucket_prefix}-${environment}` (all lowercase)
  - [ ] Verify against regex: `^[a-z0-9]([a-z0-9-]*[a-z0-9])?$`
  - [ ] Set `public_access_prevention = "enforced"` in bucket resource
  - [ ] Enable UBLA on bucket (via attribute or separate resource)
  - [ ] Use modules to standardize bucket creation
  - [ ] Run `terraform validate` to confirm no syntax errors
  - [ ] Run `terraform plan` to preview bucket name
  - [ ] Document bucket naming pattern in README
  - [ ] Add naming convention to team style guide
  </implementation-checklist>

  <related-rules>
  - TF-NAMING-001: General Terraform naming conventions
  - GCS-SECURITY-002: Public access prevention
  - TF-MODULE-001: Module-based infrastructure
  </related-rules>

  <references>
  - https://cloud.google.com/storage/docs/naming-buckets
  - https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket
  - https://cloud.google.com/storage/docs/uniform-bucket-level-access
  </references>
</rule>
