# Terraform Module Scope

<rule id="TF-MODULES-SCOPE" severity="MAJOR" category="Code Quality">
<title>Module Scope: Shallow & Focused</title>

<description>
Keep modules shallow (avoid deep nesting) and focused (one resource group per module).
Each module should be independently understandable and testable.
</description>

<problem>
Deep module nesting and scattered responsibility cause:
- Difficult to understand module dependencies
- Hard to locate where resources are defined
- Complex variable propagation through layers
- Increased debugging difficulty
</problem>

<pattern id="correct">
<title>✅ Shallow, Focused Modules</title>

**Structure: One resource group per module**
```
modules/
├── gcs_bucket/          # ✓ One focus: GCS bucket + IAM
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
│
├── vpc/                 # ✓ One focus: VPC + subnets
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
│
└── compute_instance/    # ✓ One focus: Compute instance
    ├── main.tf
    ├── variables.tf
    └── outputs.tf
```

**Module Responsibility:**
- gcs_bucket: creates bucket, configures versioning, manages IAM bindings
- vpc: creates VPC network, creates subnets, configures routes
- compute_instance: creates VM, attaches disks, configures networking

**Each module is:**
✓ Self-contained  
✓ Can be used independently  
✓ Requires minimal external knowledge  
</pattern>

<antipattern id="incorrect">
<title>❌ Deep Nesting (Avoid)</title>

```
modules/
└── platform/           # Too abstract
    └── cloud/          # Still abstract
        └── gcp/        # Still abstract
            └── storage/
                └── bucket/  # Finally concrete (5 levels!)
                    ├── main.tf
                    └── variables.tf

# Using: module "bucket" { source = "../../../../modules/platform/cloud/gcp/storage/bucket" }
# Problems: Hard to navigate, complex path, unclear dependency
```

**Nested Modules Anti-Pattern:**
```
modules/
├── platform/
│   ├── storage/
│   │   ├── main.tf (calls module.bucket_config)
│   │   └── bucket_config/
│   │       └── main.tf
# Variable propagation: var → module → submodule → resource
# Chain too long, hard to trace
```
</antipattern>

<why>
**Shallow modules are easier to:**
1. Understand at a glance
2. Debug when things fail
3. Test independently
4. Navigate with clear file paths
5. Document (each module has clear scope)

**Deep nesting causes:**
- Cognitive overload (too many levels to track)
- Difficult relative paths (../../../../..)
- Unclear which module is responsible for what
- Testing becomes integration-heavy, not unit-focused
</why>

<when-to-apply>
**Keep modules to 1-2 levels maximum:**
- `modules/gcs_bucket/` ✓ Good
- `modules/platform/cloud/bucket/` ✗ Too deep

**One resource group = one module:**
- Bucket configuration → ONE module
- VPC + subnets → ONE module (they're tightly coupled)
- Compute + networking → Split into separate modules (loose coupling)
</when-to-apply>

<implementation-checklist>
- [ ] Audit existing module nesting depth
- [ ] Flatten modules deeper than 2 levels
- [ ] Verify each module has single clear responsibility
- [ ] Update relative import paths (if refactored)
- [ ] Test all modules: `terraform plan` from each env
- [ ] Document module scope in README
</implementation-checklist>

<related-rules>
- TF-STRUCTURE-001: Project layout
- TF-MODULES-002: Module creation criteria
</related-rules>

</rule>
