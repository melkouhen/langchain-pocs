# Forbidden Patterns Reference Guide

**Version**: 1.0  
**Last Updated**: 2026-05-07  
**Severity Level**: CRITIQUE (All patterns block code)

---

## Pattern 1: timestamp() in Resource Identifiers

### Detection
```bash
grep -r "timestamp()" *.tf --include="*.tf" | grep -v "ignore_changes"
```

### Why It's Forbidden
**Reason**: Causes perpetual drift on every `terraform apply`

**Example Problem**:
```hcl
resource "google_storage_bucket" "main" {
  name = "my-bucket-${timestamp()}"  # ❌ WRONG
  # Every apply creates new bucket with new name
}
```

### Impact
- ❌ Resource recreated on every apply
- ❌ Infinite terraform plan diff
- ❌ State file bloat
- ❌ Deployment failures
- ❌ Cost overrun (resources not cleaned up)

### Correct Approach

#### Option 1: Remove timestamp (Recommended)
```hcl
# ✅ CORRECT
resource "google_storage_bucket" "main" {
  name = var.bucket_name  # Static name from variable
}
```

#### Option 2: Use Variables
```hcl
# ✅ CORRECT
variable "creation_date" {
  type    = string
  default = "2026-05-07"  # Static date, set once
}

resource "google_storage_bucket" "main" {
  labels = {
    created_date = var.creation_date
  }
}
```

#### Option 3: Use Resource Metadata
```hcl
# ✅ CORRECT
output "bucket_creation_time" {
  value       = google_storage_bucket.main.time_created
  description = "Bucket creation timestamp from GCP"
}
```

### Auto-Fix Applied
```diff
- created_at = timestamp()
+ # Timestamp removed - use resource metadata instead
```

---

## Pattern 2: timestamp() in Labels

### Detection
```bash
grep -r "timestamp()" *.tf | grep -E "(labels|tags)"
```

### Why It's Forbidden
Same as Pattern 1 - causes perpetual drift

### Specific Example
```hcl
# ❌ WRONG
resource "google_storage_bucket" "main" {
  labels = {
    created_at = timestamp()  # Triggers diff on every apply
    updated_at = timestamp()  # Makes labels mutable
  }
}
```

### Correct Approach
```hcl
# ✅ CORRECT
resource "google_storage_bucket" "main" {
  labels = {
    environment = var.environment
    team        = var.team
    managed_by  = "terraform"
    # Static labels only
  }
  
  lifecycle {
    ignore_changes = [labels]  # If labels might be modified externally
  }
}
```

---

## Pattern 3: random_id() in Resource Names

### Detection
```bash
grep -r "random_id()" *.tf | grep -E "(name|bucket_name|instance_name)"
```

### Why It's Forbidden
Causes resource name changes and untrackable drift

### Example Problem
```hcl
# ❌ WRONG
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "google_storage_bucket" "main" {
  name = "my-bucket-${random_id.bucket_suffix.hex}"  # Name changes!
  # Cannot predict bucket name
}
```

### Impact
- ❌ Bucket name unpredictable
- ❌ Difficult to reference in documentation
- ❌ Not idempotent (different name each run)
- ❌ Violates infrastructure-as-code principles

### Correct Approach

#### Option 1: Use Static Naming
```hcl
# ✅ CORRECT
variable "bucket_name_suffix" {
  type    = string
  default = "my-bucket"
}

resource "google_storage_bucket" "main" {
  name = "${var.bucket_name_suffix}-${var.environment}"
}
```

#### Option 2: Use resource_id from Terraform
```hcl
# ✅ CORRECT
resource "google_storage_bucket" "main" {
  name = "my-bucket-${terraform.workspace}"
  # Using deterministic workspace name
}
```

#### Option 3: Move random_id to Outputs Only
```hcl
# ✅ CORRECT
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# Use for outputs, not in resource names
output "random_identifier" {
  value = random_id.bucket_suffix.hex
}
```

---

## Pattern 4: date() in Resource Identifiers

### Detection
```bash
grep -r "date()" *.tf | grep -E "(name|id|identifier)"
```

### Why It's Forbidden
Changes daily, causes perpetual drift

### Example Problem
```hcl
# ❌ WRONG
resource "google_storage_bucket" "backup" {
  name = "backup-${formatdate("YYYY-MM-DD", timestamp())}"
  # New bucket created every day
}
```

### Correct Approach
```hcl
# ✅ CORRECT
variable "backup_date" {
  type        = string
  description = "Backup date (YYYY-MM-DD format)"
  default     = "2026-05-07"  # Set once, update manually if needed
}

resource "google_storage_bucket" "backup" {
  name = "backup-${var.backup_date}"
}
```

---

## Pattern 5: Hardcoded Credentials in Code

### Detection
```bash
grep -r "password\|secret\|api_key\|token" *.tf | grep "="
```

