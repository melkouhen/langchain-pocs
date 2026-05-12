# Cloud Run Secrets Management

<rule id="CLOUDRUN-SECRETS-MANAGEMENT" severity="CRITICAL" category="Security">
<title>Use Secret Manager for Sensitive Environment Variables</title>

<description>
Cloud Run services must use Secret Manager for sensitive configuration (API keys, database passwords,
OAuth tokens). Never use cleartext environment variables (`env_vars`) for credentials. Use
`env_secret_vars` to reference Secret Manager secrets, which provides encryption at rest,
access control, versioning, and audit logging.
</description>

<problem>
Storing secrets in cleartext environment variables causes:
- Credentials visible in Terraform state files
- Secrets logged in Cloud Run revision history
- No access control on who can view secrets
- No audit trail of secret access
- Secrets visible in GCP Console UI
- Difficult rotation (requires redeployment)
- Compliance violations (PCI-DSS, HIPAA, SOC2)
</problem>

<pattern id="correct">
<title>✅ Secret Manager Integration</title>

```hcl
# Step 1: Create secrets in Secret Manager
resource "google_secret_manager_secret" "db_password" {
  secret_id = "db-password"
  project   = var.project_id

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "db_password_v1" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = var.db_password  # Provided via terraform.tfvars (not committed)
}

# Step 2: Grant Cloud Run service account access to secrets
resource "google_secret_manager_secret_iam_member" "access" {
  secret_id = google_secret_manager_secret.db_password.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloudrun.email}"
}

# Step 3: Use env_secret_vars in Cloud Run service
module "cloud_run" {
  source  = "GoogleCloudPlatform/cloud-run/google"
  version = "~> 0.2.0"

  service_name = "api-service"
  project_id   = var.project_id
  location     = var.region
  image        = "gcr.io/project/api:latest"

  # ✓ Non-sensitive config in cleartext
  env_vars = [
    {
      name  = "ENVIRONMENT"
      value = "production"
    },
    {
      name  = "LOG_LEVEL"
      value = "info"
    }
  ]

  # ✓ Sensitive config via Secret Manager
  env_secret_vars = [
    {
      name = "DATABASE_PASSWORD"
      value_from = [{
        secret_key_ref = {
          name = google_secret_manager_secret.db_password.secret_id
          key  = "latest"
        }
      }]
    },
    {
      name = "API_KEY"
      value_from = [{
        secret_key_ref = {
          name = google_secret_manager_secret.api_key.secret_id
          key  = "latest"
        }
      }]
    }
  ]

  service_account_email = google_service_account.cloudrun.email
}
```

**Alternative: Volume-mounted Secrets**
```hcl
module "cloud_run" {
  source = "GoogleCloudPlatform/cloud-run/google"
  
  service_name = "api-service"
  project_id   = var.project_id
  location     = var.region
  image        = "gcr.io/project/api:latest"

  # Mount secrets as files
  volumes = [
    {
      name = "secrets-volume"
      secret = {
        secret_name  = google_secret_manager_secret.app_config.secret_id
        default_mode = 256  # 0400 in octal
        items = [
          {
            key  = "latest"
            path = "config.json"
          }
        ]
      }
    }
  ]

  volume_mounts = [
    {
      name       = "secrets-volume"
      mount_path = "/secrets"
    }
  ]
}
```
</pattern>

<antipattern id="incorrect">
<title>❌ Cleartext Credentials in Environment Variables</title>

```hcl
# ❌ WRONG: Credentials in cleartext env_vars
module "cloud_run" {
  source = "GoogleCloudPlatform/cloud-run/google"

  service_name = "api-service"
  project_id   = var.project_id
  location     = var.region
  image        = "gcr.io/project/api:latest"

  env_vars = [
    {
      name  = "DATABASE_PASSWORD"
      value = "SuperSecret123!"  # ❌ Visible in Terraform state!
    },
    {
      name  = "API_KEY"
      value = var.api_key  # ❌ Still stored in state file
    },
    {
      name  = "STRIPE_SECRET_KEY"
      value = "sk_live_xxxxxxxxxxxx"  # ❌ Payment credentials exposed!
    }
  ]
}

# ❌ WRONG: Even using variables doesn't help
variable "database_password" {
  type    = string
  default = "password123"  # ❌ Committed to Git
}

# ❌ WRONG: Sensitive = true only hides from console output, NOT from state
variable "api_key" {
  type      = string
  sensitive = true  # ⚠️ Still stored in plaintext in state file
}
```

**Where secrets leak:**
1. Terraform state file (`.tfstate`)
2. Cloud Run revision history (visible in GCP Console)
3. Git history (if committed)
4. Terraform plan output (if not using `sensitive = true`)
5. Environment variables visible to anyone with Viewer role
</antipattern>

<why>
**Security Benefits of Secret Manager:**
1. **Encryption**: Secrets encrypted at rest with customer-managed or Google-managed keys
2. **Access Control**: IAM policies control who can read secrets
3. **Versioning**: Track secret changes and rollback if needed
4. **Audit Logs**: Cloud Logging records all secret access
5. **Rotation**: Update secrets without redeploying services
6. **Separation**: Secrets stored separately from application code/state

**Compliance Requirements:**
- PCI-DSS: Cryptographic keys must be stored securely
- HIPAA: Access to PHI credentials must be auditable
- SOC2: Secrets must have access controls and audit trails
</why>

<when-to-apply>
**Use Secret Manager for:**
- Database passwords and connection strings
- API keys and tokens (Stripe, SendGrid, etc.)
- OAuth client secrets
- Private keys and certificates
- Encryption keys
- Third-party service credentials
- Webhook signing secrets

**Use cleartext env_vars for:**
- Non-sensitive configuration (log level, feature flags)
- Public endpoints and URLs
- Environment names (dev, staging, prod)
- Service discovery endpoints
</when-to-apply>

<implementation-checklist>
- [ ] Enable Secret Manager API: `gcloud services enable secretmanager.googleapis.com`
- [ ] Audit existing Cloud Run services for cleartext credentials in `env_vars`
- [ ] Create Secret Manager secrets for all sensitive values
- [ ] Store secret versions (use Terraform or `gcloud` CLI)
- [ ] Grant `roles/secretmanager.secretAccessor` to Cloud Run service accounts
- [ ] Update Cloud Run services to use `env_secret_vars` instead of `env_vars`
- [ ] Remove cleartext credentials from Terraform variables
- [ ] Rotate all previously exposed credentials
- [ ] Test service startup with Secret Manager integration
- [ ] Monitor Secret Manager audit logs for unauthorized access
- [ ] Document secret rotation procedures
</implementation-checklist>

<related-rules>
- TF-NO-SECRETS: No hardcoded secrets in Terraform code
- CLOUDRUN-SERVICE-ACCOUNT: Use dedicated service accounts
- TF-BACKEND-STATE: Encrypt state files (secrets may still leak)
</related-rules>

<references>
- https://cloud.google.com/run/docs/configuring/secrets
- https://cloud.google.com/secret-manager/docs/overview
- https://cloud.google.com/secret-manager/docs/access-control
</references>

</rule>
