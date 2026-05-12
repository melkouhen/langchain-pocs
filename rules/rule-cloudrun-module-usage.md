# Cloud Run Module Usage

<rule id="CLOUDRUN-MODULE-USAGE" severity="CRITICAL" scope="cloudrun" category="Architecture">
<title>Use Official GoogleCloudPlatform/cloud-run/google Module</title>

<description>
Always use the official GoogleCloudPlatform/cloud-run/google Terraform module instead of declaring
google_cloud_run_service resources directly. The official module provides battle-tested abstractions,
input validation, best practices enforcement, and simplified configuration for Cloud Run services.
</description>

<problem>
Declaring google_cloud_run_service resources directly causes:
- Verbose and error-prone configuration
- Missing best practices (IAM, service accounts, secrets handling)
- No input validation or type checking
- Difficult upgrades when GCP APIs change
- Inconsistent service configurations across environments
- Reinventing abstractions already provided by the module
- Higher maintenance burden for the team
</problem>

<pattern id="correct">
<title>✅ Using Official Cloud Run Module</title>

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

# main.tf
module "cloud_run_service" {
  source  = "GoogleCloudPlatform/cloud-run/google"
  version = "~> 0.12.0"  # Pin to specific version

  service_name = "api-service"
  project_id   = var.project_id
  location     = var.region
  image        = "gcr.io/${var.project_id}/api:latest"

  # Non-sensitive environment variables
  env_vars = [
    {
      name  = "ENVIRONMENT"
      value = var.environment
    },
    {
      name  = "LOG_LEVEL"
      value = "info"
    }
  ]

  # Sensitive variables via Secret Manager
  env_secret_vars = [
    {
      name = "DATABASE_PASSWORD"
      value_from = [{
        secret_key_ref = {
          name = google_secret_manager_secret.db_password.secret_id
          key  = "latest"
        }
      }]
    }
  ]

  # Service account
  service_account_email = google_service_account.cloud_run.email

  # Resource limits
  limits = {
    cpu    = "1000m"
    memory = "512Mi"
  }

  # Autoscaling
  template_annotations = {
    "autoscaling.knative.dev/minScale" = "1"
    "autoscaling.knative.dev/maxScale" = "10"
  }

  # Ingress control
  metadata = {
    annotations = {
      "run.googleapis.com/ingress" = "internal-and-cloud-load-balancing"
    }
  }

  # IAM members who can invoke the service
  members = ["serviceAccount:${google_service_account.frontend.email}"]
}

# Output the service URL
output "service_url" {
  value = module.cloud_run_service.service_url
}
```

**Benefits:**
- ✅ Simplified configuration with sensible defaults
- ✅ Input validation and type checking
- ✅ Automatic IAM policy management
- ✅ Built-in support for secrets, VPC connectors, domain mapping
- ✅ Consistent with Google Cloud best practices
- ✅ Easier to upgrade when APIs change
</pattern>

<antipattern id="incorrect">
<title>❌ Direct Resource Declaration</title>

```hcl
# ❌ WRONG: Declaring google_cloud_run_service directly
resource "google_cloud_run_service" "api" {
  name     = "api-service"
  location = var.region
  project  = var.project_id

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/api:latest"
        
        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }
        
        env {
          name  = "LOG_LEVEL"
          value = "info"
        }
        
        # ❌ Verbose secret configuration
        env {
          name = "DATABASE_PASSWORD"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.db_password.secret_id
              key  = "latest"
            }
          }
        }

        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }
      }

      service_account_name = google_service_account.cloud_run.email
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "1"
        "autoscaling.knative.dev/maxScale" = "10"
      }
    }
  }

  metadata {
    annotations = {
      "run.googleapis.com/ingress" = "internal-and-cloud-load-balancing"
    }
  }

  # ❌ Manual IAM policy management (error-prone)
  lifecycle {
    ignore_changes = [
      metadata[0].annotations["run.googleapis.com/operation-id"],
    ]
  }
}

# ❌ Separate IAM binding resource (easy to forget)
resource "google_cloud_run_service_iam_member" "invoker" {
  service  = google_cloud_run_service.api.name
  location = google_cloud_run_service.api.location
  project  = google_cloud_run_service.api.project
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.frontend.email}"
}
```

**Problems:**
❌ 50+ lines vs 30 lines with module  
❌ Complex nested blocks difficult to read  
❌ No input validation (typos in annotations go undetected)  
❌ Manual lifecycle rules needed  
❌ IAM management separated from service definition  
❌ Difficult to maintain and review  
</antipattern>

<why>
**Module Advantages:**

1. **Abstraction**: Hides GCP API complexity behind simple inputs
2. **Validation**: Type checking prevents configuration errors
3. **Best Practices**: Enforces security and operational standards
4. **Maintainability**: Updates to GCP APIs handled by module maintainers
5. **Consistency**: Same patterns across all Cloud Run services
6. **Documentation**: Well-documented inputs and outputs
7. **Community Support**: Issues and improvements shared across users

**Official Module Features:**
- Automatic IAM policy management (no separate resources)
- Simplified secret management integration
- VPC connector support
- Domain mapping helpers
- Traffic splitting for blue/green deployments
- Validated input types
- Comprehensive examples and documentation

**Team Benefits:**
- Faster development (less boilerplate)
- Fewer errors (validation catches mistakes)
- Easier onboarding (consistent patterns)
- Reduced maintenance burden
</why>

<when-to-apply>
**Always use the module for:**
- All Cloud Run services (APIs, frontends, workers)
- Development, staging, and production environments
- Both public and internal services
- Services with complex configurations (secrets, VPC, domains)

**Direct resource usage is acceptable only for:**
- Learning exercises or experimentation
- Testing module behavior (comparing against direct resources)
- Contributing to the module itself
- Edge cases not supported by the module (rare)

**If the module doesn't support your use case:**
1. Check if there's a newer version with the feature
2. Open an issue on the module repository
3. Consider contributing a PR to add the feature
4. As a last resort, use direct resources with detailed comments explaining why
</when-to-apply>

<implementation-checklist>
- [ ] Audit all direct google_cloud_run_service resources in the codebase
- [ ] Replace each with GoogleCloudPlatform/cloud-run/google module
- [ ] Pin module version to ~> 0.12.0 (or latest stable)
- [ ] Migrate environment variables to env_vars and env_secret_vars
- [ ] Migrate IAM policies to the module's members input
- [ ] Test each service after migration (terraform plan)
- [ ] Verify service URLs and IAM policies in GCP Console
- [ ] Update documentation and examples
- [ ] Train team on module usage patterns
- [ ] Establish policy: all new Cloud Run services must use the module
</implementation-checklist>

<related-rules>
- CLOUDRUN-SECRETS-MANAGEMENT: Secret Manager for sensitive env vars
- CLOUDRUN-INGRESS-SECURITY: Restrictive ingress configuration
- TF-MODULES-DRY: When to create modules (DRY principle)
- TF-VERSION-PINNING: Always pin module versions
</related-rules>

<references>
- https://registry.terraform.io/modules/GoogleCloudPlatform/cloud-run/google/latest
- https://github.com/GoogleCloudPlatform/terraform-google-cloud-run
- https://cloud.google.com/run/docs/reference/rest/v1/namespaces.services
- https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloud_run_service
</references>

</rule>
