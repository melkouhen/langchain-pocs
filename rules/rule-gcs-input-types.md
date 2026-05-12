# GCS Module Input Types Rules

<rule id="GCS-INPUT-TYPES" severity="CRITICAL" category="Code Quality">
<title>Module Input Types: Map vs Scalar</title>

<description>
The terraform-google-modules/cloud-storage/google module expects per-bucket configuration 
as maps, not scalar values. Using scalar types causes validation errors because the module 
supports multiple buckets per invocation.
</description>

<context>
Module: terraform-google-modules/cloud-storage/google
Version: ~> 12.3
Affected Parameters: force_destroy, versioning, lifecycle_rules, and other per-bucket configs
</context>

<problem>
The `force_destroy` parameter expects a map of booleans, not a single boolean value.
This design allows the module to manage multiple buckets in one invocation, requiring 
per-bucket configuration for all settings.

**Common Case:**
```hcl
force_destroy = false  # ❌ WRONG TYPE
```
Causes: `Error during terraform validate: force_destroy must be of type map(bool)`
</problem>

<pattern id="correct">
<title>✅ Correct Pattern: Use Map Syntax</title>
<explanation>Wrap all per-bucket parameters in map syntax using bucket name as key</explanation>

```hcl
force_destroy = {
  (var.bucket_name) = false
}

versioning = {
  (var.bucket_name) = true
}

lifecycle_rules = {
  (var.bucket_name) = [
    {
      action = "Delete"
      age    = 30
    }
  ]
}
```

<note>Key can be hardcoded string or variable reference like `(var.bucket_name)`</note>
</pattern>

<antipattern id="incorrect">
<title>❌ Common Mistake: Scalar Values</title>
<explanation>Using direct boolean or value instead of map structure</explanation>

```hcl
force_destroy = false                    # ❌ WRONG: Expected map(bool)
versioning = true                        # ❌ WRONG: Expected map(bool)
lifecycle_rules = [                      # ❌ WRONG: Expected map(list)
  {
    action = "Delete"
    age    = 30
  }
]
```

<result>Error: force_destroy must be of type map(bool), got bool</result>
</antipattern>

<why>
**Root Cause:** The module is designed to manage multiple GCS buckets in a single module call.
Each bucket needs its own configuration, hence all parameters are maps keyed by bucket name.

**Architecture Decision:** This multi-bucket pattern allows teams to:
- Centralize bucket management in one module invocation
- Apply consistent settings across environments
- Reduce code duplication

**Consequence of Mistake:**
- terraform validate fails immediately
- Code cannot be applied
- Entire Terraform plan blocked
- Common error: developers unfamiliar with module design try scalar values first
</why>

<validation>
<step number="1">Check parameter type in module documentation</step>
<step number="2">Run `terraform validate`</step>
<step number="3">Look for "must be of type map" errors</step>
<result-expected>✓ terraform validate successful</result-expected>
<result-failure>✗ Error: X must be of type map(Y), got Z</result-failure>
</validation>

<when-to-apply>
**Apply this rule WHENEVER:**
- Configuring any per-bucket parameter in terraform-google-modules/cloud-storage/google
- Parameters: force_destroy, versioning, lifecycle_rules, labels, logging, etc.
- Multiple or single bucket configurations

**Key Indicators You Need Maps:**
- Module documentation shows parameter type as `map(...)`
- Error message includes "must be of type map"
- Parameter applies to individual buckets (not global settings)
</when-to-apply>

<implementation-checklist>
- [ ] Review module documentation for all available parameters
- [ ] Identify which parameters are per-bucket (listed as map types)
- [ ] Wrap each per-bucket parameter in `{ (bucket_key) = value }` syntax
- [ ] Test with single bucket first: `(var.bucket_name)` as key
- [ ] Run `terraform validate` - should pass
- [ ] If managing multiple buckets, extend map: `{ bucket1 = val1, bucket2 = val2 }`
</implementation-checklist>

<related-rules>
- GCS-PROVIDER-001: Provider version constraints
- GCS-STRUCTURE-003: Environment isolation
</related-rules>

<examples>
<example number="1">
<title>Single Bucket with Multiple Configurations</title>
<code>
module "gcs_buckets" {
  source  = "terraform-google-modules/cloud-storage/google"
  version = "~> 12.3"
  
  project_id = var.project_id
  names      = ["my-bucket"]
  
  force_destroy = {
    "my-bucket" = false
  }
  
  versioning = {
    "my-bucket" = true
  }
  
  lifecycle_rules = {
    "my-bucket" = [
      {
        action = "Delete"
        age    = 30
      }
    ]
  }
}
</code>
</example>

<example number="2">
<title>Using Variables as Keys</title>
<code>
variable "bucket_name" {
  type = string
}

force_destroy = {
  (var.bucket_name) = false
}

versioning = {
  (var.bucket_name) = true
}
</code>
</example>
</examples>

<references>
- Module Registry: https://registry.terraform.io/modules/terraform-google-modules/cloud-storage/google
- Module Input Variables Section: Lists all parameter types
- Date Discovered: 2024-01-15
- Status: Validated in production
- Related Issue: Common mistake when developers new to this module
</references>

</rule>
