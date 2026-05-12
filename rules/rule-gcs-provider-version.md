# GCS Module Best Practices Rules

<rule id="GCS-PROVIDER-VERSION" severity="CRITICAL" scope="gcs" category="Code Quality">
<title>GCS Module Provider Version Constraint</title>

<description>
The terraform-google-modules/cloud-storage/google module has tightly coupled dependencies 
with specific Google provider versions. Version mismatches cause validation failures and 
missing API support.
</description>

<context>
Module: terraform-google-modules/cloud-storage/google
Version: ~> 12.3
Provider Required: >= 6.37.0
</context>

<problem>
The module version ~> 12.3 requires Google provider >= 6.37.0.
Using version ~> 5.0 is insufficient because older provider versions lack required APIs 
and data structures needed by the module.
</problem>

<pattern id="correct">
<title>✅ Correct Pattern</title>
<explanation>Update required_providers block to match module requirements exactly</explanation>

```hcl
required_providers {
  google = {
    source  = "hashicorp/google"
    version = "~> 6.0"  # Provides >= 6.37.0 for module compatibility
  }
}
```
</pattern>

<antipattern id="incorrect">
<title>❌ Common Mistake</title>
<explanation>Using older provider version constraint</explanation>

```hcl
required_providers {
  google = {
    source  = "hashicorp/google"
    version = "~> 5.0"  # ❌ WRONG: Module 12.3 needs >= 6.37.0
  }
}
```

<result>Error during `terraform validate`: Missing required fields or API operations not available in provider version 5.x</result>
</antipattern>

<why>
Module dependencies are tightly coupled to provider versions. 

**Root Cause:** The terraform-google-modules/cloud-storage/google module uses newer GCP APIs 
and data structures that only exist in Google provider version 6.37.0+.

**Consequence:** 
- terraform init: Provider downloads v5.x
- terraform validate: Fails with "unknown field" or "unsupported operation" errors
- Deployment blocked until resolved

**Prevention:** Always pin provider version to match module documentation.
</why>

<validation>
<step number="1">terraform init</step>
<step number="2">terraform validate</step>
<result-expected>✓ Provider version satisfies module requirements</result-expected>
<result-failure>✗ Error: unsupported field X in resource Y (provider version too old)</result-failure>
</validation>

<when-to-apply>
**Apply this rule WHENEVER:**
- Using terraform-google-modules/cloud-storage/google module
- Module version >= 12.x
- Writing required_providers block

**DO NOT apply if:**
- Using older module version (< 12.x) - check its documentation
- Using different provider (not hashicorp/google)
</when-to-apply>

<implementation-checklist>
- [ ] Verify module version in registry: https://registry.terraform.io/modules/terraform-google-modules/cloud-storage/google
- [ ] Check "Required Provider Versions" section of module docs
- [ ] Update required_providers.google.version to match requirement
- [ ] Run `terraform init`
- [ ] Run `terraform validate` - should pass
- [ ] Document provider version in code comments if non-obvious
</implementation-checklist>

<related-rules>
- GCS-INPUT-002: Module input types (map vs scalar)
- GCS-STRUCTURE-003: Environment isolation
</related-rules>

<references>
- Module Registry: https://registry.terraform.io/modules/terraform-google-modules/cloud-storage/google
- Google Provider: https://registry.terraform.io/providers/hashicorp/google/latest
- Module Changelog: Version 12.3 requires provider >= 6.37.0
- Date Discovered: 2024-01-15
- Status: Validated in production
</references>

</rule>
