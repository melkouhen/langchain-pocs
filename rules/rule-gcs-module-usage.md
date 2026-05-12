# GCS Bucket Module Usage

<rule id="GCS-MODULE-USAGE" severity="CRITICAL" scope="google_storage_bucket" category="Architecture">
<title>Use Official terraform-google-modules/cloud-storage/google Module</title>

<description>
Always use the official terraform-google-modules/cloud-storage/google module instead of declaring
google_storage_bucket resources directly. The official module provides consistent configuration,
security best practices, input validation, and simplified management of GCS buckets with proper
versioning, lifecycle, IAM, and encryption settings.
</description>

<problem>
Declaring google_storage_bucket resources directly causes:
- Inconsistent security configurations across buckets
- Missing critical settings (versioning, lifecycle, encryption)
- Verbose and repetitive bucket declarations
- Easy to forget Uniform Bucket-Level Access (UBLA)
- No validation of bucket naming conventions
- Difficult to enforce organization-wide policies
- Manual IAM binding management (error-prone)
- Higher risk of misconfiguration and security gaps
</problem>

<pattern id="correct">
<title>✅ Using Official Cloud Storage Module</title>

```hcl
# terraform.tf
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

# main.tf - Single bucket
module "gcs_bucket" {
  source  = "terraform-google-modules/cloud-storage/google"
  version = "~> 6.0"  # Pin to specific version

  project_id = var.project_id
  location   = var.region
  
  names = ["${var.project_id}-data-${var.environment}"]
  prefix = ""  # Names already include project_id
  
  # Enable versioning for data protection
  versioning = {
    "${var.project_id}-data-${var.environment}" = true
  }
  
  # Lifecycle rules for cost optimization
  lifecycle_rules = [{
    action = {
      type = "Delete"
    }
    condition = {
      age                   = 90
      with_state            = "ARCHIVED"
      matches_storage_class = ["NEARLINE"]
    }
  }]
  
  # Force destroy for non-production environments
  force_destroy = {
    "${var.project_id}-data-${var.environment}" = var.environment != "production"
  }
  
  # IAM bindings
  bucket_policy_only = {
    "${var.project_id}-data-${var.environment}" = true  # Enable UBLA
  }
  
  iam_members = [{
    role   = "roles/storage.objectViewer"
    member = "serviceAccount:${google_service_account.app.email}"
  }]
  
  # Encryption (optional: customer-managed key)
  encryption_key_names = {
    "${var.project_id}-data-${var.environment}" = google_kms_crypto_key.storage.id
  }
  
  # Labels for cost tracking and organization
  labels = {
    environment = var.environment
    managed_by  = "terraform"
    team        = "data-platform"
  }
}

# Multiple buckets with consistent configuration
module "app_buckets" {
  source  = "terraform-google-modules/cloud-storage/google"
  version = "~> 6.0"

  project_id = var.project_id
  location   = var.region
  
  # Create multiple buckets at once
  names = [
    "${var.project_id}-uploads-${var.environment}",
    "${var.project_id}-reports-${var.environment}",
    "${var.project_id}-backups-${var.environment}"
  ]
  prefix = ""
  
  # Apply versioning to all buckets
  versioning = {
    "${var.project_id}-uploads-${var.environment}" = true
    "${var.project_id}-reports-${var.environment}" = true
    "${var.project_id}-backups-${var.environment}" = true
  }
  
  # Storage class per bucket
  storage_class = "STANDARD"
  
  # Enable UBLA for all buckets
  bucket_policy_only = {
    "${var.project_id}-uploads-${var.environment}" = true
    "${var.project_id}-reports-${var.environment}" = true
    "${var.project_id}-backups-${var.environment}" = true
  }
  
  # Shared labels
  labels = {
    environment = var.environment
    managed_by  = "terraform"
  }
}

# Outputs
output "bucket_names" {
  value = module.gcs_bucket.names
}

output "bucket_urls" {
  value = module.gcs_bucket.urls
}
```

**Benefits:**
- ✅ Simplified configuration with sensible defaults
- ✅ Automatic UBLA enforcement
- ✅ Consistent naming and labeling
- ✅ Built-in support for versioning, lifecycle, encryption
- ✅ Validated inputs prevent common mistakes
- ✅ Easy to manage multiple buckets with same settings
</pattern>

<antipattern id="incorrect">
<title>❌ Direct Resource Declaration</title>

