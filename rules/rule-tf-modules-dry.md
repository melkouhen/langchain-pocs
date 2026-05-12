# Terraform Module Creation Criteria

<rule id="TF-MODULES-002" severity="MAJOR" category="Code Quality">
<title>Module Creation Criteria (DRY Principle)</title>

<description>
Create a module only when code is used in 2 or more places. Single-use infrastructure
should remain inline. Unnecessary modularization adds complexity without benefit.
</description>

<problem>
Over-modularization leads to:
- Too many small modules to maintain
- Module overhead (extra variables, outputs) for single-use code
- Harder to understand overall architecture
- Maintenance burden without reuse benefit
</problem>

<pattern id="correct">
<title>✅ When to Modularize</title>

**Create a module IF:**
- Code is used in 2+ environments (e.g., GCS bucket in dev AND prod)
- Code is used in 2+ projects
- Infrastructure component is cohesive and reusable

**EXAMPLE - Module Created for Reuse:**
```hcl
# modules/gcs_bucket/ created because used in:
# - envs/dev/main.tf
# - envs/prod/main.tf
# - envs/staging/main.tf
# ✓ Justified: 3 uses

module "gcs" {
  source = "../../modules/gcs_bucket"
  bucket_name = var.bucket_name
  environment = var.environment
}
```

**EXAMPLE - Keep Inline (No Module):**
```hcl
# Single-use resource: no module needed
# Used only in envs/prod/main.tf, never elsewhere

resource "google_storage_bucket" "backup" {
  name          = "prod-backups"
  location      = "EU"
  force_destroy = false
  
  versioning {
    enabled = true
  }
}
# ✓ Justified: only one use
```
</pattern>

<antipattern id="incorrect">
<title>❌ Over-Modularization</title>

```hcl
# ❌ WRONG: Module created for single use
modules/
├── simple_bucket/
│   ├── main.tf (10 lines)
│   ├── variables.tf
│   └── outputs.tf

# Used only once in envs/prod/main.tf
# Result: 3 extra files for 10 lines of code
```

**Cost of premature modularization:**
- Extra boilerplate (variables.tf, outputs.tf)
- Harder to understand flow (need to jump between files)
- Maintenance burden for no reuse benefit
- Module becomes cargo-cult code
</antipattern>

<why>
**KISS Principle (Keep It Simple, Stupid):**
- Modules have real cost: extra files, imports, documentation
- Benefits only accrue with actual reuse (2+ uses)
- Premature abstraction makes code harder to follow

**Reuse is the Only Justification:**
- If resource is used in multiple places, module reduces duplication
- Single-use resources stay simpler as inline code
- "Rule of Three": Don't abstract until third use (but 2+ is practical threshold)
</why>

<when-to-apply>
**Before creating a module, ask:**
1. Is this code used in 2+ different places?
2. Will this module be maintained separately?
3. Are benefits of parameterization worth the extra files?

If not all "yes", keep code inline.
</when-to-apply>

<implementation-checklist>
- [ ] Audit existing modules: are all used in 2+ places?
- [ ] Remove single-use modules (inline their code into envs/)
- [ ] Document which environments/projects use each module
- [ ] Update module README with use cases
- [ ] Test refactored code: `terraform plan` still works
</implementation-checklist>

<related-rules>
- TF-STRUCTURE-001: Project layout
- TF-MODULES-003: Module scope
</related-rules>

<references>
- Principle: DRY (Don't Repeat Yourself) - applied judiciously
- Status: Validated practice
</references>

</rule>
