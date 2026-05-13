# Terraform Version Management Strategy

<rule id="TF-VERSION-MANAGEMENT" severity="CRITICAL" scope="global" category="State Management">
<title>Unified Provider and Terraform Versioning Strategy</title>

<description>
This rule provides a unified strategy for version pinning across a Terraform project. It distinguishes between root configurations (e.g., `envs/dev`) and reusable modules (e.g., `modules/gcs`). An incorrect versioning strategy can lead to dependency conflicts, non-reproducible environments, and unexpected breaking changes.
</description>

<context>
- **Root Configurations:** Standalone projects that have their own backend configuration (e.g., `envs/dev`, `envs/prod`).
- **Reusable Modules:** Abstracted, reusable components of infrastructure (`modules/`).
- **Terraform Core & Providers:** The versions of the `terraform` executable and the providers (`hashicorp/google`, etc.).
</context>

<problem>
Different parts of a project might define conflicting or overly-restrictive version constraints, leading to:
- **Dependency Hell:** `terraform init` fails because Module A requires provider `~> 5.0` while Module B requires `~> 6.0`.
- **Non-Reproducible Builds:** Different developers or CI/CD runs initialize with different provider versions, causing subtle behavioral changes.
- **Inflexible Code:** Hard-coding versions in reusable modules prevents them from being used in projects with different version requirements.
</problem>

<pattern id="correct">
<title>✅ Context-Aware Version Pinning</title>
<explanation>The versioning strategy depends on the context: pin versions in the root, leave them flexible in modules.</explanation>

**1. In Root Configurations (e.g., `envs/dev/main.tf` or `versions.tf`)**
*Pin both Terraform and provider versions.*

```hcl
# In the root configuration (e.g., envs/dev/versions.tf)

terraform {
  required_version = "~> 1.9"  # Pin Terraform to a specific minor version

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"      # Pin the provider to a specific major version
    }
  }
}
```

**2. In Reusable Modules (e.g., `modules/gcs/main.tf`)**
*Omit the `version` attribute entirely. The module should inherit constraints from the calling root configuration.*

```hcl
# In a reusable module (e.g., modules/gcs/versions.tf)

terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      # NO version attribute here.
    }
  }
}
```
</pattern>

<antipattern id="incorrect-1">
<title>❌ Pinning Versions Inside a Reusable Module</title>
<explanation>This creates a rigid module that cannot adapt to different project requirements, often causing dependency conflicts.</explanation>

```hcl
# In a reusable module (e.g., modules/gcs/versions.tf) - WRONG

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"  # ❌ WRONG: This version should be defined by the root config.
    }
  }
}
```
</antipattern>

<antipattern id="incorrect-2">
<title>❌ Not Pinning Versions in the Root Configuration</title>
<explanation>This leads to non-reproducible builds, as Terraform will download the latest available provider version that fits the (absent) constraints.</explanation>

```hcl
# In the root configuration (e.g., envs/dev/versions.tf) - WRONG

terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      # ❌ WRONG: Missing 'version' attribute.
    }
  }
}
```
</antipattern>

<why>
The root configuration is the entry point of a deployment and acts as the single source of truth for operational decisions, including which versions of Terraform and its providers to use. Reusable modules, by contrast, should be flexible and agnostic to the specific versions used, as long as they are compatible. By delegating version control to the root, you centralize dependency management and avoid conflicts.
</why>

<validation>
<step number="1">In all files within `modules/`, run `grep -r 'version\s*='` to ensure no provider versions are pinned.</step>
<step number="2">In the `main.tf` or `versions.tf` of each root configuration (e.g., `envs/dev`), verify that `required_version` and `required_providers` blocks contain specific version constraints (e.g., `~>`).</step>
<step number="3">Run `terraform init` from the root directory. It should complete without any provider version conflicts.</step>
<result-expected>✓ Modules are version-agnostic. Root configurations enforce specific, consistent versions.</result-expected>
<result-failure>✗ A module contains a `version` attribute, or a root configuration is missing one.</result-failure>
</validation>

<when-to-apply>
**Always apply this rule.** It is a foundational practice for managing Terraform projects of any scale.
</when-to-apply>

<implementation-checklist>
- [ ] For every module, ensure no `version` attribute is present in the `required_providers` blocks.
- [ ] For every root configuration, ensure a `versions.tf` file exists (or the content is in `main.tf`) and pins both `required_version` and all provider `version`s.
- [ ] Use pessimistic version constraints (`~>`) to allow non-breaking patch and minor updates.
- [ ] Ensure the `.terraform.lock.hcl` file is committed to version control.
</implementation-checklist>

<related-rules>
- TF-PROVIDER-LOCKING: Provider Lock Files: Commit .terraform.lock.hcl
- TF-BACKEND-STATE: Remote State Management via GCS Backend
</related-rules>

<references>
- Terraform Docs: Provider Requirements - https://developer.hashicorp.com/terraform/language/providers/requirements
- Terraform Docs: Version Constraints - https://developer.hashicorp.com/terraform/language/expressions/version-constraints
</references>

</rule>