```hcl
# ❌ WRONG: Declaring google_storage_bucket directly
resource "google_storage_bucket" "data" {
  name          = "${var.project_id}-data-${var.environment}"
  location      = var.region
  project       = var.project_id
  storage_class = "STANDARD"
  
  # ❌ Easy to forget versioning
  versioning {
    enabled = true
  }
  
  # ❌ Easy to forget UBLA
  uniform_bucket_level_access {
    enabled = true
  }
  
  # ❌ Verbose lifecycle rules
  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age                   = 90
      with_state            = "ARCHIVED"
      matches_storage_class = ["NEARLINE"]
    }
  }
  
  # ❌ Easy to forget encryption
  encryption {
    default_kms_key_name = google_kms_crypto_key.storage.id
  }
  
  labels = {
    environment = var.environment
    managed_by  = "terraform"
    team        = "data-platform"
  }
  
  force_destroy = var.environment != "production"
}

# ❌ Separate IAM binding (easy to forget or misconfigure)
resource "google_storage_bucket_iam_member" "viewer" {
  bucket = google_storage_bucket.data.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.app.email}"
}

# ❌ Another bucket with slightly different config (inconsistency)
resource "google_storage_bucket" "uploads" {
  name          = "${var.project_id}-uploads-${var.environment}"
  location      = var.region
  project       = var.project_id
  storage_class = "STANDARD"
  
  versioning {
    enabled = true
  }
  
  # ❌ OOPS! Forgot UBLA here
  
  # ❌ Different lifecycle rules (inconsistent)
  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 60  # Different age than data bucket
    }
  }
  
  # ❌ OOPS! Forgot encryption here
  
  labels = {
    environment = var.environment
    managed_by  = "terraform"
    # Missing team label (inconsistent)
  }
}

# ❌ No IAM binding for uploads bucket (security gap)
```

**Problems:**
❌ 80+ lines for 2 buckets vs 40 lines with module  
❌ Inconsistent configurations (UBLA missing, different lifecycle ages)  
❌ Easy to forget critical security settings  
❌ Manual IAM management separated from bucket definition  
❌ No input validation (typos in storage class go undetected)  
❌ Difficult to enforce organization-wide standards  
❌ Higher maintenance burden and drift over time  
</antipattern>

<why>
**Module Advantages:**

1. **Consistency**: All buckets follow same configuration patterns
2. **Security**: Enforces UBLA, encryption, and IAM best practices
3. **Validation**: Type checking prevents configuration errors
4. **Simplicity**: Manage multiple buckets with shared settings
5. **Maintainability**: Easier to update organization-wide policies
6. **Documentation**: Well-documented inputs with examples
7. **Community Support**: Battle-tested by thousands of users

**Official Module Features:**
- Automatic Uniform Bucket-Level Access (UBLA) enforcement
- Simplified IAM policy management (no separate resources)
- Built-in support for versioning, lifecycle, and retention
- Customer-managed encryption key (CMEK) integration
- Public access prevention by default
- Consistent labeling and naming patterns
- Support for bucket-level and object-level configurations

**Team Benefits:**
- Faster bucket creation (less boilerplate)
- Fewer security gaps (validation catches mistakes)
- Easier auditing (consistent structure)
- Reduced maintenance burden
- Compliance-ready configurations
</why>

<when-to-apply>
**Always use the module for:**
- All GCS buckets (data lakes, uploads, backups, logs)
- Development, staging, and production environments
- Both private and shared buckets
- Buckets with complex IAM, lifecycle, or encryption requirements

**Direct resource usage is acceptable only for:**
- Learning exercises or experimentation
- Testing module behavior (comparing against direct resources)
- Contributing to the module itself
- Edge cases not supported by the module (extremely rare)

**If the module doesn't support your use case:**
1. Check if there's a newer version with the feature
2. Open an issue on the module repository
3. Consider contributing a PR to add the feature
4. As a last resort, use direct resources with detailed comments explaining why
</when-to-apply>

<implementation-checklist>
- [ ] Audit all direct google_storage_bucket resources in the codebase
- [ ] Replace each with terraform-google-modules/cloud-storage/google module
- [ ] Pin module version to ~> 6.0 (or latest stable)
- [ ] Migrate versioning, lifecycle, and encryption settings
- [ ] Migrate IAM policies to the module's iam_members input
- [ ] Enable UBLA for all buckets via bucket_policy_only
- [ ] Verify bucket naming follows DNS conventions (lowercase, no underscores)
- [ ] Test each bucket after migration (terraform plan)
- [ ] Verify IAM policies and bucket configurations in GCP Console
- [ ] Update documentation and examples
- [ ] Train team on module usage patterns
- [ ] Establish policy: all new GCS buckets must use the module
</implementation-checklist>

<related-rules>
- GCS-NAMING-UBLA: GCS bucket naming conventions and UBLA
- GCS-BUCKET-SYNTAX: Bucket block vs argument syntax
- GCS-INPUT-TYPES: Module input types (map vs scalar)
- TF-MODULES-DRY: When to create modules (DRY principle)
- TF-VERSION-PINNING: Always pin module versions
</related-rules>

<references>
- https://registry.terraform.io/modules/terraform-google-modules/cloud-storage/google/latest
- https://github.com/terraform-google-modules/terraform-google-cloud-storage
- https://cloud.google.com/storage/docs/uniform-bucket-level-access
- https://cloud.google.com/storage/docs/encryption/customer-managed-keys
- https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket
</references>

</rule>