### Why It's Forbidden
Security vulnerability - credentials exposed in code

### Example Problem
```hcl
# ❌ WRONG
resource "aws_rds_instance" "main" {
  password = "MySecurePassword123"  # Exposed in code!
}

provider "aws" {
  access_key = "AKIAIOSFODNN7EXAMPLE"  # Never hardcode!
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}
```

### Correct Approach
```hcl
# ✅ CORRECT
variable "database_password" {
  type        = string
  sensitive   = true  # Don't show in logs
  description = "RDS instance password"
}

resource "aws_rds_instance" "main" {
  password = var.database_password
}

provider "aws" {
  # Use environment variables or AWS credential files
  # export AWS_ACCESS_KEY_ID
  # export AWS_SECRET_ACCESS_KEY
}
```

---

## Pattern 6: Using for_each with Lists

### Detection
```bash
grep -r "for_each.*\[" *.tf | grep -v "toset"
```

### Why It's Forbidden
Lists don't have stable identifiers, causing resource churn

### Example Problem
```hcl
# ❌ WRONG
variable "bucket_names" {
  type = list(string)
  default = ["bucket-1", "bucket-2", "bucket-3"]
}

resource "google_storage_bucket" "all" {
  for_each = var.bucket_names  # Using list with for_each
  name     = each.value
  # If list order changes, resources are recreated!
}
```

### Correct Approach
```hcl
# ✅ CORRECT - Option 1: Use map
variable "buckets" {
  type = map(object({
    name = string
    region = string
  }))
  default = {
    dev = {
      name = "bucket-dev"
      region = "us-central1"
    }
    prod = {
      name = "bucket-prod"
      region = "europe-west1"
    }
  }
}

resource "google_storage_bucket" "all" {
  for_each = var.buckets
  name     = each.value.name
  location = each.value.region
}

# ✅ CORRECT - Option 2: Convert list to map
variable "bucket_names" {
  type = list(string)
}

resource "google_storage_bucket" "all" {
  for_each = tomap({ for b in var.bucket_names : b => b })
  name     = each.key
}
```

---

## Pattern 7: Using dynamic Blocks Unnecessarily

### Detection
```bash
grep -r "dynamic" *.tf
```

### Why It's Forbidden
Over-abstraction that reduces readability (violates KISS)

### Example Problem
```hcl
# ❌ WRONG - Over-complex
resource "google_storage_bucket" "main" {
  dynamic "versioning" {
    for_each = var.enable_versioning ? [1] : []
    content {
      enabled = true
    }
  }
}
```

### Correct Approach
```hcl
# ✅ CORRECT - Simpler
resource "google_storage_bucket" "main" {
  versioning {
    enabled = var.enable_versioning
  }
}
```

### When dynamic IS Appropriate
```hcl
# ✅ CORRECT - Needed for multiple items
dynamic "cors_rule" {
  for_each = var.cors_rules
  content {
    allowed_headers = cors_rule.value.allowed_headers
    allowed_methods = cors_rule.value.allowed_methods
    allowed_origins = cors_rule.value.allowed_origins
  }
}
```

---

## Pattern 8: Hardcoded Environment Values

### Detection
```bash
grep -r "\"dev\"\|\"prod\"\|\"staging\"" *.tf | grep -v "var\."
```

### Why It's Forbidden
Reduces reusability and causes duplication

### Example Problem
```hcl
# ❌ WRONG
resource "google_storage_bucket" "main" {
  labels = {
    environment = "prod"  # Hardcoded!
  }
}
```

### Correct Approach
```hcl
# ✅ CORRECT
variable "environment" {
  type    = string
  default = "dev"
}

resource "google_storage_bucket" "main" {
  labels = {
    environment = var.environment
  }
}
```

---

## Summary: Forbidden Pattern Checklist

- [ ] ❌ No `timestamp()` in resource names or labels
- [ ] ❌ No `date()` in identifiers
- [ ] ❌ No `random_id()` in resource names
- [ ] ❌ No hardcoded credentials
- [ ] ❌ No hardcoded environment names
- [ ] ❌ No `for_each` with lists
- [ ] ❌ No unnecessary `dynamic` blocks
- [ ] ❌ No hardcoded values (all use variables)

---

## Auto-Remediation Guide

| Pattern | Auto-Fix Strategy |
|---------|-------------------|
| timestamp() | Remove from identifiers/labels, document in comment |
| date() | Replace with variable |
| random_id() | Move to outputs, use deterministic naming |
| Hardcoded creds | Move to variables, mark sensitive=true |
| Hardcoded env | Extract to var.environment |
| for_each lists | Convert to map or use tomap() |
| dynamic blocks | Simplify or document necessity |
| Hardcoded values | Extract all to variables |

---

**Reference Guide Version**: 1.0  
**Last Updated**: 2026-05-07  
**Severity**: All patterns are CRITIQUE (blocking)
