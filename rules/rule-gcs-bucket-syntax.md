
# GCS Bucket Block vs Argument Syntax Rules

<rule id="GCS-BUCKET-SYNTAX" severity="CRITICAL" category="Code Quality">
<title>Distinguish GCS Bucket Block vs Argument Syntax</title>

<description>
The google_storage_bucket resource in Terraform has specific blocks that ARE valid Terraform blocks,
while others are NOT. Common confusion occurs with blocks like uniform_bucket_level_access,
versioning, and encryption where documentation may be misleading about their exact syntax.
</description>

<context>
Provider: hashicorp/google >= 6.0
Resource: google_storage_bucket
Issue: terraform validate fails with "Unsupported block type" or similar errors
</context>

<problem>
Google Cloud Terraform provider documentation sometimes shows nested attributes in bracket notation,
but Terraform resources have specific allowed blocks. Attempting to define unsupported blocks causes
validation failures immediately.

**Common Mistakes:**
```hcl
# ❌ This looks right in docs, but terraform rejects it:
resource "google_storage_bucket" "bucket" {
  uniform_bucket_level_access {
    enabled = true
  }
}

# Error: Unsupported block type "uniform_bucket_level_access"
```
</problem>

<pattern id="correct">
<title>✅ Valid Blocks for google_storage_bucket</title>

These ARE valid Terraform blocks in google_storage_bucket:
```hcl
resource "google_storage_bucket" "bucket" {
  project       = "my-project"
  name          = "my-bucket"
  location      = "EU"
  storage_class = "STANDARD"
  force_destroy = false

  # ✅ VALID: versioning block
  versioning {
    enabled = true
  }

  # ✅ VALID: lifecycle_rule blocks (repeatable)
  lifecycle_rule {
    action {
      type          = "Delete"
      storage_class = "NEARLINE"
    }
    condition {
      age = 30
    }
  }

  # ✅ VALID: encryption block
  encryption {
    default_kms_key_name = "projects/KEY_PROJECT_ID/locations/LOCATION/keyRings/KEY_RING/cryptoKeys/KEY"
  }

  # ✅ VALID: logging block
  logging {
    log_bucket        = "my-log-bucket"
    log_object_prefix = "logs/"
  }

  # ✅ These are ARGUMENTS (not blocks), use equals sign:
  public_access_prevention = "enforced"
  labels = {
    environment = "prod"
  }
}
```

**Key Rules:**
- `versioning` = **BLOCK** (use curly braces)
- `lifecycle_rule` = **BLOCK** (repeatable with for_each or dynamic)
- `encryption` = **BLOCK** (optional)
- `logging` = **BLOCK** (optional)
- `uniform_bucket_level_access` = **NOT A BLOCK** (not currently supported in provider)
- `public_access_prevention` = **ARGUMENT** (string value)
- `storage_class` = **ARGUMENT** (string value)
- `labels` = **ARGUMENT** (map of strings)
</pattern>

<antipattern id="incorrect">
<title>❌ Invalid Block Syntax</title>

```hcl
# ❌ WRONG: Trying to use uniform_bucket_level_access as a block
resource "google_storage_bucket" "bucket" {
  uniform_bucket_level_access {
    enabled = true
  }
}
# Error: Unsupported block type "uniform_bucket_level_access"

# ❌ WRONG: Using dynamic block for unsupported block type
resource "google_storage_bucket" "bucket" {
  dynamic "uniform_bucket_level_access" {
    for_each = [1]
    content {
      enabled = true
    }
  }
}
# Error: Blocks of type "uniform_bucket_level_access" are not expected here

# ❌ WRONG: Treating arguments as blocks
resource "google_storage_bucket" "bucket" {
  public_access_prevention {
    value = "enforced"
  }
}
# Error: Unsupported block type "public_access_prevention"
```
</antipattern>

<why>
**Root Cause:** The Google Cloud provider has a specific schema for google_storage_bucket.
Only certain attributes are implemented as blocks in Terraform (versioning, lifecycle_rule, encryption, logging).
Others are simple arguments that accept string or map values.

**Why uniform_bucket_level_access is NOT a block:**
- Not defined in the provider's resource schema as a block
- May be under development or planned for future versions
- Currently not supported, attempting it fails validation

**Why this matters:**
- Terraform is statically typed and validates block types early
- Mistakes are caught immediately during validation
- Misunderstanding blocks vs arguments slows down development
- Common source of frustration for developers new to GCP provider
</why>

<validation>
<step number="1">Check the provider schema for google_storage_bucket</step>
<step number="2">Run `terraform validate` (fails with "Unsupported block type" for invalid blocks)</step>
<step number="3">Consult Terraform Registry documentation: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket</step>
<step number="4">Look for "Block" vs "Argument" labels in docs</step>
<result-expected>✓ terraform validate passes, no block type errors</result-expected>
<result-failure>✗ Error: Unsupported block type "X" / Blocks of type "X" are not expected here</result-failure>
</validation>

<when-to-apply>
**Apply this rule WHENEVER:**
- Configuring google_storage_bucket resource
- Terraform validate fails with "Unsupported block type"
- Consulting GCP Terraform docs for bucket configuration

**DO NOT apply if:**
- Not using google_storage_bucket (rule is specific to this resource)
- Using different provider version with different schema
</when-to-apply>

<implementation-checklist>
- [ ] Review provider version and schema compatibility
- [ ] Identify which attributes should be blocks vs arguments in documentation
- [ ] Remove unsupported block declarations (like uniform_bucket_level_access)
- [ ] Convert argument blocks to simple assignment (e.g., `public_access_prevention = "enforced"`)
- [ ] Run `terraform validate` to confirm no block type errors
- [ ] Test with `terraform plan` to ensure resource definition is correct
- [ ] Document supported blocks in code comments for team clarity
</implementation-checklist>

<related-rules>
- GCS-PROVIDER-001: Provider version constraints for module compatibility
- GCS-INPUT-002: Module input types (maps vs scalars)
- TF-STRUCTURE-001: Project structure and organization
</related-rules>

<references>
- [Terraform google_storage_bucket Resource](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket)
- [Terraform Block Types vs Arguments](https://www.terraform.io/language/syntax/arguments)
- [GCP Storage Bucket Configuration](https://cloud.google.com/storage/docs/creating-buckets)
</references>
</rule>
